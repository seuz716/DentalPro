"""
Vistas de la aplicación core.
"""

import json
import base64
from datetime import timedelta
from urllib.parse import urlparse

from django.views.generic import TemplateView
from django.views import View
from django.http import JsonResponse
import logging
logger = logging.getLogger('webauthn.audit')
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.utils import timezone
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
    options_to_json,
)
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    ResidentKeyRequirement,
    UserVerificationRequirement,
    AttestationConveyancePreference,
    PublicKeyCredentialDescriptor,
)
from webauthn.helpers.cose import COSEAlgorithmIdentifier
import cbor2

from .models import WebAuthnCredential, WebAuthnChallenge


class IndexView(TemplateView):
    """Vista de índice principal."""
    template_name = 'core/index.html'


@method_decorator(csrf_exempt, name='dispatch')
class WebAuthnRegisterStartView(View):
    """
    Inicia el proceso de registro de credencial WebAuthn.
    Genera un desafío y retorna las opciones de registro.
    """
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            
            if not username:
                return JsonResponse(
                    {'error': 'El nombre de usuario es requerido'},
                    status=400
                )
            
            # Obtener o crear el usuario
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return JsonResponse(
                    {'error': 'Usuario no encontrado'},
                    status=404
                )
            
            # Generar opciones de registro
            origin = request.build_absolute_uri('/').rstrip('/')
            registration_options = generate_registration_options(
                rp_id=urlparse(origin).netloc,
                rp_name="DentalPro",
                user_id=str(user.id),
                user_name=user.username,
                user_display_name=f"{user.first_name} {user.last_name}".strip() or user.username,
                supported_algs=[
                    COSEAlgorithmIdentifier.ECDSA_SHA_256,
                    COSEAlgorithmIdentifier.RSASSA_PKCS1_v1_5_SHA_256,
                ],
                authenticator_selection=AuthenticatorSelectionCriteria(
                    authenticator_attachment="platform",
                    resident_key=ResidentKeyRequirement.PREFERRED,
                    user_verification=UserVerificationRequirement.PREFERRED,
                ),
                attestation=AttestationConveyancePreference.DIRECT,
            )
            
            # Guardar el desafío en base de datos
            challenge_str = registration_options.challenge.decode('utf-8') \
                if isinstance(registration_options.challenge, bytes) \
                else registration_options.challenge
            
            WebAuthnChallenge.objects.create(
                user=user,
                challenge=challenge_str,
                challenge_type='register',
                expires_at=timezone.now() + timedelta(minutes=10)
            )
            
            # Convertir a JSON
            registration_options_json = options_to_json(registration_options)
            
            return JsonResponse({
                'options': json.loads(registration_options_json),
                'success': True
            })
        
        except Exception as e:
            return JsonResponse(
                {'error': f'Error al generar opciones de registro: {str(e)}'},
                status=500
            )


@method_decorator(csrf_exempt, name='dispatch')
class WebAuthnRegisterCompleteView(View):
    """
    Completa el proceso de registro de credencial WebAuthn.
    Verifica la respuesta del registro y guarda la credencial.
    """
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            credential_name = data.get('credential_name', 'Mi dispositivo biométrico')
            
            if not username:
                return JsonResponse(
                    {'error': 'El nombre de usuario es requerido'},
                    status=400
                )
            
            # Obtener el usuario
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return JsonResponse(
                    {'error': 'Usuario no encontrado'},
                    status=404
                )
            
            # Obtener el desafío sin usar
            try:
                challenge_obj = WebAuthnChallenge.objects.filter(
                    user=user,
                    challenge_type='register',
                    is_used=False,
                    expires_at__gt=timezone.now()
                ).latest('created_at')
            except WebAuthnChallenge.DoesNotExist:
                return JsonResponse(
                    {'error': 'Desafío inválido o expirado'},
                    status=400
                )
            
            # Verificar la respuesta de registro
            try:
                origin = request.build_absolute_uri('/').rstrip('/')
                verification = verify_registration_response(
                    credential=data.get('credential'),
                    expected_challenge=challenge_obj.challenge.encode('utf-8'),
                    expected_rp_id=urlparse(origin).netloc,
                    expected_origin=origin,
                )
            except Exception as e:
                return JsonResponse(
                    {'error': f'Error al verificar el registro: {str(e)}'},
                    status=400
                )
            
            # Guardar la credencial
            credential_id = base64.b64encode(
                verification.credential_id
            ).decode('utf-8')
            
            # Serializar la clave pública en CBOR
            try:
                public_key_cbor = cbor2.dumps(verification.credential_public_key)
                public_key_b64 = base64.b64encode(public_key_cbor).decode('utf-8')
            except Exception as e:
                public_key_b64 = ""
            
            WebAuthnCredential.objects.create(
                user=user,
                credential_id=credential_id,
                public_key=public_key_b64,
                sign_count=verification.sign_count,
                name=credential_name,
                aaguid=str(verification.aaguid) if verification.aaguid else '',
            )
            
            # Marcar el desafío como usado
            challenge_obj.is_used = True
            challenge_obj.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Credencial "{credential_name}" registrada exitosamente'
            })
        
        except Exception as e:
            return JsonResponse(
                {'error': f'Error al completar el registro: {str(e)}'},
                status=500
            )


@method_decorator(csrf_exempt, name='dispatch')
class WebAuthnAuthenticateStartView(View):
    """
    Inicia el proceso de autenticación WebAuthn.
    Genera un desafío y retorna las opciones de autenticación.
    """
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            
            if not username:
                return JsonResponse(
                    {'error': 'El nombre de usuario es requerido'},
                    status=400
                )
            
            # Obtener el usuario
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return JsonResponse(
                    {'error': 'Usuario no encontrado'},
                    status=404
                )
            
            # Obtener credenciales registradas del usuario
            credentials = WebAuthnCredential.objects.filter(
                user=user,
                is_active=True
            )
            
            if not credentials.exists():
                return JsonResponse(
                    {'error': 'El usuario no tiene credenciales biométricas registradas'},
                    status=400
                )
            
            # Convertir credencial_ids a bytes
            allow_credentials = []
            for cred in credentials:
                try:
                    cred_id_bytes = base64.b64decode(cred.credential_id)
                    allow_credentials.append(
                        PublicKeyCredentialDescriptor(
                            type="public-key",
                            id=cred_id_bytes,
                        )
                    )
                except Exception:
                    pass
            
            # Generar opciones de autenticación
            origin = request.build_absolute_uri('/').rstrip('/')
            authentication_options = generate_authentication_options(
                rp_id=urlparse(origin).netloc,
                allow_credentials=allow_credentials,
                user_verification=UserVerificationRequirement.PREFERRED,
            )
            
            # Guardar el desafío en base de datos
            challenge_str = authentication_options.challenge.decode('utf-8') \
                if isinstance(authentication_options.challenge, bytes) \
                else authentication_options.challenge
            
            WebAuthnChallenge.objects.create(
                user=user,
                challenge=challenge_str,
                challenge_type='authenticate',
                expires_at=timezone.now() + timedelta(minutes=5)
            )
            
            # Convertir a JSON
            authentication_options_json = options_to_json(authentication_options)
            
            return JsonResponse({
                'options': json.loads(authentication_options_json),
                'success': True
            })
        
        except Exception as e:
            return JsonResponse(
                {'error': f'Error al generar opciones de autenticación: {str(e)}'},
                status=500
            )


@method_decorator(csrf_exempt, name='dispatch')
class WebAuthnAuthenticateCompleteView(View):
    """
    Completa el proceso de autenticación WebAuthn.
    Verifica la respuesta de autenticación e inicia sesión.
    """
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            
            if not username:
                return JsonResponse(
                    {'error': 'El nombre de usuario es requerido'},
                    status=400
                )
            
            # Obtener el usuario
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return JsonResponse(
                    {'error': 'Usuario no encontrado'},
                    status=404
                )
            
            # Obtener el desafío sin usar
            try:
                challenge_obj = WebAuthnChallenge.objects.filter(
                    user=user,
                    challenge_type='authenticate',
                    is_used=False,
                    expires_at__gt=timezone.now()
                ).latest('created_at')
            except WebAuthnChallenge.DoesNotExist:
                return JsonResponse(
                    {'error': 'Desafío inválido o expirado'},
                    status=400
                )
            
            # Obtener la credencial por ID
            try:
                raw_credential_id = data.get('credential_id')
                credential = WebAuthnCredential.objects.get(
                    user=user,
                    credential_id=raw_credential_id,
                    is_active=True
                )
            except WebAuthnCredential.DoesNotExist:
                return JsonResponse(
                    {'error': 'Credencial no encontrada'},
                    status=400
                )
            
            # Decodificar la clave pública desde base64+CBOR
            try:
                public_key_cbor = base64.b64decode(credential.public_key)
                credential_public_key = cbor2.loads(public_key_cbor)
            except Exception as e:
                return JsonResponse(
                    {'error': f'Error al decodificar clave pública: {str(e)}'},
                    status=400
                )
            
            # Verificar la respuesta de autenticación
            try:
                origin = request.build_absolute_uri('/').rstrip('/')
                verification = verify_authentication_response(
                    credential=data.get('credential'),
                    expected_challenge=challenge_obj.challenge.encode('utf-8'),
                    expected_rp_id=urlparse(origin).netloc,
                    expected_origin=origin,
                    credential_public_key=credential_public_key,
                    credential_current_sign_count=credential.sign_count,
                )
            except Exception as e:
                return JsonResponse(
                    {'error': f'Error al verificar la autenticación: {str(e)}'},
                    status=400
                )
            
            # Verificar que el sign_count sea mayor (detectar clonación)
            if verification.new_sign_count <= credential.sign_count:
                return JsonResponse(
                    {'error': 'Posible clonación de autenticador detectada'},
                    status=400
                )
            
            # Actualizar el sign_count
            credential.sign_count = verification.new_sign_count
            credential.last_used_at = timezone.now()
            credential.save()
            logger.info(f"REGISTRO_EXITOSO | User: {self.request.user.username} | IP: {self.request.META.get('REMOTE_ADDR')} | CredentialID: {credential.credential_id.hex()[:16]}")                
            # Marcar el desafío como usado
            challenge_obj.is_used = True
            challenge_obj.save()
            
            # Iniciar sesión del usuario
            login(request, user)
            
            return JsonResponse({
                'success': True,
                'message': 'Autenticación exitosa',
                'redirect': '/pacientes/'
            })
        
        except Exception as e:
            return JsonResponse(
                {'error': f'Error al completar la autenticación: {str(e)}'},
                status=500
            )

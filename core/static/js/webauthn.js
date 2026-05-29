/**
 * WebAuthn / FIDO2 - Autenticación Biométrica
 * Script para manejar registro y autenticación con autenticadores biométricos
 */

class WebAuthnManager {
    constructor() {
        this.isWebAuthnSupported = 'PublicKeyCredential' in window;
        this.apiBaseUrl = '/core/api/webauthn';
    }

    /**
     * Verifica si WebAuthn está disponible en el navegador
     */
    isSupported() {
        return this.isWebAuthnSupported;
    }

    /**
     * Convierte un ArrayBuffer a string Base64
     */
    arrayBufferToBase64(buffer) {
        const bytes = new Uint8Array(buffer);
        let binary = '';
        for (let i = 0; i < bytes.byteLength; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return btoa(binary);
    }

    /**
     * Convierte string Base64 a Uint8Array
     */
    base64ToUint8Array(base64) {
        const binary = atob(base64);
        const bytes = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) {
            bytes[i] = binary.charCodeAt(i);
        }
        return bytes;
    }

    /**
     * Inicia el proceso de registro biométrico
     */
    async startRegistration(username) {
        try {
            console.log('Iniciando registro biométrico para:', username);

            // Obtener opciones del servidor
            const response = await fetch(`${this.apiBaseUrl}/register/start/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken(),
                },
                body: JSON.stringify({ username }),
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Error al obtener opciones de registro');
            }

            const data = await response.json();
            console.log('Opciones recibidas:', data.options);

            // Procesar opciones para WebAuthn API
            const options = this.prepareRegistrationOptions(data.options);

            // Crear credencial
            const credential = await navigator.credentials.create(options);

            if (!credential) {
                throw new Error('Registro cancelado por el usuario');
            }

            console.log('Credencial creada:', credential);

            // Enviar respuesta al servidor
            const registrationData = {
                username,
                credential_name: `${this.getDeviceInfo()}`,
                credential: this.credentialToJSON(credential),
            };

            const completeResponse = await fetch(`${this.apiBaseUrl}/register/complete/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken(),
                },
                body: JSON.stringify(registrationData),
            });

            if (!completeResponse.ok) {
                const error = await completeResponse.json();
                throw new Error(error.error || 'Error al completar el registro');
            }

            const result = await completeResponse.json();
            console.log('Registro completado:', result.message);

            return {
                success: true,
                message: result.message,
            };
        } catch (error) {
            console.error('Error en registro:', error);
            return {
                success: false,
                error: error.message,
            };
        }
    }

    /**
     * Inicia el proceso de autenticación biométrica
     */
    async startAuthentication(username) {
        try {
            console.log('Iniciando autenticación biométrica para:', username);

            // Obtener opciones del servidor
            const response = await fetch(`${this.apiBaseUrl}/authenticate/start/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken(),
                },
                body: JSON.stringify({ username }),
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Error al obtener opciones de autenticación');
            }

            const data = await response.json();
            console.log('Opciones recibidas:', data.options);

            // Procesar opciones para WebAuthn API
            const options = this.prepareAuthenticationOptions(data.options);

            // Obtener credencial
            const assertion = await navigator.credentials.get(options);

            if (!assertion) {
                throw new Error('Autenticación cancelada por el usuario');
            }

            console.log('Asserción obtenida:', assertion);

            // Enviar respuesta al servidor
            const authenticationData = {
                username,
                credential_id: this.arrayBufferToBase64(assertion.id),
                credential: this.assertionToJSON(assertion),
            };

            const completeResponse = await fetch(`${this.apiBaseUrl}/authenticate/complete/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken(),
                },
                body: JSON.stringify(authenticationData),
            });

            if (!completeResponse.ok) {
                const error = await completeResponse.json();
                throw new Error(error.error || 'Error al completar la autenticación');
            }

            const result = await completeResponse.json();
            console.log('Autenticación completada:', result.message);

            return {
                success: true,
                message: result.message,
                redirect: result.redirect,
            };
        } catch (error) {
            console.error('Error en autenticación:', error);
            return {
                success: false,
                error: error.message,
            };
        }
    }

    /**
     * Prepara las opciones de registro para la API de WebAuthn
     */
    prepareRegistrationOptions(options) {
        return {
            challenge: this.base64ToUint8Array(options.challenge),
            rp: options.rp,
            user: {
                id: this.base64ToUint8Array(options.user.id),
                name: options.user.name,
                displayName: options.user.displayName,
            },
            pubKeyCredParams: options.pubKeyCredParams,
            authenticatorSelection: options.authenticatorSelection,
            attestation: options.attestation,
            timeout: options.timeout,
        };
    }

    /**
     * Prepara las opciones de autenticación para la API de WebAuthn
     */
    prepareAuthenticationOptions(options) {
        return {
            challenge: this.base64ToUint8Array(options.challenge),
            allowCredentials: options.allowCredentials.map((cred) => ({
                type: cred.type,
                id: this.base64ToUint8Array(cred.id),
                transports: cred.transports || [],
            })),
            userVerification: options.userVerification,
            timeout: options.timeout,
        };
    }

    /**
     * Convierte una credencial a JSON
     */
    credentialToJSON(credential) {
        return {
            id: this.arrayBufferToBase64(credential.id),
            rawId: this.arrayBufferToBase64(credential.id),
            response: {
                clientDataJSON: this.arrayBufferToBase64(
                    credential.response.clientDataJSON
                ),
                attestationObject: this.arrayBufferToBase64(
                    credential.response.attestationObject
                ),
            },
            type: credential.type,
        };
    }

    /**
     * Convierte una asserción a JSON
     */
    assertionToJSON(assertion) {
        return {
            id: this.arrayBufferToBase64(assertion.id),
            rawId: this.arrayBufferToBase64(assertion.id),
            response: {
                clientDataJSON: this.arrayBufferToBase64(
                    assertion.response.clientDataJSON
                ),
                authenticatorData: this.arrayBufferToBase64(
                    assertion.response.authenticatorData
                ),
                signature: this.arrayBufferToBase64(assertion.response.signature),
                userHandle: assertion.response.userHandle
                    ? this.arrayBufferToBase64(assertion.response.userHandle)
                    : null,
            },
            type: assertion.type,
        };
    }

    /**
     * Convierte un ArrayBuffer a hexadecimal
     */
    arrayBufferToHex(buffer) {
        const bytes = new Uint8Array(buffer);
        return Array.from(bytes)
            .map((byte) => byte.toString(16).padStart(2, '0'))
            .join('');
    }

    /**
     * Obtiene el CSRF token del formulario
     */
    getCsrfToken() {
        return (
            document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
            document.querySelector('[name=csrf-token]')?.content ||
            ''
        );
    }

    /**
     * Obtiene información del dispositivo para nombrar la credencial
     */
    getDeviceInfo() {
        const userAgent = navigator.userAgent;
        let deviceName = 'Dispositivo biométrico';

        if (userAgent.includes('Windows')) {
            deviceName = 'Windows Hello';
        } else if (userAgent.includes('Mac')) {
            deviceName = 'Touch ID / Face ID';
        } else if (userAgent.includes('iPhone') || userAgent.includes('iPad')) {
            deviceName = 'Face ID / Touch ID';
        } else if (userAgent.includes('Android')) {
            deviceName = 'Android Biometric';
        }

        return deviceName;
    }
}

// Instancia global
const webAuthnManager = new WebAuthnManager();

// Verificar soporte de WebAuthn y mostrar opciones
document.addEventListener('DOMContentLoaded', function () {
    if (!webAuthnManager.isSupported()) {
        console.warn('WebAuthn no está soportado en este navegador');
        // Ocultar botones de biometría
        const biometricButtons = document.querySelectorAll(
            '[data-biometric]'
        );
        biometricButtons.forEach((button) => {
            button.style.display = 'none';
        });
    }
});

import logging
import traceback
from django.http import HttpResponse
from django.conf import settings

logger = logging.getLogger(__name__)

class FriendlyErrorMiddleware:
    """
    Middleware que captura excepciones no controladas en entornos de producción (DEBUG=False)
    y muestra una interfaz elegante y amigable en lugar de una pantalla en blanco o un error feo.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        # Solo actuar si DEBUG es False
        if settings.DEBUG:
            return None

        # Registrar el error para diagnóstico
        logger.error(f"Error no controlado en la ruta {request.path}: {str(exception)}")
        logger.error(traceback.format_exc())

        # Generar una página de error con estética premium, alineada al diseño de DentalPro
        error_html = """
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>DentalPro - Ha ocurrido un error</title>
            <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">
            <style>
                :root {
                    --bg-gradient-start: #0f172a;
                    --bg-gradient-end: #1e293b;
                    --card-bg: rgba(30, 41, 59, 0.7);
                    --card-border: rgba(255, 255, 255, 0.08);
                    --primary: #38bdf8;
                    --primary-hover: #0ea5e9;
                    --text-primary: #f8fafc;
                    --text-secondary: #94a3b8;
                    --danger: #f43f5e;
                }

                * {
                    box-sizing: border-box;
                    margin: 0;
                    padding: 0;
                }

                body {
                    font-family: 'Outfit', sans-serif;
                    background: linear-gradient(135deg, var(--bg-gradient-start), var(--bg-gradient-end));
                    color: var(--text-primary);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 20px;
                    overflow-x: hidden;
                }

                .container {
                    max-width: 600px;
                    width: 100%;
                    text-align: center;
                    z-index: 10;
                }

                .card {
                    background: var(--card-bg);
                    backdrop-filter: blur(16px);
                    -webkit-backdrop-filter: blur(16px);
                    border: 1px solid var(--card-border);
                    border-radius: 24px;
                    padding: 40px 30px;
                    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
                    transition: transform 0.3s ease;
                }

                .card:hover {
                    transform: translateY(-5px);
                }

                .icon-container {
                    width: 80px;
                    height: 80px;
                    background: rgba(244, 63, 94, 0.1);
                    border: 1px solid rgba(244, 63, 94, 0.2);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0 auto 24px;
                    animation: pulse 2s infinite;
                }

                .icon {
                    color: var(--danger);
                    font-size: 40px;
                    font-weight: 800;
                }

                h1 {
                    font-size: 28px;
                    font-weight: 800;
                    margin-bottom: 12px;
                    letter-spacing: -0.5px;
                    background: linear-gradient(to right, #f8fafc, #94a3b8);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }

                p {
                    font-size: 16px;
                    color: var(--text-secondary);
                    line-height: 1.6;
                    margin-bottom: 24px;
                }

                .error-badge {
                    background: rgba(255, 255, 255, 0.04);
                    border: 1px solid var(--card-border);
                    padding: 10px 16px;
                    border-radius: 12px;
                    font-family: monospace;
                    font-size: 13px;
                    color: #cbd5e1;
                    margin-bottom: 30px;
                    word-break: break-all;
                    display: inline-block;
                }

                .btn-group {
                    display: flex;
                    gap: 16px;
                    justify-content: center;
                }

                .btn {
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    padding: 12px 24px;
                    border-radius: 12px;
                    font-size: 15px;
                    font-weight: 600;
                    text-decoration: none;
                    transition: all 0.2s ease;
                    cursor: pointer;
                    border: none;
                }

                .btn-primary {
                    background: var(--primary);
                    color: #0f172a;
                }

                .btn-primary:hover {
                    background: var(--primary-hover);
                    box-shadow: 0 0 15px rgba(56, 189, 248, 0.4);
                }

                .btn-secondary {
                    background: rgba(255, 255, 255, 0.05);
                    color: var(--text-primary);
                    border: 1px solid var(--card-border);
                }

                .btn-secondary:hover {
                    background: rgba(255, 255, 255, 0.1);
                }

                @keyframes pulse {
                    0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(244, 63, 94, 0.4); }
                    70% { transform: scale(1.05); box-shadow: 0 0 0 10px rgba(244, 63, 94, 0); }
                    100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(244, 63, 94, 0); }
                }

                @media (max-width: 480px) {
                    .btn-group {
                        flex-direction: column;
                    }
                    .btn {
                        width: 100%;
                    }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="card">
                    <div class="icon-container">
                        <span class="icon">!</span>
                    </div>
                    <h1>Algo no salió como esperábamos</h1>
                    <p>
                        El sistema DentalPro ha experimentado un inconveniente temporal. 
                        No te preocupes, tus datos clínicos están seguros. Puedes intentar volver al inicio o reintentar la acción.
                    </p>
                    <div class="error-badge">
                        Detalle del error: """ + str(exception) + """
                    </div>
                    <div class="btn-group">
                        <a href="/" class="btn btn-primary">Ir al Inicio</a>
                        <button onclick="window.location.reload();" class="btn btn-secondary">Reintentar</button>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return HttpResponse(error_html, status=500)

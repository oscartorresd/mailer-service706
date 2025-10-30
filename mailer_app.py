from flask import Flask, request, jsonify
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Cc

app = Flask(__name__)

# Configuración de SendGrid
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

DESTINATARIOS = [
    "laura@example.com",
    "administracion@example.com"
]

COPIA = "oscar.torres@example.com"
REMITENTE = "tu-correo-verificado@sendgrid.net"


@app.route('/', methods=['POST'])
def handle_webhook():
    try:
        payload = request.get_json()
        print("✅ Webhook recibido desde Tally")

        # --- Extraer campos ---
        fields = {f["label"]: f.get("value") for f in payload["data"]["fields"]}

        # --- Datos principales ---
        nombre = fields.get("Nombres", "")
        apellidos = fields.get("Apellidos", "")
        tipo_doc = fields.get("Tipo de identificación", "")
        num_doc = fields.get("Número de identificación", "")
        check_in = fields.get("Check-in", "")
        check_out = fields.get("Check-out", "")
        num_acompanantes = fields.get("Número de acompañantes", "0")

        # --- Datos acompañante (si existen) ---
        nom_a = fields.get("Nombres (acompañante)")
        ape_a = fields.get("Apellidos (acompañante)")
        tipo_a = fields.get("Tipo de identificación (acompañante)")
        num_a = fields.get("Número de identificación (acompañante)")

        # --- Lista de huéspedes ---
        lista_html = f"<li>{nombre} {apellidos}, {tipo_doc}: {num_doc}</li>"
        if num_acompanantes in ["1", 1, "uno", "Uno"] and nom_a and num_a:
            lista_html += f"<li>{nom_a} {ape_a}, {tipo_a}: {num_a}</li>"

        # --- Cuerpo del correo HTML ---
        cuerpo_html = f"""
        <div style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
            <p>Buen día,</p>

            <p>
            Sra. Laura, conforme a las instrucciones recibidas de los guardias, mediante el presente correo 
            <strong>autorizo el acceso al Apartamento 706</strong> a las siguientes personas:
            </p>

            <ul style="margin-left: 20px;">
                {lista_html}
            </ul>

            <p>
                <strong>Período de acceso:</strong><br>
                Desde el <strong>{check_in}</strong> a las 15:00 hasta el <strong>{check_out}</strong> a las 11:00.
            </p>

            <p>
                Estas personas son huéspedes autorizados únicamente para ingresar al apartamento y no cuentan con permisos para extraer ningún elemento.
                Agradeceré que esta información sea comunicada a los guardias.
            </p>

            <p>De antemano, agradezco su atención y colaboración.</p>

            <p style="margin-top: 25px;">
                <strong>Oscar Torres</strong><br>
                Apto 706<br>
                Cel. 3152887992
            </p>

            <hr style="margin-top: 25px; border: none; border-top: 1px solid #ddd;">
            <p style="font-size: 12px; color: #777;">
                Este mensaje fue generado automáticamente mediante el formulario de registro de huéspedes Airbnb.
            </p>
        </div>
        """

        # --- Construcción del correo ---
        asunto = f"Autorización de acceso - Apto 706 ({check_in} a {check_out})"

        message = Mail(
            from_email=Email(REMITENTE, name="Oscar Torres - Apto 706"),
            to_emails=[To(email) for email in DESTINATARIOS],
            cc_emails=[Cc(COPIA)],
            subject=asunto,
            html_content=cuerpo_html
        )

        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)

        print(f"📤 Correo enviado correctamente (status {response.status_code}) a {DESTINATARIOS} con copia a {COPIA}")
        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("❌ Error procesando webhook:", str(e))
        return jsonify({"error": str(e)}), 500


@app.route('/', methods=['GET'])
def home():
    return "📬 Mailer activo (versión final con fechas en asunto)", 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

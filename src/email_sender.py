import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Datos del remitente
remitente = "park.ESI@gmail.com"
contraseña = "eLmEjOrPaRkInGdElMuNdO_13071"

def send_emails(emails):
    for mail in emails:
        # Enviar el correo
        try:
            # Crear el mensaje
            mensaje = MIMEMultipart()
            mensaje["From"] = remitente
            mensaje["To"] = mail
            mensaje["Subject"] = "Aviso por bloqueo"

            # Cuerpo del mensaje
            cuerpo = "Hola,\n\nUn vehículo del parking está siendo bloqueado por uno de sus vehículos y se requiere su liberación.\
                \n\nPor favor, mueva su vehículo con la máxima brevedad.\n\n\t- ParkESI"
            mensaje.attach(MIMEText(cuerpo, "plain"))

            # Conexión con el servidor SMTP de Gmail
            servidor = smtplib.SMTP("smtp.gmail.com", 587)
            servidor.starttls()  # Cifrar la conexión
            servidor.login(remitente, contraseña)
            servidor.sendmail(remitente, mail, mensaje.as_string())
            print("Correo enviado correctamente ")
        except Exception as e:
            print(f"Error al enviar el correo: {e}")
        finally:
            servidor.quit()

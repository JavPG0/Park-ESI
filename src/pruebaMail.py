import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Datos del remitente y destinatario
remitente = "javierpalominogomez04@gmail.com"
destinatario = "aloncampi@gmail.com"
contraseña = "biyt miwg qivl ktri"


# Crear el mensaje
mensaje = MIMEMultipart()
mensaje["From"] = remitente
mensaje["To"] = destinatario
mensaje["Subject"] = "Prueba de envío de correo con Python"

# Cuerpo del mensaje
cuerpo = "Hola,\n\nEste es un correo enviado desde un script de Python.\n\nSaludos!"
mensaje.attach(MIMEText(cuerpo, "plain"))

# Enviar el correo
try:
    # Conexión con el servidor SMTP de Gmail
    servidor = smtplib.SMTP("smtp.gmail.com", 587)
    servidor.starttls()  # Cifrar la conexión
    servidor.login(remitente, contraseña)
    servidor.sendmail(remitente, destinatario, mensaje.as_string())
    print("Correo enviado correctamente ")
except Exception as e:
    print(f"Error al enviar el correo: {e}")
finally:
    servidor.quit()

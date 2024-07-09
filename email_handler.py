import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config

def send_email(to_email, subject, body):
    email_sender = config.email_sender
    email_password = config.email_password
    
    smtp_server = config.smtp_server
    smtp_port = config.smtp_port

    # Costruisci il messaggio email
    msg = MIMEMultipart()
    msg['From'] = email_sender
    msg['To'] = ",".join(to_email)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Connetti al server SMTP e invia l'email
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(email_sender, email_password)
    server.sendmail(email_sender, to_email, msg.as_string())
    server.quit()

import smtplib, os
from dotenv import load_dotenv
from email.mime.text import MIMEText

def configure():
    load_dotenv()
    

def send_email(request):
    
    configure()
    
    email_from = os.getenv('EMAIL_FROM')
    email_to = os.getenv('EMAIL_TO')
    email_password = os.getenv('EMAIL_PASSWORD')
    email_smtp = os.getenv('EMAIL_SMTP')
    
    print(f'Sendinf email from {email_from} to {email_to}')
    
    subject = 'New credentials request'
    body = f'User {request.user.username} requested new credentials for {request.POST.get("Conectar")}'
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = email_from
    msg['To'] = email_to
    
    try:
        smtp_server = smtplib.SMTP_SSL(email_smtp, 465)
        smtp_server.login(email_from, email_password)
        smtp_server.sendmail(email_from, email_to, msg.as_string())
        smtp_server.quit()
        print('Email sent!')
    except Exception as e:
        print(f'Error sending email: {e}')
        pass   
    
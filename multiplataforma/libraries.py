class Mail:

    def __init__(self):
        self.port = 465
        self.smtp_server_domain_name = "smtp.gmail.com"
        self.sender_mail = "myplataformadigital@gmail.com"
        self.password = "calidad+2022"

    def send(self, emails, subject, content):
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        username = self.sender_mail
        password = self.password
        mail_from = self.sender_mail
        mail_to = emails
        mail_subject = subject
        mail_body = content

        mimemsg = MIMEMultipart()
        mimemsg['From'] = mail_from
        mimemsg['To'] = mail_to
        mimemsg['Subject'] = mail_subject
        mimemsg.attach(MIMEText(mail_body, 'plain'))
        connection = smtplib.SMTP(host='smtp.gmail.com', port=587)
        connection.starttls()
        connection.login(username, password)
        connection.send_message(mimemsg)
        connection.quit()


def sendmail(objeto, mensaje, enviador, receptor):
    from django.core.mail import send_mail
    send_mail(objeto, mensaje, enviador, receptor, fail_silently=False)
    return None
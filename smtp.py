from email import encoders
import os
import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class SMTP:

    server = None

    def __init__(self, port: int, host: str, sender_email: str, sender_password: str, receiver_email: str):
        self.PORT = port
        self.HOST = host
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.receiver_email = receiver_email
        self.server = smtplib.SMTP(self.HOST, self.PORT)

    def start(self) -> None:
        """ start smtp connection """
        self.server.starttls()
        self.server.login(self.sender_email, self.sender_password)

    def create_mail(self, attachments: list = None, subject: str = "Python SMTP", body: str = "") -> str:
        mail = MIMEMultipart()
        mail["From"] = self.sender_email
        mail["To"] = self.receiver_email
        mail["Subject"] = subject
        mail_body = MIMEText(body)
        mail.attach(mail_body)
        if attachments:
            # attach files
            for file_path in attachments:
                attachment = open(file_path, "rb")
                base = MIMEBase('application', 'octet-stream')
                base.set_payload(attachment.read())
                encoders.encode_base64(base)
                base.add_header("Content-Disposition", f"attachment; filename= {os.path.basename(file_path)}")
                mail.attach(base)
        return mail.as_string()

    def send_mail(self, message: str, receiver: str = None) -> None:
        if not receiver:
            receiver = self.receiver_email
        try:
            self.server.sendmail(self.sender_email, receiver, message)
        except:
            self.start()
            self.send_mail(message, receiver)

    def mail(self, attachments: list = None, subject: str = "Python SMTP", body: str = "") -> None:
        created_mail = self.create_mail(attachments, subject, body)
        self.send_mail(created_mail)

    def send_mails(self, message: str, receivers: list = None) -> None:
        for receiver in receivers:
            self.send_mail(message, receiver)

    def close(self) -> None:
        self.server.close()

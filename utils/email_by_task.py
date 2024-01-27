import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import formataddr
from . import configuration
# from logger import Logger
# from models import Email
# from utils.db_conn import create_db
from datetime import datetime
# logger = Logger(__name__)


class EmailSender:
    def __init__(self, email):
        self.sPath = 'config.ini'
        self.email_config = configuration.Configuration(self.sPath)
        self.sender_email = self.email_config.read('EMAIL', 'Sender')
        self.password = self.email_config.read('EMAIL', 'Password')
        self.smtp_server = self.email_config.read('EMAIL', 'SmtpServer')
        self.email = email
        # self.session = create_db()

    def send_email(self, receiver_email, subject, body, image_url=None):
        try:
            # Create a multipart message and set headers
            message = MIMEMultipart("alternative")
            message['From'] = formataddr(
                (self.email_config.read('EMAIL', 'From'), self.sender_email))
            message["To"] = receiver_email
            # message["Bcc"] = ", ".join(receiver_email)
            message["Subject"] = subject

            # print(image_url)
            if image_url:
                with open(image_url, 'rb') as f:
                    img_data = f.read()
                    image = MIMEImage(img_data, name=image_url)
                    image.add_header('Content-ID', '<image1>')
                    message.attach(image)

            # Attach body to the message
            message.attach(MIMEText(body, 'html'))

            # Log in to server using secure context and send email
            # context = ssl.create_default_context()
            # with smtplib.SMTP_SSL(self.smtp_server, 465, context=context) as server:
            #     server.login(self.sender_email, self.password)
            #     server.send_message(message, self.sender_email, receiver_email)

            conn = smtplib.SMTP(self.smtp_server, 587)
            conn.starttls()
            conn.login(self.sender_email, self.password)
            conn.sendmail(self.sender_email, receiver_email,
                          message.as_string())
            # self.add_log()

        except Exception as e:
            # logger.error(str(e))
            print(e)
            pass

    # def add_log(self):
    #     try:
    #         email_data = Email(Subject=self.subject,
    #                            Email=self.email, CreateDate=datetime.now())
    #         # add the instance to the session and commit the transaction
    #         self.session.add(email_data)
    #         self.session.commit()
    #     except Exception as e:
    #         # logger.error(str(e))
    #         self.session.rollback()


class OTPEmail(EmailSender):
    def __init__(self, email, lang='TC'):
        super().__init__(email)
        self.subject = self.email_config.read(f'OTP_{lang.upper()}', 'Subject')
        with open(self.email_config.read(f'OTP_{lang.upper()}', 'Template'), encoding='utf-8') as f:
            self.body_template = f.read()

    def send_otp_email(self, email, otp):
        try:
            # Create email body            
            body = self.body_template.replace("OTP", str(otp))          
            # Send email
            # print(body)
            self.send_email(email, self.subject, body)
        except Exception as e:
            # logger.error(str(e))
            pass

class Change_Pwd_Email(EmailSender):
    def __init__(self, email, lang='TC'):
        super().__init__(email)
        self.subject = self.email_config.read(f'CHANGE_PWD_{lang.upper()}', 'Subject')
        with open(self.email_config.read(f'CHANGE_PWD_{lang.upper()}', 'Template'), encoding='utf-8') as f:
            self.body_template = f.read()

    def send_otp_email(self, email, otp):
        try:
            # Create email body            
            body = self.body_template.replace("OTP", str(otp))          
            # Send email
            # print(body)
            self.send_email(email, self.subject, body)
        except Exception as e:
            # logger.error(str(e))
            pass



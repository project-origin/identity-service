import sendgrid
from sendgrid.helpers.mail import Email, Content, Mail, To
from urllib.parse import urlencode

from .models import User
from .settings import (
    EMAIL_FROM_NAME,
    EMAIL_FROM_ADDRESS,
    SENDGRID_API_KEY,
    PROJECT_URL)


WELCOME_TEMPLATE = """Dear %(name)s

Your account on behalf of %(company)s has been created.

To activate your account and login, click or copy/paste this link in your browser:

%(url)s
"""


RESET_PASSWORD_TEMPLATE = """Dear %(name)s

To reset your password, click or copy/paste this link in your browser to reset your password:

%(url)s

Your verification code is:

%(reset_password_token)s
"""


class EmailService(object):

    @property
    def client(self):
        """
        :rtype: sendgrid.SendGridAPIClient
        """
        return sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)

    def send_welcome_email(self, user, challenge):
        """
        :param User user:
        :param str challenge:
        """
        query = urlencode({
            'email': user.email,
            'challenge': challenge,
            'activate_token': user.activate_token,
        })

        env = {
            'url': f'{PROJECT_URL}/verify-email?{query}',
            'name': user.name,
            'company': user.company,
        }

        body = WELCOME_TEMPLATE % env

        from_email = Email(EMAIL_FROM_ADDRESS, EMAIL_FROM_NAME)
        to_email = To(user.email)
        subject = 'Activate your account'
        content = Content('text/plain', body)
        mail = Mail(from_email, to_email, subject, content)

        self.client.client.mail.send.post(request_body=mail.get())

    def send_reset_password_email(self, user, challenge):
        """
        :param User user:
        :param str challenge:
        """
        query = urlencode({
            'email': user.email,
            'challenge': challenge,
            'verification_code': user.reset_password_token,
        })

        env = {
            'url': f'{PROJECT_URL}/enter-verification-code?{query}',
            'name': user.name,
            'company': user.company,
            'reset_password_token': user.reset_password_token,
        }

        body = RESET_PASSWORD_TEMPLATE % env

        from_email = Email(EMAIL_FROM_ADDRESS, EMAIL_FROM_NAME)
        to_email = To(user.email)
        subject = 'Reset password'
        content = Content('text/plain', body)
        mail = Mail(from_email, to_email, subject, content)

        self.client.client.mail.send.post(request_body=mail.get())


email_service = EmailService()

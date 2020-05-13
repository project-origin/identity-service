import sendgrid
from sendgrid.helpers.mail import Email, Content, Mail, To
from urllib.parse import urlencode

from .models import User
from .settings import (
    EMAIL_FROM_NAME,
    EMAIL_FROM_ADDRESS,
    SENDGRID_API_KEY,
    PROJECT_URL)


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

    def send_email(self, email, subject, body):
        """
        :param str email:
        :param str subject:
        :param str body:
        """
        pass

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
        response = self.client.client.mail.send.post(request_body=mail.get())
        print(response.status_code)
        print(response.body)
        print(response.headers)


email_service = EmailService()

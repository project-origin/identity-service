from .models import User


class EmailService(object):

    def send_email(self, email, subject, body):
        """
        :param str email:
        :param str subject:
        :param str body:
        """
        pass

    def send_reset_password_email(self, user):
        """
        :param User user:
        """
        pass


email_service = EmailService()

import hashlib
from uuid import uuid4

from .db import atomic, inject_session
from .models import User
from .settings import SECRET


class UserRegistry(object):

    @atomic
    def create(self, name, company, email, password, session):
        """
        :param str name:
        :param str company:
        :param str email:
        :param str password:
        :param Session session:
        :rtype: User
        """
        session.add(User(
            subject=str(uuid4()),
            email=self.normalize_email(email),
            password=self.password_hash(password),
            name=name,
            company=company,
        ))

    @inject_session
    def authenticate(self, email, password, session):
        """
        :param str email:
        :param str password:
        :param Session session:
        :rtype: User
        """
        filters = (
            User.email == self.normalize_email(email),
            User.password == self.password_hash(password),
        )

        return session.query(User) \
            .filter(*filters) \
            .one_or_none()

    @inject_session
    def get_user(self, session, **filters):
        """
        :param Session session:
        :rtype: User
        """
        return session.query(User) \
            .filter_by(**filters) \
            .one_or_none()

    def email_available(self, email):
        """
        :param str email:
        :rtype: bool
        """
        return self.get_user(email=self.normalize_email(email)) is None

    def normalize_email(self, email):
        """
        :param str email:
        :rtype: str
        """
        return email.strip().lower()

    def password_hash(self, password):
        """
        :param str password:
        :rtype: str
        """
        return hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), SECRET.encode('utf-8'), 100000).hex()


registry = UserRegistry()

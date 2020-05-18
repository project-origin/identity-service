import sqlalchemy as sa

from .db import ModelBase


class User(ModelBase):
    """
    Represents one used in the system who is able to authenticate.
    """
    __tablename__ = 'user'
    __table_args__ = (
        sa.UniqueConstraint('subject'),
        sa.UniqueConstraint('email'),
    )

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    created = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())
    active = sa.Column(sa.Boolean(), default=False, nullable=True)

    # Hydra Subject ID
    subject = sa.Column(sa.String(), index=True, nullable=False)

    # Details
    email = sa.Column(sa.String(), index=True, nullable=False)
    phone = sa.Column(sa.String(), index=True)
    password = sa.Column(sa.String(), nullable=False)
    name = sa.Column(sa.String(), nullable=False)
    company = sa.Column(sa.String(), nullable=False)

    # Token for activating / verifying e-mail
    activate_token = sa.Column(sa.String())

    # Token for resetting password
    reset_password_token = sa.Column(sa.String())

    def __str__(self):
        return 'User<%s>' % self.sub

    @property
    def id_token(self):
        return {
            'email': self.email,
            'phone': self.phone,
            'name': self.name,
            'company': self.company,
        }


VERSIONED_DB_MODELS = (
    User,
)

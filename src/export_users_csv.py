import sys
import csv

from identity.models import User
from identity.db import inject_session


@inject_session
def export_users_csv(session):

    writer = csv.writer(sys.stdout)
    writer.writerow((
        'id',
        'subject',
        'active',
        'name',
        'company',
        'email',
        'phone',
    ))

    for user in session.query(User):
        writer.writerow((
            user.id,
            user.subject,
            user.active,
            user.name,
            user.company,
            user.email,
            user.phone,
        ))

    sys.stdout.flush()


export_users_csv()

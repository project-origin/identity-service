import sys
import logging

from flask import Flask
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect

from .controllers import login, consent, register
from .settings import (
    DEBUG,
    SECRET,
    CORS_ORIGINS,
    TEMPLATES_DIR,
    STATIC_DIR,
)

# Import models here for SQLAlchemy to detech them
from .models import *


# -- Logging -----------------------------------------------------------------

if DEBUG:
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


# -- Flask setup -------------------------------------------------------------

app = Flask(
    import_name=__name__,
    template_folder=TEMPLATES_DIR,
    static_url_path='/static',
    static_folder=STATIC_DIR,
)

app.config['SECRET_KEY'] = SECRET

cors = CORS(app, resources={r'*': {'origins': CORS_ORIGINS}})
csrf = CSRFProtect(app)


# -- URLs/routes setup -------------------------------------------------------

app.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])
app.add_url_rule('/consent', 'consent', consent, methods=['GET', 'POST'])
app.add_url_rule('/register', 'register', register, methods=['GET', 'POST'])

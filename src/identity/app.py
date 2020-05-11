import logging
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from opencensus.ext.azure.log_exporter import AzureLogHandler

from .settings import (
    SECRET,
    TEMPLATES_DIR,
    STATIC_DIR,
    AZURE_APP_INSIGHTS_CONN_STRING,
)
from .controllers import (
    login,
    consent,
    register,
    logout,
    terms,
    error_handler,
    reset_password,
    enter_verification_code,
    change_password,
)

# Import models here for SQLAlchemy to detect them
from .models import *


# -- Flask setup -------------------------------------------------------------

app_kwargs = dict(
    import_name=__name__,
    template_folder=TEMPLATES_DIR,
    static_url_path='/static',
    static_folder=STATIC_DIR,
)

app = Flask(**app_kwargs)
app.logger.setLevel(logging.DEBUG)
app.config['SECRET_KEY'] = SECRET


if AZURE_APP_INSIGHTS_CONN_STRING:
    print('Exporting logs to Azure Application Insight', flush=True)

    handler = AzureLogHandler(
        connection_string=AZURE_APP_INSIGHTS_CONN_STRING,
        export_interval=5.0,
    )
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)


csrf = CSRFProtect(app)


# -- URLs/routes setup -------------------------------------------------------

app.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])
app.add_url_rule('/logout', 'logout', logout, methods=['GET'])
app.add_url_rule('/consent', 'consent', consent, methods=['GET', 'POST'])
app.add_url_rule('/register', 'register', register, methods=['GET', 'POST'])
app.add_url_rule('/terms', 'terms', terms, methods=['GET'])
app.add_url_rule('/reset-password', 'reset-password', reset_password, methods=['GET', 'POST'])
app.add_url_rule('/enter-verification-code', 'enter-verification-code', enter_verification_code, methods=['GET', 'POST'])
app.add_url_rule('/change-password', 'change-password', change_password, methods=['GET', 'POST'])
app.register_error_handler(404, error_handler)
app.register_error_handler(500, error_handler)

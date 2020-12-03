import logging
import os

from flask import Flask, send_from_directory
from flask_wtf.csrf import CSRFProtect
from opencensus.trace import config_integration
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.ext.flask.flask_middleware import FlaskMiddleware
from opencensus.trace.samplers import AlwaysOnSampler

from .settings import (
    SECRET,
    TEMPLATES_DIR,
    STATIC_DIR,
    AZURE_APP_INSIGHTS_CONN_STRING,
    PROJECT_NAME,
    LOG_LEVEL,
)
from .controllers import (
    login,
    consent,
    register,
    verify_email,
    logout,
    terms,
    error_handler,
    reset_password,
    enter_verification_code,
    change_password,
    edit_profile,
    disable_user,
    revoke_consent,
    show_oauth2_clients,
    delete_client,
)

# Import models here for SQLAlchemy to detect them
from .models import *


config_integration.trace_integrations(['requests'])
config_integration.trace_integrations(['sqlalchemy'])


# -- Flask setup -------------------------------------------------------------

app_kwargs = dict(
    import_name=PROJECT_NAME,
    template_folder=TEMPLATES_DIR,
    static_url_path='/static',
    static_folder=STATIC_DIR,
)

app = Flask(**app_kwargs)
app.logger.setLevel(LOG_LEVEL)
app.config['SECRET_KEY'] = SECRET


if AZURE_APP_INSIGHTS_CONN_STRING:
    print('Exporting logs to Azure Application Insight', flush=True)

    def __telemetry_processor(envelope):
        envelope.data.baseData.cloud_roleName = PROJECT_NAME
        envelope.tags['ai.cloud.role'] = PROJECT_NAME

    handler = AzureLogHandler(
        connection_string=AZURE_APP_INSIGHTS_CONN_STRING,
        export_interval=5.0,
    )
    handler.add_telemetry_processor(__telemetry_processor)
    handler.setLevel(LOG_LEVEL)
    app.logger.setLevel(LOG_LEVEL)
    app.logger.addHandler(handler)

    exporter = AzureExporter(connection_string=AZURE_APP_INSIGHTS_CONN_STRING)
    exporter.add_telemetry_processor(__telemetry_processor)

    FlaskMiddleware(
        app=app,
        sampler=AlwaysOnSampler(),
        exporter=exporter,
    )


csrf = CSRFProtect(app)


# -- URLs/routes setup -------------------------------------------------------


app.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])
app.add_url_rule('/logout', 'logout', logout, methods=['GET'])
app.add_url_rule('/consent', 'consent', consent, methods=['GET', 'POST'])
app.add_url_rule('/register', 'register', register, methods=['GET', 'POST'])
app.add_url_rule('/verify-email', 'verify-email', verify_email, methods=['GET'])
app.add_url_rule('/terms', 'terms', terms, methods=['GET'])
app.add_url_rule('/reset-password', 'reset-password', reset_password, methods=['GET', 'POST'])
app.add_url_rule('/enter-verification-code', 'enter-verification-code', enter_verification_code, methods=['GET', 'POST'])
app.add_url_rule('/change-password', 'change-password', change_password, methods=['GET', 'POST'])
app.add_url_rule('/edit-profile', 'edit-profile', edit_profile, methods=['GET', 'POST'])
app.add_url_rule('/disable-user', 'disable-user', disable_user, methods=['GET', 'POST'])
app.add_url_rule('/revoke-consent', 'revoke-consent', revoke_consent, methods=['GET', 'POST'])
app.add_url_rule('/clients', 'clients', show_oauth2_clients, methods=['GET', 'POST'])
app.add_url_rule('/clients/delete', 'delete-client', delete_client, methods=['GET'])
app.register_error_handler(404, error_handler)
app.register_error_handler(500, error_handler)

import os


DEBUG = os.environ.get('DEBUG') in ('1', 't', 'true', 'yes')

# -- Project -----------------------------------------------------------------

PROJECT_NAME = 'IdentityService'
PROJECT_URL = os.environ['PROJECT_URL']
SECRET = os.environ['SECRET']
TOKEN_EXPIRE_MINUTES = int(os.environ['TOKEN_EXPIRE_MINUTES'])
FAILURE_REDIRECT_URL = os.environ['FAILURE_REDIRECT_URL']


# -- Directories/paths -------------------------------------------------------

__current_file = os.path.abspath(__file__)
__current_folder = os.path.split(__current_file)[0]

SOURCE_DIR = os.path.abspath(os.path.join(__current_folder, '..'))
MIGRATIONS_DIR = os.path.join(SOURCE_DIR, 'migrations')
ALEMBIC_CONFIG_PATH = os.path.join(MIGRATIONS_DIR, 'alembic.ini')
TEMPLATES_DIR = os.path.join(SOURCE_DIR, 'templates')
STATIC_DIR = os.path.join(SOURCE_DIR, 'static')


# -- Database ----------------------------------------------------------------

SQL_ALCHEMY_SETTINGS = {
    'echo': DEBUG,
    'pool_pre_ping': True,
    'pool_size': int(os.environ['DATABASE_CONN_POLL_SIZE']),
}

DATABASE_URI = os.environ['DATABASE_URI']


# -- Auth/tokens -------------------------------------------------------------


HYDRA_URL = os.environ['HYDRA_URL']
HYDRA_AUTH_ENDPOINT = f'{HYDRA_URL}/oauth2/auth'
HYDRA_TOKEN_ENDPOINT = f'{HYDRA_URL}/oauth2/token'
HYDRA_USER_ENDPOINT = f'{HYDRA_URL}/userinfo'
HYDRA_WANTED_SCOPES = (
    'openid',
    'offline',
    'profile',
    'email',
    'meteringpoints.read',
    'measurements.read',
    'ggo.read',
    'ggo.transfer',
    'ggo.retire',
)


# -- Misc --------------------------------------------------------------------

AZURE_APP_INSIGHTS_CONN_STRING = os.environ.get(
    'AZURE_APP_INSIGHTS_CONN_STRING')

EMAIL_FROM_NAME = os.environ['EMAIL_FROM_NAME']
EMAIL_FROM_ADDRESS = os.environ['EMAIL_FROM_ADDRESS']
SENDGRID_API_KEY = os.environ['SENDGRID_API_KEY']

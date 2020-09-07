import json

from marshmallow import EXCLUDE
from requests import get, put, post, delete
from dataclasses import dataclass
from typing import List, Dict
from marshmallow_dataclass import class_schema
from datetime import datetime
from urllib.parse import urlencode

from identity.scopes import SCOPES
from identity.settings import HYDRA_URL, HYDRA_WANTED_SCOPES


@dataclass
class Client:
    client_id: str
    client_name: str
    redirect_uris: List[str]
    grant_types: List[str]
    response_types: List[str]
    scope: str
    owner: str
    policy_uri: str
    tos_uri: str
    client_uri: str
    logo_uri: str

    allowed_cors_origins: List[str]
    subject_type: str
    client_secret_expires_at: int
    jwks: Dict[str, str]
    created_at: datetime
    token_endpoint_auth_method: str
    updated_at: datetime
    contacts: List[str]
    metadata: Dict[str, str]
    userinfo_signed_response_alg: str
    audience: List[str]

    class Meta:
        unknown = EXCLUDE


@dataclass
class BaseRequest:
    challenge: str
    client: Client
    request_url: str
    requested_access_token_audience: List[str]
    requested_scope: List[str]
    skip: bool
    subject: str

    class Meta:
        unknown = EXCLUDE

    @property
    def scopes_readable(self) -> List[str]:
        return [SCOPES.get(s, s) for s in self.requested_scope]


@dataclass
class LoginRequest(BaseRequest):
    session_id: str

    class Meta:
        unknown = EXCLUDE


@dataclass
class ConsentRequest(BaseRequest):
    acr: str
    login_challenge: str
    login_session_id: str

    class Meta:
        unknown = EXCLUDE


@dataclass
class Session:
    access_token: Dict[str, str]
    id_token: Dict[str, str]

    class Meta:
        unknown = EXCLUDE


@dataclass
class GrantConsent:
    grant_access_token_audience: List[str]
    grant_scope: List[str]
    handled_at: str
    remember: bool
    remember_for: int
    session: Session

    class Meta:
        unknown = EXCLUDE


@dataclass
class LoginAccept:
    subject: str
    remember: bool
    remember_for: int

    class Meta:
        unknown = EXCLUDE


@dataclass
class RejectConsent:
    error: str
    error_debug: str
    error_description: str
    error_hint: str
    status_code: int

    class Meta:
        unknown = EXCLUDE


@dataclass
class RedirectResponse:
    redirect_to: str

    class Meta:
        unknown = EXCLUDE


@dataclass
class ConsentClient:
    client_id: str
    client_name: str

    class Meta:
        unknown = EXCLUDE


@dataclass
class Consent:
    grant_scope: List[str]
    consent_request: ConsentRequest

    class Meta:
        unknown = EXCLUDE

    @property
    def client_name(self) -> str:
        return self.consent_request.client.client_name

    @property
    def client_id(self) -> str:
        return self.consent_request.client.client_id

    @property
    def scopes_readable(self) -> List[str]:
        return [SCOPES.get(s, s) for s in self.grant_scope]


# Schema instances

redirect_schema = class_schema(RedirectResponse)()
reject_schema = class_schema(RejectConsent)()

login_request_schema = class_schema(LoginRequest)(unknown="EXCLUDE")
login_accept_schema = class_schema(LoginAccept)()

consent_request_schema = class_schema(ConsentRequest)(unknown="EXCLUDE")
grant_consent_schema = class_schema(GrantConsent)(unknown="EXCLUDE")

consent_schema = class_schema(Consent)(unknown="EXCLUDE")


class HydraException(Exception):
    pass


class Hydra:
    def __init__(self, url):
        self.url = url

    def get_login_request(self, challenge: str) -> LoginRequest:
        url = f'{self.url}/oauth2/auth/requests/login'
        params = {'login_challenge': challenge}

        response = get(url, params=params, verify=False)

        if response.status_code == 200:
            return login_request_schema.loads(response.content)
        else:
            raise HydraException(f'{response.status_code} from server: {response.content.decode()}')

    def accept_login(self, challenge: str, request: LoginAccept) -> RedirectResponse:
        url = f'{self.url}/oauth2/auth/requests/login/accept'
        headers = {'Content-Type': 'application/json'}
        params = {'login_challenge': challenge}
        data = login_accept_schema.dumps(request)

        response = put(url, data=data, headers=headers, params=params, verify=False)

        if response.status_code == 200:
            return redirect_schema.loads(response.content)
        else:
            # 409 Unable to insert or update resource because a resource with that value exists already
            raise HydraException(f'{response.status_code} from server: {response.content.decode()}')

    def reject_login(self, challenge: str, rejection: RejectConsent) -> RedirectResponse:
        url = f'{self.url}/oauth2/auth/requests/login/reject'
        headers = {'Content-Type': 'application/json'}
        params = {'login_challenge': challenge}
        data = reject_schema.dumps(rejection)

        response = put(url, data=data, headers=headers, params=params, verify=False)

        if response.status_code == 200:
            return redirect_schema.loads(response.content)
        else:
            raise HydraException(f'{response.status_code} from server: {response.content.decode()}')

    def accept_logout(self, challenge: str) -> RedirectResponse:
        url = f'{self.url}/oauth2/auth/requests/logout/accept'
        headers = {'Accept': 'application/json'}
        params = {'logout_challenge': challenge}

        response = put(url, headers=headers, params=params, verify=False)

        if response.status_code == 200:
            return redirect_schema.loads(response.content)
        else:
            raise HydraException(f'{response.status_code} from server: {response.content.decode()}')

    def get_consents(self, subject: str) -> List[Consent]:
        url = f'{self.url}/oauth2/auth/sessions/consent'
        headers = {'Content-Type': 'application/json'}
        params = {'subject': subject}

        response = get(url, headers=headers, params=params, verify=False)

        if response.status_code == 200:
            print(f'\n\n{response.content}\n\n')
            return consent_schema.loads(response.content, many=True)
        else:
            raise HydraException(f'{response.status_code} from server: {response.content.decode()}')

    def get_consent_request(self, challenge: str) -> ConsentRequest:
        query = urlencode({'consent_challenge': challenge})
        url = f'{self.url}/oauth2/auth/requests/consent?{query}'

        response = get(url, verify=False)

        if response.status_code == 200:
            return consent_request_schema.loads(response.content)
        else:
            raise HydraException(f'{response.status_code} from server: {response.content.decode()}')

    def accept_consent(self, challenge: str, request: GrantConsent) -> RedirectResponse:
        url = f'{self.url}/oauth2/auth/requests/consent/accept'
        headers = {'Content-Type': 'application/json'}
        params = {'consent_challenge': challenge}
        data = grant_consent_schema.dumps(request)

        response = put(url, data=data, headers=headers, params=params, verify=False)

        if response.status_code == 200:
            return redirect_schema.loads(response.content)
        else:
            raise HydraException(f'{response.status_code} from server: {response.content.decode()}')

    def reject_consent(self, challenge: str, rejection: RejectConsent) -> RedirectResponse:
        url = f'{self.url}/oauth2/auth/requests/consent/reject'
        headers = {'Content-Type': 'application/json'}
        params = {'consent_challenge': challenge}
        data = reject_schema.dumps(rejection)

        response = put(url, data=data, headers=headers, params=params, verify=False)

        if response.status_code == 200:
            return redirect_schema.loads(response.content)
        else:
            raise HydraException(f'{response.status_code} from server: {response.content.decode()}')

    def revoke_consent(self, subject: str, client_id: str) -> List[Consent]:
        url = f'{self.url}/oauth2/auth/sessions/consent'
        headers = {'Content-Type': 'application/json'}
        params = {'subject': subject, 'client': client_id}

        response = delete(url, headers=headers, params=params, verify=False)

        if response.status_code != 204:
            raise HydraException(f'{response.status_code} from server: {response.content.decode()}')

    # -- Management endpoints ------------------------------------------------

    def create_oauth2_client(self, owner, client_id, client_name, client_secret, client_callback):
        url = f'{self.url}/clients'
        headers = {'Content-Type': 'application/json'}
        data = json.dumps({
            'owner': owner,
            'client_id': client_id,
            'client_name': client_name,
            'client_secret': client_secret,
            'redirect_to': client_callback,
            'redirect_uris': [client_callback],
            'scope': ','.join(HYDRA_WANTED_SCOPES),
            'grant_types': ['authorization_code', 'refresh_token'],
            'response_types': ['token', 'code', 'id_token'],
        })

        response = post(url, data=data, headers=headers, verify=False)

        if response.status_code != 201:
            raise HydraException(f'{response.status_code} from server: {response.content.decode()}')

    def get_oauth2_clients(self):
        query = urlencode({
            'offset': 0,
            'limit': 99999,
        })

        url = f'{self.url}/clients?{query}'

        response = get(url, verify=False)

        if response.status_code == 200:
            return json.loads(response.content)
        else:
            raise HydraException(f'{response.status_code} from server: {response.content.decode()}')

    def delete_oauth2_client(self, client_id):
        url = f'{self.url}/clients/{client_id}'

        response = delete(url, verify=False)

        if response.status_code not in (200, 204):
            raise HydraException(f'{response.status_code} from server: {response.content.decode()}')


hydra = Hydra(HYDRA_URL)

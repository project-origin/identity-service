from requests import get, put
from dataclasses import dataclass, field
from typing import List, Dict
from marshmallow_dataclass import class_schema
from datetime import datetime
from urllib.parse import urlencode


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


@dataclass
class BaseRequest:
    challenge: str
    client: Client
    request_url: str
    requested_access_token_audience: List[str]
    requested_scope: List[str]
    skip: bool
    subject: str


@dataclass
class LoginRequest(BaseRequest):
    session_id: str


@dataclass
class ConsentRequest(BaseRequest):
    acr: str
    login_challenge: str
    login_session_id: str


@dataclass
class Session:
    access_token: Dict[str, str]
    id_token: Dict[str, str]


@dataclass
class GrantConsent:
    grant_access_token_audience: List[str]
    grant_scope: List[str]
    handled_at: str
    remember: bool
    remember_for: int
    session: Session


@dataclass
class LoginAccept:
    subject: str
    remember: bool
    remember_for: int


@dataclass
class RejectConsent:
    error: str
    error_debug: str
    error_description: str
    error_hint: str
    status_code: int


@dataclass
class RedirectResponse:
    redirect_to: str


# Schema instances

redirect_schema = class_schema(RedirectResponse)()
reject_schema = class_schema(RejectConsent)()

login_request_schema = class_schema(LoginRequest)(unknown="EXCLUDE")
login_accept_schema = class_schema(LoginAccept)()

consent_request_schema = class_schema(ConsentRequest)(unknown="EXCLUDE")
grant_consent_schema = class_schema(GrantConsent)(unknown="EXCLUDE")


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

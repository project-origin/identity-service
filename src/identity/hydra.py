import json
from requests import get, put, post
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from marshmallow_dataclass import class_schema
from datetime import datetime


@dataclass
class Client:
    client_id: str = field()
    client_name: str = field()
    redirect_uris: List[str] = field()
    grant_types: List[str] = field()
    response_types: List[str] = field()
    scope: str = field()
    owner: str = field()
    policy_uri: str = field()
    tos_uri: str = field()
    client_uri: str = field()
    logo_uri: str = field()

    allowed_cors_origins: List[str] = field()
    subject_type: str = field()
    client_secret_expires_at: int = field()
    jwks: Dict[str, str] = field()
    created_at: datetime = field()
    token_endpoint_auth_method: str = field()
    updated_at: datetime = field()
    contacts: List[str] = field()
    metadata: Dict[str, str] = field()
    userinfo_signed_response_alg: str = field()
    audience: List[str] = field()


@dataclass
class BaseRequest:
    challenge: str = field()

    client: Client = field()
    request_url: str = field()
    requested_access_token_audience: List[str] = field()
    requested_scope: List[str] = field()
    skip: bool = field()
    subject: str = field()


@dataclass
class LoginRequest(BaseRequest):
    session_id: str = field()


@dataclass
class ConsentRequest(BaseRequest):
    acr: str = field()
    login_challenge: str = field()
    login_session_id: str = field()


@dataclass
class Session:
    access_token: Dict[str, str] = field()
    id_token: Dict[str, str] = field()


@dataclass
class GrantConsent():
    grant_access_token_audience: List[str] = field()
    grant_scope: List[str] = field()
    handled_at: str = field()
    remember: bool = field()
    remember_for: int = field()
    session: Session = field()


@dataclass
class LoginAccept:
    subject: str = field()
    remember: bool = field()
    remember_for: int = field()


@dataclass
class RejectConcent:
    error: str = field()
    error_debug: str = field()
    error_description: str = field()
    error_hint: str = field()
    status_code: int = field()


@dataclass
class RedirectResponse:
    redirect_to: str = field()


redirect_schema = class_schema(RedirectResponse)()
reject_schema = class_schema(RejectConcent)()

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

        data = login_accept_schema.dumps(request)

        # data = json.dumps(request)
        # print('\n', 'login:', json.dumps(request), '\n')

        response = put(f'{self.url}/oauth2/auth/requests/login/accept?login_challenge={challenge}',
                       data=data,
                       headers={'Content-Type': 'application/json'},
                       verify=False)

        if response.status_code == 200:
            return redirect_schema.loads(response.content)

        # 409 Unable to insert or update resource because a resource with that value exists already

        else:
            print(response)
            print(response.content)
            raise HydraException("Bad response from auth server.")

    def reject_login(self, challenge: str, rejection: RejectConcent) -> RedirectResponse:

        response = put(f'{self.url}/oauth2/auth/requests/login/reject?login_challenge={challenge}',
                       data=reject_schema.dumps(rejection),
                       headers={'Content-Type': 'application/json'},
                       verify=False)

        if response.status_code == 200:
            return redirect_schema.loads(response.content)

        else:
            print(response)
            print(response.content)
            raise HydraException("Bad response from auth server.")

    def get_consent_request(self, challenge: str) -> ConsentRequest:

        response = get(f'{self.url}/oauth2/auth/requests/consent?consent_challenge={challenge}',
                       verify=False)

        if response.status_code == 200:
            return consent_request_schema.loads(response.content)

        else:
            print(response)
            print(response.content)
            raise HydraException("Bad response from auth server.")

    def accept_consent(self, challenge: str, request: GrantConsent) -> RedirectResponse:

        print('\n', 'consent', grant_consent_schema.dumps(request), '\n')

        response = put(f'{self.url}/oauth2/auth/requests/consent/accept?consent_challenge={challenge}',
                       data=grant_consent_schema.dumps(request),
                       headers={'Content-Type': 'application/json'},
                       verify=False)

        if response.status_code == 200:
            return redirect_schema.loads(response.content)

        else:
            print(response)
            print(response.content)
            raise HydraException("Bad response from auth server.")

    def reject_consent(self, challenge: str, rejection: RejectConcent) -> RedirectResponse:

        response = put(f'{self.url}/oauth2/auth/requests/consent/reject?consent_challenge={challenge}',
                       data=reject_schema.dumps(rejection),
                       headers={'Content-Type': 'application/json'},
                       verify=False)

        if response.status_code == 200:
            return redirect_schema.loads(response.content)

        else:
            print(response)
            print(response.content)
            raise HydraException("Bad response from auth server.")

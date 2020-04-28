from datetime import datetime, timezone
from flask import request, render_template, redirect, url_for

from .forms import LoginForm, RegisterForm, ConsentForm
from .registry import registry
from .settings import (
    HYDRA_URL,
    TOKEN_EXPIRE_MINUTES,
    FAILURE_REDIRECT_URL,
)

from .hydra import (
    Hydra,
    HydraException,
    Session,
    LoginAccept,
    GrantConsent,
    RejectConcent,
)


LOGIN_ERROR_MSG = 'The email / password combination is not correct'


hydra = Hydra(HYDRA_URL)


def register():
    """
    TODO
    """
    form = RegisterForm()
    challenge = request.args.get('challenge')

    if not challenge:
        return get_unknown_response()

    if form.validate_on_submit():
        registry.create(
            name=form.name.data,
            company=form.company.data,
            email=form.email.data,
            password=form.password.data,
        )
        return redirect(url_for('login', login_challenge=challenge))

    env = {
        'form': form,
        'login_url': url_for('login', login_challenge=challenge),
    }

    return render_template('register.html', **env)


def login():
    """
    TODO
    """
    form = LoginForm()
    challenge = request.args.get('login_challenge')
    error = None

    if not challenge:
        return get_unknown_response()

    try:
        login_request = hydra.get_login_request(challenge)
    except HydraException:
        # TODO logging
        raise
        return get_unknown_response()

    # Already logged in (remembered)?
    if login_request.skip:
        res = hydra.accept_login(challenge, LoginAccept(
            subject=login_request.subject,
            remember=login_request.skip,
            remember_for=TOKEN_EXPIRE_MINUTES,
        ))
        return redirect(res.redirect_to)

    # Login form submitted and validated correctly?
    if form.validate_on_submit():
        user = registry.authenticate(
            email=form.email.data,
            password=form.password.data,
        )

        # Authentication successful?
        if user is None:
            error = LOGIN_ERROR_MSG
        else:
            res = hydra.accept_login(challenge, LoginAccept(
                subject=user.subject,
                remember=form.remember.data,
                remember_for=60
            ))
            return redirect(res.redirect_to)

    env = {
        'form': form,
        'error': error,
        'register_url': url_for('register', challenge=challenge),
    }

    return render_template('login.html', **env)


def consent():
    """
    TODO
    """
    form = ConsentForm()
    challenge = request.args.get('consent_challenge')

    if not challenge:
        return get_unknown_response()

    # Consent form submitted - grant or deny consent?
    if form.is_submitted():
        if form.grant.data:
            req = hydra.get_consent_request(challenge)
            user = registry.get_user(subject=req.subject)
            res = hydra.accept_consent(challenge, GrantConsent(
                grant_access_token_audience=req.requested_access_token_audience,
                grant_scope=req.requested_scope,
                handled_at=get_now_iso(),
                remember=form.remember.data,
                remember_for=TOKEN_EXPIRE_MINUTES,
                session=Session(
                    access_token={},
                    id_token=user.id_token,
                )
            ))
            return redirect(res.redirect_to)
        elif form.deny.data:
            res = hydra.reject_consent(challenge, RejectConcent(
                error='consent_required',
                error_debug='User denied access to their data.',
                error_description='User denied access to their data.',
                error_hint='',
                status_code=403,
            ))
            return redirect(res.redirect_to)
        else:
            # Unknown/invalid post
            return get_unknown_response()

    # Consent form not submitted
    try:
        consent_request = hydra.get_consent_request(challenge)
    except HydraException:
        # TODO logging
        raise
        return get_unknown_response()

    user = registry.get_user(subject=consent_request.subject)

    if user is None:
        return get_unknown_response()

    # Already given consent (remembered)?
    if consent_request.skip:
        req = hydra.get_consent_request(challenge)
        res = hydra.accept_consent(challenge, GrantConsent(
            grant_access_token_audience=req.requested_access_token_audience,
            grant_scope=req.requested_scope,
            handled_at=get_now_iso(),
            remember=False,
            remember_for=TOKEN_EXPIRE_MINUTES,
            session=Session(
                access_token={},
                id_token=user.id_token,
            )
        ))
        return redirect(res.redirect_to)

    # client_name = consent_request.client.client_name
    # if client_name == "":
    #     client_name = consent_request.client.client_id

    # scopes = [SCOPES[s] for s in consent_request.requested_scope]
    scopes = [s for s in consent_request.requested_scope]

    env = {
        'form': form,
        'client_name': consent_request.client.client_name,
        'scopes': scopes,
        'challenge': challenge,
    }

    return render_template('consent.html', **env)


def get_unknown_response():
    """
    :rtype: flask.Response
    """
    return redirect(FAILURE_REDIRECT_URL)


def get_now_iso():
    """
    :rtype: str
    """
    return datetime.utcnow() \
        .replace(tzinfo=timezone.utc) \
        .astimezone() \
        .replace(microsecond=0) \
        .isoformat()

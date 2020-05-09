from datetime import datetime, timezone
from flask import request, render_template, redirect, url_for

from .forms import LoginForm, RegisterForm, ConsentForm, ResetPasswordForm, EnterVerificationCodeForm, \
    ChangePasswordForm
from .registry import registry
from .email import email_service
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
EMAIL_ERROR_MSG = 'E-mail was not recognized'
VERIFICATION_CODE_ERROR_MSG = 'Wrong verification code'
VERIFICATION_CODE_EMAIL_ERROR_MSG = 'Wrong e-mail or verification code'
PASSWORD_CONFIRM_ERROR_MSG = 'The two passwords did not match'


hydra = Hydra(HYDRA_URL)


def register():
    """
    TODO
    """
    form = RegisterForm()
    challenge = request.args.get('challenge')

    if not challenge:
        raise Exception("No challenge in form")

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
        raise Exception("No challenge in form")

    try:
        login_request = hydra.get_login_request(challenge)
    except HydraException:
        # TODO logging
        raise Exception("Hydra exception")

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
        'reset_password_url': url_for('reset-password', challenge=challenge),
    }

    return render_template('login.html', **env)


def logout():
    """
    TODO
    """
    challenge = request.args.get('logout_challenge')

    if not challenge:
        raise Exception("No logout_challenge")
    
    res = hydra.accept_logout(challenge)
    return redirect(res.redirect_to)


def consent():
    """
    TODO
    """
    form = ConsentForm()
    challenge = request.args.get('consent_challenge')

    if not challenge:
        raise Exception("No consent_challenge")

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
            raise Exception("Unknown/invalid post")

    # Consent form not submitted
    try:
        consent_request = hydra.get_consent_request(challenge)
    except HydraException:
        # TODO logging
        raise Exception("Hydra exception")

    user = registry.get_user(subject=consent_request.subject)

    if user is None:
        raise Exception("User not found")

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


# -- Reset/change password flow ----------------------------------------------


def reset_password():
    """
    User enters e-mail in formular.
    An e-mail with a verification code is then sent to the user.
    Redirects to "enter-verification-code" view afterwards.
    """
    form = ResetPasswordForm()
    challenge = request.args.get('challenge')
    error = None

    if not challenge:
        raise Exception("No challenge in args")

    # Form submitted and validated correctly?
    if form.validate_on_submit():
        user = registry.get_user(email=form.email.data)

        # Authentication successful?
        if user is None:
            error = EMAIL_ERROR_MSG
        else:
            registry.assign_reset_password_token(user)
            email_service.send_reset_password_email(user)

            return redirect(url_for(
                'enter-verification-code',
                challenge=challenge,
                email=user.email,
            ))

    env = {
        'form': form,
        'error': error,
        'login_url': url_for('login', login_challenge=challenge),
    }

    return render_template('reset-password.html', **env)


def enter_verification_code():
    """
    User enters the verification code sent to their e-mail.
    Redirects to "change-password" view afterwards.
    """
    form = EnterVerificationCodeForm()
    challenge = request.args.get('challenge')
    email = request.args.get('email')
    error = None

    if not challenge:
        raise Exception("No challenge in args")
    if not email:
        raise Exception("No email in args")

    # Form submitted and validated correctly?
    if form.validate_on_submit():
        user = registry.get_user(email=email)

        # Authentication successful?
        if user is None:
            error = EMAIL_ERROR_MSG
        elif (user.reset_password_token is None
              or user.reset_password_token != form.verification_code.data):
            error = VERIFICATION_CODE_ERROR_MSG
        else:
            return redirect(url_for(
                'change-password',
                challenge=challenge,
                email=user.email,
                verification_code=form.verification_code.data,
            ))

    env = {
        'form': form,
        'error': error,
        'login_url': url_for('login', login_challenge=challenge),
    }

    return render_template('enter-verification-code.html', **env)


def change_password():
    """
    User enters the verification code sent to their e-mail.
    Redirects to "change-password" view afterwards.
    """
    form = ChangePasswordForm()
    challenge = request.args.get('challenge')
    email = request.args.get('email')
    verification_code = request.args.get('verification_code')
    error = None
    complete = False

    if not challenge:
        raise Exception("No challenge in args")
    if not email:
        raise Exception("No email in args")
    if not verification_code:
        raise Exception("No verification_code in args")

    user = registry.get_user(
        email=email,
        reset_password_token=verification_code,
    )

    if user is None or user.reset_password_token is None:
        error = VERIFICATION_CODE_EMAIL_ERROR_MSG
    elif form.validate_on_submit():
        if form.password1.data != form.password2.data:
            error = PASSWORD_CONFIRM_ERROR_MSG
        else:
            registry.assign_password(user, form.password1.data)
            complete = True

    env = {
        'form': form,
        'error': error,
        'complete': complete,
        'login_url': url_for('login', login_challenge=challenge),
    }

    return render_template('change-password.html', **env)


# -- Misc --------------------------------------------------------------------


def terms():
    """
    TODO
    """
    return render_template('terms.html')


def error_handler(e=None):
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

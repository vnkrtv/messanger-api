class AuthError(Exception):
    pass


class LoginError(AuthError):
    pass


class RegisterError(AuthError):
    pass


class AccessDeniedError(AuthError):
    pass

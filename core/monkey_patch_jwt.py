import jwt

# Ensure PyJWT names exist for allauth compatibility
if not hasattr(jwt, "decode"):
    from jwt import decode
    jwt.decode = decode

if not hasattr(jwt, "PyJWTError"):
    try:
        from jwt.exceptions import InvalidTokenError as PyJWTError
    except:
        class PyJWTError(Exception):
            pass
    jwt.PyJWTError = PyJWTError

if not hasattr(jwt, "ExpiredSignatureError"):
    try:
        from jwt.exceptions import ExpiredSignatureError
        jwt.ExpiredSignatureError = ExpiredSignatureError
    except:
        class ExpiredSignatureError(jwt.PyJWTError):
            pass
        jwt.ExpiredSignatureError = ExpiredSignatureError

if not hasattr(jwt, "InvalidAudienceError"):
    try:
        from jwt.exceptions import InvalidAudienceError
        jwt.InvalidAudienceError = InvalidAudienceError
    except:
        class InvalidAudienceError(jwt.PyJWTError):
            pass
        jwt.InvalidAudienceError = InvalidAudienceError

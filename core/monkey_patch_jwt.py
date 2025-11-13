import jwt

# Ensure PyJWT names exist for django-allauth compatibility

# Make sure jwt.decode exists (PyJWT >= 2.x already has it)
if not hasattr(jwt, "decode"):
    original_decode = jwt.PyJWT().decode
    jwt.decode = original_decode

# Ensure PyJWTError exists
if not hasattr(jwt, "PyJWTError"):
    try:
        from jwt.exceptions import InvalidTokenError as PyJWTError
    except:
        class PyJWTError(Exception):
            pass
    jwt.PyJWTError = PyJWTError

# Ensure ExpiredSignatureError exists
if not hasattr(jwt, "ExpiredSignatureError"):
    try:
        from jwt.exceptions import ExpiredSignatureError
        jwt.ExpiredSignatureError = ExpiredSignatureError
    except:
        class ExpiredSignatureError(jwt.PyJWTError):
            pass
        jwt.ExpiredSignatureError = ExpiredSignatureError

# Ensure InvalidAudienceError exists
if not hasattr(jwt, "InvalidAudienceError"):
    try:
        from jwt.exceptions import InvalidAudienceError
        jwt.InvalidAudienceError = InvalidAudienceError
    except:
        class InvalidAudienceError(jwt.PyJWTError):
            pass
        jwt.InvalidAudienceError = InvalidAudienceError

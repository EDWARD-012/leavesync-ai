import jwt

# Compatibility patch for AllAuth + PyJWT >= 3.0
if not hasattr(jwt, "PyJWTError"):
    jwt.PyJWTError = jwt.exceptions.PyJWTError

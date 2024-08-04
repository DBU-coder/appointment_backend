from fastapi import HTTPException, status


class BaseApiException(HTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Internal server error"

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class UserAlreadyExistsException(BaseApiException):
    status_code = status.HTTP_409_CONFLICT
    detail = "User already exists"


class IncorrectCredentialsException(BaseApiException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Incorrect credentials"


class InvalidTokenException(BaseApiException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Invalid token"


class InvalidTokenTypeException(BaseApiException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Invalid token type"


class ExpiredTokenException(BaseApiException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Token has expired"


class NoPermissionsException(BaseApiException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "You do not have permission to access this resource"

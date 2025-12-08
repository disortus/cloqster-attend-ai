import jwt
from datetime import datetime, timedelta

secret_key = 'your-secret-key'

def create_token(payload: dict):
    token_payload = {
        **payload,
        'exp': datetime.now() + timedelta(hours=1)
    }
    return jwt.encode(token_payload, secret_key, algorithm='HS256')


def token_validation(token):
    try:
        return jwt.decode(token, secret_key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise Exception("Token has expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token format")
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")

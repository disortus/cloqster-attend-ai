import bcrypt

def hash_password(password: str):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return hashed

def verify_password(password: str, hashed: str):
    valid = bcrypt.checkpw(password.encode(), hashed)
    return valid

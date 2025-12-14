import bcrypt

def hash_password(password: str):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    print(hashed)
    return hashed

def verify_password(password: str, hashed: str):
    valid = bcrypt.checkpw(password.encode(), hashed)
    return valid

hash_password("admin12345")
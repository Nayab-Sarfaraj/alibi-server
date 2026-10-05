from pwdlib import PasswordHash

password_hasher = PasswordHash.recommended()

def hash_password(password:str)->str:
    hashed_password=password_hasher.hash(password)
    return hashed_password


def verify_password(plain_password:str,hashed_password:str)->bool:
    return password_hasher.verify(plain_password,hashed_password)


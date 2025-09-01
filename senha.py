import hashlib

senha = '3r!v4ld0Jun!0r'
hash_senha = hashlib.sha256(senha.encode()).hexdigest()
print(hash_senha)
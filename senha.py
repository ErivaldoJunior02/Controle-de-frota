import hashlib

senha = 'juninho0209'
hash_senha = hashlib.sha256(senha.encode()).hexdigest()
print(hash_senha)
import hashlib

def md5(data):
    md5 = hashlib.md5()
    md5.update(data.encode())
    return md5.hexdigest()
from hashlib import sha1

def hash(s):
     return sha1(s).hexdigest()

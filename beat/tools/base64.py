import base64

def uri_b64encode(s):
     return base64.urlsafe_b64encode(s).strip('=')

def uri_b64decode(s):
     return base64.urlsafe_b64decode(s + '=' * (4 - len(s) % 4))

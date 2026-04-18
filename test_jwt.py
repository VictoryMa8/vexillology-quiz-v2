import sys
try:
    import jwt
    print(jwt.__file__)
    print(dir(jwt))
except Exception as e:
    print(e)

import os

class Constant:
    '''
    This class is used to store all the constant values
    '''
    REQUEST_SECRET_KEY   = os.getenv('REQUEST_SECRET_KEY')
    JWT_SECRET_KEY       = os.getenv('JWT_SECRET_KEY')
    JWT_ALGORITHM        = os.getenv('JWT_ALGORITHM', 'HS256')
    LIMIT_REQUESTS       = os.getenv('LIMIT_REQUESTS', '300')
    EXPIRE_IN            = int(os.getenv('EXPIRE_IN', '86400'))

CONST = Constant
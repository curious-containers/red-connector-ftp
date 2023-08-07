import os
import sys
import ftplib
from functools import wraps
from urllib.parse import urlparse

import jsonschema

def parseFTP(url):
    parsed_url = urlparse(url)
    ftp_host = parsed_url.hostname
    ftp_path = parsed_url.path
    if ftp_path.startswith("/"):
        ftp_path = ftp_path[1:]
    
    return ftp_host, ftp_path

def graceful_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except jsonschema.exceptions.ValidationError as e:
            if hasattr(e, 'context'):
                print('{}:{}Context: {}'.format(repr(e), os.linesep, e.context), file=sys.stderr)
                exit(1)

            print(repr(e), file=sys.stderr)
            exit(2)

        except Exception as e:
            print('{}: {}'.format(type(e).__name__, e), file=sys.stderr)
            exit(3)

    return wrapper


class InvalidAccessInformationError(Exception):
    pass

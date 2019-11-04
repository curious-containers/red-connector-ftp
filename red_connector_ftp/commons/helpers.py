import os
import sys
from functools import wraps

import jsonschema


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

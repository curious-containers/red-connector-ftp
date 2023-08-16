from copy import deepcopy

_AUTH_SCHEMA = {
    'type': 'object',
    'properties': {
        'username': {'type': 'string'},
        'password': {'type': 'string'},
    },
    'additionalProperties': False,
    'required': ['username']
}

FILE_SCHEMA = {
    'type': 'object',
    'properties': {
        'url': {'type': 'string'},
        'port': {'type': 'integer'},
        'auth': _AUTH_SCHEMA,
    },
    'additionalProperties': False,
    'required': ['url']
}

ARCHIVE_SCHEMA = deepcopy(FILE_SCHEMA)
ARCHIVE_SCHEMA['properties']['archiveFormat'] = {'enum': ['zip', 'tar', 'gztar', 'bztar', 'xztar']}
ARCHIVE_SCHEMA['required'].append('archiveFormat')

_LISTING_SUB_FILE_SCHEMA = {
    'type': 'object',
    'properties': {
        'class': {'enum': ['File']},
        'basename': {'type': 'string'},
        'size': {'type': 'number'},
        'checksum': {'type': 'string'}
    },
    'required': ['class', 'basename'],
    'additionalProperties': False
}

_LISTING_SUB_DIRECTORY_SCHEMA = {
    'type': 'object',
    'properties': {
        'class': {'enum': ['Directory']},
        'basename': {'type': 'string'},
        'listing': {'$ref': '#/'}
    },
    'additionalProperties': False,
    'required': ['class', 'basename']
}

# WARNING: Do not embed this schema into another schema,
# because this breaks the '$ref' in listing_sub_directory_schema
LISTING_SCHEMA = {
    'type': 'array',
    'items': {
        'oneOf': [_LISTING_SUB_FILE_SCHEMA, _LISTING_SUB_DIRECTORY_SCHEMA]
    }
}
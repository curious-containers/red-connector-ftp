from copy import deepcopy

FILE_SCHEMA = {
    'type': 'object',
    'properties': {
        'url': {'type': 'string'},
    },
    'additionalProperties': False,
    'required': ['url']
}

ARCHIVE_SCHEMA = deepcopy(FILE_SCHEMA)
ARCHIVE_SCHEMA['properties']['archiveFormat'] = {'enum': ['zip', 'tar', 'gztar', 'bztar', 'xztar']}
ARCHIVE_SCHEMA['required'].append('archiveFormat')

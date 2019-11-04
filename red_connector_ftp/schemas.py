FILE_SCHEMA = {
    'type': 'object',
    'properties': {
        'host': {'type': 'string'},
        'url': {'type': 'string'},
    },
    'additionalProperties': False,
    'required': ['host', 'url']
}

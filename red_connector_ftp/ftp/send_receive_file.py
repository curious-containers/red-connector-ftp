import json
import os
from argparse import ArgumentParser
from ftplib import FTP

import jsonschema
from red_connector_ftp.commons.helpers import graceful_error, InvalidAccessInformationError
from red_connector_ftp.commons.schemas import FILE_SCHEMA

RECEIVE_FILE_DESCRIPTION = 'Receive input file from FTP server.'
RECEIVE_FILE_VALIDATE_DESCRIPTION = 'Validate access data for receive-file.'


def _receive_file(access, local_file_path):
    with open(access) as f:
        access = json.load(f)

    if not os.path.isdir(os.path.dirname(local_file_path)):
        raise NotADirectoryError(
            'Could not create local file "{}". The parent directory does not exist.'.format(local_file_path)
        )

    host = access.get('host')
    if host is None:
        raise InvalidAccessInformationError('Could not find "host" in access information.')

    url = access.get('url')
    if url is None:
        raise InvalidAccessInformationError('Could not find "url" in access information.')

    with FTP(host) as ftp_client:
        ftp_client.login()

        with open(local_file_path, 'wb') as output_file:
            ftp_client.retrbinary('RETR {}'.format(url), output_file.write)


def _receive_file_validate(access):
    with open(access) as f:
        access = json.load(f)

    jsonschema.validate(access, FILE_SCHEMA)


@graceful_error
def receive_file():
    parser = ArgumentParser(description=RECEIVE_FILE_DESCRIPTION)
    parser.add_argument(
        'access', action='store', type=str, metavar='ACCESSFILE',
        help='Local path to ACCESSFILE in JSON format.'
    )
    parser.add_argument(
        'local_file_path', action='store', type=str, metavar='LOCALFILE',
        help='Local output file path.'
    )
    args = parser.parse_args()
    _receive_file(**args.__dict__)


@graceful_error
def receive_file_validate():
    parser = ArgumentParser(description=RECEIVE_FILE_VALIDATE_DESCRIPTION)
    parser.add_argument(
        'access', action='store', type=str, metavar='ACCESSFILE',
        help='Local path to ACCESSFILE in JSON format.'
    )
    args = parser.parse_args()
    _receive_file_validate(**args.__dict__)



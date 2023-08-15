import json
import os
import ftputil
import ftputil.error
from argparse import ArgumentParser

import jsonschema
from red_connector_ftp.commons.helpers import graceful_error, InvalidAccessInformationError, parse_ftp, get_ftp_client
from red_connector_ftp.commons.schemas import FILE_SCHEMA

RECEIVE_FILE_DESCRIPTION = 'Receive input file from FTP server.'
RECEIVE_FILE_VALIDATE_DESCRIPTION = 'Validate access data for receive-file.'

SEND_FILE_DESCRIPTION = 'Send output file to FTP server.'
SEND_FILE_VALIDATE_DESCRIPTION = 'Validate access data for send-file.'


def _receive_file(access, local_file_path):
    with open(access) as f:
        access = json.load(f)
    
    if not os.path.isdir(os.path.dirname(os.path.abspath(local_file_path))):
        raise NotADirectoryError(
            'Could not create local file "{}". The parent directory does not exist.'.format(local_file_path)
        )

    url = access.get('url')
    if url is None:
        raise InvalidAccessInformationError('Could not find "url" in access information.')
    
    ftp_host, ftp_path = parse_ftp(url)
    ftp_client = get_ftp_client(ftp_host, access)
    
    if ftp_client.path.isfile(ftp_path):
        ftp_client.download(ftp_path, local_file_path)
    else:
        raise FileNotFoundError('Could not find remote file "{}"'.format(ftp_path))
    
    ftp_client.close()


def _receive_file_validate(access):
    with open(access) as f:
        access = json.load(f)

    jsonschema.validate(access, FILE_SCHEMA)


def _send_file(access, local_file_path):
    with open(access) as f:
        access = json.load(f)
    
    if not os.path.isfile(local_file_path):
        raise FileNotFoundError('Could not find local file "{}"'.format(local_file_path))

    url = access.get('url')
    if url is None:
        raise InvalidAccessInformationError('Could not find "url" in access information.')
    
    ftp_host, ftp_path = parse_ftp(url)
    remote_dir = os.path.dirname(ftp_path)
    ftp_client = get_ftp_client(ftp_host, access)
    
    if remote_dir:
        ftp_client.makedirs(remote_dir, exist_ok=True)
    ftp_client.upload(local_file_path, ftp_path)
    
    ftp_client.close()


def _send_file_validate(access):
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


@graceful_error
def send_file():
    parser = ArgumentParser(description=SEND_FILE_DESCRIPTION)
    parser.add_argument(
        'access', action='store', type=str, metavar='ACCESSFILE',
        help='Local path to ACCESSFILE in JSON format.'
    )
    parser.add_argument(
        'local_file_path', action='store', type=str, metavar='LOCALFILE',
        help='Local output file path.'
    )
    args = parser.parse_args()
    _send_file(**args.__dict__)


@graceful_error
def send_file_validate():
    parser = ArgumentParser(description=SEND_FILE_VALIDATE_DESCRIPTION)
    parser.add_argument(
        'access', action='store', type=str, metavar='ACCESSFILE',
        help='Local path to ACCESSFILE in JSON format.'
    )
    args = parser.parse_args()
    _send_file_validate(**args.__dict__)

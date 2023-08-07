import json
import os
import ftplib
from argparse import ArgumentParser
from urllib.request import urlopen
from urllib.parse import urlparse

import jsonschema
from red_connector_ftp.commons.helpers import graceful_error, InvalidAccessInformationError, getFTPConnetion, createRemoteDirectorys
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
    
    ftp, ftp_path = getFTPConnetion(url)
    with open(local_file_path, 'wb') as f:
        ftp.retrbinary(f"RETR {ftp_path}", f.write)
    ftp.quit()


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
    
    ftp, ftp_path = getFTPConnetion(url)
    
    remote_dir, remote_filename = os.path.split(ftp_path)
    createRemoteDirectorys(ftp, remote_dir)
    
    with open(local_file_path, 'rb') as f:
        ftp.storbinary(f"STOR {remote_filename}", f)
    ftp.quit()


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
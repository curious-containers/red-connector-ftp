import json
import os
import ftputil
import ftputil.error
from argparse import ArgumentParser

import jsonschema
from red_connector_ftp.commons.helpers import graceful_error, InvalidAccessInformationError, parse_ftp, download_ftp_directory, \
    download_ftp_listing, upload_ftp_directory, upload_ftp_listing, get_ftp_client
from red_connector_ftp.commons.schemas import FILE_SCHEMA, LISTING_SCHEMA

RECEIVE_DIR_DESCRIPTION = 'Receive input dir from FTP server.'
RECEIVE_DIR_VALIDATE_DESCRIPTION = 'Validate access data for receive-dir.'

SEND_DIR_DESCRIPTION = 'Send output dir to FTP server.'
SEND_DIR_VALIDATE_DESCRIPTION = 'Validate access data for send-dir.'


def _load_access_listing(access, listing):
    with open(access) as f:
        access = json.load(f)

    if listing:
        with open(listing) as f:
            listing = json.load(f)

    return access, listing


def _receive_dir(access, local_dir_path, listing):
    access, listing = _load_access_listing(access, listing)
    local_dir_path = os.path.normpath(local_dir_path)
    
    if not os.path.isdir(os.path.dirname(os.path.abspath(local_dir_path))):
        raise FileNotFoundError(
            'Could not create local directory "{}", because parent directory does not exist'.format(local_dir_path)
        )

    url = access.get('url')
    if url is None:
        raise InvalidAccessInformationError('Could not find "url" in access information.')
    
    ftp_host, ftp_path = parse_ftp(url)
    ftp_client = get_ftp_client(ftp_host, access)
    
    if listing:
        download_ftp_listing(ftp_client, local_dir_path, ftp_path, listing)
    else:
        download_ftp_directory(ftp_client, local_dir_path, ftp_path)
    
    ftp_client.close()


def _receive_dir_validate(access, listing):
    access, listing = _load_access_listing(access, listing)

    jsonschema.validate(access, FILE_SCHEMA)
    if listing:
        jsonschema.validate(listing, LISTING_SCHEMA)


def _send_dir(access, local_dir_path, listing):
    access, listing = _load_access_listing(access, listing)
    local_dir_path = os.path.normpath(local_dir_path)
    
    if not os.path.isdir(local_dir_path):
        raise NotADirectoryError('Could not find local directory "{}"'.format(local_dir_path))
    
    url = access.get('url')
    if url is None:
        raise InvalidAccessInformationError('Could not find "url" in access information.')
    
    ftp_host, ftp_path = parse_ftp(url)
    ftp_client = get_ftp_client(ftp_host, access)
    
    if listing:
        if ftp_path:
            ftp_client.makedirs(ftp_path, exist_ok=True)
        upload_ftp_listing(ftp_client, local_dir_path, ftp_path, listing)
    else:
        upload_ftp_directory(ftp_client, local_dir_path, ftp_path)
    
    ftp_client.close()


def _send_dir_validate(access, listing):
    access, listing = _load_access_listing(access, listing)

    jsonschema.validate(access, FILE_SCHEMA)
    if listing:
        jsonschema.validate(listing, LISTING_SCHEMA)


@graceful_error
def receive_dir():
    parser = ArgumentParser(description=RECEIVE_DIR_DESCRIPTION)
    parser.add_argument(
        'access', action='store', type=str, metavar='ACCESSFILE',
        help='Local path to ACCESSFILE in JSON format.'
    )
    parser.add_argument(
        'local_dir_path', action='store', type=str, metavar='LOCALDIR',
        help='Local input dir path.'
    )
    parser.add_argument(
        '--listing', action='store', type=str, metavar='LISTINGFILE',
        help='Local path to LISTINGFILE in JSON format.'
    )
    args = parser.parse_args()
    _receive_dir(**args.__dict__)


@graceful_error
def receive_dir_validate():
    parser = ArgumentParser(description=RECEIVE_DIR_VALIDATE_DESCRIPTION)
    parser.add_argument(
        'access', action='store', type=str, metavar='ACCESSFILE',
        help='Local path to ACCESSFILE in JSON format.'
    )
    parser.add_argument(
        '--listing', action='store', type=str, metavar='LISTINGFILE',
        help='Local path to LISTINGFILE in JSON format.'
    )
    args = parser.parse_args()
    _receive_dir_validate(**args.__dict__)


@graceful_error
def send_dir():
    parser = ArgumentParser(description=SEND_DIR_DESCRIPTION)
    parser.add_argument(
        'access', action='store', type=str, metavar='ACCESSFILE',
        help='Local path to ACCESSFILE in JSON format.'
    )
    parser.add_argument(
        'local_dir_path', action='store', type=str, metavar='LOCALDIR',
        help='Local output dir path.'
    )
    parser.add_argument(
        '--listing', action='store', type=str, metavar='LISTINGFILE',
        help='Local path to LISTINGFILE in JSON format.'
    )
    args = parser.parse_args()
    _send_dir(**args.__dict__)


@graceful_error
def send_dir_validate():
    parser = ArgumentParser(description=SEND_DIR_VALIDATE_DESCRIPTION)
    parser.add_argument(
        'access', action='store', type=str, metavar='ACCESSFILE',
        help='Local path to ACCESSFILE in JSON format.'
    )
    parser.add_argument(
        '--listing', action='store', type=str, metavar='LISTINGFILE',
        help='Local path to LISTINGFILE in JSON format.'
    )
    args = parser.parse_args()
    _send_dir_validate(**args.__dict__)

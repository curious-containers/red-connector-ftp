import tempfile
import json
from argparse import ArgumentParser
from ftplib import FTP
from urllib.parse import urlparse

import jsonschema
import shutil

from red_connector_ftp.commons.helpers import InvalidAccessInformationError, graceful_error
from red_connector_ftp.commons.schemas import ARCHIVE_SCHEMA

RECEIVE_DIR_DESCRIPTION = 'Receive input dir from FTP server.'
RECEIVE_DIR_VALIDATE_DESCRIPTION = 'Validate access data for receive-dir.'


def _receive_dir(access, local_dir_path, listing):
    del listing  # ignore listing
    with open(access) as f:
        access = json.load(f)

    url = access.get('url')
    if url is None:
        raise InvalidAccessInformationError('Could not find "url" in access information.')

    parsed_url = urlparse(url)

    with FTP(parsed_url.netloc) as ftp_client:
        ftp_client.login()

        with tempfile.NamedTemporaryFile(suffix='.zip') as archive_output_file:
            ftp_client.retrbinary('RETR {}'.format(parsed_url.path), archive_output_file.write)
            archive_output_file.flush()

            shutil.unpack_archive(archive_output_file.name, local_dir_path, access['archiveFormat'])


def _receive_dir_validate(access, listing):
    del listing  # ignore listing

    with open(access) as f:
        access = json.load(f)

    jsonschema.validate(access, ARCHIVE_SCHEMA)


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

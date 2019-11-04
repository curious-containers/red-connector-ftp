import tempfile
import json
from argparse import ArgumentParser
from urllib.request import urlopen

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

    with tempfile.NamedTemporaryFile(suffix='.zip') as f:
        r = urlopen(url)
        while True:
            chunk = r.read(4096)
            if not chunk:
                break
            f.write(chunk)

        f.flush()
        shutil.unpack_archive(f.name, local_dir_path, access['archiveFormat'])


def _receive_dir_validate(access, listing):
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

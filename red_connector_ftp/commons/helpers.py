import os
import sys
import ftputil
import ftputil.session
from functools import wraps
from urllib.parse import urlparse

import jsonschema

def parse_ftp(url):
    """
    Parses the given FTP URL and extracts the FTP host and path.

    :param url: The FTP URL to parse.
    :return: A tuple containing the FTP host and path.
    """
    parsed_url = urlparse(url)
    ftp_host = parsed_url.hostname
    ftp_path = parsed_url.path
    if ftp_path.startswith("/"):
        ftp_path = ftp_path[1:]
    
    return ftp_host, ftp_path

def get_ftp_client(ftp_host, access):
    """
    Creates and returns an FTP client for the specified FTP host with optional authentication.

    :param ftp_host: The hostname or IP address of the FTP server.
    :param access: An dictionary containing access information, such as authentication details.
    :return: An instance of ftputil.FTPHost connected to the FTP server.
    """
    ftp_username = "anonymous"
    ftp_password = None
    ftp_port = 21
    
    if 'auth' in access:
        ftp_username = access['auth']['username']
        if 'password' in access['auth']:
            ftp_password = access['auth']['password']
    if 'port' in access:
        ftp_port = access['port']
    
    session_factory = ftputil.session.session_factory(port=ftp_port)
    return ftputil.FTPHost(ftp_host, ftp_username, ftp_password, session_factory=session_factory)

def download_ftp_directory(ftp_host, base_directory, remote_directory):
    """
    Recursively downloads files and directories from a remote FTP server to a local directory.

    :param ftp_host: An FTPClient connected to the remote host.
    :param base_directory: The local base directory where files will be downloaded.
    :param remote_directory: The remote directory to download from.
    """
    os.makedirs(base_directory, exist_ok=True)
    elements = ftp_host.listdir(remote_directory)
    for element in elements:
        element_path = os.path.join(remote_directory, element)
        local_path = os.path.join(base_directory, element)
        if ftp_host.path.isfile(element_path):
            ftp_host.download(element_path, local_path)
        else:
            download_ftp_directory(ftp_host, local_path, element_path)


def upload_ftp_directory(ftp_host, base_directory, remote_directory):
    """
    Recursively uploads files and directories from a local directory to a remote FTP server.

    :param ftp_host: An FTPClient connected to the remote host.
    :param base_directory: The local base directory to upload from.
    :param remote_directory: The remote directory where files will be uploaded.
    """
    if remote_directory:
        ftp_host.makedirs(remote_directory, exist_ok=True)
    elements = os.listdir(base_directory)
    for element in elements:
        element_path = os.path.join(base_directory, element)
        remote_path = os.path.join(remote_directory, element)
        if(os.path.isfile(element_path)):
            ftp_host.upload(element_path, remote_path)
        else:
            upload_ftp_directory(ftp_host, element_path, remote_path)


def download_ftp_listing(ftp_host, base_directory, remote_directory, listing, path="./"):
    """
    Downloads the directories given in the listing using the given ftp_host.
    The read/write/execute permissions of the remote and local directories may differ.

    :param ftp_host: A FTPClient, that is connected to a host.
    :param base_directory: The path to the base directory, where to create the fetched files and directories.
                           This base directory should already be present on the local filesystem.
    :param remote_directory: The path to the remote base directory from where to fetch the subfiles and directories.
    :param listing: A complete listing with complete urls for every containing file.
    :param path: A path specifying which subdirectory of remote_directory should be fetched and where to place it
                 under base_directory. The files are fetched from os.path.join(remote_directory, path) and placed
                 under os.path.join(base_directory, path)
    """
    for sub in listing:
        sub_path = os.path.normpath(os.path.join(path, sub['basename']))
        remote_path = os.path.normpath(os.path.join(remote_directory, sub_path))
        local_path = os.path.normpath(os.path.join(base_directory, sub_path))

        if sub['class'] == 'File':
            ftp_host.download(remote_path, local_path)

        elif sub['class'] == 'Directory':
            os.makedirs(local_path, exist_ok=True)
            listing = sub.get('listing')
            if listing:
                download_ftp_listing(ftp_host, base_directory, remote_directory, listing, sub_path)


def upload_ftp_listing(ftp_host, base_directory, remote_directory, listing, path="./"):
    """
    Sends the files/directories given in the listing using the given ftp_host.
    The read/write/execute permissions of the remote and local directories may differ.

    :param ftp_host: A paramiko FTPClient, that is connected to a host.
    :param base_directory: The path to the directory, where the files to send are stored.
                           This base directory should already be present on the local filesystem and contain all files
                           and directories given in listing.
    :param remote_directory: The path to the remote base directory where to put the subfiles and directories.
    :param listing: A listing specifying the directories and files to send to the remote host.
    :param path: A path specifying which subdirectory of remote_directory should be fetched and where to place it
                 under base_directory. The files are fetched from os.path.join(remote_directory, path) and placed
                 under os.path.join(base_directory, path)
    """
    for sub in listing:
        sub_path = os.path.normpath(os.path.join(path, sub['basename']))
        remote_path = os.path.normpath(os.path.join(remote_directory, sub_path))
        local_path = os.path.normpath(os.path.join(base_directory, sub_path))

        if sub['class'] == 'File':
            ftp_host.upload(local_path, remote_path)

        elif sub['class'] == 'Directory':
            ftp_host.makedirs(remote_path, exist_ok=True)
            listing = sub.get('listing')
            if listing:
                upload_ftp_listing(ftp_host, base_directory, remote_directory, listing, sub_path)


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

"""This script downloads a Plex Playlists into physical files in your filesystem.

Requirements
------------
  - plexapi: For communication with Plex
"""

import os
import argparse
import requests
import plexapi
from plexapi.server import PlexServer

class DownloadOptions():
    def __init__(self, args):
        self.host = args.host
        self.token = args.token
        self.playlist = args.playlist
        self.saveto = args.save_to
        self.orderby = args.order_by
        self.keep_original_filename = args.original_filenames
        pass

def list_playlists(baseurl: str, token: str):
    """ Lists all playlists on the given Plex server by library
    """

    print('Connecting to plex...', end='')
    try:
        plex = PlexServer(baseurl, token)
    except (plexapi.exceptions.Unauthorized, requests.exceptions.ConnectionError):
        print(' failed')
        return
    print(' done')

    print('Getting playlists... ', end='')
    playlists = plex.playlists()
    print(' done')

    print('')
    print('Supply any of the following playlists to --playlist <playlist>:')
    playlistsBySection = {}
    for item in playlists:
        if playlistsBySection.get(item.playlistType) == None:
            playlistsBySection[item.playlistType] = []
        
        playlistsBySection[item.playlistType].append(item.title)

    for section, lists in playlistsBySection.items():
        print ('\t%s:' % section)
        for list in lists:
            print('\t\t%s' % list)

def download_playlist(options: DownloadOptions):
    """ Downloads a given playlist from the specified Plex server and stores the files locally.
    """

    print('Connecting to plex...', end='')
    try:
        plex = PlexServer(options.host, options.token)
    except (plexapi.exceptions.Unauthorized, requests.exceptions.ConnectionError):
        print(' failed')
        return
    print(' done')

    print('Getting playlist...', end='')
    try:
        playlist = plex.playlist(options.playlist)
    except (plexapi.exceptions.NotFound):
        print(' failed')
        return
    print(' done')

    saveto = './%s/' % (playlist.title if options.saveto == None else options.saveto)
    
    print('Iterating playlist...', end='')
    items = playlist.items()
    print(' %s items found' % playlist.leafCount)

    if options.orderby != None:
        items.sort(key = lambda x: getattr(x, options.orderby))
    
    print('Downloading files...', end='')
    i = 1
    for item in items:
        files = item.download(saveto, keep_original_name=options.keep_original_filename)
        if (options.keep_original_filename):
            continue

        file = files[0]
        dir = os.path.dirname(file)
        _, ext = os.path.splitext(file)
        newfile = os.path.join(dir, '%03d%s' % (i, ext))
        os.rename(file, newfile)
        i += 1
    print(' done')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        '-p', '--playlist',
        type = str,
        help = "The name of the Playlist in Plex for which to create the M3U playlist"
    )
    mode.add_argument('-l', '--list',
        action = 'store_true',
        help = "Use this option to get a list of all available playlists")
    
    parser.add_argument(
        '--host',
        type = str,
        help = "The URL to the Plex Server, i.e.: http://192.168.0.100:32400",
        default = 'http://192.168.0.100:32400'
    )
    parser.add_argument(
        '--token',
        type = str,
        help = "The Token used to authenticate with the Plex Server",
        default = 'xxiaNX8rigEPYadJRrv3'
    )
    parser.add_argument(
        '--order-by',
        type = str,
        help = "Supply a property by which to sort the list. By default the list is exported in the same order as saved in Plex"
    )
    parser.add_argument(
        '--save-to',
        type = str,
        help = "Supply a directory where to save the downloaded files to"
    )
    parser.add_argument(
        '--original-filenames',
        action = 'store_true',
        help = "Use this option to download the files using their original filename"
    )
    
    args = parser.parse_args()
    if (args.list):
        list_playlists(args.host, args.token)
    else:
        options = DownloadOptions(args=args)
        download_playlist(options)

if __name__ == "__main__":
    main()
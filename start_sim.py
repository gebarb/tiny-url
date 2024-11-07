import cmd
import hashlib
import base64
from datetime import datetime
import os
import re
from pprint import pprint
import sys
import getopt
import uuid

from core.engine import HitEngine, UrlEngine


class TurlSim(cmd.Cmd):
    intro = 'Welcome to the Tiny-Url Simulation.\nType help or ? to list commands.\n'
    prompt = '(tiny-url) '

    def __init__(self, db_name=None, base_domain=None):
        super(TurlSim, self).__init__()

        self.UUID = str(uuid.uuid4()).replace('-', '_')

        if db_name:
            conn_string = f"sqlite:///{db_name.replace('.', '_')}.db"
        else:
            conn_string = f"sqlite:///test_{self.UUID}.db"

        if base_domain:
            self.BASE_DOMAIN = f"https://{base_domain}"
        else:
            self.BASE_DOMAIN = 'https://turl.com'

        self.URL_ENGINE = UrlEngine(conn_string=conn_string)
        self.HIT_ENGINE = HitEngine(conn_string=conn_string)

        self._init_db()

    """ Shell Methods """

    def do_create(self, arg):
        """
            Create a Short URL for the specified Long URL.
            If a second parameter is supplied, that string will be used as the hash key for the Short URL.
            ie: `create https://www.google.com ABCDEF`
            Alternatively, the second parameter may also include the tiny-url domain.
            ie: `create https://www.google.com https://turl.com/ABCDEF`
        """
        is_custom = False
        long_url, *short_url = arg.split()
        short_url = short_url[0] if short_url else None

        if long_url:
            # Create the `url` record (or retrieve it if it already exists)
            url_id = self.URL_ENGINE.create_url(long_url)

            # If no Short URL supplied, generate one based on the Primary Index of the Long URL
            if not short_url or not isinstance(short_url, str) or short_url == '':
                short_url = self._generate_short_url(url_id)
            # Attempt to create the supplied Short URL
            else:
                short_url = self._parse_hash_from_url(short_url)
                is_custom = True

            try:
                short_url = self._create_url_hash(url_id, short_url, is_custom)
                print(
                    f"{self.BASE_DOMAIN}/{short_url} has been created and mapped to {long_url}.")
                print(f"The hash_key for this Short URL is {short_url}.")
            except Exception as e:
                print(e)
        else:
            print('No Destination Long URL was supplied.')

    def do_delete(self, hash_key):
        """
            Delete a Short URL based on the specified hash key.
            ie: `delete ABCDEF`
        """
        hash_key = self._parse_hash_from_url(hash_key)
        if hash_key and hash_key != '':
            url = self.URL_ENGINE.get_url(hash_key)
            if url:
                self.URL_ENGINE.delete_url(hash_key)
                print(f"The Short URL for hash key '{
                      hash_key}' has been deleted.")
            else:
                print('The requested Short URL was not found in the system.')
        else:
            print('No Short URL was supplied.')

    def do_click(self, hash_key):
        """
            Mimic redirect behavior by getting the Long URL corresponding to the specified Short URL hash_key.
            ie: `redirect ABCDEF`
        """
        self._handle_click(hash_key)

    def do_redirect(self, hash_key):
        """
            Mimic redirect behavior by getting the Long URL corresponding to the specified Short URL hash_key.
            ie: `redirect ABCDEF`
        """
        self._handle_click(hash_key)

    def do_get(self, hash_key):
        """
            Get the full URL Object corresponding to the specified Short URL hash_key.
            ie: `get ABCDEF`
        """
        hash_key = self._parse_hash_from_url(hash_key)
        if hash_key and hash_key != '':
            url = self.URL_ENGINE.get_url(hash_key)
            if url:
                if url.get('is_deleted', False):
                    print(f"This Short URL was deleted at { url.get('date_modified').strftime('%m/%d/%Y, %H:%M:%S')}")
                else:
                    print(f"The Long URL Object to redirect for hash key '{hash_key}' is:")
                    pprint(dict({'url': url.get('url')}, **url))
            else:
                print('The requested Short URL was not found in the system.')
        else:
            print('No Short URL was supplied.')

    def do_stats(self, hash_key):
        """
            Get click statistics for the specified Short URL hash_key.
            This will correlate to the total number of times that the `redirect` command was ran within this simulation.
            ie: `stats ABCDEF`
        """
        hash_key = self._parse_hash_from_url(hash_key)
        if hash_key and hash_key != '':
            statistics = self.HIT_ENGINE.get_statistics(hash_key)
            if statistics:
                print(f"The Short URL for hash key '{hash_key}' has had {statistics.get('num_clicks', 0)} clicks during this simulation.")
                if statistics.get('is_deleted', False):
                    print(f"This Short URL was deleted at {statistics.get(
                        'date_modified').strftime('%m/%d/%Y, %H:%M:%S')}")
            else:
                print('The requested Short URL was not found in the system.')
        else:
            print('No Short URL was supplied.')

    def do_exit(self, arg):
        """
            Close the Tiny-URL Simulation.
        """
        if os.path.exists(f"test_{self.UUID}.db"):
            os.remove(f"test_{self.UUID}.db")
        return True

    """ Functionality Methods """

    def _handle_click(self, hash_key):
        hash_key = self._parse_hash_from_url(hash_key)
        if hash_key and hash_key != '':
            url = self.URL_ENGINE.get_url(hash_key)
            if url and not url.get('is_deleted', False):
                # Log the redirect for analytics
                hit = {
                    'url_hash_id': url.get('id'),
                    'date_created': datetime.now()
                }
                self.HIT_ENGINE.create_hit(hit)
                print('Click Count for this Short URL has been incremented.')
                print(f"The Long URL to redirect for hash key '{hash_key}' is {url.get('url')}")
            else:
                print('The requested Short URL was not found in the system.')
        else:
            print('No Short URL was supplied.')

    def _init_db(self):
        self.URL_ENGINE.create_tables()
        self.HIT_ENGINE.create_table()

    def _create_url_hash(self, url_id, hash_key, is_custom=False, tries=0):
        url = self.URL_ENGINE.get_url(hash_key)
        # URL Mapping already exists
        if url:
            # If a Custom URL is supplied, raise an Exception
            if is_custom:
                raise Exception('CONFLICT! Short URL already exists.')
            # Otherwise, try again with a new hash_key
            else:
                tries = tries + 1
                hash_key = self._generate_short_url(url_id + tries)
                hash_key = self._create_url_hash(
                    url_id, hash_key, is_custom, tries)
        else:
            url_hash = {
                'hash_key': hash_key,
                'url_id': url_id,
                'date_created': datetime.now()
            }
            self.URL_ENGINE.create_url_hash(url_hash)
        return hash_key

    def _generate_short_url(self, url_id):
        return self._generate_url_hash(url_id)

    @staticmethod
    def _generate_url_hash(url_id):
        # Generate the unique hash for the Short URL based on the Primary Index of the long_url
        hasher = hashlib.md5(str(url_id).encode('utf-8'))
        return base64.urlsafe_b64encode(hasher.digest()).decode('utf-8')[:8]

    def _parse_hash_from_url(self, url):
        regx = re.compile(r"https?://(www\.)?")
        return regx.sub('', url.replace(self.BASE_DOMAIN, '')).strip().strip('/')

    @staticmethod
    def _clean_url(url):
        regx = re.compile(r"https?://(www\.)?")
        return regx.sub('', url).strip().strip('/')


def main(argv):
    db_name = None
    base_domain = None
    try:
        opts, args = getopt.getopt(argv, "n:d:", ["name=", "domain="])
        for opt, arg in opts:
            if opt in ('-d', '--domain'):
                base_domain = arg
            elif opt in ('-n', '--name'):
                db_name = arg

    except getopt.GetoptError as e:
        sys.exit(2)

    TurlSim(db_name=db_name, base_domain=base_domain).cmdloop()


if __name__ == '__main__':
    main(sys.argv[1:])

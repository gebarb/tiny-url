import base64
from datetime import datetime
import hashlib
import re
from flask import jsonify, request, Response
from core.engine import UrlEngine
from core.factory.base import BaseFactory


class UrlFactory(BaseFactory):
    def __init__(self, app, **kwargs):
        super(UrlFactory, self).__init__(app, **kwargs)

        self.URL_ENGINE = UrlEngine(app=app, **kwargs)

    def handle_get_long_url(self, hash_key):
        url = self.URL_ENGINE.get_url(hash_key)
        if url:
            if url.get('is_deleted', False):
                return Response(f"This Short URL was deleted at {url.get('date_modified').strftime('%m/%d/%Y, %H:%M:%S')}", status=400)
            else:
                return jsonify(success=True, url=url)
        else:
            return Response('The requested Short URL was not found in the system.', status=400)

    def handle_create_short_url(self):
        is_custom = False
        # (Required) The Long URL to create a Short URL for
        dest_url = request.json.get('dest_url') if request.headers.get(
            'Content-Type') == 'application/json' else request.form.get('dest_url')
        # (Optional) The User supplied Short URL to use (if possible)
        src_url = request.json.get('src_url') if request.headers.get(
            'Content-Type') == 'application/json' else request.form.get('src_url')

        if dest_url:
            # Create the `url` record (or retrieve it if it already exists)
            url_id = self.URL_ENGINE.create_url(dest_url)

            # If no Short URL supplied, generate one based on the Primary Index of the Long URL
            if not src_url or src_url == '':
                src_url = self._generate_short_url(url_id)
            # Attempt to create the supplied Short URL
            else:
                regx = re.compile(r"https?://(www\.)?")
                src_url = regx.sub('', src_url.replace(
                    self.APP.config.get('BASE_DOMAIN'), '')).strip().strip('/')
                is_custom = True

            try:
                src_url = self._create_url_hash(url_id, src_url, is_custom)
            except Exception as e:
                return Response(str(e), status=400)

            return jsonify(success=True, url=f"{self.APP.config.get('BASE_DOMAIN')}/{src_url}")

        else:
            return Response('A Destination Long URL was not supplied.', status=400)

    def _create_url_hash(self, url_id, short_url, is_custom=False, tries=0):
        url = self.URL_ENGINE.get_url(short_url)
        # URL Mapping already exists
        if url:
            # If a Custom URL is supplied, raise an Exception
            if is_custom:
                raise Exception('CONFLICT! Short URL already exists.')
            # Otherwise, try again with a new hash_key
            else:
                tries = tries + 1
                short_url = self._generate_short_url(url_id + tries)
                short_url = self._create_url_hash(url_id, short_url, is_custom)
        else:
            url_hash = {
                'hash_key': short_url,
                'url_id': url_id,
                'date_created': datetime.now()
            }
            self.URL_ENGINE.create_url_hash(url_hash)
        return short_url

    def _generate_short_url(self, url_id):
        return self._generate_url_hash(url_id)

    @staticmethod
    def _generate_url_hash(url_id):
        # Generate the unique hash for the Short URL based on the Primary Index of the long_url
        hasher = hashlib.md5(str(url_id).encode('utf-8'))
        return base64.urlsafe_b64encode(hasher.digest()).decode('utf-8')[:8]

    def handle_delete_short_url(self, hash_key):
        if hash_key:
            url = self.URL_ENGINE.get_url(hash_key)
            if url:
                self.URL_ENGINE.delete_url(hash_key)
                return jsonify(success=True)
            else:
                return Response('The requested Short URL was not found in the system.', status=400)

        return Response('No Short URL was supplied.', status=400)

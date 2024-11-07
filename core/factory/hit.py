from datetime import datetime
from flask import jsonify, request, redirect, Response
from core.engine import HitEngine, UrlEngine
from core.factory.base import BaseFactory


class HitFactory(BaseFactory):
    def __init__(self, app, **kwargs):
        super(HitFactory, self).__init__(app, **kwargs)

        kwargs.update({'app': app})
        self.HIT_ENGINE = HitEngine(**kwargs)
        self.URL_ENGINE = UrlEngine(**kwargs)

    def handle_redirect(self, hash_key):
        # Check if a URL exists for the specified hash_key
        url = self.URL_ENGINE.get_url(hash_key)
        if url and not url.get('is_deleted', False):
            # Log the redirect for analytics
            hit = {
                'url_hash_id': url.get('id'),
                'ip_address': request.remote_addr,
                'user_agent': request.headers.get('User-Agent'),
                'date_created': datetime.now()
            }
            self.HIT_ENGINE.create_hit(hit)

            # Handle the redirect
            return redirect(url.get('url'))
        # If unable to find a matching Short URL for the supplied hash
        return Response('The requested Short URL was not found in the system.', status=404)

    def handle_statistics(self, hash_key):
        # Check if a URL exists for the specified hash_key
        statistics = self.HIT_ENGINE.get_statistics(hash_key)
        if statistics and statistics.get('id'):
            if statistics.get('is_deleted', False):
                return Response(f"This Short URL was deleted at {statistics.get('date_modified').strftime('%m/%d/%Y, %H:%M:%S')}", status=400)
            else:
                return jsonify(success=True, statistics=statistics)

        # If unable to find a matching Short URL for the supplied hash
        return Response('The requested Short URL was not found in the system.', status=400)

import re
import json
import traceback

from couchpotato.core.helpers.variable import tryInt, getIdentifier
from couchpotato.core.logger import CPLog
from couchpotato.core.media._base.providers.torrent.base import TorrentProvider


log = CPLog(__name__)


class Base(TorrentProvider):

    urls = {
        'test': 'https://hdbits.org/',
        'detail': 'https://hdbits.org/details.php?id=%s',
        'download': 'https://hdbits.org/download.php?id=%s&passkey=%s',
        'api': 'https://hdbits.org/api/torrents'
    }

    http_time_between_calls = 1 #seconds

    def _post_query(self, **params):

        post_data = {
            'username': self.conf('username'),
            'passkey': self.conf('passkey')
        }
        post_data.update(params)

        try:
            result = self.getJsonData(self.urls['api'], data = json.dumps(post_data))

            if result:
                if result['status'] != 0:
                    log.error('Error searching hdbits: %s' % result['message'])
                else:
                    return result['data']
        except:
            pass

        return None

    def _search(self, movie, quality, results):

        match = re.match(r'tt(\d{7})', getIdentifier(movie))

        data = self._post_query(imdb = {'id': match.group(1)})

        if data:
            try:
                for result in data:
                    results.append({
                        'id': result['id'],
                        'name': result['name'],
                        'url': self.urls['download'] % (result['id'], self.conf('passkey')),
                        'detail_url': self.urls['detail'] % result['id'],
                        'size': tryInt(result['size'])/1024/1024,
                        'seeders': tryInt(result['seeders']),
                        'leechers': tryInt(result['leechers'])
                    })
            except:
                log.error('Failed getting results from %s: %s', (self.getName(), traceback.format_exc()))


config = [{
    'name': 'hdbits',
    'groups': [
        {
            'tab': 'searcher',
            'list': 'torrent_providers',
            'name': 'HDBits',
            'description': 'See <a href="http://hdbits.org">HDBits</a>',
            'options': [
                {
                    'name': 'enabled',
                    'type': 'enabler',
                    'default': False,
                },
                {
                    'name': 'username',
                    'default': '',
                },
                {
                    'name': 'passkey',
                    'default': '',
                },
                {
                    'name': 'seed_ratio',
                    'label': 'Seed ratio',
                    'type': 'float',
                    'default': 1,
                    'description': 'Will not be (re)moved until this seed ratio is met.',
                },
                {
                    'name': 'seed_time',
                    'label': 'Seed time',
                    'type': 'int',
                    'default': 40,
                    'description': 'Will not be (re)moved until this seed time (in hours) is met.',
                },
                {
                    'name': 'extra_score',
                    'advanced': True,
                    'label': 'Extra Score',
                    'type': 'int',
                    'default': 0,
                    'description': 'Starting score for each release found via this provider.',
                },
            ],
        },
    ],
}]

import psycopg2
import random


class OnDemandConnectionContext(object):

    """open/close postgresql connection on demand"""

    def __init__(self, dbparams):
        self.dbparams = dbparams
        self.conn = None

    def __enter__(self):
        if isinstance(self.dbparams, dict):
            params = self.dbparams

            # if multiple hosts are provided, select one at random
            host = params.get('host')
            if host and isinstance(host, list):
                host = random.choice(host)
                params = params.copy()
                params['host'] = host

            self.conn = psycopg2.connect(**params)

        else:
            assert isinstance(self.dbparams, str), \
                    'Unknown dbparams: %s' % self.dbparams
            self.conn = psycopg2.connect(self.dbparams)
        return self.conn

    def __exit__(self, type, value, traceback):
        assert self.conn
        self.conn.close()
        self.conn = None


class ConnectionContextManager(object):

    """
    postgresql connection manager

    This just opens and closes a connection for every call, but provides a hook
    to modify that behavior in the future if desired.
    """

    def __init__(self, dbparams):
        self.dbparams = dbparams

    def __call__(self):
        return OnDemandConnectionContext(self.dbparams)

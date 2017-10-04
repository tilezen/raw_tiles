import psycopg2


class OnDemandConnectionContext(object):

    """open/close postgresql connection on demand"""

    def __init__(self, dbparams):
        self.dbparams = dbparams
        self.conn = None

    def __enter__(self):
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

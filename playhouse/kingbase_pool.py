"""Synchronous KingbaseES connection pools for the PostgreSQL wire driver."""

from playhouse.kingbase_native import KingbaseMySQLDatabase
from playhouse.pool import PooledDatabase


class PooledKingbaseMySQLDatabase(PooledDatabase, KingbaseMySQLDatabase):
    """Reuse Kingbase MySQL-mode connections without PyMySQL-specific ping."""

    def _is_closed(self, conn):
        return bool(conn.closed)

    def _can_reuse(self, conn):
        return not self._is_closed(conn)

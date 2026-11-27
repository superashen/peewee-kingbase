"""Kingbase-specific schema migration DDL and legacy factory alias."""

from peewee import ForeignKeyField
from peewee import Index
from peewee import SQL
from peewee import Table

from playhouse.migrate import PostgresqlMigrator
from playhouse.migrate import SchemaMigrator
from playhouse.migrate import make_index_name
from playhouse.migrate import operation


class KingbaseMySQLMigrator(PostgresqlMigrator):
    """Use PostgreSQL-style DDL accepted by Kingbase MySQL compatibility mode."""

    explicit_create_foreign_key = True

    def add_inline_fk_sql(self, ctx, field):
        # This mode uses the explicit foreign-key operation.
        pass

    @operation
    def add_index(self, table, columns, unique=False, using=None):
        ctx = self.make_context()
        index_name = make_index_name(table, columns)
        table_obj = Table(table)
        cols = [getattr(table_obj.c, column) for column in columns]
        index = Index(index_name, table_obj, cols, unique=unique, using=using)
        with ctx(index_using_precedes_table=False):
            ctx.sql(index)
        return ctx

    @operation
    def rename_table(self, old_name, new_name):
        # Do not attempt to rename a PostgreSQL sequence with the table.
        return SchemaMigrator.rename_table(
            self, old_name, new_name, with_context=True)


class KingbaseSQLServerMigrator(KingbaseMySQLMigrator):
    """Use SQL Server's ADD syntax for the public migration entrypoint."""

    @operation
    def alter_column_type(self, table, column, field, cast=None):
        if cast is not None:
            raise ValueError('SQL Server ALTER COLUMN does not support USING.')
        ctx = self.make_context()
        return (self._alter_column(ctx, table, column)
                .literal(' ')
                .sql(field.ddl_datatype(ctx))
                .literal(' NULL' if field.null else ' NOT NULL'))

    @operation
    def alter_add_column(self, table, column_name, field):
        ctx = self.make_context()
        old_null, field.null = field.null, True
        try:
            if field.column_name != column_name:
                field.name = field.column_name = column_name
            self._alter_table(ctx, table).literal(' ADD ').sql(field.ddl(ctx))
            if any(isinstance(item, SQL) and
                   'default' in item.sql.lower() for item in
                   (field.constraints or ())):
                ctx.literal(' WITH VALUES')
            if isinstance(field, ForeignKeyField):
                self.add_inline_fk_sql(ctx, field)
        finally:
            field.null = old_null
        return ctx


class KingbaseSchemaMigrator(SchemaMigrator):
    """Compatibility alias for callers of the previous Kingbase entrypoint."""

    @classmethod
    def from_database(cls, database):
        return SchemaMigrator.from_database(database)


__all__ = ['KingbaseMySQLMigrator', 'KingbaseSQLServerMigrator',
           'KingbaseSchemaMigrator']

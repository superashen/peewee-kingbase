.. image:: https://media.charlesleifer.com/blog/photos/peewee4-logo.png

peewee
======

Peewee is a simple and small ORM. It has few (but expressive) concepts, making
it easy to learn and intuitive to use.

Peewee is a single module with no required dependencies and has been running
production workloads of all sizes since 2010.

* a small, expressive ORM
* flexible query-builder that exposes full power of SQL
* supports sqlite, mysql, mariadb, postgresql
* this source tree adds KingbaseES MySQL, Oracle and SQL Server compatibility-mode adapters
* `asyncio support <https://docs.peewee-orm.com/en/latest/peewee/asyncio.html>`__
  built on the standard async drivers (aiosqlite, asyncpg, aiomysql)
* tons of extensions
* use with `flask <https://docs.peewee-orm.com/en/latest/peewee/framework_integration.html#flask>`__,
  `fastapi <https://docs.peewee-orm.com/en/latest/peewee/framework_integration.html#fastapi>`__,
  `pydantic <https://docs.peewee-orm.com/en/latest/peewee/orm_utils.html#module-playhouse.pydantic_utils>`__, and
  `more <https://docs.peewee-orm.com/en/latest/peewee/framework_integration.html>`__.

New to peewee? These may help:

* `Quickstart <https://docs.peewee-orm.com/en/latest/peewee/quickstart.html#quickstart>`_
* `Example twitter app <https://docs.peewee-orm.com/en/latest/peewee/example.html#example>`_
* `Using peewee interactively <https://docs.peewee-orm.com/en/latest/peewee/interactive.html#interactive>`_
* `Models and fields <http://docs.peewee-orm.com/en/latest/peewee/models.html>`_
* `Querying <http://docs.peewee-orm.com/en/latest/peewee/querying.html>`_
* `Relationships and joins <http://docs.peewee-orm.com/en/latest/peewee/relationships.html>`_
* `Extensive library of SQL / Peewee examples <https://docs.peewee-orm.com/en/latest/peewee/query_library.html#query-library>`_
* `Flask setup <https://docs.peewee-orm.com/en/latest/peewee/framework_integration.html#flask>`_
  or `FastAPI setup <https://docs.peewee-orm.com/en/latest/peewee/framework_integration.html#fastapi>`_

Installation:

.. code-block:: console

    pip install peewee

The command above installs upstream Peewee. To use the KingbaseES adapters
described below, install this adapted source tree instead.

Sqlite comes built-in provided by the standard-lib ``sqlite3`` module. Other
backends can be installed using the following instead:

.. code-block:: console

    pip install peewee[mysql]  # Install peewee with pymysql.
    pip install peewee[postgres]  # Install peewee with psycopg2.
    pip install peewee[psycopg3]  # Install peewee with psycopg3.

    # AsyncIO implementations.
    pip install peewee[aiosqlite]  # Install peewee with aiosqlite.
    pip install peewee[aiomysql]  # Install peewee with aiomysql.
    pip install peewee[asyncpg]  # Install peewee with asyncpg.

KingbaseES compatibility modes
------------------------------

This Peewee 4.2.6 source tree includes adapters for KingbaseES MySQL,
Oracle and SQL Server compatibility modes. Select the adapter that matches
the target instance's ``database_mode``; passing a different SQL dialect to
an instance does not change its mode. The verified targets are V9R3C18
(MySQL), V9R2C16 (Oracle) and V9R4C19 (SQL Server).

The synchronous entry points are ``KingbaseMySQLDatabase``,
``KingbaseOracleDatabase`` and ``KingbaseSQLServerDatabase`` in
``playhouse.kingbase_native``. They retain Peewee's model and query API while
adapting connections, SQL compilation, schema operations and catalog
reflection for the selected mode. Synchronous connections in all three modes
require ``ksycopg2``. Install the official KingbaseES package separately
into the same Python environment as Peewee. For the verified Linux x86_64 /
CPython 3.10 environment, PyPI provides a matching ``ksycopg2`` 2.9.0 wheel.
The driver is not bundled in the Peewee source tree. If the client library
cannot be loaded, follow the KingbaseES driver documentation to install the
matching ``libkci`` library and configure its library search path.
The MySQL-only synchronous pool and reconnect classes are
``PooledKingbaseMySQLDatabase`` in
``playhouse.kingbase_pool`` and ``ReconnectKingbaseMySQLDatabase`` in
``playhouse.kingbase_reconnect``.

For asynchronous use, install ``asyncpg-kes`` in the same environment. It is
imported as ``asyncpg`` and supports ``kes_mode='mysql'``, ``'oracle'`` or
``'sqlserver'``; the ordinary ``asyncpg`` distribution is not a substitute.
The optional extra ``kingbase-async`` declares this dependency, while the
ordinary Peewee ``asyncpg`` extra remains unchanged. The adapters check for
``kes_mode`` support and raise ``ImproperlyConfigured`` before connecting if
the required driver is unavailable.

.. code-block:: console

    # Run from this adapted Peewee source tree.
    python -m pip install -e .
    # Install the official KingbaseES synchronous client package.
    python -m pip install "ksycopg2==2.9.0"
    # For asynchronous access, install the matching asyncpg-kes source or wheel.
    python -m pip install -e /path/to/asyncpg-kes

Use a database name and connection settings for the chosen instance. For
example, the synchronous MySQL-mode entry point is:

.. code-block:: python

    import os
    from peewee import CharField, Model
    from playhouse.kingbase_native import KingbaseMySQLDatabase

    db = KingbaseMySQLDatabase(
        os.environ['KINGBASE_DB'],
        host=os.environ['KINGBASE_HOST'],
        port=int(os.environ['KINGBASE_PORT']),
        user=os.environ['KINGBASE_USER'],
        password=os.environ['KINGBASE_PASSWORD'])

    class User(Model):
        name = CharField(unique=True)

        class Meta:
            database = db

    with db:
        db.create_tables([User], safe=True)
        User.get_or_create(name='example')
        print(User.get(User.name == 'example').name)

For Oracle or SQL Server, replace the database class with
``KingbaseOracleDatabase`` or ``KingbaseSQLServerDatabase`` and supply that
mode's database name and connection settings. Oracle mode preserves distinct
empty strings by default; set ``preserve_empty_strings=False`` on its database
constructor if native Oracle empty-string semantics are required.

The asynchronous entry points are ``AsyncKingbaseMySQLDatabase``,
``AsyncKingbaseOracleDatabase`` and ``AsyncKingbaseSQLServerDatabase`` in
``playhouse.kingbase_async``. They provide an independent asynchronous pool
and execution API; a synchronous Peewee query can be passed to ``aexecute()``,
``afetchrow()`` or ``alist()``. Model helpers include ``aget()``, ``acreate()``,
``acreate_tables()`` and ``adrop_tables()``. Use ``atransaction()`` for
commit/rollback and close the pool at application shutdown:

.. code-block:: python

    import asyncio
    import os
    from playhouse.kingbase_async import AsyncKingbaseSQLServerDatabase

    db = AsyncKingbaseSQLServerDatabase(
        os.environ['KINGBASE_SQLSERVER_DB'],
        host=os.environ['KINGBASE_HOST'],
        port=int(os.environ['KINGBASE_SQLSERVER_PORT']),
        user=os.environ['KINGBASE_USER'],
        password=os.environ['KINGBASE_PASSWORD'])

    async def main():
        await db.connect_async()
        try:
            async with db.atransaction():
                value = await db.afetchval(
                    'SELECT CAST(%s AS INTEGER)', (1,))
                print(value)
        finally:
            await db.close_async()

    asyncio.run(main())

Validation
~~~~~~~~~~

The repository's KingbaseES test runner covers synchronous integration,
database interfaces, asynchronous integration and the Peewee full suite. It
uses protected local instance settings and creates disposable test users and
databases. From this source tree, run the MySQL/Oracle matrix or the SQL
Server matrix as follows (these scripts require the corresponding local
``tests/kingbase/.env.*.local`` configuration and target instances):

.. code-block:: console

    PGTZ=UTC bash tests/kingbase/run_new_versions_full.sh
    bash tests/kingbase/run_sqlserver_full.sh

The Oracle full-suite result uses a UTC test connection session. In the
recorded runs, MySQL completed 1665 full-suite tests with 233 skipped;
Oracle completed 1665 with 206 skipped under UTC; SQL Server completed 1665
with 206 skipped. Each recorded full-suite process exited successfully.
Skipped tests are not counted as executed passes. Exact commands, per-stage
results and logs are in ``tests/kingbase/results/``: see
``v9-new-full-2026-11-12-120332-4276fe/`` for MySQL,
``v9-new-full-2026-11-21-144521-4069bb/`` for the current Oracle full suite,
and ``v9-new-full-2026-11-12-143703-790fb1/`` for SQL Server. The runner is
configured for these local V9 instances; adjust its instance-specific test
configuration before using it against another environment.

Examples
--------

Defining models is similar to Django or SQLAlchemy:

.. code-block:: python

    from peewee import *
    import datetime


    db = SqliteDatabase('my_database.db')

    class BaseModel(Model):
        class Meta:
            database = db

    class User(BaseModel):
        username = CharField(unique=True)

    class Tweet(BaseModel):
        user = ForeignKeyField(User, backref='tweets')
        message = TextField()
        created_date = DateTimeField(default=datetime.datetime.now)
        is_published = BooleanField(default=True)

Connect to the database and create tables:

.. code-block:: python

    db.connect()
    db.create_tables([User, Tweet])

Create a few rows:

.. code-block:: python

    charlie = User.create(username='charlie')
    huey = User(username='huey')
    huey.save()

    # No need to set `is_published` or `created_date` since they
    # will just use the default values we specified.
    Tweet.create(user=charlie, message='My first tweet')

Queries are expressive and composable:

.. code-block:: python

    # A simple query selecting a user.
    User.get(User.username == 'charlie')

    # Get tweets created by one of several users.
    usernames = ['charlie', 'huey', 'mickey']
    users = User.select().where(User.username.in_(usernames))
    tweets = Tweet.select().where(Tweet.user.in_(users))

    # We could accomplish the same using a JOIN:
    tweets = (Tweet
              .select()
              .join(User)
              .where(User.username.in_(usernames)))

    # How many tweets were published today?
    tweets_today = (Tweet
                    .select()
                    .where(
                        (Tweet.created_date >= datetime.date.today()) &
                        (Tweet.is_published == True))
                    .count())

    # Paginate the user table and show me page 3 (users 41-60).
    User.select().order_by(User.username).paginate(3, 20)

    # Order users by the number of tweets they've created:
    tweet_ct = fn.Count(Tweet.id)
    users = (User
             .select(User, tweet_ct.alias('ct'))
             .join(Tweet, JOIN.LEFT_OUTER)
             .group_by(User)
             .order_by(tweet_ct.desc()))

    # Do an atomic update (for illustrative purposes only, imagine a simple
    # table for tracking a "count" associated with each URL). We don't want to
    # naively get the save in two separate steps since this is prone to race
    # conditions.
    Counter.update(count=Counter.count + 1).where(Counter.url == request.url).execute()

Check out the `example twitter app <http://docs.peewee-orm.com/en/latest/peewee/example.html>`_.

Asyncio
-------

.. code-block:: python

    import asyncio
    from peewee import *
    from playhouse.pwasyncio import AsyncPostgresqlDatabase

    db = AsyncPostgresqlDatabase('my_app')

    class User(db.Model):
        username = CharField(unique=True)

    class Tweet(db.Model):
        user = ForeignKeyField(User, backref='tweets')
        message = TextField()

    async def main():
        async with db:
            await db.acreate_tables([User, Tweet])

            # Queries are awaited on the event loop using asyncpg.
            huey = await User.acreate(username='huey')
            tweet = await Tweet.acreate(user=huey, message='meow')

            async with db.atomic():
                tweet.message = 'purr'
                await tweet.asave()

            # Create a query - nothing is executed yet.
            query = Tweet.select(Tweet, User).join(User)

            # Execute and buffer the results.
            tweets = await query.aexecute()  # Or: await db.list(query)
            for tweet in tweets:
                print(tweet.user.username, '->', tweet.message)

            # Streaming results via server-side cursor.
            async for tweet in db.iterate(query):
                print(tweet.user.username, '->', tweet.message)

        await db.close_pool()

    asyncio.run(main())

See the `asyncio docs <https://docs.peewee-orm.com/en/latest/peewee/asyncio.html>`_
for details.

Learning more
-------------

Check the `documentation <http://docs.peewee-orm.com/>`_ for more examples.

Specific question? Come hang out in the #peewee channel on irc.libera.chat, or post to the mailing list, http://groups.google.com/group/peewee-orm . If you would like to report a bug, `create a new issue <https://github.com/coleifer/peewee/issues/new>`_ on GitHub.

Still want more info?
---------------------

.. image:: https://media.charlesleifer.com/blog/photos/wat.jpg

I've written a number of blog posts about building applications and web-services with peewee (and usually Flask). If you'd like to see some real-life applications that use peewee, the following resources may be useful:

* `Building a note-taking app with Flask and Peewee <https://charlesleifer.com/blog/saturday-morning-hack-a-little-note-taking-app-with-flask/>`_ as well as `Part 2 <https://charlesleifer.com/blog/saturday-morning-hacks-revisiting-the-notes-app/>`_ and `Part 3 <https://charlesleifer.com/blog/saturday-morning-hacks-adding-full-text-search-to-the-flask-note-taking-app/>`_.
* `Analytics web service built with Flask and Peewee <https://charlesleifer.com/blog/saturday-morning-hacks-building-an-analytics-app-with-flask/>`_.
* `Personalized news digest (with a boolean query parser!) <https://charlesleifer.com/blog/saturday-morning-hack-personalized-news-digest-with-boolean-query-parser/>`_.
* `Structuring Flask apps with Peewee <https://charlesleifer.com/blog/structuring-flask-apps-a-how-to-for-those-coming-from-django/>`_.
* `Creating a lastpass clone with Flask and Peewee <https://charlesleifer.com/blog/creating-a-personal-password-manager/>`_.
* `Creating a bookmarking web-service that takes screenshots of your bookmarks <https://charlesleifer.com/blog/building-bookmarking-service-python-and-phantomjs/>`_.
* `Building a pastebin, wiki and a bookmarking service using Flask and Peewee <https://charlesleifer.com/blog/dont-sweat-small-stuff-use-flask-blueprints/>`_.
* `Encrypted databases with Python and SQLCipher <https://charlesleifer.com/blog/encrypted-sqlite-databases-with-python-and-sqlcipher/>`_.
* `Dear Diary: An Encrypted, Command-Line Diary with Peewee <https://charlesleifer.com/blog/dear-diary-an-encrypted-command-line-diary-with-python/>`_.

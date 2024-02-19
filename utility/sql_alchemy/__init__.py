from .model import SQLAlchemy_Manager
from .globals import sqlAlchemy_manager


def initialize(app, echo: bool = False):
    """Initialize SQL Alchemy with application."""

    # get application config.
    sql_alchemy_database_uri = app.config['SQLALCHEMY_DATABASE_URI']

    from sqlalchemy import create_engine
    # an Engine, which the Session will use for connection resources.
    engine = create_engine(sql_alchemy_database_uri, pool_recycle=280, pool_pre_ping=True, echo=echo)

    # create sqlalchemy manager.
    sqlAlchemy_manager.setup_engine(engine)


def setup(uri: str, pool_recycle: int = 280, pool_pre_ping: bool = True, echo: bool = False):
    """Setup for console.
    Requires:
        'uri': SQL Alchemy Database Uri.
    Options:
        'pool_recycle': connection pool recycle time distance.
        'pool_pre_ping': connection pool recycle pre ping.
        'echo': is enable echo.
    """

    # an Engine, which the Session will use for connection resources.
    from sqlalchemy import create_engine
    engine = create_engine(uri, pool_recycle=pool_recycle, pool_pre_ping=pool_pre_ping, echo=echo)

    # create sqlalchemy manager.
    sqlAlchemy_manager.setup_engine(engine)

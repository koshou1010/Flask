import contextlib


class SQLAlchemy_Manager:
    Engine = None
    session_maker = None

    # set attribute for all element.
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        if self.Engine:
            # create a configured "Session" class
            from sqlalchemy.orm import sessionmaker
            self.session_maker = sessionmaker(autocommit=False, autoflush=False, bind=self.Engine)

    def setup_engine(self, engine):
        self.Engine = engine

        # create a configured "Session" class
        from sqlalchemy.orm import sessionmaker
        self.session_maker = sessionmaker(autocommit=False, autoflush=False, bind=self.Engine)

    # Create Tables bound to specific engine.
    def create_all(self):
        from .globals import Base
        Base.metadata.create_all(self.Engine)

    # create connection with an __enter__ method and an __exit__ method for the with statement.
    @contextlib.contextmanager
    def Session(self):
        # later, some unit of code wants to create a session that is bound to a specific Connection.
        conn = self.Engine.connect()
        dbsession = self.session_maker(bind=conn)
        try:
            yield dbsession
        finally:
            conn.close()
            dbsession.close()

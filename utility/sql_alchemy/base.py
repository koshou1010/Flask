from sqlalchemy import Column, ForeignKey, types, desc
from datetime import datetime, date
from decimal import Decimal
from json import dumps, load
from .globals import sqlAlchemy_manager


class BaseModel:
    """Create base unit for all db model."""

    # is data valid.
    valid_flag = Column(types.Boolean, nullable=False, default=True)
    # record the user creating data.
    create_user = Column(types.String(40), nullable=False)
    # record the time data created.
    create_datetime = Column(types.DateTime, nullable=False, default=datetime.now)
    # record the user updating data.
    update_user = Column(types.String(40), nullable=False)
    # record the time data updated.
    update_datetime = Column(types.DateTime, nullable=False, onupdate=datetime.now, default=datetime.now)

    # set attribute for all element.
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    # soft delete.
    def Delete(self):
        self.ValidFlag = False

    def jsonify_dictionary(self):
        fields = {}
        for field in [x for x in dir(self) if not x.startswith('_') and x != 'metadata']:
            data = self.__getattribute__(field)
            try:
                dumps(data)  # this will fail on non-encodable values, like other classes
                fields[field] = data
            except TypeError:
                if isinstance(data, Decimal):
                    fields[field] = float(data)

                # if datetime, return isoformat.
                elif isinstance(data, (date, datetime)):
                    fields[field] = data.isoformat()

        # a json-encodable dict.
        return fields

    # get specific data by identity.
    @classmethod
    def find_by_id(cls, id: int, validflag: bool = True):
        with sqlAlchemy_manager.Session() as session:
            query = session.query(cls).filter_by(Id=id, ValidFlag=validflag)
            result = next(iter(query or []), None)
        return result

import datetime

import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Changes(SqlAlchemyBase):
    __tablename__ = 'changes'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    from_text = sqlalchemy.Column(sqlalchemy.String,
                                  nullable=True)
    to_text = sqlalchemy.Column(sqlalchemy.String,
                                nullable=True)
    subject = sqlalchemy.Column(sqlalchemy.String,
                                nullable=True)
    edited_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                    default=datetime.datetime.now)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User')

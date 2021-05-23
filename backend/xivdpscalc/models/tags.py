"""Model for tags in the database"""
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, declared_attr
from sqlalchemy.schema import Column, Table
from sqlalchemy.types import Integer, String

from xivdpscalc import db
from xivdpscalc.models.types import HexColor

TAG_NAME_MAX_LENGTH = 64


class Tag(db.Model):
  __tablename__ = 'tags'

  id = Column(Integer, primary_key=True)
  name = Column(String(TAG_NAME_MAX_LENGTH))
  color = Column(HexColor)


class HasTags:
  @declared_attr
  def tags(cls):
    tag_association = Table(
      f'{cls.__tablename__}_tags',
      cls.metadata,
      Column(
        'tag_id',
        ForeignKey('tags.id'),
        primary_key=True
      ),
      Column(
        f'{cls.__tablename__}_id',
        ForeignKey(f'{cls.__tablename__}.id')
      )
    )
    return relationship(Tag, secondary=tag_association)

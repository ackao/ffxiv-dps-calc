"""Model for saving gearsets in the database"""
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.schema import Column
from sqlalchemy.types import JSON, String, Text, Boolean, Integer
from uuid import uuid4

from xivdpscalc import db
from xivdpscalc.models.tags import HasTags


class Gearset(db.Model, HasTags):
    __tablename__ = 'gearsets'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(64))
    description = Column(Text())
    etro_id = Column(UUID(as_uuid=True))
    stats = Column(JSON)
    estimates = Column(JSON)
    sim_version = Column(Integer)
    recommended = Column(Boolean)

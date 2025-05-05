import enum, uuid

from sqlalchemy import Column, String, Enum, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import BYTEA, OID
from sqlalchemy.orm import relationship
from datetime import datetime


Base = declarative_base()

class MediaType(enum.Enum):
    TEXT  = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"

class Storage(enum.Enum):
    BYTEA = "bytea"
    LO    = "large_object"

class CrewOutput(Base):
    __tablename__ = "crew_output"

    id            = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id       = Column(String, ForeignKey("crew_task.id"), nullable=False)
    agent_name    = Column(String, nullable=False)
    media_type    = Column(Enum(MediaType), nullable=False)
    mime_type     = Column(String, nullable=False)

    storage_kind  = Column(Enum(Storage), nullable=False)
    data_bytea    = Column(BYTEA)    # se storage_kind == BYTEA
    lo_oid        = Column(OID)      # se storage_kind == LO

    created_at    = Column(DateTime, default=datetime.utcnow)
    task          = relationship("CrewTask", back_populates="outputs")

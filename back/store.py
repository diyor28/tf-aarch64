from sqlalchemy import Column, Integer, DateTime, String, func, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from back.utils import get_filename

Base = declarative_base()

db_uri = "sqlite:///./data/data.db?check_same_thread=False"
eng = create_engine(db_uri)
Session = sessionmaker(bind=eng)


def default_id(context):
    params = context.get_current_parameters()
    return get_filename(params["python"], params["package"], params["type"])


class Build(Base):
    __tablename__ = "builds"

    class Status:
        PENDING = 'pending'
        BUILDING = 'building'
        FAILED = 'failed'
        CANCELLED = 'cancelled'
        COMPLETED = 'completed'

    class Type:
        TENSORFLOW = 'tensorflow'
        TFX = 'tfx'

    id = Column(String, primary_key=True, default=default_id)
    python = Column(String)
    package = Column(String)
    file = Column(String, nullable=True)
    status = Column(String, default=Status.PENDING)
    type = Column(String, default=Type.TENSORFLOW)
    created_at = Column(DateTime, server_default=func.now())
    update_at = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return "<Build(python='%s', tensorflow='%s')>" % (
            self.python,
            self.tensorflow
        )

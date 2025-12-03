from sqlalchemy import Column, Integer,String,TIMESTAMP,CheckConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import func
import uuid


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    email = Column(String,unique=True,index=True,nullable=False)
    password = Column(String,nullable=False)
    nickname = Column(String,nullable=False)
    avatar_url = Column(String)
    subscription_tier = Column(String,default='Free')
    balance = Column(Integer,default=0)
    created_at = Column(TIMESTAMP,default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        CheckConstraint("subscription_tier IN ('Free', 'Pro')", name='valid_subscription_tier'),
    )
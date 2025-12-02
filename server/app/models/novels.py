import uuid
from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base  # 假设你的 Base 是在这里定义的

class Novels(Base):
    __tablename__ = "novels"  # 注意：这里必须是等号 =
    # 1. 主键 ID
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # 2. 外键 User ID
    # 对应 SQL: user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE
    user_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    # 3. 标题
    # 对应 SQL: title VARCHAR(200) NOT NULL
    title = Column(String(200), nullable=False)
    # 4. 描述
    # 对应 SQL: description TEXT
    description = Column(Text)
    # 5. 封面 URL
    # 对应 SQL: cover_url VARCHAR(500)
    cover_url = Column(String(500))
    # 6. 状态
    # 对应 SQL: status ... DEFAULT 'draft' CHECK (...)
    # server_default 是告诉数据库设置默认值，default 是告诉 Python 设置默认值
    status = Column(String(20), server_default="draft", default="draft", nullable=False)
    # 7. 字数
    # 对应 SQL: word_count INTEGER DEFAULT 0
    word_count = Column(Integer, server_default="0", default=0)
    # 8. 软删除标记
    # 对应 SQL: is_deleted BOOLEAN DEFAULT FALSE
    is_deleted = Column(Boolean, server_default="false", default=False)
    # 9. 删除时间
    # 对应 SQL: deleted_at TIMESTAMP
    deleted_at = Column(TIMESTAMP(timezone=False), nullable=True)
    # 10. 创建时间
    # 对应 SQL: created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    created_at = Column(TIMESTAMP(timezone=False), server_default=func.now(), nullable=False)
    # 11. 更新时间
    # 对应 SQL: updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    # 通常我们还会加上 onupdate=func.now() 让 Python 在更新时自动修改这个时间
    updated_at = Column(
        TIMESTAMP(timezone=False), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False
    )
    # 约束条件 (对应 SQL 中的 CHECK)
    __table_args__ = (
        CheckConstraint("status IN ('draft', 'published', 'completed')", name="check_novel_status"),
    )
    # 关系属性 (可选，方便在代码中通过 novel.owner 访问用户对象)
    # owner = relationship("User", back_populates="novels")
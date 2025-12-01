# 后端数据库表设计汇总 (V1.1)

## 数据库概述
- **数据库类型**: PostgreSQL
- **ORM**: SQLAlchemy
- **字符集**: UTF-8
- **UUID支持**: 开启uuid-ossp扩展
- **特殊类型**: 使用ARRAY和JSONB处理标签与属性

## 初始化SQL
```sql
-- 开启UUID扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- 开启pg_trgm扩展（可选，后续用于模糊搜索优化）
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

## 核心表结构

### 1. 用户表 (users)
> **安全策略说明**: 本表**严禁**存储 OpenAI/Claude 等平台的 API Key。
> 用户 Key 仅由前端加密缓存在用户设备 (LocalStorage) 中，后端仅做内存级透传，不落盘、不记录日志。
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nickname VARCHAR(100) NOT NULL,
    avatar_url VARCHAR(500),
    subscription_tier VARCHAR(20) DEFAULT 'Free' CHECK (subscription_tier IN ('Free', 'Pro')),
    balance INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**字段说明:**
- `id`: 主键，自增
- `email`: 邮箱，唯一索引
- `password_hash`: 密码哈希值
- `nickname`: 用户昵称
- `avatar_url`: 头像URL（支持外部链接或系统预设）
- `subscription_tier`: 会员等级（Free/Pro）
- `balance`: 用户余额/额度
- `created_at`: 创建时间
- `updated_at`: 更新时间

### 2. 小说表 (novels)
```sql
CREATE TABLE novels (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    cover_url VARCHAR(500),
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'completed')),
    word_count INTEGER DEFAULT 0,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**字段说明:**
- `id`: 主键，自增
- `user_id`: 用户ID，外键关联users表
- `title`: 小说标题
- `description`: 小说简介
- `cover_url`: 封面图片URL
- `status`: 小说状态（草稿/已发布/已完成）
- `word_count`: 总字数
- `is_deleted`: 软删除标记
- `created_at`: 创建时间
- `updated_at`: 更新时间

### 3. 卷表 (volumes)
```sql
CREATE TABLE volumes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    novel_id UUID NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    sort_order INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**字段说明:**
- `id`: 主键，自增
- `novel_id`: 小说ID，外键关联novels表
- `title`: 卷标题
- `description`: 卷简介
- `sort_order`: 排序序号
- `created_at`: 创建时间
- `updated_at`: 更新时间

### 4. 章节表 (chapters)
> **V1.1 变更**: 新增 `summary` 字段，用于存储 AI 生成的章节摘要，优化长文本续写的 Context 消耗。
```sql
CREATE TABLE chapters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    volume_id UUID NOT NULL REFERENCES volumes(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    
    -- AI 上下文压缩核心字段
    summary TEXT,  
    
    word_count INTEGER DEFAULT 0,
    sort_order INTEGER NOT NULL,
    client_updated_at TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**字段说明:**
- `id`: 主键，自增
- `volume_id`: 卷ID，外键关联volumes表
- `title`: 章节标题
- `content`: 章节内容（Markdown格式）
- `word_count`: 章节字数
- `sort_order`: 排序序号
- `is_deleted`: 软删除标记
- `created_at`: 创建时间
- `updated_at`: 更新时间

### 5. 人物表 (characters)
> **V1.1 变更**: 新增 `tags` 字段 (Postgres Array 类型)，用于标记阵营、种族、身份等（如 `['宗门', '反派', '元婴期']`）。
```sql
CREATE TABLE characters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    novel_id UUID NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    gender VARCHAR(10) CHECK (gender IN ('male', 'female', 'other')),
    avatar_url VARCHAR(500),
    
    -- 核心设定
    tags TEXT[], -- 使用数组存储标签，便于索引检索
    description TEXT,
    personality TEXT,
    background TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**字段说明:**
- `id`: 主键，自增
- `novel_id`: 小说ID，外键关联novels表
- `name`: 人物姓名
- `gender`: 性别
- `avatar_url`: 立绘图片URL
- `description`: 人物描述
- `personality`: 性格特点
- `background`: 背景故事
- `created_at`: 创建时间
- `updated_at`: 更新时间

### 6. 人物关系表 (character_relationships)
```sql
CREATE TABLE character_relationships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    novel_id UUID NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    character_from_id UUID NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    character_to_id UUID NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    relationship_type VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK(character_from_id != character_to_id)
);
```

**字段说明:**
- `id`: 主键，自增
- `novel_id`: 小说ID，外键关联novels表
- `character_from_id`: 关系发起方人物ID
- `character_to_id`: 关系接受方人物ID
- `relationship_type`: 关系类型（朋友/敌人/家人/恋人等）
- `description`: 关系描述
- `created_at`: 创建时间
- `updated_at`: 更新时间

### 7. 地点表 (locations)
```sql
CREATE TABLE locations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    novel_id UUID NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50),
    description TEXT,
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**字段说明:**
- `id`: 主键，自增
- `novel_id`: 小说ID，外键关联novels表
- `name`: 地点名称
- `type`: 地点类型（城市/建筑/自然景观等）
- `description`: 地点描述
- `image_url`: 地点图片URL
- `created_at`: 创建时间
- `updated_at`: 更新时间

### 8. 物品表 (items)
```sql
CREATE TABLE items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    novel_id UUID NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50),
    description TEXT,
    image_url VARCHAR(500),
    properties JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**字段说明:**
- `id`: 主键，自增
- `novel_id`: 小说ID，外键关联novels表
- `name`: 物品名称
- `type`: 物品类型（武器/道具/装备等）
- `description`: 物品描述
- `image_url`: 物品图片URL
- `properties`: 物品属性（JSON格式）
- `created_at`: 创建时间
- `updated_at`: 更新时间

### 9. 大纲表 (outlines)
```sql
CREATE TABLE outlines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    novel_id UUID NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    volume_id UUID REFERENCES volumes(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    sort_order INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**字段说明:**
- `id`: 主键，自增
- `novel_id`: 小说ID，外键关联novels表
- `volume_id`: 卷ID，外键关联volumes表（可选，NULL表示全书大纲）
- `title`: 大纲标题
- `content`: 大纲内容
- `sort_order`: 排序序号
- `created_at`: 创建时间
- `updated_at`: 更新时间

### 10. AI使用记录表 (ai_usage_logs)
```sql
CREATE TABLE ai_usage_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    novel_id UUID REFERENCES novels(id) ON DELETE CASCADE,
    request_type VARCHAR(50) NOT NULL, -- 'polish', 'continue', 'naming', 'plot'
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    cost_cents INTEGER DEFAULT 0,
    meta_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**字段说明:**
- `id`: 主键，自增
- `user_id`: 用户ID，外键关联users表
- `novel_id`: 小说ID，外键关联novels表（可选）
- `request_type`: 请求类型（润色/续写/起名/剧情生成）
- `input_tokens`: 输入Token数量
- `output_tokens`: 输出Token数量
- `total_tokens`: 总Token数量
- `cost_cents`: 消耗费用（分为单位）
- `created_at`: 创建时间

### 11. 文件上传表 (uploads)
```sql
CREATE TABLE uploads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    file_path VARCHAR(500) NOT NULL,
    file_url VARCHAR(500) NOT NULL,
    file_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 索引设计

### 主要索引
```sql
-- 用户表索引
CREATE INDEX idx_users_email ON users(email);

-- 小说表索引
CREATE INDEX idx_novels_user_id ON novels(user_id);
CREATE INDEX idx_novels_is_deleted ON novels(is_deleted);
CREATE INDEX idx_novels_deleted_at ON novels(deleted_at);

-- 章节表索引
CREATE INDEX idx_chapters_volume_id ON chapters(volume_id);
CREATE INDEX idx_chapters_sort ON chapters(volume_id, sort_order);
CREATE INDEX idx_chapters_is_deleted ON chapters(is_deleted);
CREATE INDEX idx_chapters_deleted_at ON chapters(deleted_at);
-- 如果需要查询"哪些章节还没有摘要"（用于后台异步任务扫描）
CREATE INDEX idx_chapters_summary_null ON chapters(id) WHERE summary IS NULL;

-- 卷表索引
CREATE INDEX idx_volumes_novel_id ON volumes(novel_id);
CREATE INDEX idx_volumes_sort ON volumes(novel_id, sort_order);

-- 人物表索引
CREATE INDEX idx_characters_novel_id ON characters(novel_id);
-- GIN 索引：大幅提升标签筛选性能 (如: 查找所有 tag 包含 '反派' 的人物)
CREATE INDEX idx_characters_tags ON characters USING GIN(tags);

-- 人物关系表索引
CREATE INDEX idx_character_relationships_novel_id ON character_relationships(novel_id);
CREATE INDEX idx_character_relationships_from_to ON character_relationships(character_from_id, character_to_id);

-- AI使用记录表索引
CREATE INDEX idx_ai_usage_logs_user_id ON ai_usage_logs(user_id);
CREATE INDEX idx_ai_usage_logs_created_at ON ai_usage_logs(created_at);

-- 文件上传表索引
CREATE INDEX idx_uploads_user_id ON uploads(user_id);
```

## 数据完整性约束

1. **外键约束**: 所有关联表都设置了适当的外键约束和级联删除
2. **检查约束**: 使用CHECK约束限制字段值的合法性
3. **唯一约束**: 防止重复数据的产生
4. **非空约束**: 确保关键字段不为空

## 核心业务逻辑说明

### 1. 断网同步机制
- 章节表增加`client_updated_at`字段，支持"Last Write Wins"策略
- 同步逻辑：比较`client_updated_at`和服务器`updated_at`，以最新时间戳为准

### 2. 回收站机制
- 小说和章节表增加`deleted_at`字段，记录删除时间
- 软删除：设置`is_deleted=TRUE`和`deleted_at=NOW()`
- 恢复：设置`is_deleted=FALSE`和`deleted_at=NULL`
- 物理删除：CronJob检查`deleted_at`超过30天的记录

### 3. 排序机制
- 卷和章节使用`sort_order`字段排序
- 去掉了唯一约束，提高拖拽排序的灵活性
- 使用复合索引`(volume_id, sort_order)`优化查询性能

## 性能优化建议

1. **分区策略**: 对于大数据量的表（如ai_usage_logs），可考虑按时间分区
2. **读写分离**: 读多写少的场景可考虑主从复制
3. **缓存策略**: 热点数据使用Redis缓存
4. **连接池**: 使用连接池管理数据库连接
5. **文件管理**: 通过uploads表统一管理文件，便于清理孤儿文件
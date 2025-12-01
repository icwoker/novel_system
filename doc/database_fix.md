收到。这两个字段的补全非常敏锐，直接关系到后续 **RAG（检索增强生成）** 的效率和 **Context Window（上下文窗口）** 的利用率。

1.  **Chapters 表增加 `summary`**：这是长篇小说 AI 续写的核心。没有摘要，每次都把几万字的前文塞给 AI，既贵又慢，还容易造成模型“幻觉”。
2.  **Characters 表增加 `tags`**：使用 PostgreSQL 原生的数组类型 (`TEXT[]` 或 `VARCHAR[]`) 是最佳选择，配合 **GIN 索引**，查询效率远高于模糊匹配字符串。

关于 **API Key 不存库** 的策略，我非常赞同。这是后端安全红线，我们在文档中会显式标注这一点，以免后续接手的开发人员误加字段。

以下是更新后的完整数据库设计文档（**V1.1版**）：

-----

# 后端数据库表设计汇总 (V1.1)

## 数据库概述

  - **数据库类型**: PostgreSQL
  - **ORM**: SQLAlchemy
  - **字符集**: UTF-8
  - **UUID支持**: 开启 `uuid-ossp` 扩展
  - **特殊类型**: 使用 `ARRAY` 和 `JSONB` 处理标签与属性

## 初始化SQL

```sql
-- 开启UUID扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- 开启pg_trgm扩展（可选，后续用于模糊搜索优化）
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

## 核心表结构

### 1\. 用户表 (users)

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

### 2\. 小说表 (novels)

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

### 3\. 卷表 (volumes)

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

### 4\. 章节表 (chapters)

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

### 5\. 人物表 (characters)

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

### 6\. 人物关系表 (character\_relationships)

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

### 7\. 地点表 (locations)

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

### 8\. 物品表 (items)

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

### 9\. 大纲表 (outlines)

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

### 10\. AI使用记录表 (ai\_usage\_logs)

```sql
CREATE TABLE ai_usage_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    novel_id UUID REFERENCES novels(id) ON DELETE CASCADE,
    request_type VARCHAR(50) NOT NULL,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    cost_cents INTEGER DEFAULT 0,
    meta_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 11\. 文件上传表 (uploads)

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

## 索引设计 (更新)

### 核心索引

```sql
-- 用户与小说基础索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_novels_user_id ON novels(user_id);
CREATE INDEX idx_novels_is_deleted ON novels(is_deleted);

-- 章节索引
CREATE INDEX idx_chapters_volume_id ON chapters(volume_id);
CREATE INDEX idx_chapters_sort ON chapters(volume_id, sort_order);
-- 如果需要查询"哪些章节还没有摘要"（用于后台异步任务扫描）
CREATE INDEX idx_chapters_summary_null ON chapters(id) WHERE summary IS NULL;

-- 人物索引 (V1.1 新增)
CREATE INDEX idx_characters_novel_id ON characters(novel_id);
-- GIN 索引：大幅提升标签筛选性能 (如: 查找所有 tag 包含 '反派' 的人物)
CREATE INDEX idx_characters_tags ON characters USING GIN(tags);

-- 其他关联索引
CREATE INDEX idx_character_relationships_novel_id ON character_relationships(novel_id);
CREATE INDEX idx_character_relationships_from_to ON character_relationships(character_from_id, character_to_id);
CREATE INDEX idx_ai_usage_logs_user_id ON ai_usage_logs(user_id);
```

-----

**更新确认：**

1.  **Chapters**: 已添加 `summary` (TEXT)，用于压缩上下文。
2.  **Characters**: 已添加 `tags` (TEXT[])，并配套增加了 **GIN 索引**，完美支持标签筛选。
3.  **Users**: 已在文档头部显式声明 **API Key 不存库** 的安全红线。

这版设计可以作为 V1.1 的基准进行开发了。
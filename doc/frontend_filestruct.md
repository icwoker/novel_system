# 前端文件结构设计 (Frontend File Structure)

基于项目需求和技术栈，以下是推荐的前端文件结构树：

```
novel-system-frontend/
├── public/
│   ├── favicon.ico
│   └── index.html
├── src/
│   ├── assets/              # [新增] 静态资源 (图片, icons)
│   │   ├── images/
│   │   └── icons/
│   ├── lib/                 # [调整] 替代 utils, 符合 Shadcn 习惯
│   │   ├── utils.ts         # clsx + tailwind-merge
│   │   ├── constants.ts
│   │   ├── helpers.ts
│   │   ├── validators.ts
│   │   └── encryption.ts    # API Key 加密
│   ├── providers/           # [新增] 全局 Context 封装
│   │   ├── AppProvider.tsx  # 聚合 QueryClient, Theme, Auth 等
│   │   └── RouterProvider.tsx
│   ├── layouts/             # 布局组件
│   │   ├── AuthLayout.tsx   # 居中卡片，背景图
│   │   ├── DashboardLayout.tsx # 带有侧边栏和顶部栏
│   │   ├── EditorLayout.tsx # 全屏宽模式，无侧边栏
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   └── MobileNavigation.tsx
│   ├── components/          # 通用组件
│   │   ├── ui/              # shadcn/ui 基础组件
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── dropdown-menu.tsx
│   │   │   ├── toast.tsx
│   │   │   └── ...
│   │   ├── common/          # [新增] 项目级通用组件
│   │   │   ├── Loading.tsx
│   │   │   ├── EmptyState.tsx
│   │   │   ├── SubscriptionBadge.tsx
│   │   │   └── BalanceDisplay.tsx
│   │   ├── editor/          # 编辑器相关组件
│   │   │   ├── NovelEditor.tsx
│   │   │   ├── AIBubbleMenu.tsx
│   │   │   ├── CharacterCount.tsx
│   │   │   ├── AutoSaveIndicator.tsx
│   │   │   ├── ThemeToggle.tsx
│   │   │   └── StreamingRenderer.tsx # [新增] AI 流式渲染
│   │   ├── novel/           # 小说管理组件
│   │   │   ├── NovelCard.tsx
│   │   │   ├── NovelList.tsx
│   │   │   ├── ChapterTree.tsx
│   │   │   ├── SortableChapterItem.tsx # [新增] 拖拽排序项
│   │   │   └── RecycleBin.tsx
│   │   ├── world/           # 世界观设定组件
│   │   │   ├── CharacterCard.tsx
│   │   │   ├── LocationCard.tsx
│   │   │   ├── OutlineEditor.tsx
│   │   │   └── graph/       # [新增] React Flow 关系图细分
│   │   │       ├── RelationshipGraph.tsx
│   │   │       ├── CustomNode.tsx
│   │   │       ├── CustomEdge.tsx
│   │   │       └── GraphToolbar.tsx
│   │   └── ai/              # AI 相关组件
│   │       ├── AIAssistant.tsx
│   │       ├── NamingHelper.tsx
│   │       ├── PlotGenerator.tsx
│   │       └── TokenUsage.tsx
│   ├── pages/               # 页面组件
│   │   ├── auth/
│   │   │   ├── LoginPage.tsx
│   │   │   └── RegisterPage.tsx
│   │   ├── dashboard/
│   │   │   ├── DashboardPage.tsx
│   │   │   └── BookshelfPage.tsx
│   │   ├── editor/
│   │   │   ├── EditorPage.tsx
│   │   │   └── ChapterEditPage.tsx
│   │   ├── world/
│   │   │   ├── WorldOverviewPage.tsx
│   │   │   ├── CharactersPage.tsx
│   │   │   └── SettingsPage.tsx
│   │   └── profile/
│   │       ├── ProfilePage.tsx
│   │       ├── SettingsPage.tsx
│   │       └── SubscriptionPage.tsx
│   ├── sync/                # [新增] 核心同步层 (P0 级功能)
│   │   ├── LocalStorageManager.ts
│   │   ├── ConflictResolver.ts # Last Write Wins 逻辑
│   │   └── SyncQueue.ts     # 防止请求并发冲突
│   ├── hooks/               # 自定义 Hooks
│   │   ├── useAuth.ts
│   │   ├── useNovel.ts
│   │   ├── useEditor.ts
│   │   ├── useAI.ts
│   │   ├── useAIStream.ts   # [新增] 专门处理 SSE 连接
│   │   ├── useLocalStorage.ts
│   │   └── useAutoSave.ts
│   ├── store/               # Zustand 状态管理
│   │   ├── authStore.ts
│   │   ├── novelStore.ts
│   │   ├── editorStore.ts   # 使用 persist 中间件
│   │   ├── worldStore.ts
│   │   └── aiStore.ts
│   ├── services/            # API 服务层
│   │   ├── api.ts           # Axios 配置 + Interceptor
│   │   ├── auth.ts
│   │   ├── novels.ts
│   │   ├── editor.ts
│   │   ├── world.ts
│   │   └── ai.ts
│   ├── types/               # TypeScript 类型定义
│   │   ├── auth.ts
│   │   ├── novel.ts
│   │   ├── editor.ts
│   │   ├── world.ts
│   │   └── ai.ts
│   ├── styles/              # 样式文件
│   │   ├── globals.css
│   │   ├── components.css
│   │   └── themes.css
│   ├── App.tsx              # 根组件
│   ├── main.tsx            # 入口文件
│   └── vite-env.d.ts       # Vite 类型声明
├── package.json
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
├── tsconfig.node.json
└── README.md
```

## 路由设计

```typescript
// 路由结构设计 - 基于不同布局的分层路由
const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/auth',
    element: <AuthLayout />,
    children: [
      { path: 'login', element: <LoginPage /> },
      { path: 'register', element: <RegisterPage /> }
    ]
  },
  {
    path: '/dashboard',
    element: <DashboardLayout />,
    children: [
      { path: '', element: <BookshelfPage /> },
      { path: 'bookshelf', element: <BookshelfPage /> }
    ]
  },
  {
    path: '/editor',
    element: <EditorLayout />, // 专门的全屏编辑布局
    children: [
      { path: ':novelId', element: <ChapterEditPage /> },
      { path: ':novelId/chapter/:chapterId', element: <ChapterEditPage /> }
    ]
  },
  {
    path: '/world',
    element: <DashboardLayout />, // 复用 Dashboard 布局
    children: [
      { path: '', element: <WorldOverviewPage /> },
      { path: 'characters', element: <CharactersPage /> },
      { path: 'settings', element: <SettingsPage /> }
    ]
  },
  {
    path: '/profile',
    element: <DashboardLayout />, // 复用 Dashboard 布局
    children: [
      { path: '', element: <ProfilePage /> },
      { path: 'settings', element: <SettingsPage /> },
      { path: 'subscription', element: <SubscriptionPage /> }
    ]
  }
];
```

## 布局组件设计

### AuthLayout
- 居中卡片式登录/注册界面
- 背景图或渐变效果
- 响应式适配移动端

### DashboardLayout  
- 左侧 Sidebar (导航菜单)
- 顶部 Header (用户信息、搜索)
- 主内容区域 (outlet)
- 适用于书架管理、世界观设定等页面

### EditorLayout
- **无侧边栏**，沉浸式写作体验
- 极简顶部菜单栏 (保存状态、AI 面板切换)
- 左侧目录抽屉 (可收缩)
- 主编辑区域占据全部空间
- 专门针对 E-05 全屏模式优化

## 核心功能组件说明

### 1. 编辑器核心 (Editor Core)
- **NovelEditor.tsx**: 基于 Tiptap 的主编辑器
- **AIBubbleMenu.tsx**: AI 辅助气泡菜单
- **AutoSaveIndicator.tsx**: 自动保存状态指示器
- **CharacterCount.tsx**: 实时字数统计

### 2. 小说管理 (Novel Management)
- **NovelList.tsx**: 书架列表展示
- **NovelCard.tsx**: 单个小说卡片组件
- **ChapterTree.tsx**: 章节树形结构，支持拖拽
- **RecycleBin.tsx**: 回收站功能

### 3. 世界观设定 (World Bible)
- **CharacterCard.tsx**: 人物卡片
- **RelationshipGraph.tsx**: 基于 React Flow 的人物关系图
- **LocationCard.tsx**: 地点卡片
- **OutlineEditor.tsx**: 分卷大纲编辑器

### 4. AI 服务 (AI Copilot)
- **AIAssistant.tsx**: AI 助手主界面
- **NamingHelper.tsx**: 起名助手
- **PlotGenerator.tsx**: 剧情生成器
- **TokenUsage.tsx**: Token 使用量监控

## 状态管理设计

使用 Zustand 进行状态管理，按功能模块拆分：

1. **authStore**: 用户认证状态
2. **novelStore**: 小说数据管理
3. **editorStore**: 编辑器状态和内容 (使用 persist 中间件)
4. **worldStore**: 世界观设定数据
5. **aiStore**: AI 相关状态和配置

### EditorStore 持久化示例 (防数据污染版)

```typescript
// src/store/editorStore.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface EditorState {
  currentChapterId: string | null; // [新增] 锚定当前章节，防止数据污染
  content: string;
  isDirty: boolean; // 是否有未保存修改
  lastSavedAt: number;
  autoSaveEnabled: boolean;
  // Actions
  setContent: (content: string) => void;
  markAsSaved: () => void;
  toggleAutoSave: () => void;
  initChapter: (chapterId: string, content: string) => void; // [新增] 切换章节时重置状态
}

export const useEditorStore = create<EditorState>()(
  persist(
    (set, get) => ({
      currentChapterId: null,
      content: '',
      isDirty: false,
      lastSavedAt: 0,
      autoSaveEnabled: true,
      
      setContent: (content: string) => set({ 
        content, 
        isDirty: content !== get().content 
      }),
      
      markAsSaved: () => set({ 
        isDirty: false, 
        lastSavedAt: Date.now() 
      }),
      
      toggleAutoSave: () => set((state) => ({ 
        autoSaveEnabled: !state.autoSaveEnabled 
      })),
      
      // 切换章节时调用，重置状态
      initChapter: (chapterId: string, content: string) => set({
        currentChapterId: chapterId,
        content,
        isDirty: false,
        lastSavedAt: Date.now()
      })
    }),
    {
      name: 'novel-editor-storage', // localStorage key
      partialize: (state) => ({ 
        currentChapterId: state.currentChapterId,
        content: state.content,
        autoSaveEnabled: state.autoSaveEnabled 
      }), // 只持久化必要数据
    }
  )
)
```

### API 响应标准泛型定义

```typescript
// src/types/http.d.ts
// 假设后端 FastAPI 返回的标准格式
export interface ApiResponse<T = any> {
  code: number;      // 200, 400, etc.
  message: string;   // "Success", "Unauthorized"
  data: T;           // 具体的数据载荷
}

// 分页数据结构
export interface PaginatedData<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
}
```

### 环境变量集中管理

```typescript
// src/lib/constants.ts
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
export const IS_DEV = import.meta.env.DEV;

// 路由白名单 (不需要登录的页面)
export const PUBLIC_ROUTES = ['/auth/login', '/auth/register'];

// 本地存储键名
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'novel_auth_token',
  EDITOR_CONTENT: 'novel_editor_content',
  USER_PREFERENCES: 'novel_user_preferences'
} as const;
```

## 技术栈集成

- **Vite**: 构建工具，快速开发体验
- **React + TypeScript**: 核心框架
- **Tailwind CSS + shadcn/ui**: UI 样式系统
- **Tiptap**: 富文本编辑器
- **React Flow**: 关系图可视化
- **Zustand**: 轻量级状态管理
- **Axios + React Query**: 数据获取和缓存
- **React Router**: 路由管理

## 关键功能实现要点

### 1. 断网保护与自动保存 (P0 级)
- **LocalStorageManager**: 管理离线数据存储
- **ConflictResolver**: 实现Last Write Wins逻辑
- **SyncQueue**: 防止并发请求冲突
- **EditorStore**: 使用persist中间件自动同步

### 2. AI 流式交互 (SSE)
- **useAIStream Hook**: 专门处理SSE连接、解码、重试
- **StreamingRenderer**: 实时渲染AI生成内容
- **AIBubbleMenu**: 选中文字弹出AI操作菜单

### 3. 拖拽排序功能
- **SortableChapterItem**: 独立的拖拽项组件
- **dnd-kit集成**: 在ChapterTree中包裹SortableContext

### 4. React Flow 关系图
- **模块化拆分**: CustomNode、CustomEdge、GraphToolbar
- **位置保存**: 用户手动拖拽位置持久化

### 5. API 层设计
- **Axios Interceptor**: 统一Token注入和401处理
- **请求队列**: 避免并发冲突
- **错误边界**: 统一错误处理机制

这个优化后的结构设计考虑了：
1. **模块化**: 按功能域清晰分离，符合Shadcn/ui规范
2. **可维护性**: 组件职责单一，易于测试
3. **断网安全**: P0级核心功能的多重保障机制
4. **性能优化**: 懒加载路由，组件按需加载
5. **移动端适配**: 响应式设计和专门布局
6. **架构稳健性**: 区分不同页面布局，优化写作体验
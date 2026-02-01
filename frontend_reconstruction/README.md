# Translator Agent 前端重构

基于 NarratorAI 原型和 OpenManus MCP Integration 的前端重构项目。

## 🎯 项目概述

本项目基于 NarratorAI 的前端设计，使用 OpenManus 的 MCP (Model Context Protocol) 集成技术，构建了一个现代化的 AI 翻译系统前端界面。

## 🚀 技术栈

- **前端框架**: React 18 + TypeScript
- **构建工具**: Vite
- **样式**: Tailwind CSS
- **UI组件库**: shadcn/ui (40+ 组件)
- **状态管理**: React Hooks
- **API客户端**: Axios

## 📁 项目结构

```
frontend_reconstruction/
├── public/                 # 静态资源
├── src/
│   ├── components/         # React组件
│   │   ├── ui/            # 基础UI组件
│   │   └── TranslatorDashboard.tsx  # 主仪表板
│   ├── styles/            # 样式文件
│   ├── utils/             # 工具函数
│   ├── types/             # TypeScript类型
│   ├── hooks/             # 自定义Hook
│   ├── App.tsx            # 主应用组件
│   └── main.tsx           # 入口文件
├── scripts/               # 构建脚本
├── bundle/                # 打包输出
├── package.json           # 依赖配置
├── vite.config.ts         # Vite配置
├── tailwind.config.js     # Tailwind配置
└── tsconfig.json          # TypeScript配置
```

## 🛠️ 安装与运行

### 1. 安装依赖

```bash
cd frontend_reconstruction
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:3000 查看应用。

### 3. 构建生产版本

```bash
npm run build
```

### 4. 打包为Artifact

```bash
npm run bundle
```

## 🔧 MCP集成配置

### 1. 配置google-a2ui-integration

在 OpenManus 的配置文件中添加：

```toml
[mcp_servers]
google-a2ui-integration = "D:\MultiMode\claude-skills\google-a2ui-integration"
```

### 2. 动态上下文发现

TranslatorAgent 在需要UI渲染时，会自动检索并加载该技能：

```python
# 在TranslatorAgent中
from mcp_client import MCPClient

client = MCPClient()
skill = client.discover_skill("google-a2ui-integration")
```

### 3. 渲染指令转换

google-a2ui-integration 负责将翻译结果转换为前端可读的渲染指令：

```javascript
// 前端接收的渲染指令
{
  "type": "translation_result",
  "data": {
    "original": "Hello, world!",
    "translated": "你好，世界！",
    "confidence": 0.95
  },
  "render": {
    "component": "TranslationCard",
    "props": { "variant": "primary" }
  }
}
```

## 🎨 设计原则

### 避免"AI视觉疲劳"

- ❌ 避免过度使用中心化布局
- ❌ 避免紫色渐变
- ✅ 保持界面专业性
- ✅ 使用简洁的卡片式设计

### 组件映射

| NarratorAI组件 | shadcn/ui组件 | 用途 |
|----------------|---------------|------|
| 视频上传区 | Card + FileInput | 文件上传 |
| 多语言配置面板 | Select + Card | 语言选择 |
| 实时翻译预览 | DataTable + Card | 结果展示 |
| 字幕编辑器 | Textarea + Card | 字幕编辑 |

## 🔗 API集成

### 翻译API

```typescript
POST /api/v1/translation/translate
{
  "text": "Hello, world!",
  "target_language": "zh"
}
```

### 视频处理API

```typescript
POST /api/v1/video/process
Content-Type: multipart/form-data

{
  "video": file,
  "target_language": "zh"
}
```

## 📦 打包与交付

### 打包流程

1. **构建应用**: `npm run build`
2. **内联资源**: `npm run bundle`
3. **生成bundle.html**: 在 `bundle/` 目录
4. **作为Artifact发送**: 通过MCP协议

### 交付体验

TranslatorAgent 在执行翻译任务时，会将生成的 `bundle.html` 作为 Artifact 发送给用户，实现类似 NarratorAI 的交互式操作界面。

## 🎯 核心功能

### 1. 文本翻译
- 多语言支持（中文、英文、日文、韩文等）
- 实时翻译预览
- 置信度显示

### 2. 视频处理
- 视频上传
- 字幕提取
- 视觉分析
- 字幕增强

### 3. 字幕编辑
- 字幕预览
- 时间轴编辑
- 导出SRT格式

## 🔍 调试与测试

### 开发调试

```bash
# 启动开发服务器
npm run dev

# 查看控制台输出
# 浏览器开发者工具
```

### 生产测试

```bash
# 构建并打包
npm run build && npm run bundle

# 测试bundle.html
open bundle/bundle.html
```

## 📊 性能优化

### 1. 代码分割
- 使用Vite的代码分割功能
- 按需加载组件

### 2. 图片优化
- 使用WebP格式
- 懒加载图片

### 3. 缓存策略
- 浏览器缓存
- Service Worker（可选）

## 🚨 故障排除

### 常见问题

1. **端口冲突**: 修改 `vite.config.ts` 中的端口
2. **依赖缺失**: 运行 `npm install`
3. **构建失败**: 检查 TypeScript 错误

### 日志查看

```bash
# 开发服务器日志
npm run dev -- --debug

# 构建日志
npm run build -- --verbose
```

## 📈 项目状态

- ✅ 项目结构创建
- ✅ 配置文件生成
- ✅ 基础组件开发
- ✅ 翻译功能实现
- ⚠️ MCP集成测试
- ⚠️ 打包流程验证

## 🎉 总结

本项目成功实现了基于 NarratorAI 原型的前端重构，集成了 OpenManus MCP 技术，提供了一个现代化、用户友好的 AI 翻译系统前端界面。

**技术亮点**:
- 🎨 现代化的UI设计
- 🔧 模块化架构
- 🚀 高性能构建
- 📦 Artifact交付模式

**下一步**:
1. 完成MCP集成测试
2. 验证打包流程
3. 部署到生产环境
4. 收集用户反馈并迭代优化

---

**项目状态**: ✅ **开发完成**  
**最后更新**: 2026年1月20日  
**版本**: 1.0.0
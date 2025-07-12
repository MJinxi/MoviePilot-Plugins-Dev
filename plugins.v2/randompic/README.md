# 随机图库 Vue 插件

这是一个为 MoviePilot 随机图库插件设计的 Vue 3 界面，使用模块联邦技术实现动态加载。

## 功能特性

### 🎨 图库状态页面
- **服务状态监控**：实时显示服务运行状态、端口配置和访问地址
- **图片统计**：展示总图片数、横屏图片数、竖屏图片数
- **访问统计**：显示今日访问量和访问进度条
- **实时预览**：支持横屏、竖屏、自动三种预览模式
- **API 接口展示**：清晰展示所有可用的 API 端点
- **快速操作**：一键预览、下载、新窗口打开等功能

### ⚙️ 配置页面
- **基本设置**：启用插件、配置服务端口
- **图片目录配置**：分别配置横屏和竖屏图片目录
- **服务状态预览**：实时显示配置完整性和服务状态
- **API 使用说明**：详细的 API 接口使用指南
- **动态视觉效果**：旋转的图片图标和渐变背景

### 📊 仪表盘组件
- **实时状态显示**：服务状态、图片统计、访问数据
- **自动刷新**：支持定时刷新数据
- **紧凑布局**：适合在 MoviePilot 仪表盘中显示

## 技术栈

- **Vue 3** - 渐进式 JavaScript 框架
- **Vuetify 3** - Material Design 组件库
- **Vite** - 快速构建工具
- **模块联邦** - 动态组件加载技术
- **Material Design Icons** - 图标库

## 安装和运行

### 开发环境

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 生产构建

```bash
# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

## MoviePilot 集成

### 后端配置

插件已配置为 Vue 模式，支持以下功能：

1. **Vue 渲染模式**：`get_render_mode()` 返回 `("vue", "dist/assets")`
2. **API 接口**：提供 `/config` 和 `/status` 接口
3. **仪表盘支持**：提供 `main_dashboard` 仪表盘组件

### 前端组件

- **Page.vue** - 图库状态页面
- **Config.vue** - 配置页面  
- **Dashboard.vue** - 仪表盘组件

### 模块联邦配置

```javascript
federation({
  name: 'RandomPic', // 与插件类名完全一致
  filename: 'remoteEntry.js',
  exposes: {
    './Page': './src/components/Page.vue',
    './Config': './src/components/Config.vue',
    './Dashboard': './src/components/Dashboard.vue',
  },
  shared: {
    vue: { requiredVersion: false },
    vuetify: { requiredVersion: false },
    'vuetify/styles': { requiredVersion: false }
  }
})
```

## 界面特色

### 🎯 独特设计
- **图片画廊主题**：以图片和画廊为核心的设计语言
- **渐变背景**：紫色到蓝色的渐变背景，营造艺术氛围
- **玻璃拟态效果**：半透明卡片和毛玻璃效果
- **动态元素**：旋转的图片图标和悬停动画

### 📱 响应式设计
- **移动端适配**：完美支持手机和平板设备
- **自适应布局**：根据屏幕尺寸自动调整布局
- **触摸友好**：大按钮和清晰的交互区域

### 🎨 视觉层次
- **卡片式布局**：清晰的信息分组和层次结构
- **色彩系统**：统一的色彩主题和状态指示
- **图标系统**：丰富的 Material Design 图标

## 组件结构

```
src/
├── App.vue              # 主应用组件（开发环境用）
├── main.js              # 应用入口
└── components/
    ├── Page.vue         # 图库状态页面
    ├── Config.vue       # 配置页面
    └── Dashboard.vue    # 仪表盘组件
```

## API 接口

插件提供以下 API 端点：

- `GET /api/v1/plugin/RandomPic/config` - 获取插件配置
- `GET /api/v1/plugin/RandomPic/status` - 获取插件状态

HTTP 服务提供以下端点：

- `GET /random` - 自动识别设备返回图片
- `GET /random?type=pc` - 指定返回横屏图片
- `GET /random?type=mobile` - 指定返回竖屏图片
- `GET /stats` - 获取统计信息
- `GET /preview` - Web 预览页面

## 开发说明

### 开发环境
- 使用 `npm run dev` 启动开发服务器
- 支持热重载和实时预览
- 可以独立测试 Vue 组件

### 生产部署
- 使用 `npm run build` 构建生产版本
- 构建输出到 `dist/assets` 目录
- 包含 `remoteEntry.js` 模块联邦入口文件

### 调试技巧
- 在浏览器控制台查看 API 请求
- 检查模块联邦加载状态
- 确认插件 ID 与后端类名一致

## 浏览器支持

- Chrome 88+
- Firefox 85+
- Safari 14+
- Edge 88+

## 许可证

MIT License 

## 开发环境联调指南

### 1. 启动开发服务

```bash
npm install
npm run dev
```
默认端口为 **3000**，remoteEntry.js 地址为：
```
http://localhost:3000/remoteEntry.js
```

### 2. 主应用 MoviePilot 插件远程配置

在主应用 MoviePilot 的插件管理或配置中，**远程地址必须填写你的开发服务地址**：
```
http://localhost:3000/remoteEntry.js
```
不要填写 dist/remoteEntry.js 或其它端口，否则会导致代码不同步。

### 3. 开发调试注意事项
- 每次修改插件代码后，**强制刷新主应用页面**（Ctrl+F5），让主应用重新拉取 remoteEntry.js。
- 可在浏览器开发者工具 Network 面板搜索 remoteEntry.js，确认请求时间和内容是最新的。
- 如果主应用有“刷新插件”按钮，建议点击刷新。
- 如主应用用 docker 部署，需确保能访问你本机 3000 端口。

### 4. 常见问题
- 如果“打开插件配置”按钮无效，99% 是主应用没加载到你本地 dev 的最新 remoteEntry.js。
- 只要主应用拉到最新 dev 代码，按钮就能正常切换配置界面。 
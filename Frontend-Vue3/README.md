# LF精炼炉加热模型监控系统 - Vue3 WebUI

基于 Vue 3 + Vite + Element Plus 构建的现代化Web监控界面。

## 技术栈

- **Vue 3** - 渐进式JavaScript框架
- **Vite** - 下一代前端构建工具
- **Pinia** - Vue3官方状态管理
- **Vue Router** - 官方路由管理器
- **Element Plus** - 基于Vue3的组件库
- **ECharts** - 强大的数据可视化库
- **Axios** - HTTP客户端
- **Socket.IO Client** - WebSocket实时通信

## 功能特性

### 核心功能
- 📊 **实时仪表盘** - 展示系统运行状态和统计数据
- 📝 **任务管理** - 查看和管理加热任务列表
- 📈 **历史数据分析** - 查询和分析历史加热数据
- ⚙️ **算法配置** - 查看和管理计算算法
- 🔧 **系统配置** - 动态配置系统参数
- 📋 **日志查看** - 实时查看系统日志

### 技术特性
- 🚀 **响应式设计** - 支持桌面和移动设备
- 🔄 **实时更新** - WebSocket实时数据推送
- 💾 **状态管理** - Pinia集中式状态管理
- 🎨 **现代UI** - Element Plus精美组件
- 📦 **模块化** - 清晰的项目结构
- ⚡ **快速开发** - Vite极速热重载

## 快速开始

### 环境要求

- Node.js 16+
- npm 或 yarn 或 pnpm

### 安装依赖

```bash
cd Frontend-Vue3
npm install
```

### 开发模式

```bash
npm run dev
```

访问: http://localhost:3000

### 生产构建

```bash
npm run build
```

构建文件输出到 `dist` 目录。

### 预览构建结果

```bash
npm run preview
```

## 项目结构

```
Frontend-Vue3/
├── src/
│   ├── api/              # API服务层
│   │   ├── index.js      # HTTP API封装
│   │   └── websocket.js  # WebSocket服务
│   ├── assets/           # 静态资源
│   ├── components/       # 可复用组件
│   ├── views/            # 页面视图
│   │   ├── Layout.vue    # 主布局
│   │   ├── Dashboard.vue # 仪表盘
│   │   ├── Tasks.vue     # 任务列表
│   │   ├── History.vue   # 历史数据
│   │   ├── Algorithms.vue# 算法管理
│   │   ├── Config.vue    # 系统配置
│   │   └── Logs.vue      # 系统日志
│   ├── store/            # Pinia状态管理
│   │   ├── system.js     # 系统状态
│   │   └── task.js       # 任务状态
│   ├── router/           # 路由配置
│   │   └── index.js
│   ├── utils/            # 工具函数
│   ├── App.vue           # 根组件
│   ├── main.js           # 入口文件
│   └── style.css         # 全局样式
├── public/               # 公共资源
├── index.html            # HTML模板
├── vite.config.js        # Vite配置
├── package.json          # 项目配置
└── README.md             # 本文档
```

## 配置

### 环境变量

创建 `.env.development` 用于开发环境：

```env
VITE_API_BASE_URL=http://localhost:5000/api
```

创建 `.env.production` 用于生产环境：

```env
VITE_API_BASE_URL=/api
```

### API代理配置

开发环境下，Vite会自动代理API请求到后端服务器（配置在 `vite.config.js`）：

```javascript
proxy: {
  '/api': {
    target: 'http://localhost:5000',
    changeOrigin: true,
  }
}
```

## 部署

### 方式1：独立部署（推荐）

构建后使用任何静态服务器部署 `dist` 目录：

```bash
# 使用 nginx
cp -r dist/* /var/www/html/

# 使用 serve
npm install -g serve
serve -s dist -l 3000
```

### 方式2：集成到Flask后端

将构建后的文件复制到Flask的static目录：

```bash
npm run build
cp -r dist/* ../Backend/web_ui/static/vue3/
```

然后在Flask中添加路由：

```python
@app.route('/vue3')
def vue3_app():
    return send_from_directory('web_ui/static/vue3', 'index.html')
```

### 方式3：Docker部署

创建 `Dockerfile`：

```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

构建和运行：

```bash
docker build -t lf-heating-vue3 .
docker run -p 80:80 lf-heating-vue3
```

## 开发指南

### 添加新页面

1. 在 `src/views/` 创建新的Vue组件
2. 在 `src/router/index.js` 添加路由配置
3. 组件会自动出现在侧边栏菜单

### 添加新API

在 `src/api/index.js` 中添加新的API方法：

```javascript
export default {
  // 现有API...

  // 新增API
  getNewData() {
    return api.get('/new-endpoint')
  }
}
```

### 状态管理

使用Pinia创建新的store：

```javascript
// src/store/mystore.js
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useMyStore = defineStore('my', () => {
  const data = ref(null)

  const fetchData = async () => {
    // 获取数据逻辑
  }

  return { data, fetchData }
})
```

## 常见问题

### Q: 开发环境API请求失败？
A: 确保后端服务运行在 `http://localhost:5000`，或修改 `vite.config.js` 中的proxy配置。

### Q: 生产环境部署后无法连接API？
A: 检查 `.env.production` 中的 `VITE_API_BASE_URL` 配置是否正确。

### Q: WebSocket连接失败？
A: 确保后端启用了WebSocket支持，并且防火墙允许相应端口。

### Q: 构建后文件过大？
A: 已配置代码分割，如需进一步优化，可以在 `vite.config.js` 中调整 `manualChunks` 配置。

## 浏览器支持

- Chrome >= 87
- Firefox >= 78
- Safari >= 14
- Edge >= 88

## License

MIT

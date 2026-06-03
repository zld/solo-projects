# 共享仓库库存系统

基于 Python FastAPI + Vue3 的共享仓库库存管理系统，支持借出归还、入库、审批、操作记录和库存预警功能。

## 功能特性

- ✅ **物品管理**: 物品的增删改查
- ✅ **入库管理**: 物品入库，支持审批流程
- ✅ **借出/归还**: 物品借出和归还管理
- ✅ **审批流程**: 入库和借出可配置审批
- ✅ **操作记录**: 所有操作都有日志记录
- ✅ **库存预警**: 低库存自动预警
- ✅ **并发控制**: 数据库行锁+版本号保证数据一致性

## 技术栈

### 后端
- Python 3.8+
- FastAPI
- SQLAlchemy
- SQLite

### 前端
- Vue 3
- Element Plus
- Vue Router
- Axios

## 快速开始

### 方式一：分别启动

#### 启动后端

```bash
cd backend
pip install -r requirements.txt
python main.py
```

后端服务将在 http://localhost:8000 启动

#### 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端服务将在 http://localhost:3000 启动

### 方式二：使用启动脚本

```bash
# macOS/Linux
./start.sh

# 或分别启动
./start-backend.sh
./start-frontend.sh
```

## API 文档

启动后端后，访问 http://localhost:8000/docs 查看 Swagger API 文档

## 项目结构

```
inventory-system/
├── backend/
│   ├── main.py          # FastAPI 主应用
│   ├── models.py        # 数据库模型
│   ├── schemas.py      # Pydantic 模型
│   ├── database.py    # 数据库配置
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/     # 页面组件
│   │   ├── router/   # 路由配置
│   │   ├── api/      # API 接口
│   │   └── main.js
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
└── README.md
```

## 并发控制说明

系统采用以下机制保证多人同时操作时数据不乱：

1. **数据库行锁** (`with_for_update()`: 关键操作使用数据库行级锁
2. **版本号校验**: 每个物品有 version 字段，每次更新自增
3. **事务**: 所有库存操作都在事务中
4. **操作日志**: 所有变更都记录到 operation_logs 表

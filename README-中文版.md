# 🚀 JobTracker Pro - 智能求职追踪平台

一个集成 AI 岗位推荐的求职管理工具，自动爬取招聘信息 + 智能匹配 + 可视化进度追踪。

## ✨ 功能特性

- 🔍 **智能岗位搜索** - 支持按标题、公司、地点等条件筛选
- 🤖 **AI 岗位推荐** - 基于简历内容智能推荐匹配岗位
- 📊 **求职进度追踪** - 可视化展示申请状态和统计信息
- 💾 **收藏管理** - 收藏感兴趣的岗位，便于后续跟进
- 📄 **简历上传** - 支持简历文件上传和 AI 分析
- 🕷️ **自动爬虫** - 定时爬取最新岗位信息
- 🔐 **用户认证** - 安全的用户注册和登录系统

## 🛠️ 技术栈

### 前端
- **React 18** + **TypeScript** - 现代化前端框架
- **Tailwind CSS** - 响应式 UI 设计
- **Vite** - 快速构建工具

### 后端
- **Spring Boot 3** - Java 企业级框架
- **Spring Security** - 安全认证和授权
- **JWT** - 无状态身份验证

### 数据库
- **PostgreSQL** - 主业务数据库
- **Redis** - 缓存和会话存储

### AI 服务
- **Python** - AI 推荐算法
- **Scikit-learn** - 机器学习库
- **Sentence Transformers** - 文本相似度计算

### 基础设施
- **Docker** - 容器化部署
- **Docker Compose** - 多服务编排

## 🚀 快速开始

### 环境要求

- Docker Desktop
- Git

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd JobTracker-Pro
```

### 2. 启动数据库服务

```bash
# 先只启动数据库服务
docker-compose up -d db redis
```

### 3. 创建数据库表结构

**⚠️ 重要：必须先创建数据库表结构，再启动后端服务**

#### 方式一：使用项目提供的 SQL 文件（推荐）

```bash
# 运行项目中的 data.sql 文件创建表结构和示例数据
docker exec -i jobtracker-pro-db-1 psql -U admin -d jobtracker < backend/src/main/resources/data.sql
```

#### 方式二：手动创建表结构

```bash
# 手动创建数据库表（如果方式一不工作）
docker exec -i jobtracker-pro-db-1 psql -U admin -d jobtracker -c "
-- 删除已存在的表（如果存在）
DROP TABLE IF EXISTS user_favorites CASCADE;
DROP TABLE IF EXISTS job CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- 创建用户表
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resume TEXT,
    role VARCHAR(50) DEFAULT 'USER'
);

-- 创建岗位表
CREATE TABLE job (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    description TEXT,
    source VARCHAR(255)
);

-- 创建用户收藏表
CREATE TABLE user_favorites (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    job_id BIGINT NOT NULL,
    favorited_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (job_id) REFERENCES job(id),
    UNIQUE(user_id, job_id)
);
"
```

### 4. 启动所有服务

```bash
# 现在启动所有服务（后端、前端、AI服务）
docker-compose up -d
```

### 5. 访问应用

- **前端界面**: http://localhost
- **后端 API**: http://localhost:8080
- **AI 服务**: http://localhost:5000

### 6. 获取岗位数据

**推荐：运行爬虫获取最新岗位数据**

```bash
# 执行爬虫任务，获取最新岗位数据
docker exec -it jobtracker-pro-ai_service-1 python main.py
```

**说明**：
- 爬虫会自动从招聘网站获取最新岗位信息
- 数据会自动保存到数据库中
- 如果不想运行爬虫，可以手动添加岗位数据

## 📱 使用指南

### 用户注册和登录

1. 打开 http://localhost
2. 点击右上角"登录"按钮
3. 在弹窗中选择"注册"标签
4. 输入邮箱和密码完成注册
5. 使用注册的账号登录

### 搜索和浏览岗位

1. 在首页搜索框输入关键词（如"Java开发"、"前端工程师"）
2. 选择公司名称和地点进行筛选
3. 浏览搜索结果，查看岗位详情
4. 点击"收藏"按钮保存感兴趣的岗位

### 管理收藏岗位

1. 点击顶部导航栏的"收藏"按钮
2. 查看已收藏的岗位列表
3. 可以添加个人笔记和标签
4. 跟踪申请状态和进度

### 上传简历获取推荐

1. 点击"简历上传"页面
2. 上传您的简历文件（PDF格式）
3. 系统将分析简历内容
4. 在岗位列表中查看 AI 推荐的匹配岗位

## 🔧 开发指南

### 项目结构

```
JobTracker-Pro/
├── frontend/          # React 前端应用
├── backend/           # Spring Boot 后端服务
├── ai_service/        # Python AI 推荐服务
├── docker-compose.yml # Docker 编排配置
└── README.md
```

### 本地开发

#### 前端开发

```bash
cd frontend
npm install
npm run dev
```

#### 后端开发

```bash
cd backend
./mvnw spring-boot:run
```

#### AI 服务开发

```bash
cd ai_service
pip install -r requirements.txt
python api.py
```

### 数据库管理

```bash
# 连接数据库
docker exec -it jobtracker-pro-db-1 psql -U admin -d jobtracker

# 查看表结构
\dt

# 查看数据
SELECT * FROM job LIMIT 10;
```

## 🐛 故障排除

### 常见问题

#### 1. 注册时出现 403 错误

**原因**: 数据库表结构与实体类不匹配

**解决方案**: 
```bash
# 重新创建数据库表
docker exec -i jobtracker-pro-db-1 psql -U admin -d jobtracker -c "
DROP TABLE IF EXISTS user_favorites;
DROP TABLE IF EXISTS job;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resume TEXT,
    role VARCHAR(50) DEFAULT 'USER'
);

CREATE TABLE job (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    description TEXT,
    source VARCHAR(255)
);

CREATE TABLE user_favorites (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    job_id BIGINT NOT NULL,
    favorited_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (job_id) REFERENCES job(id),
    UNIQUE(user_id, job_id)
);
"
```

#### 2. 服务无法启动

**检查服务状态**:
```bash
docker-compose ps
```

**查看日志**:
```bash
docker-compose logs backend
docker-compose logs frontend
docker-compose logs ai_service
```

**重启服务**:
```bash
docker-compose restart
```

#### 3. 爬虫无法获取数据

**检查网络连接**:
```bash
docker exec -it jobtracker-pro-ai_service-1 ping google.com
```

**手动运行爬虫**:
```bash
docker exec -it jobtracker-pro-ai_service-1 python main.py
```

## 📊 API 文档

### 认证接口

- `POST /api/auth/signup` - 用户注册
- `POST /api/auth/signin` - 用户登录

### 岗位接口

- `GET /api/jobs` - 获取岗位列表
- `GET /api/jobs/{id}` - 获取岗位详情
- `POST /api/jobs/favorite` - 收藏岗位
- `GET /api/jobs/favorites` - 获取收藏列表

### 内部接口

- `POST /api/internal/jobs/batch-intake` - 批量导入岗位数据

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- Spring Boot 团队提供的优秀框架
- React 社区的支持
- 所有贡献者的努力

---

**立即开始您的求职之旅！** 🎯

如有问题，请提交 Issue 或联系开发团队。

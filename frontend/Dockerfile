# --- Build Stage ---
# 使用官方的 Node.js 镜像作为构建环境
FROM node:20-alpine AS build

# 设置工作目录
WORKDIR /app

# 复制 package.json 和 package-lock.json 文件
COPY package.json package-lock.json ./

# 安装项目依赖
RUN npm install

# 复制所有源代码
COPY . .

# 构建生产版本的静态文件
RUN npm run build

# --- Run Stage ---
# 使用官方的 Nginx 镜像作为 Web 服务器
FROM nginx:1.27-alpine

# 将构建阶段生成的静态文件复制到 Nginx 的网站根目录
COPY --from=build /app/dist /usr/share/nginx/html

# 将自定义的 Nginx 配置文件复制到容器中
COPY Nginx.conf /etc/nginx/conf.d/default.conf

# 暴露 Nginx 默认的 80 端口
EXPOSE 80

# Nginx 默认会启动，我们保持默认命令
CMD ["nginx", "-g", "daemon off;"]

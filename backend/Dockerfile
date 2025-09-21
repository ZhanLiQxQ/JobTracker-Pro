# --- Build Stage ---
# 使用官方的 Maven 镜像作为构建环境，包含 Java 17
FROM maven:3.9.6-eclipse-temurin-17-focal AS build

# 设置工作目录
WORKDIR /app

# 复制 pom.xml 文件并下载依赖，以便利用Docker的层缓存
COPY pom.xml .
RUN mvn dependency:go-offline -B

# 复制所有源代码
COPY src ./src

# 打包应用成 jar 文件，跳过测试
RUN mvn package -DskipTests

# --- Run Stage ---
# 使用轻量的 OpenJDK 镜像作为运行环境
FROM openjdk:17-jdk-slim

# 设置工作目录
WORKDIR /app

# 从构建阶段复制打包好的 jar 文件
COPY --from=build /app/target/*.jar app.jar

# 暴露后端应用运行的端口
EXPOSE 8080

# 容器启动时运行 jar 文件
# 传入 SPRING_PROFILES_ACTIVE=prod 来激活生产环境配置
ENTRYPOINT ["java", "-Dspring.profiles.active=prod", "-jar", "app.jar"]

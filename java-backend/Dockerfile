# 使用Maven构建阶段
FROM maven:3.9-eclipse-temurin-17 AS build

# 设置工作目录
WORKDIR /app

# 复制pom.xml和源代码
COPY pom.xml .
COPY src ./src

# 构建应用
RUN mvn clean package -DskipTests

# 使用JRE运行阶段
FROM eclipse-temurin:17-jre-alpine

# 设置工作目录
WORKDIR /app

# 创建非root用户
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

# 从构建阶段复制jar文件
COPY --from=build /app/target/*.jar app.jar

# 暴露端口
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/api/agent/health/simple || exit 1

# 启动命令
ENTRYPOINT ["java", "-jar", "app.jar"]
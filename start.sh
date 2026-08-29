#!/bin/bash

# 智能座舱AI Agent启动脚本
# 作者：智能座舱开发团队
# 版本：1.0.0

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示横幅
show_banner() {
    echo -e "${BLUE}"
    echo "=========================================="
    echo "  智能座舱AI Agent启动脚本"
    echo "=========================================="
    echo -e "${NC}"
    echo "项目结构："
    echo "  - Java后端服务 (端口: 8080)"
    echo "  - Python AI服务 (端口: 5000)"
    echo "  - 前端演示界面 (端口: 80/前端文件)"
    echo "  - Redis服务 (端口: 6379，可选)"
    echo ""
}

# 检查依赖
check_dependencies() {
    log_info "检查系统依赖..."
    
    # 检查Java
    if command -v java &> /dev/null; then
        JAVA_VERSION=$(java -version 2>&1 | head -n 1 | cut -d '"' -f2)
        log_success "Java已安装: $JAVA_VERSION"
    else
        log_error "Java未安装，请安装JDK 17+"
        exit 1
    fi
    
    # 检查Maven
    if command -v mvn &> /dev/null; then
        MAVEN_VERSION=$(mvn -v | grep "Apache Maven" | cut -d ' ' -f3)
        log_success "Maven已安装: $MAVEN_VERSION"
    else
        log_error "Maven未安装，请安装Maven 3.6+"
        exit 1
    fi
    
    # 检查Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d ' ' -f2)
        log_success "Python已安装: $PYTHON_VERSION"
    else
        log_error "Python3未安装，请安装Python 3.8+"
        exit 1
    fi
    
    # 检查pip
    if command -v pip3 &> /dev/null; then
        log_success "pip已安装"
    else
        log_warning "pip未安装，将尝试安装Python依赖"
    fi
    
    log_success "所有依赖检查通过"
}

# 启动Python服务
start_python_service() {
    log_info "启动Python AI服务..."
    
    cd python-ai-service
    
    # 检查虚拟环境
    if [ ! -d "venv" ]; then
        log_info "创建Python虚拟环境..."
        python3 -m venv venv
    fi
    
    # 激活虚拟环境并安装依赖
    log_info "安装Python依赖..."
    source venv/bin/activate
    pip install -r requirements.txt
    
    # 启动服务
    log_info "启动Python服务 (端口: 5000)..."
    python app.py &
    PYTHON_PID=$!
    
    # 等待服务启动
    sleep 5
    if curl -s http://localhost:5000/health > /dev/null; then
        log_success "Python服务启动成功 (PID: $PYTHON_PID)"
    else
        log_error "Python服务启动失败"
        exit 1
    fi
    
    cd ..
}

# 启动Java服务
start_java_service() {
    log_info "启动Java后端服务..."
    
    cd java-backend
    
    # 构建项目
    log_info "构建Java项目..."
    mvn clean package -DskipTests
    
    # 启动服务
    log_info "启动Java服务 (端口: 8080)..."
    java -jar target/*.jar &
    JAVA_PID=$!
    
    # 等待服务启动
    sleep 10
    if curl -s http://localhost:8080/api/agent/health/simple > /dev/null; then
        log_success "Java服务启动成功 (PID: $JAVA_PID)"
    else
        log_error "Java服务启动失败"
        exit 1
    fi
    
    cd ..
}

# 打开前端
open_frontend() {
    log_info "准备前端演示界面..."
    
    # 检查前端文件
    if [ -f "frontend/index.html" ]; then
        log_success "前端文件已就绪"
        echo ""
        echo -e "${GREEN}前端访问地址:${NC}"
        echo "  文件路径: file://$(pwd)/frontend/index.html"
        echo "  或使用浏览器打开上述文件"
        echo ""
    else
        log_error "前端文件不存在"
        exit 1
    fi
}

# 显示服务信息
show_service_info() {
    echo -e "${GREEN}"
    echo "=========================================="
    echo "  服务启动完成！"
    echo "=========================================="
    echo -e "${NC}"
    echo "服务状态："
    echo "  ✅ Python AI服务: http://localhost:5000"
    echo "  ✅ Java后端服务: http://localhost:8080"
    echo "  ✅ 前端界面: file://$(pwd)/frontend/index.html"
    echo ""
    echo "API文档："
    echo "  Swagger UI: http://localhost:8080/swagger-ui.html"
    echo ""
    echo "测试命令："
    echo "  curl -X POST http://localhost:8080/api/agent/process \\"
    echo "    -H 'Content-Type: application/json' \\"
    echo "    -d '{\"message\":\"把空调温度调到22度\",\"sessionId\":\"test\"}'"
    echo ""
    echo "按 Ctrl+C 停止所有服务"
    echo ""
}

# 停止服务
stop_services() {
    log_info "停止所有服务..."
    
    # 停止Java服务
    if [ ! -z "$JAVA_PID" ]; then
        kill $JAVA_PID 2>/dev/null && log_success "Java服务已停止"
    fi
    
    # 停止Python服务
    if [ ! -z "$PYTHON_PID" ]; then
        kill $PYTHON_PID 2>/dev/null && log_success "Python服务已停止"
    fi
    
    log_success "所有服务已停止"
}

# 主函数
main() {
    show_banner
    check_dependencies
    
    # 设置退出时清理
    trap stop_services EXIT INT TERM
    
    # 启动服务
    start_python_service
    start_java_service
    open_frontend
    
    show_service_info
    
    # 等待用户中断
    wait
}

# 运行主函数
main "$@"
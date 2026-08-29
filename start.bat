@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM 智能座舱AI Agent启动脚本 (Windows版本)
REM 作者：智能座舱开发团队
REM 版本：1.0.0

title 智能座舱AI Agent启动脚本

REM 颜色定义
for /f %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"
set "RED=%ESC%[31m"
set "GREEN=%ESC%[32m"
set "YELLOW=%ESC%[33m"
set "BLUE=%ESC%[34m"
set "NC=%ESC%[0m"

REM 日志函数
:log_info
    echo %BLUE%[INFO]%NC% %*
    exit /b

:log_success
    echo %GREEN%[SUCCESS]%NC% %*
    exit /b

:log_warning
    echo %YELLOW%[WARNING]%NC% %*
    exit /b

:log_error
    echo %RED%[ERROR]%NC% %*
    exit /b

REM 显示横幅
call :show_banner

REM 检查依赖
call :check_dependencies

REM 设置退出时清理
set "cleanup=call :stop_services"
for %%a in (exit int term) do (
    if not defined trap_%%a (
        set "trap_%%a=1"
        trap %%a %cleanup%
    )
)

REM 启动服务
call :start_python_service
call :start_java_service
call :open_frontend

REM 显示服务信息
call :show_service_info

REM 等待用户中断
echo 按任意键停止所有服务...
pause >nul
call :stop_services
exit /b 0

REM ==========================================
REM 函数定义
REM ==========================================

:show_banner
    echo %BLUE%
    echo ==========================================
    echo   智能座舱AI Agent启动脚本
    echo ==========================================
    echo %NC%
    echo 项目结构：
    echo   - Java后端服务 (端口: 8080)
    echo   - Python AI服务 (端口: 5000)
    echo   - 前端演示界面 (端口: 80/前端文件)
    echo   - Redis服务 (端口: 6379，可选)
    echo.
    exit /b

:check_dependencies
    call :log_info "检查系统依赖..."
    
    REM 检查Java
    where java >nul 2>&1
    if %errorlevel% equ 0 (
        for /f "tokens=3" %%i in ('java -version 2^>^&1 ^| findstr /i "version"') do (
            set "java_version=%%i"
            set "java_version=!java_version:"=!"
        )
        call :log_success "Java已安装: !java_version!"
    ) else (
        call :log_error "Java未安装，请安装JDK 17+"
        exit /b 1
    )
    
    REM 检查Maven
    where mvn >nul 2>&1
    if %errorlevel% equ 0 (
        for /f "tokens=3" %%i in ('mvn -v ^| findstr /i "Apache Maven"') do (
            set "maven_version=%%i"
        )
        call :log_success "Maven已安装: !maven_version!"
    ) else (
        call :log_error "Maven未安装，请安装Maven 3.6+"
        exit /b 1
    )
    
    REM 检查Python
    where python >nul 2>&1
    if %errorlevel% equ 0 (
        for /f "tokens=2" %%i in ('python --version 2^>^&1') do (
            set "python_version=%%i"
        )
        call :log_success "Python已安装: !python_version!"
    ) else (
        call :log_error "Python未安装，请安装Python 3.8+"
        exit /b 1
    )
    
    REM 检查pip
    where pip >nul 2>&1
    if %errorlevel% equ 0 (
        call :log_success "pip已安装"
    ) else (
        call :log_warning "pip未安装，将尝试安装Python依赖"
    )
    
    call :log_success "所有依赖检查通过"
    exit /b

:start_python_service
    call :log_info "启动Python AI服务..."
    
    cd python-ai-service
    
    REM 检查虚拟环境
    if not exist venv (
        call :log_info "创建Python虚拟环境..."
        python -m venv venv
    )
    
    REM 激活虚拟环境并安装依赖
    call :log_info "安装Python依赖..."
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    
    REM 启动服务
    call :log_info "启动Python服务 (端口: 5000)..."
    start "Python AI Service" /B python app.py
    set "PYTHON_PID=!errorlevel!"
    
    REM 等待服务启动
    timeout /t 5 /nobreak >nul
    curl -s http://localhost:5000/health >nul 2>&1
    if %errorlevel% equ 0 (
        call :log_success "Python服务启动成功"
    ) else (
        call :log_error "Python服务启动失败"
        exit /b 1
    )
    
    cd ..
    exit /b

:start_java_service
    call :log_info "启动Java后端服务..."
    
    cd java-backend
    
    REM 构建项目
    call :log_info "构建Java项目..."
    mvn clean package -DskipTests
    
    REM 启动服务
    call :log_info "启动Java服务 (端口: 8080)..."
    start "Java Backend Service" /B java -jar target\*.jar
    set "JAVA_PID=!errorlevel!"
    
    REM 等待服务启动
    timeout /t 10 /nobreak >nul
    curl -s http://localhost:8080/api/agent/health/simple >nul 2>&1
    if %errorlevel% equ 0 (
        call :log_success "Java服务启动成功"
    ) else (
        call :log_error "Java服务启动失败"
        exit /b 1
    )
    
    cd ..
    exit /b

:open_frontend
    call :log_info "准备前端演示界面..."
    
    REM 检查前端文件
    if exist frontend\index.html (
        call :log_success "前端文件已就绪"
        echo.
        echo %GREEN%前端访问地址:%NC%
        echo   文件路径: %CD%\frontend\index.html
        echo   或使用浏览器打开上述文件
        echo.
    ) else (
        call :log_error "前端文件不存在"
        exit /b 1
    )
    exit /b

:show_service_info
    echo %GREEN%
    echo ==========================================
    echo   服务启动完成！
    echo ==========================================
    echo %NC%
    echo 服务状态：
    echo   ✅ Python AI服务: http://localhost:5000
    echo   ✅ Java后端服务: http://localhost:8080
    echo   ✅ 前端界面: %CD%\frontend\index.html
    echo.
    echo API文档：
    echo   Swagger UI: http://localhost:8080/swagger-ui.html
    echo.
    echo 测试命令：
    echo   curl -X POST http://localhost:8080/api/agent/process ^
    echo     -H "Content-Type: application/json" ^
    echo     -d "{\"message\":\"把空调温度调到22度\",\"sessionId\":\"test\"}"
    echo.
    echo 按任意键停止所有服务
    echo.
    exit /b

:stop_services
    call :log_info "停止所有服务..."
    
    REM 停止Java服务
    taskkill /F /IM java.exe /T >nul 2>&1
    if %errorlevel% equ 0 (
        call :log_success "Java服务已停止"
    )
    
    REM 停止Python服务
    taskkill /F /IM python.exe /T >nul 2>&1
    if %errorlevel% equ 0 (
        call :log_success "Python服务已停止"
    )
    
    call :log_success "所有服务已停止"
    exit /b
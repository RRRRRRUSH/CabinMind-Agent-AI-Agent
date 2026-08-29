#!/usr/bin/env python3
"""
智能座舱AI Agent演示脚本
用于测试和演示项目功能
"""

import json
import requests
import time
import sys

def test_python_service():
    """测试Python AI服务"""
    print("=" * 60)
    print("测试Python AI服务 (端口: 5000)")
    print("=" * 60)
    
    base_url = "http://localhost:5000"
    
    # 测试健康检查
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"健康检查: {'✅ 通过' if response.status_code == 200 else '❌ 失败'}")
        if response.status_code == 200:
            print(f"响应: {response.json()}")
    except Exception as e:
        print(f"健康检查: ❌ 失败 - {e}")
        return False
    
    # 测试意图识别
    test_cases = [
        "把空调温度调到22度",
        "播放周杰伦的音乐",
        "导航到最近的加油站",
        "打开驾驶座车窗",
        "今天天气怎么样"
    ]
    
    for i, message in enumerate(test_cases, 1):
        try:
            payload = {
                "message": message,
                "sessionId": f"test-session-{i}",
                "context": []
            }
            
            response = requests.post(
                f"{base_url}/api/intent/recognize",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                intent = result.get('intent', 'unknown')
                confidence = result.get('confidence', 0)
                print(f"\n测试 {i}: '{message}'")
                print(f"  意图: {intent}")
                print(f"  置信度: {confidence:.2f}")
                print(f"  方法: {result.get('method', 'unknown')}")
            else:
                print(f"\n测试 {i}: ❌ 失败 - 状态码: {response.status_code}")
                
        except Exception as e:
            print(f"\n测试 {i}: ❌ 异常 - {e}")
    
    return True

def test_java_service():
    """测试Java后端服务"""
    print("\n" + "=" * 60)
    print("测试Java后端服务 (端口: 8080)")
    print("=" * 60)
    
    base_url = "http://localhost:8080"
    
    # 测试健康检查
    try:
        response = requests.get(f"{base_url}/api/agent/health/simple", timeout=5)
        print(f"健康检查: {'✅ 通过' if response.status_code == 200 else '❌ 失败'}")
        if response.status_code == 200:
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"健康检查: ❌ 失败 - {e}")
        return False
    
    # 测试完整Agent处理
    test_cases = [
        {
            "message": "把空调温度调到22度",
            "description": "空调控制"
        },
        {
            "message": "播放周杰伦的音乐，音量调到80",
            "description": "媒体控制"
        },
        {
            "message": "导航到北京天安门",
            "description": "导航控制"
        },
        {
            "message": "打开天窗一半",
            "description": "车窗控制"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            payload = {
                "message": test_case["message"],
                "sessionId": f"demo-session-{i}",
                "context": [],
                "verbose": True
            }
            
            print(f"\n测试 {i}: {test_case['description']}")
            print(f"  消息: '{test_case['message']}'")
            
            response = requests.post(
                f"{base_url}/api/agent/process",
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                success = result.get('success', False)
                intent = result.get('intent', 'unknown')
                confidence = result.get('confidence', 0)
                response_msg = result.get('response', '')
                
                print(f"  结果: {'✅ 成功' if success else '❌ 失败'}")
                print(f"  意图: {intent}")
                print(f"  置信度: {confidence:.2f}")
                print(f"  响应: {response_msg}")
                
                # 显示详细信息（如果启用verbose）
                if result.get('details'):
                    print(f"  详细信息: 可用")
            else:
                print(f"  结果: ❌ 失败 - 状态码: {response.status_code}")
                
        except Exception as e:
            print(f"  结果: ❌ 异常 - {e}")
    
    return True

def test_system_info():
    """测试系统信息端点"""
    print("\n" + "=" * 60)
    print("测试系统信息")
    print("=" * 60)
    
    base_url = "http://localhost:8080"
    
    try:
        # 获取系统信息
        response = requests.get(f"{base_url}/api/agent/info", timeout=5)
        
        if response.status_code == 200:
            info = response.json()
            print("系统信息:")
            print(f"  系统名称: {info.get('system_name', 'N/A')}")
            print(f"  版本: {info.get('version', 'N/A')}")
            
            # Python服务信息
            python_info = info.get('python_service', {})
            print(f"  Python服务: {python_info.get('service', 'N/A')}")
            
            # 工具信息
            tools_info = info.get('tools', {})
            available_tools = tools_info.get('available_tools', [])
            print(f"  可用工具: {', '.join(available_tools)}")
            
            return True
        else:
            print(f"获取系统信息失败: 状态码 {response.status_code}")
            return False
            
    except Exception as e:
        print(f"获取系统信息异常: {e}")
        return False

def run_demo():
    """运行完整演示"""
    print("🚗 智能座舱AI Agent演示")
    print("=" * 60)
    
    # 检查服务是否运行
    print("检查服务状态...")
    
    services_ready = True
    
    # 检查Python服务
    try:
        response = requests.get("http://localhost:5000/health", timeout=3)
        if response.status_code != 200:
            print("❌ Python服务未运行")
            services_ready = False
        else:
            print("✅ Python服务运行正常")
    except:
        print("❌ Python服务未运行")
        services_ready = False
    
    # 检查Java服务
    try:
        response = requests.get("http://localhost:8080/api/agent/health/simple", timeout=3)
        if response.status_code != 200:
            print("❌ Java服务未运行")
            services_ready = False
        else:
            print("✅ Java服务运行正常")
    except:
        print("❌ Java服务未运行")
        services_ready = False
    
    if not services_ready:
        print("\n⚠️  请先启动服务:")
        print("   Linux/Mac: ./start.sh")
        print("   Windows: start.bat")
        print("   或使用: docker-compose up -d")
        return
    
    print("\n" + "=" * 60)
    print("开始演示...")
    print("=" * 60)
    
    # 运行测试
    test_python_service()
    test_java_service()
    test_system_info()
    
    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)
    print("\n下一步:")
    print("1. 打开前端界面: frontend/index.html")
    print("2. 访问API文档: http://localhost:8080/swagger-ui.html")
    print("3. 查看Docker容器: docker-compose ps")
    print("4. 停止服务: Ctrl+C 或 docker-compose down")

if __name__ == "__main__":
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n\n演示被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n演示出错: {e}")
        sys.exit(1)
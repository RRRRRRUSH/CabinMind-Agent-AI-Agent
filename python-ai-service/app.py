#!/usr/bin/env python3
"""
智能座舱AI Agent - Python AI服务
提供意图识别、自然语言处理等AI能力
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 导入自定义模块
from services.deepseek_service import DeepSeekService
from services.intent_recognizer import IntentRecognizer
from algorithms.intent_classifier import IntentClassifier

# 初始化服务
deepseek_service = DeepSeekService()
intent_classifier = IntentClassifier()
intent_recognizer = IntentRecognizer(deepseek_service, intent_classifier)

@app.route('/')
def index():
    """服务首页"""
    return jsonify({
        'service': 'Smart Cabin AI Service',
        'version': '1.0.0',
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'endpoints': {
            'health': '/health',
            'recognize_intent': '/api/intent/recognize',
            'process_message': '/api/message/process'
        }
    })

@app.route('/health')
def health():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'smart-cabin-ai-service'
    })

@app.route('/api/intent/recognize', methods=['POST'])
def recognize_intent():
    """
    意图识别API
    接收自然语言指令，返回结构化意图
    """
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Missing required field: message'
            }), 400
        
        message = data['message']
        context = data.get('context', [])
        session_id = data.get('sessionId', 'default')
        
        logger.info(f"Recognizing intent for message: {message}")
        
        # 使用混合方法进行意图识别
        result = intent_recognizer.recognize(
            message=message,
            context=context,
            session_id=session_id
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error recognizing intent: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/message/process', methods=['POST'])
def process_message():
    """
    完整消息处理API
    包括意图识别和参数提取
    """
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Missing required field: message'
            }), 400
        
        message = data['message']
        context = data.get('context', [])
        session_id = data.get('sessionId', 'default')
        
        logger.info(f"Processing message: {message}")
        
        # 处理消息
        result = intent_recognizer.process_message(
            message=message,
            context=context,
            session_id=session_id
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/debug/classify', methods=['POST'])
def debug_classify():
    """
    调试端点：显示意图分类的详细过程
    """
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Missing required field: message'
            }), 400
        
        message = data['message']
        
        # 获取分类详情
        keyword_result = intent_classifier.keyword_matching(message)
        hybrid_result = intent_classifier.classify_with_hybrid(message)
        
        return jsonify({
            'message': message,
            'keyword_matching': keyword_result,
            'hybrid_classification': hybrid_result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in debug classify: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    # 从环境变量获取端口，默认为5000
    port = int(os.getenv('PYTHON_SERVER_PORT', 5000))
    host = os.getenv('PYTHON_SERVER_HOST', '0.0.0.0')
    
    logger.info(f"Starting Smart Cabin AI Service on {host}:{port}")
    logger.info(f"DeepSeek API Key configured: {'Yes' if os.getenv('DEEPSEEK_API_KEY') else 'No'}")
    
    app.run(
        host=host,
        port=port,
        debug=os.getenv('APP_ENVIRONMENT', 'development') == 'development'
    )
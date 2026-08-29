"""
DeepSeek API服务封装
提供与大语言模型的交互能力
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from openai import OpenAI

logger = logging.getLogger(__name__)

class DeepSeekService:
    """DeepSeek API服务类"""
    
    def __init__(self):
        """初始化DeepSeek服务"""
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        self.api_url = os.getenv('DEEPSEEK_API_URL', 'https://api.deepseek.com')
        self.model = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
        
        if not self.api_key:
            logger.warning("DeepSeek API key not found in environment variables")
            # 在开发环境中可以使用模拟模式
            self.mock_mode = os.getenv('MOCK_MODE', 'false').lower() == 'true'
            self.client = None
        else:
            self.mock_mode = False
            # 配置OpenAI客户端（DeepSeek兼容OpenAI API）
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.api_url
            )
        
        logger.info(f"DeepSeek service initialized. Mock mode: {self.mock_mode}")
    
    def chat_completion(self, 
                       messages: List[Dict[str, str]], 
                       temperature: float = 0.7,
                       max_tokens: int = 1000) -> Dict[str, Any]:
        """
        调用DeepSeek聊天补全API
        
        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            temperature: 温度参数，控制随机性
            max_tokens: 最大生成token数
            
        Returns:
            API响应字典
        """
        if self.mock_mode:
            logger.info("Mock mode: Returning mock response")
            return self._mock_chat_completion(messages)
        
        if not self.client:
            logger.error("OpenAI client not initialized")
            return {
                'success': False,
                'error': 'OpenAI client not initialized. Check API key.',
                'content': None
            }
        
        try:
            logger.info(f"Calling DeepSeek API with {len(messages)} messages")
            
            # 使用OpenAI 1.0+ API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False
            )
            
            # 提取响应内容
            result = {
                'success': True,
                'content': response.choices[0].message.content,
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                },
                'model': response.model,
                'finish_reason': response.choices[0].finish_reason
            }
            
            logger.info(f"DeepSeek API call successful. Tokens used: {result['usage']['total_tokens']}")
            return result
            
        except Exception as e:
            logger.error(f"API call error: {str(e)}")
            return {
                'success': False,
                'error': f'API call error: {str(e)}',
                'content': None
            }
    
    def recognize_intent(self, 
                        user_message: str, 
                        context: Optional[List[str]] = None,
                        system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        专门用于意图识别的API调用
        
        Args:
            user_message: 用户消息
            context: 上下文消息列表
            system_prompt: 系统提示词
            
        Returns:
            意图识别结果
        """
        # 构建消息列表
        messages = []
        
        # 添加系统提示词
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            # 默认系统提示词
            messages.append({
                "role": "system", 
                "content": """你是一个智能座舱助手，专门处理车载环境下的指令。
                请将用户的自然语言指令解析为结构化JSON格式。
                输出必须是有效的JSON，包含以下字段：
                - intent: 意图类型（climate_control, media_control, navigation, window_control, unknown）
                - parameters: 参数字典
                - confidence: 置信度（0.0-1.0）
                - explanation: 简要解释
                
                示例输出：
                {
                  "intent": "climate_control",
                  "parameters": {"temperature": 22, "mode": "cool"},
                  "confidence": 0.9,
                  "explanation": "用户要求调节空调温度"
                }"""
            })
        
        # 添加上下文
        if context:
            for ctx in context[-3:]:  # 只保留最近3条上下文
                messages.append({"role": "user", "content": ctx})
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": user_message})
        
        # 调用API
        response = self.chat_completion(
            messages=messages,
            temperature=0.3,  # 较低的温度以获得更确定的输出
            max_tokens=500
        )
        
        if not response.get('success', False):
            return response
        
        # 尝试解析JSON响应
        try:
            content = response['content']
            # 提取JSON部分（可能包含其他文本）
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                intent_result = json.loads(json_str)
                
                # 验证必要字段
                required_fields = ['intent', 'parameters', 'confidence']
                if all(field in intent_result for field in required_fields):
                    return {
                        'success': True,
                        'intent_result': intent_result,
                        'raw_response': content
                    }
                else:
                    logger.warning(f"Missing required fields in intent result: {intent_result}")
                    return {
                        'success': False,
                        'error': 'Invalid intent result format',
                        'raw_response': content
                    }
            else:
                logger.warning(f"No JSON found in response: {content}")
                return {
                    'success': False,
                    'error': 'No JSON response found',
                    'raw_response': content
                }
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}. Response: {response.get('content')}")
            return {
                'success': False,
                'error': f'JSON decode error: {str(e)}',
                'raw_response': response.get('content')
            }
        except Exception as e:
            logger.error(f"Error parsing intent response: {str(e)}")
            return {
                'success': False,
                'error': f'Parse error: {str(e)}',
                'raw_response': response.get('content')
            }
    
    def _mock_chat_completion(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """模拟聊天补全响应（用于开发和测试）"""
        # 提取最后一条用户消息
        last_user_message = None
        for msg in reversed(messages):
            if msg['role'] == 'user':
                last_user_message = msg['content']
                break
        
        # 基于关键词的简单意图识别
        intent_map = {
            'climate_control': ['温度', '空调', '加热', '制冷', '风速', '调温'],
            'media_control': ['播放', '音乐', '暂停', '下一首', '音量', '歌曲'],
            'navigation': ['导航', '去', '目的地', '路线', '地图', '加油站'],
            'window_control': ['车窗', '打开', '关闭', '天窗', '窗户']
        }
        
        detected_intent = 'unknown'
        parameters = {}
        
        if last_user_message:
            for intent, keywords in intent_map.items():
                if any(keyword in last_user_message for keyword in keywords):
                    detected_intent = intent
                    
                    # 简单参数提取
                    if intent == 'climate_control':
                        import re
                        temp_match = re.search(r'(\d+)度', last_user_message)
                        if temp_match:
                            parameters['temperature'] = int(temp_match.group(1))
                    
                    break
        
        mock_response = {
            "intent": detected_intent,
            "parameters": parameters,
            "confidence": 0.8 if detected_intent != 'unknown' else 0.3,
            "explanation": f"识别为{detected_intent}意图" if detected_intent != 'unknown' else "无法识别意图"
        }
        
        return {
            'success': True,
            'content': json.dumps(mock_response, ensure_ascii=False),
            'usage': {
                'prompt_tokens': 50,
                'completion_tokens': 30,
                'total_tokens': 80
            },
            'model': 'deepseek-chat-mock',
            'finish_reason': 'stop'
        }
    
    def is_available(self) -> bool:
        """检查服务是否可用"""
        if self.mock_mode:
            return True
        
        if not self.api_key:
            return False
        
        # 可以添加更详细的健康检查
        return True
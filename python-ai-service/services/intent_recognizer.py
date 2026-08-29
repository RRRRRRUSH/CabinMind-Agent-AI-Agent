"""
意图识别服务
整合DeepSeek API和自定义算法，提供混合意图识别能力
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class IntentRecognizer:
    """意图识别器 - 整合DeepSeek和自定义算法"""
    
    def __init__(self, deepseek_service, intent_classifier):
        """
        初始化意图识别器
        
        Args:
            deepseek_service: DeepSeek服务实例
            intent_classifier: 意图分类器实例
        """
        self.deepseek_service = deepseek_service
        self.intent_classifier = intent_classifier
        
        # 配置权重
        self.deepseek_weight = 0.7  # DeepSeek权重
        self.classifier_weight = 0.3  # 自定义分类器权重
        
        # 置信度阈值
        self.confidence_threshold = 0.5
        
        logger.info("Intent recognizer initialized")
    
    def recognize(self, 
                 message: str, 
                 context: Optional[List[str]] = None,
                 session_id: str = 'default') -> Dict[str, Any]:
        """
        识别用户意图（混合方法）
        
        Args:
            message: 用户消息
            context: 上下文消息列表
            session_id: 会话ID
            
        Returns:
            意图识别结果
        """
        logger.info(f"Recognizing intent for message: {message}")
        
        # 1. 使用自定义分类器进行初步识别
        classifier_result = self.intent_classifier.classify_with_hybrid(message, context)
        logger.info(f"Classifier result: {classifier_result['intent']} (confidence: {classifier_result['confidence']:.2f})")
        
        # 2. 使用DeepSeek进行精细识别
        deepseek_result = self.deepseek_service.recognize_intent(
            user_message=message,
            context=context
        )
        
        deepseek_intent = 'unknown'
        deepseek_confidence = 0.0
        deepseek_parameters = {}
        
        if deepseek_result.get('success', False):
            intent_data = deepseek_result.get('intent_result', {})
            deepseek_intent = intent_data.get('intent', 'unknown')
            deepseek_confidence = intent_data.get('confidence', 0.0)
            deepseek_parameters = intent_data.get('parameters', {})
            logger.info(f"DeepSeek result: {deepseek_intent} (confidence: {deepseek_confidence:.2f})")
        else:
            logger.warning(f"DeepSeek API call failed: {deepseek_result.get('error')}")
        
        # 3. 混合决策
        final_result = self._hybrid_decision(
            classifier_result=classifier_result,
            deepseek_intent=deepseek_intent,
            deepseek_confidence=deepseek_confidence,
            deepseek_parameters=deepseek_parameters,
            message=message
        )
        
        # 4. 添加元数据
        final_result.update({
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id,
            'original_message': message,
            'context_used': context if context else [],
            'recognition_method': final_result.get('method', 'hybrid'),
            'components': {
                'classifier': {
                    'intent': classifier_result['intent'],
                    'confidence': classifier_result['confidence'],
                    'method': classifier_result['method']
                },
                'deepseek': {
                    'intent': deepseek_intent,
                    'confidence': deepseek_confidence,
                    'success': deepseek_result.get('success', False)
                }
            }
        })
        
        logger.info(f"Final intent: {final_result['intent']} (confidence: {final_result['confidence']:.2f})")
        return final_result
    
    def process_message(self,
                       message: str,
                       context: Optional[List[str]] = None,
                       session_id: str = 'default') -> Dict[str, Any]:
        """
        完整消息处理，包括意图识别和参数验证
        
        Args:
            message: 用户消息
            context: 上下文消息列表
            session_id: 会话ID
            
        Returns:
            完整处理结果
        """
        # 1. 识别意图
        intent_result = self.recognize(message, context, session_id)
        
        # 2. 验证参数
        validated_params = self._validate_parameters(
            intent=intent_result['intent'],
            parameters=intent_result['parameters']
        )
        
        # 3. 生成响应消息
        response_message = self._generate_response(
            intent=intent_result['intent'],
            parameters=validated_params,
            confidence=intent_result['confidence']
        )
        
        # 4. 构建完整响应
        result = {
            'success': intent_result['confidence'] >= self.confidence_threshold,
            'intent': intent_result['intent'],
            'confidence': intent_result['confidence'],
            'parameters': validated_params,
            'response': response_message,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'details': {
                'recognition_details': intent_result,
                'parameter_validation': {
                    'original': intent_result['parameters'],
                    'validated': validated_params,
                    'changes_made': validated_params != intent_result['parameters']
                }
            }
        }
        
        return result
    
    def _hybrid_decision(self,
                        classifier_result: Dict[str, Any],
                        deepseek_intent: str,
                        deepseek_confidence: float,
                        deepseek_parameters: Dict[str, Any],
                        message: str) -> Dict[str, Any]:
        """
        混合决策逻辑
        
        Args:
            classifier_result: 分类器结果
            deepseek_intent: DeepSeek识别意图
            deepseek_confidence: DeepSeek置信度
            deepseek_parameters: DeepSeek提取的参数
            message: 原始消息
            
        Returns:
            混合决策结果
        """
        classifier_intent = classifier_result['intent']
        classifier_confidence = classifier_result['confidence']
        
        # 情况1: 两者结果一致
        if classifier_intent == deepseek_intent and classifier_intent != 'unknown':
            combined_confidence = (
                classifier_confidence * self.classifier_weight +
                deepseek_confidence * self.deepseek_weight
            )
            
            # 合并参数（优先使用DeepSeek的参数）
            combined_parameters = {**classifier_result['parameters'], **deepseek_parameters}
            
            return {
                'intent': classifier_intent,
                'confidence': combined_confidence,
                'parameters': combined_parameters,
                'method': 'hybrid_consistent',
                'decision_reason': 'Both methods agree'
            }
        
        # 情况2: 分类器置信度高且不为unknown
        elif (classifier_confidence >= self.confidence_threshold and 
              classifier_intent != 'unknown' and
              classifier_confidence >= deepseek_confidence):
            
            return {
                'intent': classifier_intent,
                'confidence': classifier_confidence,
                'parameters': classifier_result['parameters'],
                'method': 'hybrid_classifier_preferred',
                'decision_reason': 'Classifier has higher confidence'
            }
        
        # 情况3: DeepSeek置信度高且不为unknown
        elif (deepseek_confidence >= self.confidence_threshold and 
              deepseek_intent != 'unknown' and
              deepseek_confidence >= classifier_confidence):
            
            return {
                'intent': deepseek_intent,
                'confidence': deepseek_confidence,
                'parameters': deepseek_parameters,
                'method': 'hybrid_deepseek_preferred',
                'decision_reason': 'DeepSeek has higher confidence'
            }
        
        # 情况4: 两者都不确定，但分类器有结果
        elif classifier_intent != 'unknown':
            return {
                'intent': classifier_intent,
                'confidence': classifier_confidence * 0.8,  # 降低置信度
                'parameters': classifier_result['parameters'],
                'method': 'hybrid_fallback_classifier',
                'decision_reason': 'Fallback to classifier with low confidence'
            }
        
        # 情况5: 完全无法识别
        else:
            return {
                'intent': 'unknown',
                'confidence': 0.0,
                'parameters': {},
                'method': 'hybrid_unknown',
                'decision_reason': 'Unable to recognize intent'
            }
    
    def _validate_parameters(self, intent: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证和规范化参数
        
        Args:
            intent: 意图类型
            parameters: 原始参数
            
        Returns:
            验证后的参数
        """
        validated = parameters.copy()
        
        if intent == 'climate_control':
            # 验证温度范围
            if 'temperature' in validated:
                temp = validated['temperature']
                if not isinstance(temp, (int, float)):
                    try:
                        temp = float(temp)
                    except (ValueError, TypeError):
                        temp = 22  # 默认值
                
                # 限制在合理范围
                if temp < 16:
                    temp = 16
                elif temp > 30:
                    temp = 30
                
                validated['temperature'] = int(temp)
            
            # 确保有模式参数
            if 'mode' not in validated:
                validated['mode'] = 'auto'
        
        elif intent == 'media_control':
            # 验证音量范围
            if 'volume' in validated:
                volume = validated['volume']
                if not isinstance(volume, (int, float)):
                    try:
                        volume = int(volume)
                    except (ValueError, TypeError):
                        volume = 50  # 默认值
                
                # 限制在0-100
                if volume < 0:
                    volume = 0
                elif volume > 100:
                    volume = 100
                
                validated['volume'] = int(volume)
        
        elif intent == 'navigation':
            # 清理目的地字符串
            if 'destination' in validated:
                dest = validated['destination']
                if isinstance(dest, str):
                    # 移除多余空格和标点
                    dest = dest.strip().rstrip('。.!?！？')
                    validated['destination'] = dest
        
        elif intent == 'window_control':
            # 确保有动作参数
            if 'action' not in validated:
                validated['action'] = 'open'  # 默认打开
            
            # 确保有位置参数
            if 'window_position' not in validated:
                validated['window_position'] = 'all'  # 默认所有窗户
        
        return validated
    
    def _generate_response(self, 
                          intent: str, 
                          parameters: Dict[str, Any],
                          confidence: float) -> str:
        """
        根据意图和参数生成响应消息
        
        Args:
            intent: 意图类型
            parameters: 参数
            confidence: 置信度
            
        Returns:
            响应消息
        """
        if intent == 'unknown' or confidence < 0.3:
            return "抱歉，我没有理解您的指令。请尝试换一种说法。"
        
        responses = {
            'climate_control': self._generate_climate_response,
            'media_control': self._generate_media_response,
            'navigation': self._generate_navigation_response,
            'window_control': self._generate_window_response
        }
        
        generator = responses.get(intent, lambda p, c: "指令已接收。")
        return generator(parameters, confidence)
    
    def _generate_climate_response(self, parameters: Dict[str, Any], confidence: float) -> str:
        """生成空调控制响应"""
        parts = []
        
        if 'temperature' in parameters:
            parts.append(f"温度已设置为{parameters['temperature']}度")
        
        if 'mode' in parameters:
            mode_map = {
                'auto': '自动模式',
                'cool': '制冷模式',
                'heat': '制热模式'
            }
            mode_text = mode_map.get(parameters['mode'], parameters['mode'])
            parts.append(f"空调模式：{mode_text}")
        
        if 'fan_speed' in parameters:
            speed_map = {
                'high': '高速',
                'medium': '中速',
                'low': '低速'
            }
            speed_text = speed_map.get(parameters['fan_speed'], parameters['fan_speed'])
            parts.append(f"风速：{speed_text}")
        
        if parts:
            return "已调整空调设置：" + "，".join(parts)
        else:
            return "空调设置已调整。"
    
    def _generate_media_response(self, parameters: Dict[str, Any], confidence: float) -> str:
        """生成媒体控制响应"""
        if 'action' in parameters:
            action = parameters['action']
            if action == 'play':
                if 'artist' in parameters:
                    return f"正在播放{parameters['artist']}的音乐"
                else:
                    return "开始播放音乐"
            elif action == 'pause':
                return "已暂停播放"
            elif action == 'next':
                return "切换到下一首歌曲"
            elif action == 'previous':
                return "切换到上一首歌曲"
        
        if 'volume' in parameters:
            return f"音量已调整为{parameters['volume']}%"
        elif 'volume_action' in parameters:
            action = parameters['volume_action']
            if action == 'increase':
                return "音量已调大"
            elif action == 'decrease':
                return "音量已调小"
        
        return "媒体设置已调整。"
    
    def _generate_navigation_response(self, parameters: Dict[str, Any], confidence: float) -> str:
        """生成导航响应"""
        if 'destination' in parameters:
            dest = parameters['destination']
            
            if parameters.get('is_home', False):
                return "正在规划回家路线。"
            elif parameters.get('is_work', False):
                return "正在规划去公司的路线。"
            elif parameters.get('search_nearby', False):
                poi_type = parameters.get('poi_type', '地点')
                poi_map = {
                    'gas_station': '加油站',
                    'restaurant': '餐厅',
                    'hotel': '酒店'
                }
                poi_text = poi_map.get(poi_type, poi_type)
                return f"正在搜索附近的{poi_text}。"
            else:
                return f"正在规划去{dest}的路线。"
        
        return "导航功能已启动。"
    
    def _generate_window_response(self, parameters: Dict[str, Any], confidence: float) -> str:
        """生成车窗控制响应"""
        action = parameters.get('action', 'open')
        position = parameters.get('window_position', 'all')
        degree = parameters.get('degree', 'fully')
        
        action_text = "打开" if action == 'open' else "关闭"
        degree_text = {
            'slightly': '一点',
            'half': '一半',
            'fully': ''
        }.get(degree, '')
        
        position_map = {
            'all': '所有车窗',
            '左窗': '左侧车窗',
            '右窗': '右侧车窗',
            '前窗': '前车窗',
            '后窗': '后车窗',
            '天窗': '天窗',
            '驾驶座': '驾驶座车窗',
            '副驾驶': '副驾驶车窗'
        }
        
        position_text = position_map.get(position, position)
        
        return f"{position_text}{action_text}{degree_text}。"
    
    def update_weights(self, deepseek_weight: float, classifier_weight: float):
        """
        更新混合权重
        
        Args:
            deepseek_weight: DeepSeek权重
            classifier_weight: 分类器权重
        """
        total = deepseek_weight + classifier_weight
        if total > 0:
            self.deepseek_weight = deepseek_weight / total
            self.classifier_weight = classifier_weight / total
            logger.info(f"Weights updated: DeepSeek={self.deepseek_weight:.2f}, Classifier={self.classifier_weight:.2f}")
        else:
            logger.warning("Weights sum to zero, keeping current values")
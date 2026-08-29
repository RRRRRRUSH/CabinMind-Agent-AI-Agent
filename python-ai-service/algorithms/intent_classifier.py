"""
自定义意图分类算法
结合规则匹配和简单机器学习方法
"""

import re
import json
import logging
from typing import Dict, List, Tuple, Any, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)

class IntentClassifier:
    """意图分类器 - 自定义算法实现"""
    
    def __init__(self):
        """初始化意图分类器"""
        # 关键词模式定义
        self.keyword_patterns = {
            'climate_control': {
                'keywords': ['温度', '空调', '加热', '制冷', '风速', '调温', '暖气', '冷气', '暖风', '冷风'],
                'patterns': [
                    r'(\d+)度',  # 匹配温度
                    r'调(高|低|大|小)',  # 匹配调节方向
                    r'(自动|手动)模式'  # 匹配模式
                ]
            },
            'media_control': {
                'keywords': ['播放', '音乐', '暂停', '下一首', '音量', '歌曲', '歌', '专辑', '艺术家', '静音'],
                'patterns': [
                    r'音量(调|设为)(\d+)',  # 匹配音量设置
                    r'播放(.+)的歌',  # 匹配播放特定歌曲
                    r'(暂停|继续|停止)'  # 匹配控制命令
                ]
            },
            'navigation': {
                'keywords': ['导航', '去', '目的地', '路线', '地图', '加油站', '餐厅', '酒店', '回家', '去公司'],
                'patterns': [
                    r'去(.+)',  # 匹配目的地
                    r'导航到(.+)',  # 匹配导航目的地
                    r'最近的(.+)'  # 匹配最近的地点
                ]
            },
            'window_control': {
                'keywords': ['车窗', '打开', '关闭', '天窗', '窗户', '左窗', '右窗', '前窗', '后窗'],
                'patterns': [
                    r'(打开|关闭)(.+窗)',  # 匹配开关窗户
                    r'(.+窗)(打开|关闭)',  # 匹配窗户开关
                    r'开(一点|一半|全部)'  # 匹配开窗程度
                ]
            }
        }
        
        # 意图优先级（数值越高优先级越高）
        self.intent_priority = {
            'climate_control': 4,
            'navigation': 3,
            'media_control': 2,
            'window_control': 1
        }
        
        # 训练数据（可以扩展为从文件加载）
        self.training_data = self._load_training_data()
        
        logger.info("Intent classifier initialized")
    
    def _load_training_data(self) -> Dict[str, List[str]]:
        """加载训练数据（简化版）"""
        return {
            'climate_control': [
                '把空调温度调到22度',
                '打开空调制冷模式',
                '调高风速',
                '温度太高了调低一点',
                '开启自动空调'
            ],
            'media_control': [
                '播放周杰伦的音乐',
                '音量调大一点',
                '下一首歌',
                '暂停播放',
                '我想听流行音乐'
            ],
            'navigation': [
                '导航到最近的加油站',
                '去北京天安门',
                '回家路线',
                '找一家附近的餐厅',
                '去公司怎么走'
            ],
            'window_control': [
                '打开驾驶座车窗',
                '关闭所有窗户',
                '天窗开一半',
                '副驾驶窗户打开',
                '关上车窗'
            ]
        }
    
    def keyword_matching(self, text: str) -> Dict[str, Any]:
        """
        基于关键词匹配的意图分类
        
        Args:
            text: 输入文本
            
        Returns:
            分类结果
        """
        text_lower = text.lower()
        scores = defaultdict(float)
        matched_keywords = defaultdict(list)
        
        # 计算每个意图的匹配分数
        for intent, config in self.keyword_patterns.items():
            # 关键词匹配
            keyword_score = 0
            for keyword in config['keywords']:
                if keyword in text:
                    keyword_score += 1
                    matched_keywords[intent].append(keyword)
            
            # 正则模式匹配
            pattern_score = 0
            for pattern_str in config['patterns']:
                if re.search(pattern_str, text):
                    pattern_score += 1
            
            # 计算总分（关键词权重0.6，模式权重0.4）
            total_score = (keyword_score * 0.6 + pattern_score * 0.4) / max(len(config['keywords']), 1)
            scores[intent] = total_score
        
        # 找到最高分
        if scores:
            best_intent = max(scores.items(), key=lambda x: (x[1], self.intent_priority.get(x[0], 0)))
            confidence = best_intent[1]
            
            # 提取参数
            parameters = self._extract_parameters(text, best_intent[0])
            
            return {
                'intent': best_intent[0] if confidence > 0.1 else 'unknown',
                'confidence': min(confidence, 1.0),
                'parameters': parameters,
                'method': 'keyword_matching',
                'matched_keywords': dict(matched_keywords)
            }
        else:
            return {
                'intent': 'unknown',
                'confidence': 0.0,
                'parameters': {},
                'method': 'keyword_matching',
                'matched_keywords': {}
            }
    
    def similarity_based_classification(self, text: str) -> Dict[str, Any]:
        """
        基于相似度的分类（简化版）
        使用编辑距离和简单特征
        
        Args:
            text: 输入文本
            
        Returns:
            分类结果
        """
        # 简单的编辑距离计算
        def edit_distance(s1: str, s2: str) -> int:
            """计算编辑距离（简化版）"""
            if len(s1) < len(s2):
                return edit_distance(s2, s1)
            
            if len(s2) == 0:
                return len(s1)
            
            previous_row = range(len(s2) + 1)
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            
            return previous_row[-1]
        
        # 计算与训练数据的相似度
        scores = defaultdict(float)
        best_matches = defaultdict(list)
        
        for intent, examples in self.training_data.items():
            distances = []
            for example in examples:
                distance = edit_distance(text, example)
                max_len = max(len(text), len(example))
                similarity = 1 - (distance / max_len) if max_len > 0 else 0
                distances.append(similarity)
                
                # 记录最佳匹配
                if similarity > 0.6:
                    best_matches[intent].append({
                        'example': example,
                        'similarity': similarity
                    })
            
            # 取最高相似度作为该意图的分数
            if distances:
                scores[intent] = max(distances)
        
        # 找到最佳匹配
        if scores:
            best_intent = max(scores.items(), key=lambda x: x[1])
            confidence = best_intent[1]
            
            return {
                'intent': best_intent[0] if confidence > 0.3 else 'unknown',
                'confidence': confidence,
                'parameters': self._extract_parameters(text, best_intent[0]),
                'method': 'similarity_based',
                'best_matches': dict(best_matches)
            }
        else:
            return {
                'intent': 'unknown',
                'confidence': 0.0,
                'parameters': {},
                'method': 'similarity_based',
                'best_matches': {}
            }
    
    def classify_with_hybrid(self, text: str, context: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        混合分类方法
        结合关键词匹配和相似度分类
        
        Args:
            text: 输入文本
            context: 上下文信息
            
        Returns:
            混合分类结果
        """
        # 获取两种方法的分类结果
        keyword_result = self.keyword_matching(text)
        similarity_result = self.similarity_based_classification(text)
        
        # 权重设置
        keyword_weight = 0.7
        similarity_weight = 0.3
        
        # 如果有关键词匹配，增加其权重
        if keyword_result['confidence'] > 0.5:
            keyword_weight = 0.8
            similarity_weight = 0.2
        
        # 合并结果
        if keyword_result['intent'] == similarity_result['intent']:
            # 两种方法结果一致
            combined_confidence = (
                keyword_result['confidence'] * keyword_weight +
                similarity_result['confidence'] * similarity_weight
            )
            
            # 合并参数
            combined_params = {**similarity_result['parameters'], **keyword_result['parameters']}
            
            return {
                'intent': keyword_result['intent'],
                'confidence': combined_confidence,
                'parameters': combined_params,
                'method': 'hybrid',
                'details': {
                    'keyword_result': keyword_result,
                    'similarity_result': similarity_result,
                    'weights': {'keyword': keyword_weight, 'similarity': similarity_weight}
                }
            }
        else:
            # 两种方法结果不一致，选择置信度高的
            if keyword_result['confidence'] >= similarity_result['confidence']:
                return {
                    'intent': keyword_result['intent'],
                    'confidence': keyword_result['confidence'],
                    'parameters': keyword_result['parameters'],
                    'method': 'hybrid_fallback_keyword',
                    'details': {
                        'keyword_result': keyword_result,
                        'similarity_result': similarity_result,
                        'conflict': True
                    }
                }
            else:
                return {
                    'intent': similarity_result['intent'],
                    'confidence': similarity_result['confidence'],
                    'parameters': similarity_result['parameters'],
                    'method': 'hybrid_fallback_similarity',
                    'details': {
                        'keyword_result': keyword_result,
                        'similarity_result': similarity_result,
                        'conflict': True
                    }
                }
    
    def _extract_parameters(self, text: str, intent: str) -> Dict[str, Any]:
        """
        根据意图提取参数
        
        Args:
            text: 输入文本
            intent: 意图类型
            
        Returns:
            参数字典
        """
        parameters = {}
        
        if intent == 'climate_control':
            # 提取温度
            temp_match = re.search(r'(\d+)度', text)
            if temp_match:
                parameters['temperature'] = int(temp_match.group(1))
            
            # 提取模式
            if '自动' in text:
                parameters['mode'] = 'auto'
            elif '制冷' in text or '冷气' in text:
                parameters['mode'] = 'cool'
            elif '加热' in text or '暖气' in text:
                parameters['mode'] = 'heat'
            
            # 提取风速
            if '风速' in text or '风量' in text:
                if '大' in text or '高' in text:
                    parameters['fan_speed'] = 'high'
                elif '小' in text or '低' in text:
                    parameters['fan_speed'] = 'low'
                else:
                    parameters['fan_speed'] = 'medium'
        
        elif intent == 'media_control':
            # 提取音量
            volume_match = re.search(r'音量(调|设为)?(\d+)', text)
            if volume_match:
                parameters['volume'] = int(volume_match.group(2))
            elif '调大' in text or '加大' in text:
                parameters['volume_action'] = 'increase'
            elif '调小' in text or '减小' in text:
                parameters['volume_action'] = 'decrease'
            
            # 提取播放控制
            if '播放' in text:
                parameters['action'] = 'play'
            elif '暂停' in text:
                parameters['action'] = 'pause'
            elif '下一首' in text or '下一曲' in text:
                parameters['action'] = 'next'
            elif '上一首' in text or '上一曲' in text:
                parameters['action'] = 'previous'
            
            # 提取音乐信息
            artist_match = re.search(r'播放(.+?)的歌', text)
            if artist_match:
                parameters['artist'] = artist_match.group(1)
        
        elif intent == 'navigation':
            # 提取目的地
            dest_match = re.search(r'(去|导航到|到)(.+)', text)
            if dest_match:
                parameters['destination'] = dest_match.group(2).strip()
            
            # 检查是否是特定地点
            if '回家' in text:
                parameters['destination'] = '家'
                parameters['is_home'] = True
            elif '去公司' in text or '到公司' in text:
                parameters['destination'] = '公司'
                parameters['is_work'] = True
            
            # 检查是否是查找附近
            if '最近' in text or '附近' in text:
                parameters['search_nearby'] = True
                if '加油站' in text:
                    parameters['poi_type'] = 'gas_station'
                elif '餐厅' in text:
                    parameters['poi_type'] = 'restaurant'
                elif '酒店' in text:
                    parameters['poi_type'] = 'hotel'
        
        elif intent == 'window_control':
            # 提取窗户位置
            window_positions = ['左窗', '右窗', '前窗', '后窗', '天窗', '驾驶座', '副驾驶']
            for pos in window_positions:
                if pos in text:
                    parameters['window_position'] = pos
                    break
            
            # 提取动作
            if '打开' in text or '开' in text:
                parameters['action'] = 'open'
            elif '关闭' in text or '关' in text:
                parameters['action'] = 'close'
            
            # 提取程度
            if '一点' in text:
                parameters['degree'] = 'slightly'
            elif '一半' in text:
                parameters['degree'] = 'half'
            elif '全部' in text:
                parameters['degree'] = 'fully'
        
        return parameters
    
    def evaluate(self, test_cases: List[Tuple[str, str]]) -> Dict[str, Any]:
        """
        评估分类器性能
        
        Args:
            test_cases: 测试用例列表，每个元素为(文本, 真实意图)
            
        Returns:
            评估结果
        """
        correct = 0
        total = len(test_cases)
        confusion_matrix = defaultdict(lambda: defaultdict(int))
        
        for text, true_intent in test_cases:
            result = self.classify_with_hybrid(text)
            predicted_intent = result['intent']
            
            confusion_matrix[true_intent][predicted_intent] += 1
            
            if predicted_intent == true_intent:
                correct += 1
        
        accuracy = correct / total if total > 0 else 0
        
        return {
            'accuracy': accuracy,
            'correct': correct,
            'total': total,
            'confusion_matrix': dict(confusion_matrix)
        }
package com.smartcabin.service;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

/**
 * 工具调用服务
 * 负责执行具体的座舱控制操作
 */
@Slf4j
@Service
public class ToolService {
    
    /**
     * 执行工具调用
     */
    public Map<String, Object> executeTool(String intent, Map<String, Object> parameters) {
        log.info("执行工具调用: intent={}, parameters={}", intent, parameters);
        
        try {
            Map<String, Object> result = new HashMap<>();
            
            switch (intent) {
                case "climate_control":
                    result = executeClimateControl(parameters);
                    break;
                case "media_control":
                    result = executeMediaControl(parameters);
                    break;
                case "navigation":
                    result = executeNavigation(parameters);
                    break;
                case "window_control":
                    result = executeWindowControl(parameters);
                    break;
                default:
                    result.put("success", false);
                    result.put("message", "未知的意图类型: " + intent);
                    result.put("error", "UNKNOWN_INTENT");
                    break;
            }
            
            log.info("工具执行结果: success={}, message={}", 
                     result.get("success"), result.get("message"));
            return result;
            
        } catch (Exception e) {
            log.error("工具执行异常: {}", e.getMessage(), e);
            
            Map<String, Object> errorResult = new HashMap<>();
            errorResult.put("success", false);
            errorResult.put("message", "工具执行失败: " + e.getMessage());
            errorResult.put("error", e.getClass().getSimpleName());
            return errorResult;
        }
    }
    
    /**
     * 执行空调控制
     */
    private Map<String, Object> executeClimateControl(Map<String, Object> parameters) {
        log.info("执行空调控制: {}", parameters);
        
        Map<String, Object> result = new HashMap<>();
        
        try {
            // 模拟空调控制逻辑
            Integer temperature = (Integer) parameters.get("temperature");
            String mode = (String) parameters.get("mode");
            String fanSpeed = (String) parameters.get("fan_speed");
            
            StringBuilder message = new StringBuilder("空调设置已更新");
            
            if (temperature != null) {
                message.append(String.format("，温度: %d°C", temperature));
            }
            
            if (mode != null) {
                String modeText = switch (mode) {
                    case "auto" -> "自动模式";
                    case "cool" -> "制冷模式";
                    case "heat" -> "制热模式";
                    default -> mode;
                };
                message.append(String.format("，模式: %s", modeText));
            }
            
            if (fanSpeed != null) {
                String speedText = switch (fanSpeed) {
                    case "high" -> "高速";
                    case "medium" -> "中速";
                    case "low" -> "低速";
                    default -> fanSpeed;
                };
                message.append(String.format("，风速: %s", speedText));
            }
            
            message.append("。");
            
            result.put("success", true);
            result.put("message", message.toString());
            result.put("action", "climate_control");
            result.put("parameters_applied", parameters);
            
            // 模拟执行延迟
            Thread.sleep(500);
            
        } catch (Exception e) {
            result.put("success", false);
            result.put("message", "空调控制失败: " + e.getMessage());
            result.put("error", "CLIMATE_CONTROL_ERROR");
        }
        
        return result;
    }
    
    /**
     * 执行媒体控制
     */
    private Map<String, Object> executeMediaControl(Map<String, Object> parameters) {
        log.info("执行媒体控制: {}", parameters);
        
        Map<String, Object> result = new HashMap<>();
        
        try {
            String action = (String) parameters.get("action");
            Integer volume = (Integer) parameters.get("volume");
            String volumeAction = (String) parameters.get("volume_action");
            String artist = (String) parameters.get("artist");
            
            StringBuilder message = new StringBuilder();
            
            if (action != null) {
                switch (action) {
                    case "play":
                        if (artist != null) {
                            message.append(String.format("正在播放%s的音乐", artist));
                        } else {
                            message.append("开始播放音乐");
                        }
                        break;
                    case "pause":
                        message.append("已暂停播放");
                        break;
                    case "next":
                        message.append("切换到下一首歌曲");
                        break;
                    case "previous":
                        message.append("切换到上一首歌曲");
                        break;
                    default:
                        message.append("执行媒体控制操作");
                }
            } else if (volume != null) {
                message.append(String.format("音量已调整为%d%%", volume));
            } else if (volumeAction != null) {
                if ("increase".equals(volumeAction)) {
                    message.append("音量已调大");
                } else if ("decrease".equals(volumeAction)) {
                    message.append("音量已调小");
                }
            } else {
                message.append("媒体设置已更新");
            }
            
            result.put("success", true);
            result.put("message", message.toString());
            result.put("action", "media_control");
            result.put("parameters_applied", parameters);
            
            // 模拟执行延迟
            Thread.sleep(300);
            
        } catch (Exception e) {
            result.put("success", false);
            result.put("message", "媒体控制失败: " + e.getMessage());
            result.put("error", "MEDIA_CONTROL_ERROR");
        }
        
        return result;
    }
    
    /**
     * 执行导航控制
     */
    private Map<String, Object> executeNavigation(Map<String, Object> parameters) {
        log.info("执行导航控制: {}", parameters);
        
        Map<String, Object> result = new HashMap<>();
        
        try {
            String destination = (String) parameters.get("destination");
            Boolean isHome = (Boolean) parameters.get("is_home");
            Boolean isWork = (Boolean) parameters.get("is_work");
            Boolean searchNearby = (Boolean) parameters.get("search_nearby");
            String poiType = (String) parameters.get("poi_type");
            
            StringBuilder message = new StringBuilder();
            
            if (isHome != null && isHome) {
                message.append("正在规划回家路线，预计用时25分钟。");
            } else if (isWork != null && isWork) {
                message.append("正在规划去公司的路线，预计用时35分钟。");
            } else if (searchNearby != null && searchNearby) {
                String poiText = switch (poiType) {
                    case "gas_station" -> "加油站";
                    case "restaurant" -> "餐厅";
                    case "hotel" -> "酒店";
                    default -> "地点";
                };
                message.append(String.format("正在搜索附近的%s，找到3个结果。", poiText));
            } else if (destination != null) {
                message.append(String.format("正在规划去%s的路线，开始导航。", destination));
            } else {
                message.append("导航功能已启动");
            }
            
            result.put("success", true);
            result.put("message", message.toString());
            result.put("action", "navigation");
            result.put("parameters_applied", parameters);
            
            // 模拟执行延迟
            Thread.sleep(800);
            
        } catch (Exception e) {
            result.put("success", false);
            result.put("message", "导航控制失败: " + e.getMessage());
            result.put("error", "NAVIGATION_ERROR");
        }
        
        return result;
    }
    
    /**
     * 执行车窗控制
     */
    private Map<String, Object> executeWindowControl(Map<String, Object> parameters) {
        log.info("执行车窗控制: {}", parameters);
        
        Map<String, Object> result = new HashMap<>();
        
        try {
            String action = (String) parameters.get("action");
            String windowPosition = (String) parameters.get("window_position");
            String degree = (String) parameters.get("degree");
            
            String actionText = "open".equals(action) ? "打开" : "关闭";
            String positionText = getWindowPositionText(windowPosition);
            String degreeText = getDegreeText(degree);
            
            String message = String.format("%s%s%s。", positionText, actionText, degreeText);
            
            result.put("success", true);
            result.put("message", message);
            result.put("action", "window_control");
            result.put("parameters_applied", parameters);
            
            // 模拟执行延迟
            Thread.sleep(400);
            
        } catch (Exception e) {
            result.put("success", false);
            result.put("message", "车窗控制失败: " + e.getMessage());
            result.put("error", "WINDOW_CONTROL_ERROR");
        }
        
        return result;
    }
    
    /**
     * 获取车窗位置文本
     */
    private String getWindowPositionText(String position) {
        if (position == null) {
            return "车窗";
        }
        
        return switch (position) {
            case "all" -> "所有车窗";
            case "左窗" -> "左侧车窗";
            case "右窗" -> "右侧车窗";
            case "前窗" -> "前车窗";
            case "后窗" -> "后车窗";
            case "天窗" -> "天窗";
            case "驾驶座" -> "驾驶座车窗";
            case "副驾驶" -> "副驾驶车窗";
            default -> position;
        };
    }
    
    /**
     * 获取开窗程度文本
     */
    private String getDegreeText(String degree) {
        if (degree == null) {
            return "";
        }
        
        return switch (degree) {
            case "slightly" -> "一点";
            case "half" -> "一半";
            case "fully" -> "全部";
            default -> degree;
        };
    }
    
    /**
     * 检查工具服务健康状态
     */
    public boolean checkHealth() {
        // 工具服务总是健康的（模拟）
        return true;
    }
    
    /**
     * 获取工具信息
     */
    public Map<String, Object> getToolsInfo() {
        Map<String, Object> toolsInfo = new HashMap<>();
        
        Map<String, Object> climateTool = new HashMap<>();
        climateTool.put("name", "climate_control");
        climateTool.put("description", "空调控制工具");
        climateTool.put("parameters", new String[]{"temperature", "mode", "fan_speed"});
        
        Map<String, Object> mediaTool = new HashMap<>();
        mediaTool.put("name", "media_control");
        mediaTool.put("description", "媒体控制工具");
        mediaTool.put("parameters", new String[]{"action", "volume", "volume_action", "artist"});
        
        Map<String, Object> navigationTool = new HashMap<>();
        navigationTool.put("name", "navigation");
        navigationTool.put("description", "导航工具");
        navigationTool.put("parameters", new String[]{"destination", "is_home", "is_work", "search_nearby", "poi_type"});
        
        Map<String, Object> windowTool = new HashMap<>();
        windowTool.put("name", "window_control");
        windowTool.put("description", "车窗控制工具");
        windowTool.put("parameters", new String[]{"action", "window_position", "degree"});
        
        toolsInfo.put("available_tools", new String[]{"climate_control", "media_control", "navigation", "window_control"});
        toolsInfo.put("climate_control", climateTool);
        toolsInfo.put("media_control", mediaTool);
        toolsInfo.put("navigation", navigationTool);
        toolsInfo.put("window_control", windowTool);
        toolsInfo.put("timestamp", java.time.LocalDateTime.now().toString());
        
        return toolsInfo;
    }
}
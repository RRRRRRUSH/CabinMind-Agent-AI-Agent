package com.smartcabin.service;

import com.smartcabin.model.AgentRequest;
import com.smartcabin.model.AgentResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

/**
 * Agent核心服务
 * 负责协调意图识别和工具调用
 */
@Slf4j
@Service
public class AgentService {
    
    private final PythonBridgeService pythonBridgeService;
    private final ToolService toolService;
    
    @Autowired
    public AgentService(PythonBridgeService pythonBridgeService, ToolService toolService) {
        this.pythonBridgeService = pythonBridgeService;
        this.toolService = toolService;
    }
    
    /**
     * 处理Agent请求
     */
    public AgentResponse processRequest(AgentRequest request) {
        log.info("处理Agent请求: sessionId={}, message={}", 
                 request.getSessionId(), request.getMessage());
        
        try {
            // 1. 调用Python服务进行意图识别和消息处理
            Map<String, Object> pythonResult = pythonBridgeService.processMessage(
                request.getMessage(),
                request.getSessionId(),
                request.getContext()
            );
            
            // 2. 检查Python服务返回的结果
            if (!Boolean.TRUE.equals(pythonResult.get("success"))) {
                log.warn("Python服务识别失败: {}", pythonResult.get("error"));
                return AgentResponse.error(
                    "意图识别失败: " + pythonResult.get("error"),
                    request.getSessionId()
                );
            }
            
            // 3. 提取识别结果
            String intent = (String) pythonResult.get("intent");
            Double confidence = pythonResult.get("confidence") instanceof Number ? 
                               ((Number) pythonResult.get("confidence")).doubleValue() : 0.0;
            Map<String, Object> parameters = (Map<String, Object>) pythonResult.get("parameters");
            String responseMessage = (String) pythonResult.get("response");
            
            // 4. 根据意图执行相应的工具
            if (confidence >= 0.5) { // 置信度阈值
                try {
                    // 执行工具调用
                    Map<String, Object> toolResult = toolService.executeTool(intent, parameters);
                    
                    // 如果工具执行成功，可以更新响应消息
                    if (Boolean.TRUE.equals(toolResult.get("success"))) {
                        String toolResponse = (String) toolResult.get("message");
                        if (toolResponse != null && !toolResponse.isEmpty()) {
                            responseMessage = toolResponse;
                        }
                    }
                    
                    // 将工具执行结果添加到详细信息中
                    if (request.isVerbose()) {
                        Map<String, Object> details = new HashMap<>();
                        details.put("tool_execution", toolResult);
                        details.put("python_recognition", pythonResult);
                        
                        return AgentResponse.success(intent, confidence, parameters, responseMessage, request.getSessionId())
                                .withDetails(details);
                    }
                    
                } catch (Exception e) {
                    log.error("工具执行失败: {}", e.getMessage(), e);
                    // 工具执行失败，但意图识别成功，仍然返回识别结果
                    responseMessage = "识别到意图但执行失败: " + e.getMessage();
                }
            } else {
                log.warn("意图识别置信度过低: intent={}, confidence={}", intent, confidence);
                responseMessage = "识别置信度过低，请重新表述您的需求。";
            }
            
            // 5. 构建响应
            AgentResponse response = AgentResponse.success(
                intent, confidence, parameters, responseMessage, request.getSessionId()
            );
            
            // 6. 如果启用详细模式，添加详细信息
            if (request.isVerbose()) {
                Map<String, Object> details = new HashMap<>();
                details.put("python_recognition", pythonResult);
                response.withDetails(details);
            }
            
            log.info("Agent处理完成: intent={}, confidence={:.2f}", intent, confidence);
            return response;
            
        } catch (Exception e) {
            log.error("Agent处理失败: {}", e.getMessage(), e);
            return AgentResponse.error(
                "处理请求时发生错误: " + e.getMessage(),
                request.getSessionId()
            );
        }
    }
    
    /**
     * 仅进行意图识别（不执行工具）
     */
    public AgentResponse recognizeIntent(AgentRequest request) {
        log.info("进行意图识别: sessionId={}, message={}", 
                 request.getSessionId(), request.getMessage());
        
        try {
            // 调用Python服务进行意图识别
            Map<String, Object> pythonResult = pythonBridgeService.recognizeIntent(
                request.getMessage(),
                request.getSessionId(),
                request.getContext()
            );
            
            // 提取识别结果
            String intent = (String) pythonResult.get("intent");
            Double confidence = pythonResult.get("confidence") instanceof Number ? 
                               ((Number) pythonResult.get("confidence")).doubleValue() : 0.0;
            Map<String, Object> parameters = (Map<String, Object>) pythonResult.get("parameters");
            
            // 构建响应消息
            String responseMessage = String.format("识别到意图: %s (置信度: %.2f)", intent, confidence);
            
            // 构建响应
            AgentResponse response = AgentResponse.success(
                intent, confidence, parameters, responseMessage, request.getSessionId()
            );
            
            // 如果启用详细模式，添加详细信息
            if (request.isVerbose()) {
                Map<String, Object> details = new HashMap<>();
                details.put("python_recognition", pythonResult);
                response.withDetails(details);
            }
            
            log.info("意图识别完成: intent={}, confidence={:.2f}", intent, confidence);
            return response;
            
        } catch (Exception e) {
            log.error("意图识别失败: {}", e.getMessage(), e);
            return AgentResponse.error(
                "意图识别失败: " + e.getMessage(),
                request.getSessionId()
            );
        }
    }
    
    /**
     * 检查系统健康状态
     */
    public Map<String, Object> checkSystemHealth() {
        Map<String, Object> healthStatus = new HashMap<>();
        
        // 检查Python服务
        boolean pythonHealthy = pythonBridgeService.checkHealth();
        healthStatus.put("python_service", pythonHealthy);
        
        // 检查工具服务
        boolean toolsHealthy = toolService.checkHealth();
        healthStatus.put("tool_service", toolsHealthy);
        
        // 总体状态
        boolean overallHealthy = pythonHealthy && toolsHealthy;
        healthStatus.put("overall", overallHealthy);
        healthStatus.put("timestamp", java.time.LocalDateTime.now().toString());
        
        log.info("系统健康检查: python={}, tools={}, overall={}", 
                 pythonHealthy, toolsHealthy, overallHealthy);
        
        return healthStatus;
    }
    
    /**
     * 获取系统信息
     */
    public Map<String, Object> getSystemInfo() {
        Map<String, Object> systemInfo = new HashMap<>();
        
        // 获取Python服务信息
        Map<String, Object> pythonInfo = pythonBridgeService.getServiceInfo();
        systemInfo.put("python_service", pythonInfo);
        
        // 获取工具信息
        Map<String, Object> toolsInfo = toolService.getToolsInfo();
        systemInfo.put("tools", toolsInfo);
        
        // 添加系统元数据
        systemInfo.put("system_name", "Smart Cabin AI Agent");
        systemInfo.put("version", "1.0.0");
        systemInfo.put("timestamp", java.time.LocalDateTime.now().toString());
        
        return systemInfo;
    }
}
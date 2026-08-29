package com.smartcabin.model;

import lombok.Data;
import java.time.LocalDateTime;
import java.util.Map;

/**
 * Agent响应DTO
 */
@Data
public class AgentResponse {
    
    /**
     * 是否成功
     */
    private boolean success;
    
    /**
     * 识别到的意图
     */
    private String intent;
    
    /**
     * 置信度 (0.0-1.0)
     */
    private double confidence;
    
    /**
     * 提取的参数
     */
    private Map<String, Object> parameters;
    
    /**
     * 响应消息
     */
    private String response;
    
    /**
     * 会话ID
     */
    private String sessionId;
    
    /**
     * 时间戳
     */
    private LocalDateTime timestamp;
    
    /**
     * 详细信息（verbose模式时包含）
     */
    private Map<String, Object> details;
    
    /**
     * 错误信息（失败时包含）
     */
    private String error;
    
    /**
     * 构造成功响应
     */
    public static AgentResponse success(String intent, double confidence, 
                                       Map<String, Object> parameters, 
                                       String response, String sessionId) {
        AgentResponse res = new AgentResponse();
        res.setSuccess(true);
        res.setIntent(intent);
        res.setConfidence(confidence);
        res.setParameters(parameters);
        res.setResponse(response);
        res.setSessionId(sessionId);
        res.setTimestamp(LocalDateTime.now());
        return res;
    }
    
    /**
     * 构造失败响应
     */
    public static AgentResponse error(String error, String sessionId) {
        AgentResponse res = new AgentResponse();
        res.setSuccess(false);
        res.setError(error);
        res.setSessionId(sessionId);
        res.setTimestamp(LocalDateTime.now());
        return res;
    }
    
    /**
     * 添加详细信息
     */
    public AgentResponse withDetails(Map<String, Object> details) {
        this.details = details;
        return this;
    }
}
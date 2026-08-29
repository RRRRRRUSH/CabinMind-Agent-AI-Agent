package com.smartcabin.model;

import lombok.Data;
import jakarta.validation.constraints.NotBlank;
import java.util.List;

/**
 * Agent请求DTO
 */
@Data
public class AgentRequest {
    
    /**
     * 用户消息
     */
    @NotBlank(message = "消息不能为空")
    private String message;
    
    /**
     * 会话ID
     */
    private String sessionId = "default";
    
    /**
     * 上下文消息列表
     */
    private List<String> context;
    
    /**
     * 是否启用详细输出
     */
    private boolean verbose = false;
}
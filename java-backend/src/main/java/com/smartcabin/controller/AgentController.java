package com.smartcabin.controller;

import com.smartcabin.model.AgentRequest;
import com.smartcabin.model.AgentResponse;
import com.smartcabin.service.AgentService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import jakarta.validation.Valid;
import java.util.Map;

/**
 * Agent REST控制器
 * 提供智能座舱AI Agent的API接口
 */
@Slf4j
@RestController
@RequestMapping("/api/agent")
@Tag(name = "智能座舱AI Agent", description = "智能座舱AI Agent API接口")
@Validated
public class AgentController {
    
    private final AgentService agentService;
    
    @Autowired
    public AgentController(AgentService agentService) {
        this.agentService = agentService;
    }
    
    /**
     * 处理Agent请求（完整流程：意图识别 + 工具调用）
     */
    @PostMapping("/process")
    @Operation(summary = "处理Agent请求", description = "完整的Agent处理流程，包括意图识别和工具调用")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "处理成功"),
        @ApiResponse(responseCode = "400", description = "请求参数错误"),
        @ApiResponse(responseCode = "500", description = "服务器内部错误")
    })
    public ResponseEntity<AgentResponse> processRequest(
            @Parameter(description = "Agent请求参数", required = true)
            @Valid @RequestBody AgentRequest request) {
        
        log.info("收到Agent处理请求: sessionId={}, message={}", 
                 request.getSessionId(), request.getMessage());
        
        AgentResponse response = agentService.processRequest(request);
        
        if (response.isSuccess()) {
            log.info("Agent处理成功: intent={}, confidence={:.2f}", 
                     response.getIntent(), response.getConfidence());
            return ResponseEntity.ok(response);
        } else {
            log.warn("Agent处理失败: error={}", response.getError());
            return ResponseEntity.ok(response); // 仍然返回200，但success=false
        }
    }
    
    /**
     * 仅进行意图识别
     */
    @PostMapping("/recognize")
    @Operation(summary = "意图识别", description = "仅进行意图识别，不执行工具调用")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "识别成功"),
        @ApiResponse(responseCode = "400", description = "请求参数错误"),
        @ApiResponse(responseCode = "500", description = "服务器内部错误")
    })
    public ResponseEntity<AgentResponse> recognizeIntent(
            @Parameter(description = "Agent请求参数", required = true)
            @Valid @RequestBody AgentRequest request) {
        
        log.info("收到意图识别请求: sessionId={}, message={}", 
                 request.getSessionId(), request.getMessage());
        
        AgentResponse response = agentService.recognizeIntent(request);
        
        if (response.isSuccess()) {
            log.info("意图识别成功: intent={}, confidence={:.2f}", 
                     response.getIntent(), response.getConfidence());
            return ResponseEntity.ok(response);
        } else {
            log.warn("意图识别失败: error={}", response.getError());
            return ResponseEntity.ok(response); // 仍然返回200，但success=false
        }
    }
    
    /**
     * 健康检查端点
     */
    @GetMapping("/health")
    @Operation(summary = "健康检查", description = "检查系统健康状态")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "系统健康"),
        @ApiResponse(responseCode = "503", description = "系统不健康")
    })
    public ResponseEntity<Map<String, Object>> healthCheck() {
        log.info("收到健康检查请求");
        
        Map<String, Object> healthStatus = agentService.checkSystemHealth();
        boolean overallHealthy = (Boolean) healthStatus.get("overall");
        
        if (overallHealthy) {
            log.info("系统健康检查通过");
            return ResponseEntity.ok(healthStatus);
        } else {
            log.warn("系统健康检查失败: {}", healthStatus);
            return ResponseEntity.status(503).body(healthStatus);
        }
    }
    
    /**
     * 系统信息端点
     */
    @GetMapping("/info")
    @Operation(summary = "系统信息", description = "获取系统信息和配置")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "获取成功")
    })
    public ResponseEntity<Map<String, Object>> getSystemInfo() {
        log.info("收到系统信息请求");
        
        Map<String, Object> systemInfo = agentService.getSystemInfo();
        return ResponseEntity.ok(systemInfo);
    }
    
    /**
     * 简单健康检查（用于前端）
     */
    @GetMapping("/health/simple")
    @Operation(summary = "简单健康检查", description = "简单的健康检查，返回状态字符串")
    public ResponseEntity<String> simpleHealthCheck() {
        return ResponseEntity.ok("OK");
    }
    
    /**
     * 全局异常处理
     */
    @ExceptionHandler(Exception.class)
    public ResponseEntity<AgentResponse> handleException(Exception e) {
        log.error("处理请求时发生异常: {}", e.getMessage(), e);
        
        AgentResponse errorResponse = AgentResponse.error(
            "处理请求时发生错误: " + e.getMessage(),
            "error-session"
        );
        
        return ResponseEntity.ok(errorResponse);
    }
}
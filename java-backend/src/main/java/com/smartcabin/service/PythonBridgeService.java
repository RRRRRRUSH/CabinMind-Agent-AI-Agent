package com.smartcabin.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.client.RestClientException;

import java.util.HashMap;
import java.util.Map;

/**
 * Python AI服务桥接服务
 * 负责与Python Flask服务通信
 */
@Slf4j
@Service
public class PythonBridgeService {
    
    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;
    
    @Value("${app.python.service.url:http://localhost:5000}")
    private String pythonServiceUrl;
    
    @Value("${app.python.service.timeout:10000}")
    private int timeout;
    
    public PythonBridgeService() {
        this.restTemplate = new RestTemplate();
        this.objectMapper = new ObjectMapper();
    }
    
    /**
     * 调用Python服务进行意图识别
     */
    public Map<String, Object> recognizeIntent(String message, String sessionId, java.util.List<String> context) {
        String url = pythonServiceUrl + "/api/intent/recognize";
        
        try {
            // 构建请求体
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("message", message);
            requestBody.put("sessionId", sessionId);
            if (context != null && !context.isEmpty()) {
                requestBody.put("context", context);
            }
            
            // 设置请求头
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<Map<String, Object>> requestEntity = new HttpEntity<>(requestBody, headers);
            
            log.info("调用Python意图识别服务: {}", url);
            log.debug("请求数据: {}", requestBody);
            
            // 发送请求
            ResponseEntity<Map> response = restTemplate.exchange(
                url, 
                HttpMethod.POST, 
                requestEntity, 
                Map.class
            );
            
            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                Map<String, Object> result = response.getBody();
                log.info("Python服务响应成功: intent={}, confidence={}", 
                         result.get("intent"), result.get("confidence"));
                return result;
            } else {
                log.error("Python服务返回错误状态: {}", response.getStatusCode());
                throw new RuntimeException("Python服务返回错误状态: " + response.getStatusCode());
            }
            
        } catch (RestClientException e) {
            log.error("调用Python服务失败: {}", e.getMessage(), e);
            throw new RuntimeException("Python服务调用失败: " + e.getMessage(), e);
        }
    }
    
    /**
     * 调用Python服务进行完整消息处理
     */
    public Map<String, Object> processMessage(String message, String sessionId, java.util.List<String> context) {
        String url = pythonServiceUrl + "/api/message/process";
        
        try {
            // 构建请求体
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("message", message);
            requestBody.put("sessionId", sessionId);
            if (context != null && !context.isEmpty()) {
                requestBody.put("context", context);
            }
            
            // 设置请求头
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<Map<String, Object>> requestEntity = new HttpEntity<>(requestBody, headers);
            
            log.info("调用Python消息处理服务: {}", url);
            log.debug("请求数据: {}", requestBody);
            
            // 发送请求
            ResponseEntity<Map> response = restTemplate.exchange(
                url, 
                HttpMethod.POST, 
                requestEntity, 
                Map.class
            );
            
            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                Map<String, Object> result = response.getBody();
                log.info("Python消息处理成功: success={}, intent={}", 
                         result.get("success"), result.get("intent"));
                return result;
            } else {
                log.error("Python消息处理服务返回错误状态: {}", response.getStatusCode());
                throw new RuntimeException("Python消息处理服务返回错误状态: " + response.getStatusCode());
            }
            
        } catch (RestClientException e) {
            log.error("调用Python消息处理服务失败: {}", e.getMessage(), e);
            throw new RuntimeException("Python消息处理服务调用失败: " + e.getMessage(), e);
        }
    }
    
    /**
     * 检查Python服务健康状态
     */
    public boolean checkHealth() {
        String url = pythonServiceUrl + "/health";
        
        try {
            ResponseEntity<Map> response = restTemplate.getForEntity(url, Map.class);
            return response.getStatusCode().is2xxSuccessful();
        } catch (RestClientException e) {
            log.warn("Python服务健康检查失败: {}", e.getMessage());
            return false;
        }
    }
    
    /**
     * 获取Python服务信息
     */
    public Map<String, Object> getServiceInfo() {
        String url = pythonServiceUrl + "/";
        
        try {
            ResponseEntity<Map> response = restTemplate.getForEntity(url, Map.class);
            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                return response.getBody();
            }
        } catch (RestClientException e) {
            log.warn("获取Python服务信息失败: {}", e.getMessage());
        }
        
        return new HashMap<>();
    }
    
    /**
     * 调试端点：显示意图分类详情
     */
    public Map<String, Object> debugClassify(String message) {
        String url = pythonServiceUrl + "/api/debug/classify";
        
        try {
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("message", message);
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<Map<String, Object>> requestEntity = new HttpEntity<>(requestBody, headers);
            
            ResponseEntity<Map> response = restTemplate.exchange(
                url, 
                HttpMethod.POST, 
                requestEntity, 
                Map.class
            );
            
            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                return response.getBody();
            }
        } catch (RestClientException e) {
            log.warn("调试分类失败: {}", e.getMessage());
        }
        
        return new HashMap<>();
    }
}
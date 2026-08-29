package com.smartcabin.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import io.swagger.v3.oas.models.servers.Server;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

/**
 * Swagger/OpenAPI配置
 */
@Configuration
public class SwaggerConfig {
    
    @Bean
    public OpenAPI smartCabinOpenAPI() {
        Server localServer = new Server()
                .url("http://localhost:8080")
                .description("本地开发环境");
        
        Server devServer = new Server()
                .url("http://dev.smartcabin.com")
                .description("开发环境");
        
        Contact contact = new Contact()
                .name("智能座舱开发团队")
                .email("contact@smartcabin.com")
                .url("https://smartcabin.com");
        
        License mitLicense = new License()
                .name("MIT License")
                .url("https://opensource.org/licenses/MIT");
        
        Info info = new Info()
                .title("智能座舱AI Agent API")
                .version("1.0.0")
                .contact(contact)
                .description("""
                    智能座舱AI Agent API文档
                    
                    ## 功能概述
                    - 意图识别：将自然语言指令解析为结构化意图
                    - 工具调用：执行座舱控制操作（空调、媒体、导航、车窗）
                    - 上下文记忆：支持多轮对话上下文
                    - 混合决策：结合DeepSeek API和自定义算法
                    
                    ## 技术栈
                    - 后端：Java Spring Boot 3.1.x
                    - AI服务：Python Flask + DeepSeek API
                    - 前端：HTML/CSS/JavaScript
                    
                    ## 快速开始
                    1. 启动Python AI服务（端口5000）
                    2. 启动Java后端服务（端口8080）
                    3. 访问前端界面进行测试
                    """)
                .termsOfService("https://smartcabin.com/terms")
                .license(mitLicense);
        
        return new OpenAPI()
                .info(info)
                .servers(List.of(localServer, devServer));
    }
}
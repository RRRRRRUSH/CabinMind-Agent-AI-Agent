package com.smartcabin;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cache.annotation.EnableCaching;

/**
 * 智能座舱AI Agent应用主类
 */
@SpringBootApplication
@EnableCaching
public class SmartCabinAgentApplication {

    public static void main(String[] args) {
        SpringApplication.run(SmartCabinAgentApplication.class, args);
        System.out.println("==========================================");
        System.out.println("智能座舱AI Agent服务启动成功!");
        System.out.println("API文档: http://localhost:8080/swagger-ui.html");
        System.out.println("健康检查: http://localhost:8080/actuator/health");
        System.out.println("==========================================");
    }
}
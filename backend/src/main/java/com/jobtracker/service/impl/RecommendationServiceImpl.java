package com.jobtracker.service.impl;

import com.jobtracker.service.RecommendationService;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestOperations;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile; 
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.core.io.ByteArrayResource;

import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.ArrayList;
import java.util.HashMap;
// ...

@Service
public class RecommendationServiceImpl implements RecommendationService {
    // ... existing code ...
    @Value("${ai.service.url:http://localhost:5000}")
    private String aiServiceBaseUrl;
    
    private final RestTemplate restTemplate = new RestTemplate();
    
    private String getAiServiceFileUrl() {
        return aiServiceBaseUrl + "/recommend_file";
    }
    @Override
    public List<Map<String, Object>> getRecommendationsFromFile(MultipartFile resumeFile, String authToken) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);
        // Forward authentication token from frontend to Python service
        headers.set("Authorization", authToken);

        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();

        try {
            // Wrap MultipartFile into a resource that can be sent
            ByteArrayResource fileAsResource = new ByteArrayResource(resumeFile.getBytes()) {
                @Override
                public String getFilename() {
                    return resumeFile.getOriginalFilename();
                }
            };
            body.add("resume_file", fileAsResource);
        } catch (IOException e) {
            throw new RuntimeException("Failed to read file", e);
        }

        HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);

        ResponseEntity<List> response = restTemplate.postForEntity(getAiServiceFileUrl(), requestEntity, List.class);

        if (response.getStatusCode() == HttpStatus.OK) {
            return response.getBody();
        } else {
            throw new RuntimeException("Failed to get recommendations from AI service. Status: " + response.getStatusCode());
        }
    }
}

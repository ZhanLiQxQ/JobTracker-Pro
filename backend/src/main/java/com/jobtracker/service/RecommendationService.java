package com.jobtracker.service;

import org.springframework.web.multipart.MultipartFile;

import java.util.List;
import java.util.Map;

public interface RecommendationService {
    List<Map<String, Object>> getRecommendationsFromFile(MultipartFile resumeFile, String authToken);
}

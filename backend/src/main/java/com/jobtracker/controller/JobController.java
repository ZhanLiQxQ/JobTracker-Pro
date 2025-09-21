package com.jobtracker.controller;

import com.jobtracker.entity.Job;
import com.jobtracker.entity.Users;
import com.jobtracker.service.JobService;
import com.jobtracker.service.RecommendationService;
import com.jobtracker.service.S3Service;
import com.jobtracker.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

import lombok.extern.slf4j.Slf4j;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api/jobs")
@RequiredArgsConstructor // This annotation automatically generates constructor for all final fields
@Slf4j
public class JobController {

    private final JobService jobService;
    private final UserService userService;
    private final RecommendationService recommendationService;
    private final S3Service s3Service;


    // Public access interfaces
    @GetMapping
    public ResponseEntity<List<Job>> getAllJobs(
            @RequestParam(required = false) String title,
            @RequestParam(required = false) String company,
            @RequestParam(required = false) String location) {
        return ResponseEntity.ok(jobService.searchJobs(title, company, location));
    }

    @GetMapping("/{id}")
    public ResponseEntity<Job> getJobById(@PathVariable Long id) {
        return ResponseEntity.ok(jobService.getJobById(id));
    }

    // Authentication required interfaces - user favorites
    @GetMapping("/favorites")
    public ResponseEntity<List<Job>> getUserFavorites(Authentication authentication) {
        Users user = userService.getUserFromAuthentication(authentication);
        return ResponseEntity.ok(jobService.getUserFavorites(user));
    }

    @PostMapping("/{jobId}/favorite")
    public ResponseEntity<Void> addToFavorites(
            @PathVariable Long jobId,
            @RequestBody(required = false) String notes,
            Authentication authentication) {
        Users user = userService.getUserFromAuthentication(authentication);
        jobService.addToFavorites(user, jobId, notes);
        return ResponseEntity.ok().build();
    }

    @DeleteMapping("/{jobId}/favorite")
    public ResponseEntity<Void> removeFromFavorites(
            @PathVariable Long jobId,
            Authentication authentication) {
        Users user = userService.getUserFromAuthentication(authentication);
        jobService.removeFromFavorites(user, jobId);
        return ResponseEntity.ok().build();
    }




    // 👇 *** New file upload interface *** 👇
    @PostMapping("/recommend-file")
    public ResponseEntity<?> getRecommendationsFromFile(
            @RequestParam("resume") MultipartFile file,
            @RequestHeader("Authorization") String authToken) {

        if (file.isEmpty()) {
            return ResponseEntity.badRequest().body("Please select a file to upload.");
        }

        try {
            List<Map<String, Object>> recommendedJobs = recommendationService.getRecommendationsFromFile(file, authToken);
            return ResponseEntity.ok(recommendedJobs);
        } catch (Exception e) {
            return ResponseEntity.status(500).body("Error getting recommendations: " + e.getMessage());
        }
    }

    // 👇 *** S3 file upload interface *** 👇
    @PostMapping("/upload-resume")
    public ResponseEntity<?> uploadResume(
            @RequestParam("resume") MultipartFile file,
            Authentication authentication) {
        
        if (file.isEmpty()) {
            return ResponseEntity.badRequest().body("Please select a file to upload.");
        }
        
        // Check file type
        String contentType = file.getContentType();
        if (contentType == null || (!contentType.equals("application/pdf") && !contentType.equals("application/vnd.openxmlformats-officedocument.wordprocessingml.document"))) {
            return ResponseEntity.badRequest().body("Only PDF and DOCX files are allowed.");
        }
        
        try {
            // Get current user
            String username = authentication.getName();
            Users user = userService.findByUsername(username);
            
            // Upload to S3
            String s3Key = s3Service.uploadResume(file, user.getId());
            
            // Return S3 object key and presigned URL
            String presignedUrl = s3Service.getPresignedUrl(s3Key);
            
            return ResponseEntity.ok(Map.of(
                "message", "File uploaded successfully",
                "s3Key", s3Key,
                "downloadUrl", presignedUrl
            ));
            
        } catch (Exception e) {
            log.error("Error uploading file: ", e);
            return ResponseEntity.status(500).body("Error uploading file: " + e.getMessage());
        }
    }
    
    // 👇 *** Get resume download link *** 👇
    @GetMapping("/resume/{s3Key}")
    public ResponseEntity<?> getResumeDownloadUrl(@PathVariable String s3Key, Authentication authentication) {
        try {
            // Verify user permissions (more complex permission checks can be added here)
            String username = authentication.getName();
            Users user = userService.findByUsername(username);
            
            // Check if file exists
            if (!s3Service.fileExists(s3Key)) {
                return ResponseEntity.notFound().build();
            }
            
            // Generate presigned URL
            String presignedUrl = s3Service.getPresignedUrl(s3Key);
            
            return ResponseEntity.ok(Map.of(
                "downloadUrl", presignedUrl
            ));
            
        } catch (Exception e) {
            log.error("Error getting download URL: ", e);
            return ResponseEntity.status(500).body("Error getting download URL: " + e.getMessage());
        }
    }
}
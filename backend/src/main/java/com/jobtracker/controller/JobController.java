package com.jobtracker.controller;

import com.jobtracker.entity.Job;
import com.jobtracker.entity.Users;
import com.jobtracker.service.JobService;
import com.jobtracker.service.RecommendationService;
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


    // Public access interfaces
    @GetMapping
    public ResponseEntity<List<Job>> getAllJobs(
            @RequestParam(required = false) String query,
            Authentication authentication) { // Inject Authentication for future extension

        List<Job> jobs;

        // 1. Routing logic: if there's a search term, use hybrid search, otherwise use normal list
        if (query != null && !query.trim().isEmpty()) {
            // Call the searchHybridJobs method we added in the Service interface
            jobs = jobService.searchHybridJobs(query);
        } else {
            jobs = jobService.getAllPublicJobs();
        }
        System.out.println("Deploy Test v1");

        // (Optional optimization) If you want to handle isFavorite in the backend, you can call jobService.attachFavorites(jobs, user) here
        // But to match your existing frontend logic (frontend sends second request to check favorites), just return jobs directly here

        return ResponseEntity.ok(jobs);
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




    // New file upload interface
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

}
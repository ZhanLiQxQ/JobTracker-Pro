package com.jobtracker.controller;
import com.jobtracker.entity.Job;
import com.jobtracker.service.JobService;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/internal") // All internal interfaces start with /api/internal
public class InternalController {

    private final JobService jobService;

    @Value("${app.internal-api-key}") // Inject API Key from configuration file
    private String internalApiKey;

    public InternalController(JobService jobService) {
        this.jobService = jobService;
    }

    /**
     * Internal interface: Get all job information (for AI service use)
     */
    @GetMapping("/jobs")
    public ResponseEntity<?> getAllJobsForInternalService(@RequestHeader("X-Internal-API-Key") String apiKey) {
        if (!isApiKeyValid(apiKey)) {
            return unauthorizedResponse();
        }
        return ResponseEntity.ok(jobService.getAllPublicJobs());
    }

    /**
     * Internal interface: Batch receive job data scraped by crawler
     */
    @PostMapping("/jobs/batch-intake")
    public ResponseEntity<?> createJobsFromScraper(
            @RequestBody List<Job> jobs,
            @RequestHeader("X-Internal-API-Key") String apiKey) {

        if (!isApiKeyValid(apiKey)) {
            return unauthorizedResponse();
        }

        if (jobs == null || jobs.isEmpty()) {
            return ResponseEntity.badRequest().body("Job list cannot be empty");
        }

        try {
            List<Job> savedJobs = jobService.createJobsBatch(jobs);
            return ResponseEntity.ok(Map.of(
                "message", "Successfully batch saved jobs",
                "count", savedJobs.size(),
                "jobs", savedJobs
            ));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(Map.of("error", "Failed to batch save jobs: " + e.getMessage()));
        }
    }

    // Helper method to validate API Key
    private boolean isApiKeyValid(String apiKey) {
        return internalApiKey.equals(apiKey);
    }

    // Helper method to return unauthorized response
    private ResponseEntity<String> unauthorizedResponse() {
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("Invalid or missing API Key");
    }
}

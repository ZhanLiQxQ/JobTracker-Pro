// src/main/java/com/jobtracker/controller/AdminController.java
package com.jobtracker.controller;

import com.jobtracker.entity.Job;
import com.jobtracker.entity.Users;
import com.jobtracker.service.JobService;
import com.jobtracker.service.UserService; // Assuming you have a UserService
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/admin") // All interfaces start with /api/admin
@RequiredArgsConstructor // This annotation automatically generates constructor for all final fields
public class AdminController {

    private final JobService jobService;

    /**
     * Get all user data
     * This interface will be intercepted by SecurityConfig because the path is /api/admin/users
     * Only users with ADMIN role can successfully call it
     */
    // Admin interfaces
    @PutMapping("job/{id}")
    public ResponseEntity<Job> updateJob(@PathVariable Long id, @RequestBody Job job) {
        return ResponseEntity.ok(jobService.updateJob(id, job));
    }

    @DeleteMapping("job/{id}")
    public ResponseEntity<Void> deleteJob(@PathVariable Long id) {
        jobService.deleteJob(id);
        return ResponseEntity.ok().build();
    }

    // You can add more admin-specific features here, such as deleting users, viewing system logs, etc.
}
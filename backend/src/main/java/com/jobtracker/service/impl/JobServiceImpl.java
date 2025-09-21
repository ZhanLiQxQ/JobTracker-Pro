package com.jobtracker.service.impl;

import com.jobtracker.entity.Job;
import com.jobtracker.entity.Users;
import com.jobtracker.entity.UserFavorite;
import com.jobtracker.repository.JobRepository;
import com.jobtracker.repository.UserFavoriteRepository;
import com.jobtracker.service.JobService;
import lombok.RequiredArgsConstructor;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.annotation.Propagation;

import java.util.List;
import java.util.ArrayList;
import java.util.Optional;

@Service
@RequiredArgsConstructor
@Transactional
public class JobServiceImpl implements JobService {

    private final JobRepository jobRepository;
    private final UserFavoriteRepository userFavoriteRepository;

    @Override
    @Cacheable(value = "jobs", key = "'all'")
    public List<Job> getAllPublicJobs() {
        return jobRepository.findAll();
    }


    @Override
    @Cacheable(value = "jobs", key = "T(String).format('search:%s:%s:%s', #title != null ? #title : 'null', #company != null ? #company : 'null', #location != null ? #location : 'null')")
    public List<Job> searchJobs(String title, String company, String location) {
        // If no search parameters, return all jobs directly (using all cache)
        if ((title == null || title.trim().isEmpty()) && 
            (company == null || company.trim().isEmpty()) && 
            (location == null || location.trim().isEmpty())) {
            return getAllPublicJobs();
        }
        return jobRepository.searchJobs(title, company, location);
    }

    @Override
    @Cacheable(value = "jobs", key = "'job:' + #id")
    public Job getJobById(Long id) {
        return jobRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Job not found"));
    }

    @Override
    public List<Job> getUserFavorites(Users user) {
        List<UserFavorite> favorites = userFavoriteRepository.findByUserWithJob(user);
        return favorites.stream()
                .map(UserFavorite::getJob)
                .toList();
    }

    @Override
    public void addToFavorites(Users user, Long jobId, String notes) {
        Job job = getJobById(jobId);
        if (!userFavoriteRepository.existsByUserAndJob(user, job)) {
            UserFavorite favorite = new UserFavorite();
            favorite.setUser(user);
            favorite.setJob(job);
            favorite.setNotes(notes);
            userFavoriteRepository.save(favorite);
        }
    }

    @Override
    public void removeFromFavorites(Users user, Long jobId) {
        Job job = getJobById(jobId);
        userFavoriteRepository.deleteByUserAndJob(user, job);
    }

    @Override
    @Transactional(propagation = Propagation.REQUIRED, rollbackFor = Exception.class)
    @CacheEvict(value = "jobs", allEntries = true)  // Clear all jobs cache
    public Job createJob(Job job) {
        // Validate URL is not empty
        if (job.getUrl() == null || job.getUrl().trim().isEmpty()) {
            throw new IllegalArgumentException("Job URL cannot be empty");
        }
        
        // Check if same job already exists (based on URL)
        Optional<Job> existingJob = jobRepository.findByUrl(job.getUrl());
        if (existingJob.isPresent()) {
            throw new IllegalArgumentException("Job URL already exists: " + job.getUrl());
        }
        
        return jobRepository.save(job);
    }

    @Override
    @Transactional(propagation = Propagation.REQUIRED, rollbackFor = Exception.class)
    @CacheEvict(value = "jobs", allEntries = true)  // Clear all jobs cache
    public List<Job> createJobsBatch(List<Job> jobs) {
        if (jobs == null || jobs.isEmpty()) {
            return List.of();
        }
        
        List<Job> savedJobs = new ArrayList<>();
        List<Job> skippedJobs = new ArrayList<>();
        
        System.out.println("Starting batch save of " + jobs.size() + " jobs...");
        
        for (Job job : jobs) {
            try {
                // Validate URL is not empty
                if (job.getUrl() == null || job.getUrl().trim().isEmpty()) {
                    System.err.println("Skipping invalid job (URL is empty): " + job.getTitle() + " - " + job.getCompany());
                    skippedJobs.add(job);
                    continue;
                }
                
                // Check if same job already exists (based on URL)
                Optional<Job> existingJob = jobRepository.findByUrl(job.getUrl());
                
                if (existingJob.isPresent()) {
                    // If exists, skip duplicate job
                    skippedJobs.add(job);
                    System.out.println("Skipping duplicate job (URL already exists): " + job.getTitle() + " - " + job.getCompany() + " | URL: " + job.getUrl());
                } else {
                    // If not exists, save new job
                    Job savedJob = jobRepository.save(job);
                    savedJobs.add(savedJob);
                    System.out.println("Successfully saved job: " + job.getTitle() + " - " + job.getCompany());
                }
            } catch (Exception e) {
                System.err.println("Error saving job: " + job.getTitle() + " - " + job.getCompany() + ", error: " + e.getMessage());
                // In transaction, single job error does not affect other jobs saving
                skippedJobs.add(job);
            }
        }
        
        System.out.println("Batch save completed - Success: " + savedJobs.size() + ", Skipped: " + skippedJobs.size());
        return savedJobs;
    }

    @Override
    @CacheEvict(value = "jobs", allEntries = true)  // Clear all jobs cache
    public Job updateJob(Long id, Job job) {
        Job existingJob = getJobById(id);
        job.setId(id);
        return jobRepository.save(job);
    }

    @Override
    @CacheEvict(value = "jobs", allEntries = true)  // Clear all jobs cache
    public void deleteJob(Long id) {
        Job job = getJobById(id);
        jobRepository.delete(job);
    }
}
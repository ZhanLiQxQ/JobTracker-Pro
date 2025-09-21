package com.jobtracker.service;
import com.jobtracker.entity.Job;
import com.jobtracker.entity.Users;
import com.jobtracker.entity.UserFavorite;

import java.util.List;

public interface JobService {
    // Public access methods
    List<Job> getAllPublicJobs();
    List<Job> searchJobs(String title, String company, String location);
    Job getJobById(Long id);

    // Authentication required methods
    List<Job> getUserFavorites(Users user);
    void addToFavorites(Users user, Long jobId, String notes);
    void removeFromFavorites(Users user, Long jobId);

    Job createJob(Job job);
    List<Job> createJobsBatch(List<Job> jobs);
    Job updateJob(Long id, Job job);
    void deleteJob(Long id);


}
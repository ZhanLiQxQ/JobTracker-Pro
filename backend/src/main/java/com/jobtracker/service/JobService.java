package com.jobtracker.service;
import com.jobtracker.entity.Job;
import com.jobtracker.entity.Users;
import com.jobtracker.entity.UserFavorite;

import java.util.List;

public interface JobService {
    // 公开访问的方法
    List<Job> getAllPublicJobs();
    List<Job> searchPublicJobsByTitle(String title);
    List<Job> searchJobs(String title, String company, String location);
    Job getJobById(Long id);

    // 需要认证的方法
    List<Job> getUserFavorites(Users user);
    void addToFavorites(Users user, Long jobId, String notes);
    void removeFromFavorites(Users user, Long jobId);
    List<Job> getAllJobsForUser(Users user);
    Job createJob(Job job, Users user);
    Job updateJob(Long id, Job job, Users user);
    void deleteJob(Long id, Users user);
    List<Job> searchJobsByTitle(String title, Users user);
    List<Job> recommendJobs(String query, Users user);
    void fetchAndStoreJobsFromExternalSources(String query);
}
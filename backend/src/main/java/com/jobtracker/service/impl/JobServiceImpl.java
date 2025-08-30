package com.jobtracker.service.impl;

import com.jobtracker.entity.Job;
import com.jobtracker.entity.Users;
import com.jobtracker.entity.UserFavorite;
import com.jobtracker.repository.JobRepository;
import com.jobtracker.repository.UserFavoriteRepository;
import com.jobtracker.service.JobService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
@RequiredArgsConstructor
@Transactional
public class JobServiceImpl implements JobService {

    private final JobRepository jobRepository;
    private final UserFavoriteRepository userFavoriteRepository;

    @Override
    public List<Job> getAllPublicJobs() {
        return jobRepository.findAll();
    }

    @Override
    public List<Job> searchPublicJobsByTitle(String title) {
        return jobRepository.findByTitleContainingIgnoreCase(title);
    }

    @Override
    public List<Job> searchJobs(String title, String company, String location) {
        return jobRepository.searchJobs(title, company, location);
    }

    @Override
    public Job getJobById(Long id) {
        return jobRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Job not found"));
    }

    @Override
    public List<Job> getUserFavorites(Users user) {
        return userFavoriteRepository.findByUser(user)
                .stream()
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
    public Job createJob(Job job) {
        return jobRepository.save(job);
    }

    @Override
    public Job updateJob(Long id, Job job) {
        Job existingJob = getJobById(id);
        job.setId(id);
        return jobRepository.save(job);
    }

    @Override
    public void deleteJob(Long id) {
        Job job = getJobById(id);
        jobRepository.delete(job);
    }

//    @Override
//    public List<Job> searchJobsByTitle(String title, Users user) {
//        return jobRepository.findByTitleContainingIgnoreCaseAndUsers(title, user);
//    }

    @Override
    public List<Job> recommendJobs(String query) {
        // TODO: 实现推荐逻辑
        return List.of();
    }

    @Override
    public void fetchAndStoreJobsFromExternalSources(String query) {
        // TODO: 实现爬虫逻辑
    }
}
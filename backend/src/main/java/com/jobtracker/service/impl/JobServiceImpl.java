package com.jobtracker.service.impl;
import org.springframework.web.client.RestTemplate;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
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
import org.springframework.data.jpa.domain.Specification;
import jakarta.persistence.criteria.Predicate;

import java.util.*;
import java.util.concurrent.CompletableFuture;
import java.util.stream.Collectors;

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

    // 注入 RestTemplate (建议在 Config 类里定义 Bean，或者这里直接 new)
    private final RestTemplate restTemplate = new RestTemplate();

    // Python AI 服务的地址，从配置文件读取，默认 localhost:5001
    @Value("${ai.service.url:http://localhost:5001}")
    private String aiServiceUrl;

    // --- 1. 保持原有的 SQL 搜索作为底层能力 (改为 private 或保留 public 供内部调用) ---
    public List<Job> searchJobsSql(String query) {
        if (query == null || query.trim().isEmpty()) {
            return jobRepository.findAll();
        }
        Specification<Job> spec = (root, cq, cb) -> {
            String searchTerm = "%" + query.toLowerCase().trim() + "%";
            return cb.or(
                    cb.like(cb.lower(root.get("title")), searchTerm),
                    cb.like(cb.lower(root.get("company")), searchTerm),
                    cb.like(cb.lower(root.get("location")), searchTerm)
            );
        };
        return jobRepository.findAll(spec);
    }

    // --- 2. 新增：混合搜索 (面试核心亮点) ---
    @Override
    // 注意：混合搜索通常不建议缓存整个结果，因为涉及 AI 和个性化，或者设置较短的过期时间
    public List<Job> searchHybridJobs(String query) {
        if (query == null || query.trim().isEmpty()) {
            return getAllPublicJobs();
        }

        long start = System.currentTimeMillis();

        // [面试亮点] 异步编排：同时发起 SQL 和 AI 请求

        // 任务 A: SQL 搜索
        CompletableFuture<List<Job>> sqlTask = CompletableFuture.supplyAsync(() -> {
            return searchJobsSql(query);
        }).exceptionally(ex -> {
            System.err.println("SQL Search failed: " + ex.getMessage());
            return Collections.emptyList();
        });

        // 任务 B: AI 语义搜索
        CompletableFuture<List<Long>> aiTask = CompletableFuture.supplyAsync(() -> {
            return fetchJobIdsFromAI(query);
        }).exceptionally(ex -> {
            System.err.println("AI Service failed (Graceful Degradation): " + ex.getMessage());
            return Collections.emptyList(); // [面试亮点] 降级策略：AI 挂了不影响主流程
        });

        // 等待两者完成
        CompletableFuture.allOf(sqlTask, aiTask).join();

        try {
            List<Job> sqlJobs = sqlTask.get();
            List<Long> aiJobIds = aiTask.get();

            // 如果 AI 没结果，直接返回 SQL 结果 (避免计算 RRF)
            if (aiJobIds.isEmpty()) {
                return sqlJobs;
            }

            // [面试亮点] 执行 RRF 融合算法
            List<Job> rankedJobs = applyRRF(sqlJobs, aiJobIds);

            System.out.println("Hybrid Search took: " + (System.currentTimeMillis() - start) + "ms");
            return rankedJobs;

        } catch (Exception e) {
            e.printStackTrace();
            // 兜底：万一合并逻辑出错，返回 SQL 结果
            return searchJobsSql(query);
        }
    }

    // --- 3. 辅助方法：调用 Python AI ---
    private List<Long> fetchJobIdsFromAI(String query) {
        String url = aiServiceUrl + "/rag/search_only";
        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("query", query);
        requestBody.put("k", 20); // 获取前 20 个语义相关

        try {
            // 定义一个简单的内部类来接 Python 的返回值
            ResponseEntity<AISearchResponse> response = restTemplate.postForEntity(
                    url, requestBody, AISearchResponse.class
            );

            if (response.getBody() != null && response.getBody().results != null) {
                return response.getBody().results.stream()
                        .map(r -> r.job_id)
                        .collect(Collectors.toList());
            }
        } catch (Exception e) {
            throw new RuntimeException("Connect to AI Service failed");
        }
        return Collections.emptyList();
    }

    // --- 4. 辅助方法：RRF 算法实现 ---
    private List<Job> applyRRF(List<Job> sqlJobs, List<Long> aiJobIds) {
        Map<Long, Double> scores = new HashMap<>();
        int k = 60; // RRF 常数

        // 计算 SQL 分数
        for (int i = 0; i < sqlJobs.size(); i++) {
            long id = sqlJobs.get(i).getId();
            scores.put(id, scores.getOrDefault(id, 0.0) + (1.0 / (k + i + 1)));
        }

        // 计算 AI 分数
        for (int i = 0; i < aiJobIds.size(); i++) {
            long id = aiJobIds.get(i);
            scores.put(id, scores.getOrDefault(id, 0.0) + (1.0 / (k + i + 1)));
        }

        // 重新拉取所有涉及的 Job (为了获取 AI 搜出来但 SQL 没搜出来的 Job 详情)
        // 这一步可以用 findAllById 优化
        List<Long> allIds = new ArrayList<>(scores.keySet());
        List<Job> allJobs = jobRepository.findAllById(allIds);
        Map<Long, Job> jobMap = allJobs.stream().collect(Collectors.toMap(Job::getId, j -> j));

        // 排序并返回
        return scores.entrySet().stream()
                .sorted(Map.Entry.<Long, Double>comparingByValue().reversed()) // 分数高在前
                .map(entry -> jobMap.get(entry.getKey()))
                .filter(java.util.Objects::nonNull) // 过滤掉数据库里可能不存在的脏数据
                .collect(Collectors.toList());
    }

    // --- DTO: 用来接 Python 返回值 ---
    // 可以放在单独文件，也可以作为内部静态类
    private static class AISearchResponse {
        public List<ResultItem> results;
        public static class ResultItem {
            public Long job_id;
            public Double score;
        }
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
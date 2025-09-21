package com.jobtracker.repository;
import com.jobtracker.entity.Job;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.CrudRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface JobRepository extends JpaRepository<Job, Long> {
    // Search jobs
    List<Job> findByTitleContainingIgnoreCase(String title);
    List<Job> findByCompanyContainingIgnoreCase(String company);
    List<Job> findByLocationContainingIgnoreCase(String location);
    
    // Find duplicate jobs (based on URL)
    Optional<Job> findByUrl(String url);
    
    // Combined search
    @Query("SELECT j FROM Job j WHERE " +
           "(:title IS NULL OR j.title LIKE %:title%) AND " +
           "(:company IS NULL OR j.company LIKE %:company%) AND " +
           "(:location IS NULL OR j.location LIKE %:location%)")
    List<Job> searchJobs(String title, String company, String location);
}
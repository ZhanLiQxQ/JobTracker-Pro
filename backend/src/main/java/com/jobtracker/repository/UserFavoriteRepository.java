 package com.jobtracker.repository;
import com.jobtracker.entity.Users;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface UserFavoriteRepository extends JpaRepository<UserFavorite, Long> {
    List<UserFavorite> findByUser(Users user);
    boolean existsByUserAndJob(Users user, com.jobtracker.entity.Job job);
    void deleteByUserAndJob(Users user, com.jobtracker.entity.Job job);
}
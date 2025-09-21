 package com.jobtracker.entity;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Data
@NoArgsConstructor
@Table(name = "user_favorites")
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})  // Ignore lazy loading related properties
public class UserFavorite {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)  // Changed back to lazy loading, user info not needed
    @JoinColumn(name = "user_id", nullable = false)
    private Users user;

    @ManyToOne(fetch = FetchType.EAGER)  // Keep eager loading, job info needed
    @JoinColumn(name = "job_id", nullable = false)
    private Job job;

    private LocalDateTime favoritedAt = LocalDateTime.now();
    private String notes;
}
package com.jobtracker.entity;

import com.fasterxml.jackson.annotation.JsonIgnore;
import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.ArrayList;
import java.util.List;


@Entity
@Data
@NoArgsConstructor
public class Users {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false)
    private String email;

    @Column(nullable = false)
    private String password;

    private String role = "USER";

//    @OneToMany(mappedBy = "users", cascade = CascadeType.ALL)
//    @JsonIgnore
//    private List<Job> job = new ArrayList<>();

    // 新增简历字段，用于AI匹配
    @Column(columnDefinition = "TEXT")
    private String resume;
}
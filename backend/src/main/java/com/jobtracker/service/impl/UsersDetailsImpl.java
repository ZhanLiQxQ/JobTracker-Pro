package com.jobtracker.service.impl;

import com.jobtracker.entity.Users;
import lombok.AllArgsConstructor;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

import java.util.Collection;
import java.util.Collections;

@AllArgsConstructor
public class UsersDetailsImpl implements UserDetails {
    private final Users user;

    // 新增构造函数（用于JwtAuthFilter直接构建）
    public UsersDetailsImpl(String email, String role) {
        this.user = new Users();
        this.user.setEmail(email);
        this.user.setRole(role);
    }

    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return Collections.singletonList(new SimpleGrantedAuthority("ROLE_" + user.getRole()));
    }

    @Override
    public String getPassword() {
        return user.getPassword();
    }

    @Override
    public String getUsername() {
        return user.getEmail();
    }

    public Long getId() {
        return user.getId();
    }

    // 其他方法保持不变...
}
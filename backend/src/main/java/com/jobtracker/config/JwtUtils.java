package com.jobtracker.config;

import com.jobtracker.service.impl.UsersDetailsImpl;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.util.Date;

// JwtUtils.java
@Component
public class JwtUtils {
    private final SecretKey secretKey; // 注入统一的 SecretKey
    private final int jwtExpirationMs;

    public JwtUtils(@Value("${jwt.expiration}") int jwtExpirationMs, SecretKey secretKey) {
        this.secretKey = secretKey;
        this.jwtExpirationMs = jwtExpirationMs;
    }

    public String generateJwtToken(Authentication authentication) {
        UsersDetailsImpl userPrincipal = (UsersDetailsImpl) authentication.getPrincipal();
        return Jwts.builder()
                .setSubject(userPrincipal.getUsername())
                .setIssuedAt(new Date())
                .setExpiration(new Date(System.currentTimeMillis() + jwtExpirationMs))
                .signWith(secretKey, SignatureAlgorithm.HS512) // 使用 SecretKey
                .compact();
    }
}


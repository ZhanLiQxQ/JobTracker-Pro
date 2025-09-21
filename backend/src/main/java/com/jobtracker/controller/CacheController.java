package com.jobtracker.controller;

import com.jobtracker.util.RedisUtil;
import lombok.RequiredArgsConstructor;
import org.springframework.cache.CacheManager;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/cache")
@RequiredArgsConstructor
public class CacheController {

    private final CacheManager cacheManager;
    private final RedisUtil redisUtil;

    /**
     * Clear all cache
     */
    @DeleteMapping("/clear")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<String> clearAllCache() {
        cacheManager.getCacheNames()
                .forEach(cacheName -> cacheManager.getCache(cacheName).clear());
        redisUtil.clearAll();
        return ResponseEntity.ok("All cache cleared");
    }

    /**
     * Clear specified cache
     */
    @DeleteMapping("/clear/{cacheName}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<String> clearCache(@PathVariable String cacheName) {
        var cache = cacheManager.getCache(cacheName);
        if (cache != null) {
            cache.clear();
            return ResponseEntity.ok("Cache " + cacheName + " cleared");
        }
        return ResponseEntity.notFound().build();
    }

    /**
     * Get cache statistics
     */
    @GetMapping("/stats")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<String> getCacheStats() {
        StringBuilder stats = new StringBuilder();
        stats.append("Cache statistics:\n");
        
        cacheManager.getCacheNames().forEach(cacheName -> {
            var cache = cacheManager.getCache(cacheName);
            if (cache instanceof org.springframework.data.redis.cache.RedisCache) {
                stats.append(cacheName).append(": Redis cache\n");
            } else {
                stats.append(cacheName).append(": Local cache\n");
            }
        });
        
        return ResponseEntity.ok(stats.toString());
    }
}

package com.jobtracker.util;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class RRFCalculator {
    // Industry standard k is usually 60
    private static final int K = 60;

    /**
     * Calculate Reciprocal Rank Fusion score
     * @param sqlIds SQL search result ID list (ordered)
     * @param aiIds AI search result ID list (ordered)
     * @return Map<JobId, Score>
     */
    public static Map<Long, Double> calculateScores(List<Long> sqlIds, List<Long> aiIds) {
        Map<Long, Double> scores = new HashMap<>();

        // 1. Calculate SQL ranking score
        for (int i = 0; i < sqlIds.size(); i++) {
            Long id = sqlIds.get(i);
            // Formula: 1 / (k + rank)
            double score = 1.0 / (K + i + 1);
            scores.put(id, scores.getOrDefault(id, 0.0) + score);
        }

        // 2. Calculate AI ranking score (accumulate)
        for (int i = 0; i < aiIds.size(); i++) {
            Long id = aiIds.get(i);
            double score = 1.0 / (K + i + 1);
            scores.put(id, scores.getOrDefault(id, 0.0) + score);
        }

        return scores;
    }
}
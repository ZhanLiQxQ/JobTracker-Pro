package com.jobtracker.util;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class RRFCalculator {
    // 工业界通常 k 取 60
    private static final int K = 60;

    /**
     * 计算倒数排名融合分数
     * @param sqlIds SQL 搜索出来的 ID 列表 (有序)
     * @param aiIds AI 搜索出来的 ID 列表 (有序)
     * @return Map<JobId, Score>
     */
    public static Map<Long, Double> calculateScores(List<Long> sqlIds, List<Long> aiIds) {
        Map<Long, Double> scores = new HashMap<>();

        // 1. 计算 SQL 的排名分
        for (int i = 0; i < sqlIds.size(); i++) {
            Long id = sqlIds.get(i);
            // 公式: 1 / (k + rank)
            double score = 1.0 / (K + i + 1);
            scores.put(id, scores.getOrDefault(id, 0.0) + score);
        }

        // 2. 计算 AI 的排名分 (累加)
        for (int i = 0; i < aiIds.size(); i++) {
            Long id = aiIds.get(i);
            double score = 1.0 / (K + i + 1);
            scores.put(id, scores.getOrDefault(id, 0.0) + score);
        }

        return scores;
    }
}
-- 更新Job表的唯一约束：从(title, company)改为url
-- 这个脚本用于修改现有的唯一约束

-- 1. 首先删除现有的唯一约束
DO $$
BEGIN
    -- 检查是否存在旧的唯一约束
    IF EXISTS (
        SELECT 1 
        FROM information_schema.table_constraints 
        WHERE table_name = 'job' 
        AND constraint_name = 'uk7q3pxg7dus3251mcbest4h8of'
        AND constraint_type = 'UNIQUE'
    ) THEN
        -- 删除旧的唯一约束
        ALTER TABLE job DROP CONSTRAINT uk7q3pxg7dus3251mcbest4h8of;
        RAISE NOTICE '成功删除旧的唯一约束 (title, company)';
    ELSE
        RAISE NOTICE '旧的唯一约束不存在，无需删除';
    END IF;
END $$;

-- 2. 添加新的唯一约束（基于url）
DO $$
BEGIN
    -- 检查是否已存在url的唯一约束
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.table_constraints 
        WHERE table_name = 'job' 
        AND constraint_type = 'UNIQUE'
        AND constraint_name LIKE '%url%'
    ) THEN
        -- 添加新的唯一约束
        ALTER TABLE job ADD CONSTRAINT uk_job_url UNIQUE (url);
        RAISE NOTICE '成功添加新的唯一约束 (url)';
    ELSE
        RAISE NOTICE 'url的唯一约束已存在';
    END IF;
END $$;

-- 3. 验证约束是否添加成功
SELECT 
*
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu 
    ON tc.constraint_name = kcu.constraint_name
WHERE tc.table_name = 'job' 
    AND tc.constraint_type = 'UNIQUE'
ORDER BY tc.constraint_name;


select *
from jobtracker.public.job
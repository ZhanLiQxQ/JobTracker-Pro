-- Update Job table unique constraint: from (title, company) to url
-- This script is used to modify existing unique constraints

-- 1. First delete existing unique constraint
DO $$
BEGIN
    -- Check if old unique constraint exists
    IF EXISTS (
        SELECT 1 
        FROM information_schema.table_constraints 
        WHERE table_name = 'job' 
        AND constraint_name = 'uk7q3pxg7dus3251mcbest4h8of'
        AND constraint_type = 'UNIQUE'
    ) THEN
        -- 删除旧的唯一约束
        ALTER TABLE job DROP CONSTRAINT uk7q3pxg7dus3251mcbest4h8of;
        RAISE NOTICE 'Successfully deleted old unique constraint (title, company)';
    ELSE
        RAISE NOTICE 'Old unique constraint does not exist, no need to delete';
    END IF;
END $$;

-- 2. Add new unique constraint (based on url)
DO $$
BEGIN
    -- Check if url unique constraint already exists
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.table_constraints 
        WHERE table_name = 'job' 
        AND constraint_type = 'UNIQUE'
        AND constraint_name LIKE '%url%'
    ) THEN
        -- 添加新的唯一约束
        ALTER TABLE job ADD CONSTRAINT uk_job_url UNIQUE (url);
        RAISE NOTICE 'Successfully added new unique constraint (url)';
    ELSE
        RAISE NOTICE 'url unique constraint already exists';
    END IF;
END $$;

-- 3. Verify if constraint was added successfully
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
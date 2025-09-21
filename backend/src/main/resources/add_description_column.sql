-- 为现有的job表添加description列
-- 如果列不存在则添加，如果存在则跳过

DO $$
BEGIN
    -- 检查description列是否存在
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'job' 
        AND column_name = 'description'
    ) THEN
        -- 添加description列
        ALTER TABLE job ADD COLUMN description TEXT;
        RAISE NOTICE '成功添加description列到job表';
    ELSE
        RAISE NOTICE 'description列已存在于job表中';
    END IF;
END $$;

-- 验证列是否添加成功
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'job' 
ORDER BY ordinal_position;


INSERT INTO job (title, company, location, description, source)
VALUES ('测试职位', '测试公司', '测试地点', '这是一个测试描述', '测试来源')
RETURNING *;

-- 1. 查看当前数据库
SELECT current_database();

-- 2. 查看job表结构
\d job

-- 3. 查看job表的所有列
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'job'
ORDER BY ordinal_position;
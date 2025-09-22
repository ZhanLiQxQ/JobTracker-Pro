-- Add description column to existing job table
-- Add if column does not exist, skip if it exists

DO $$
BEGIN
    -- Check if description column exists
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'job' 
        AND column_name = 'description'
    ) THEN
        -- Add description column
        ALTER TABLE job ADD COLUMN description TEXT;
        RAISE NOTICE 'Successfully added description column to job table';
    ELSE
        RAISE NOTICE 'description column already exists in job table';
    END IF;
END $$;

-- Verify if column was added successfully
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'job' 
ORDER BY ordinal_position;


INSERT INTO job (title, company, location, description, source)
VALUES ('Test Job', 'Test Company', 'Test Location', 'This is a test description', 'Test Source')
RETURNING *;

-- 1. View current database
SELECT current_database();

-- 2. View job table structure
\d job

-- 3. View all columns of job table
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'job'
ORDER BY ordinal_position;
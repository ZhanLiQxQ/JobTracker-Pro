
-- Order of table deletion is important due to foreign key constraints
-- First delete tables with foreign key dependencies
DROP TABLE IF EXISTS user_favorite CASCADE;

-- Then delete the dependent tables
DROP TABLE IF EXISTS job CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create users table
CREATE TABLE users (
                       id BIGSERIAL PRIMARY KEY,
                       email VARCHAR(255) NOT NULL UNIQUE,
                       password VARCHAR(255) NOT NULL,
                       role VARCHAR(255) DEFAULT 'USER',
                       resume TEXT,
                       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create job table
CREATE TABLE job (
                     id BIGSERIAL PRIMARY KEY,
                     title VARCHAR(255),
                     company VARCHAR(255),
                     location VARCHAR(255),
                     url VARCHAR(500),
                     source VARCHAR(255),
                     description TEXT,
                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create user_favorite table
CREATE TABLE user_favorite (
                               id BIGSERIAL PRIMARY KEY,
                               user_id BIGINT NOT NULL,
                               job_id BIGINT NOT NULL,
                               favorited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                               notes TEXT,
                               created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                               updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key constraints
                               CONSTRAINT fk_user_favorite_user
                                   FOREIGN KEY (user_id)
                                       REFERENCES users(id)
                                       ON DELETE CASCADE,

                               CONSTRAINT fk_user_favorite_job
                                   FOREIGN KEY (job_id)
                                       REFERENCES job(id)
                                       ON DELETE CASCADE,

    -- Ensure same user cannot favorite same job multiple times
                               CONSTRAINT unique_user_job
                                   UNIQUE (user_id, job_id)
);



-- Insert some public job data
INSERT INTO job (title, company, location, description, source) VALUES
('Java开发工程师', '阿里巴巴', '杭州', '负责Java后端开发，要求3年以上经验，熟悉Spring Boot、MySQL等技术栈', 'LinkedIn'),
('前端开发工程师', '腾讯', '深圳', '负责React/Vue开发，要求2年以上经验，熟悉现代前端技术', 'Indeed'),
('全栈工程师', '字节跳动', '北京', '负责前后端开发，要求4年以上经验，熟悉多种编程语言', 'Boss直聘'),
('Python开发工程师', '百度', '北京', '负责Python后端开发，要求3年以上经验，熟悉Django、Flask等框架', '拉勾'),
('DevOps工程师', '美团', '北京', '负责CI/CD流程，要求3年以上经验，熟悉Docker、Kubernetes等工具', '猎聘'),
('产品经理', '小米', '北京', '负责产品规划和设计，要求5年以上经验，有互联网产品经验', '智联招聘'),
('UI设计师', '网易', '杭州', '负责产品界面设计，要求3年以上经验，熟悉设计工具和设计规范', '前程无忧'),
('数据分析师', '滴滴', '北京', '负责数据分析和挖掘，要求2年以上经验，熟悉SQL和Python', '脉脉');
 -- 插入一些公开的职位数据
INSERT INTO job (title, company, status, applied_at, description, source, is_public, id)
VALUES 
('Java开发工程师', '阿里巴巴', 'APPLIED', NOW(), '负责Java后端开发', 'LinkedIn', true, 1),
('前端开发工程师', '腾讯', 'APPLIED', NOW(), '负责React/Vue开发', 'Indeed', true, 1),
('全栈工程师', '字节跳动', 'APPLIED', NOW(), '负责前后端开发', 'Boss直聘', true, 1),
('Python开发工程师', '百度', 'APPLIED', NOW(), '负责Python后端开发', '拉勾', true, 1),
('DevOps工程师', '美团', 'APPLIED', NOW(), '负责CI/CD流程', '猎聘', true, 1);
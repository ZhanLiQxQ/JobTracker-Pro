# 🚀 JobTracker Pro - Intelligent Job Tracking Platform

An intelligent job management tool with AI-powered job recommendations, automated job scraping, and visual progress tracking.

## ✨ Features

- 🔍 **Smart Job Search** - Filter jobs by title, company, location, and more
- 🤖 **AI Job Recommendations** - Get personalized job suggestions based on your resume
- 📊 **Progress Tracking** - Visualize your application status and statistics
- 💾 **Favorites Management** - Save interesting jobs for later follow-up
- 📄 **Resume Upload** - Upload and analyze your resume with AI
- 🕷️ **Automated Scraping** - Automatically fetch the latest job postings
- 🔐 **User Authentication** - Secure user registration and login system

## 🛠️ Tech Stack

### Frontend
- **React 18** + **TypeScript** - Modern frontend framework
- **Tailwind CSS** - Responsive UI design
- **Vite** - Fast build tool

### Backend
- **Spring Boot 3** - Java enterprise framework
- **Spring Security** - Security authentication and authorization
- **JWT** - Stateless authentication

### Database
- **PostgreSQL** - Main business database
- **Redis** - Caching and session storage

### AI Service
- **Python** - AI recommendation algorithms
- **Scikit-learn** - Machine learning library
- **Sentence Transformers** - Text similarity computation

### Infrastructure
- **Docker** - Containerized deployment
- **Docker Compose** - Multi-service orchestration

## 🚀 Quick Start

### Prerequisites

- Docker Desktop
- Git

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd JobTracker-Pro
```

### 2. Start Database Services

```bash
# Start only database services first
docker-compose up -d db redis
```

### 3. Create Database Schema

**⚠️ Important: Must create database tables before starting backend services**

#### Method 1: Use Project SQL File (Recommended)

```bash
# Run the data.sql file to create table structure and sample data
docker exec -i jobtracker-pro-db-1 psql -U admin -d jobtracker < backend/src/main/resources/data.sql
```

#### Method 2: Manual Table Creation

```bash
# Manually create database tables (if Method 1 doesn't work)
docker exec -i jobtracker-pro-db-1 psql -U admin -d jobtracker -c "
-- Drop existing tables (if they exist)
DROP TABLE IF EXISTS user_favorites CASCADE;
DROP TABLE IF EXISTS job CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create users table
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resume TEXT,
    role VARCHAR(50) DEFAULT 'USER'
);

-- Create job table
CREATE TABLE job (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    description TEXT,
    source VARCHAR(255)
);

-- Create user favorites table
CREATE TABLE user_favorites (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    job_id BIGINT NOT NULL,
    favorited_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (job_id) REFERENCES job(id),
    UNIQUE(user_id, job_id)
);
"
```

### 4. Start All Services

```bash
# Now start all services (backend, frontend, AI service)
docker-compose up -d
```

### 5. Access the Application

- **Frontend Interface**: http://localhost
- **Backend API**: http://localhost:8080
- **AI Service**: http://localhost:5000

### 6. Get Job Data

**Recommended: Run scraper to get latest job data**

```bash
# Execute scraper to get latest job data
docker exec -it jobtracker-pro-ai_service-1 python main.py
```

**Note**:
- Scraper will automatically fetch latest job information from job websites
- Data will be automatically saved to the database
- If you don't want to run the scraper, you can manually add job data

## 📱 User Guide

### User Registration and Login

1. Open http://localhost
2. Click the "Login" button in the top right corner
3. Select the "Register" tab in the popup
4. Enter your email and password to complete registration
5. Use your registered account to log in

### Search and Browse Jobs

1. Enter keywords in the search box on the homepage (e.g., "Java Developer", "Frontend Engineer")
2. Filter by company name and location
3. Browse search results and view job details
4. Click the "Favorite" button to save interesting jobs

### Manage Favorite Jobs

1. Click the "Favorites" button in the top navigation
2. View your list of favorited jobs
3. Add personal notes and tags
4. Track application status and progress

### Upload Resume for AI Recommendations

1. Go to the "Resume Upload" page
2. Upload your resume file (PDF format)
3. The system will analyze your resume content
4. View AI-recommended matching jobs in the job list

## 🔧 Development Guide

### Project Structure

```
JobTracker-Pro/
├── frontend/          # React frontend application
├── backend/           # Spring Boot backend service
├── ai_service/        # Python AI recommendation service
├── docker-compose.yml # Docker orchestration configuration
└── README.md
```

### Local Development

#### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

#### Backend Development

```bash
cd backend
./mvnw spring-boot:run
```

#### AI Service Development

```bash
cd ai_service
pip install -r requirements.txt
python api.py
```

### Database Management

```bash
# Connect to database
docker exec -it jobtracker-pro-db-1 psql -U admin -d jobtracker

# View table structure
\dt

# View data
SELECT * FROM job LIMIT 10;
```

## 🐛 Troubleshooting

### Common Issues

#### 1. 403 Error During Registration

**Cause**: Database table structure doesn't match entity classes

**Solution**: 
```bash
# Recreate database tables
docker exec -i jobtracker-pro-db-1 psql -U admin -d jobtracker -c "
DROP TABLE IF EXISTS user_favorites;
DROP TABLE IF EXISTS job;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resume TEXT,
    role VARCHAR(50) DEFAULT 'USER'
);

CREATE TABLE job (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    description TEXT,
    source VARCHAR(255)
);

CREATE TABLE user_favorites (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    job_id BIGINT NOT NULL,
    favorited_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (job_id) REFERENCES job(id),
    UNIQUE(user_id, job_id)
);
"
```

#### 2. Services Won't Start

**Check service status**:
```bash
docker-compose ps
```

**View logs**:
```bash
docker-compose logs backend
docker-compose logs frontend
docker-compose logs ai_service
```

**Restart services**:
```bash
docker-compose restart
```

#### 3. Scraper Can't Fetch Data

**Check network connection**:
```bash
docker exec -it jobtracker-pro-ai_service-1 ping google.com
```

**Run scraper manually**:
```bash
docker exec -it jobtracker-pro-ai_service-1 python main.py
```

## 📊 API Documentation

### Authentication Endpoints

- `POST /api/auth/signup` - User registration
- `POST /api/auth/signin` - User login

### Job Endpoints

- `GET /api/jobs` - Get job list
- `GET /api/jobs/{id}` - Get job details
- `POST /api/jobs/favorite` - Favorite a job
- `GET /api/jobs/favorites` - Get favorites list

### Internal Endpoints

- `POST /api/internal/jobs/batch-intake` - Batch import job data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- Spring Boot team for the excellent framework
- React community for support
- All contributors for their efforts

---

**Start your job search journey now!** 🎯

If you have any questions, please submit an Issue or contact the development team.

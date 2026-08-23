CREATE DATABASE IF NOT EXISTS resume_screening;
USE resume_screening;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    mobile VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    qualification VARCHAR(100),
    experience VARCHAR(100),
    location VARCHAR(100),
    photo VARCHAR(255),
    role VARCHAR(20) NOT NULL DEFAULT 'candidate',
    email_verified TINYINT(1) DEFAULT 1,
    two_factor_enabled TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    department VARCHAR(100) NOT NULL,
    experience VARCHAR(100),
    location VARCHAR(100),
    description TEXT,
    required_skills TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'Open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS resumes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    job_id INT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    email VARCHAR(150),
    mobile VARCHAR(30),
    qualification VARCHAR(100),
    experience VARCHAR(100),
    location VARCHAR(100),
    detected_skills TEXT,
    matching_skills TEXT,
    missing_skills TEXT,
    ats_score DECIMAL(5,2) DEFAULT 0,
    ai_score DECIMAL(5,2) DEFAULT 0,
    ml_label VARCHAR(50),
    status VARCHAR(20) DEFAULT 'Pending',
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    decision_at TIMESTAMP NULL,
    screened_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    admin_id INT NULL,
    action VARCHAR(100) NOT NULL,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    is_read TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS otp_codes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    otp VARCHAR(6) NOT NULL,
    purpose VARCHAR(30) NOT NULL,
    expires_at DATETIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

INSERT INTO jobs
(title, department, experience, location, description, required_skills)
SELECT 'Python Developer', 'IT', 'Fresher / 0-2 Years', 'Pune',
'Develop Python applications and backend services.',
'Python, Flask, SQL, MySQL, HTML, CSS, JavaScript'
WHERE NOT EXISTS (
    SELECT 1 FROM jobs WHERE title='Python Developer'
);

INSERT INTO jobs
(title, department, experience, location, description, required_skills)
SELECT 'Full Stack Developer', 'IT', 'Fresher / 0-2 Years', 'Pune',
'Build web applications using frontend and backend technologies.',
'Python, Flask, HTML, CSS, JavaScript, MySQL, React'
WHERE NOT EXISTS (
    SELECT 1 FROM jobs WHERE title='Full Stack Developer'
);

INSERT INTO jobs
(title, department, experience, location, description, required_skills)
SELECT 'Data Analyst', 'Analytics', 'Fresher / 0-2 Years', 'Pune',
'Work with data, reports and basic machine learning techniques.',
'Python, Pandas, NumPy, SQL, Excel, Machine Learning'
WHERE NOT EXISTS (
    SELECT 1 FROM jobs WHERE title='Data Analyst'
);

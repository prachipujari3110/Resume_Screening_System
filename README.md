# 🤖 AI Resume Screening System

An AI and Machine Learning based Resume Screening System that helps recruiters automatically analyze, match, classify, and rank candidate resumes according to job requirements.

## 📌 Project Overview

The AI Resume Screening System is a web-based application developed using Python and Flask.

The system helps recruiters reduce manual resume screening time by automatically processing resumes, extracting candidate information, detecting skills, matching resumes with job requirements, calculating ATS scores, and using Machine Learning for resume classification.

### 🎯 Main Objectives

- Automate resume screening
- Extract information from PDF resumes
- Detect candidate skills
- Match candidate skills with job requirements
- Calculate ATS score
- Classify resumes using Machine Learning
- Generate an AI-based suitability score
- Store candidate and screening information in MySQL

---

## 🚀 Key Features

### 👤 User & Candidate Management

- User registration and login
- Candidate profile management
- Resume upload
- Candidate information management
- Secure password handling

### 📄 Resume Processing

- PDF resume upload
- Text extraction from PDF
- Resume text preprocessing
- Skill detection
- Candidate information extraction

### 🎯 ATS Resume Matching

The ATS module compares the skills available in a candidate's resume with the skills required for a selected job.

The system calculates:

- Matching Skills
- Missing Skills
- ATS Score
- Candidate suitability

### 🤖 Artificial Intelligence & Machine Learning

The system uses Machine Learning techniques for resume classification.

**Machine Learning Pipeline:**

```text
Resume Text
     ↓
Text Preprocessing
     ↓
TF-IDF
     ↓
Logistic Regression
     ↓
Prediction
     ↓
Confidence Score



The Machine Learning prediction and ATS score are combined to generate an AI suitability score.

📊 Admin Dashboard

The administrator can:

Manage candidates
Manage jobs
View submitted resumes
View ATS scores
View AI scores
Monitor candidate status
View screening results
🗄️ MySQL Database

MySQL is used to store:

User information
Candidate information
Job information
Resume information
Screening results
ATS scores
AI prediction results
🧠 AI / ML Technology
TF-IDF

TF-IDF (Term Frequency-Inverse Document Frequency) is used to convert resume text into numerical features that can be processed by the Machine Learning model.

It helps the model identify important words and terms in resume documents.

Logistic Regression

Logistic Regression is used for resume classification.

The model predicts the classification of a resume based on the extracted text features.

ATS Skill Matching

The ATS module compares:

Candidate Resume Skills

with:

Required Job Skills

and calculates the percentage of matching skills.

📊 Dataset

The project includes a synthetic resume dataset for academic and demonstration purposes.

Dataset Location
dataset/resumes.csv
Dataset Information

The dataset contains information such as:

Resume ID
Resume Text
Skills
Experience
Education
Label

The dataset is intended for educational and academic project demonstration.

🛠️ Technology Stack
Backend
Python
Flask
AI / Machine Learning
Pandas
NumPy
Scikit-learn
TF-IDF
Logistic Regression
PDF Processing
pypdf
Database
MySQL
phpMyAdmin
Frontend
HTML5
CSS3
JavaScript
Development Tools
Visual Studio Code
Git
GitHub
🔄 System Workflow
User Login
    ↓
Job Requirements
    ↓
Upload Resume
    ↓
PDF Text Extraction
    ↓
Text Preprocessing
    ↓
Skill Detection
    ↓
ATS Skill Matching
    ↓
ATS Score
    ↓
ML Prediction
    ↓
TF-IDF
    ↓
Logistic Regression
    ↓
AI Suitability Score
    ↓
Resume Screening Result
📁 Project Structure
Resume_Screening_System/
│
├── app.py
├── config.py
├── database.py
├── database.sql
├── ml_engine.py
├── check_setup.py
├── requirements.txt
├── README.md
│
├── dataset/
│   └── resumes.csv
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   └── ...
│
└── uploads/
    └── resumes/
⚙️ Installation & Setup
1. Clone the Repository
git clone https://github.com/prachipujari3110/Resume_Screening_System.git

Go to the project folder:

cd Resume_Screening_System
2. Install Required Packages
pip install -r requirements.txt
3. Configure MySQL

Start MySQL using XAMPP or MySQL Server.

Import the following file into MySQL/phpMyAdmin:

database.sql

Make sure the MySQL configuration in the project matches your local MySQL setup.

4. Check Project Setup
python check_setup.py
5. Run the Application
python app.py

Open the application in your browser:

http://127.0.0.1:5000
🔐 Security

The project supports security practices such as:

Password hashing
User authentication
Database validation
File upload validation
Environment-based configuration

Sensitive information such as database passwords, API keys, and secret credentials should not be stored directly in the GitHub repository.

📈 Future Enhancements

Future versions of the project can include:

Deep Learning based resume analysis
BERT-based NLP
Advanced semantic skill matching
Resume ranking
Email notifications
Interview scheduling
Candidate recommendation system
Job recommendation
Cloud deployment
Advanced analytics dashboard
🎓 Academic Project

This project is developed as an academic MCA project to demonstrate practical knowledge of:

Python
Flask
HTML
CSS
JavaScript
MySQL
Natural Language Processing
Machine Learning
Data Processing
Git
GitHub
👩‍💻 Author
Prachi Pujari

GitHub:

https://github.com/prachipujari3110

⭐ Project Goal

The goal of this project is to build an intelligent resume screening solution that combines ATS-based skill matching and Machine Learning to help recruiters identify suitable candidates faster and more efficiently.
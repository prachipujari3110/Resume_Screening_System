AI RESUME SCREENING SYSTEM

TECHNOLOGY
Python, Flask, MySQL, Pandas, NumPy, Scikit-learn, pypdf, HTML, CSS, JavaScript

AI / ML / DATASET
- ATS skill matching compares resume skills with job requirements.
- A 500-record resume dataset is included in dataset/resumes.csv.
- Scikit-learn uses TF-IDF + Logistic Regression for resume classification.
- The ML prediction and confidence are combined with the ATS score for the AI suitability score.

RUN
1. Start MySQL on port 3308.
2. Import database.sql into MySQL/phpMyAdmin.
3. Install packages: pip install -r requirements.txt
4. Check setup: python check_setup.py
5. Start: python app.py
6. Open: http://127.0.0.1:5000

NOTE
The dataset is synthetic and intended for an academic project/demo.

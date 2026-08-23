import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "dataset", "resumes.csv")

_model = None
_vectorizer = None

def train_model():
    global _model, _vectorizer
    data = pd.read_csv(DATASET_PATH)
    data = data.dropna(subset=["Resume_Text", "Label"])
    _vectorizer = TfidfVectorizer(stop_words="english", max_features=1500)
    x = _vectorizer.fit_transform(data["Resume_Text"].astype(str))
    _model = LogisticRegression(max_iter=1000, random_state=42)
    _model.fit(x, data["Label"].astype(str))

def predict_resume(text):
    global _model, _vectorizer
    if _model is None or _vectorizer is None:
        train_model()
    x = _vectorizer.transform([text or ""])
    label = _model.predict(x)[0]
    probabilities = _model.predict_proba(x)[0]
    confidence = round(float(max(probabilities)) * 100, 2)
    return label, confidence

train_model()

import pandas as pd
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# Load dataset
df = pd.read_csv("data/tickets.csv")

# Input text
X = df["ticket_text"]

# Outputs
y_category = df["category"]
y_priority = df["priority"]

# Convert text to numbers
vectorizer = TfidfVectorizer()

X_vectorized = vectorizer.fit_transform(X)

# ------------------------
# Category Model
# ------------------------

category_model = MultinomialNB()

category_model.fit(X_vectorized, y_category)

# ------------------------
# Priority Model
# ------------------------

priority_model = MultinomialNB()

priority_model.fit(X_vectorized, y_priority)

# ------------------------
# Save Models
# ------------------------

joblib.dump(category_model, "models/category_model.pkl")

joblib.dump(priority_model, "models/priority_model.pkl")

joblib.dump(vectorizer, "models/vectorizer.pkl")

print("Models Saved Successfully!")
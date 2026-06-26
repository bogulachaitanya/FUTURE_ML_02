import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix

# Load Dataset
df = pd.read_csv("data/tickets.csv")

X = df["ticket_text"]
y = df["category"]

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# TF-IDF
vectorizer = TfidfVectorizer()

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Train Model
model = MultinomialNB()

model.fit(X_train_vec, y_train)

# Predict
predictions = model.predict(X_test_vec)

# Confusion Matrix
cm = confusion_matrix(y_test, predictions)

print("Confusion Matrix:\n")
print(cm)
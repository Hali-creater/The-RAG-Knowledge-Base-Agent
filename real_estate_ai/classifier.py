import re
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import numpy as np

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    nlp = None

class IntentClassifier:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.model = LogisticRegression()
        self._train_mock_model()

    def _train_mock_model(self):
        # Mock training data
        training_data = [
            ("I am selling my house urgently, direct owner.", "Seller"),
            ("Urgent sale! Must sell now.", "Seller"),
            ("Available for sale by owner.", "Seller"),
            ("Looking to buy a 3 bedroom apartment.", "Buyer"),
            ("Budget is 500k, searching for property.", "Buyer"),
            ("Want to purchase a studio near downtown.", "Buyer"),
            ("Need to find a house for my family.", "Buyer"),
            ("Selling my villa in the suburbs.", "Seller"),
            ("Interested in buying real estate.", "Buyer"),
            ("For sale: 2BHK flat.", "Seller")
        ]
        X, y = zip(*training_data)
        X_vec = self.vectorizer.fit_transform(X)
        self.model.fit(X_vec, y)

    def classify(self, text):
        X_vec = self.vectorizer.transform([text.lower()])
        prediction = str(self.model.predict(X_vec)[0])
        probabilities = self.model.predict_proba(X_vec)[0]
        confidence = float(np.max(probabilities))

        # Rule-based fallback/reinforcement
        text_lower = text.lower()
        if 'sell' in text_lower or 'owner' in text_lower:
            if prediction != "Seller":
                confidence = (confidence + 0.5) / 2
        if 'buy' in text_lower or 'budget' in text_lower:
            if prediction != "Buyer":
                confidence = (confidence + 0.5) / 2

        return prediction, confidence

# Singleton instance
_classifier = IntentClassifier()

def classify_intent(text):
    return _classifier.classify(text)

if __name__ == "__main__":
    texts = [
        "I am selling my house urgently, direct owner.",
        "Looking to buy a 3 bedroom apartment within a budget of 500k.",
        "Just wanted to ask about the market."
    ]
    for t in texts:
        print(f"Text: {t} -> {classify_intent(t)}")

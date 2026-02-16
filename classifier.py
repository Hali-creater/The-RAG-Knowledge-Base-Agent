import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import numpy as np

class IntentClassifier:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.model = LogisticRegression()
        self._train_mock_model()

    def _train_mock_model(self):
        # Training data for Buyer, Seller, and Investor
        training_data = [
            ("I am selling my house urgently, direct owner.", "Seller"),
            ("Urgent sale! Must sell now.", "Seller"),
            ("Available for sale by owner.", "Seller"),
            ("Looking to buy a 3 bedroom apartment.", "Buyer"),
            ("Budget is 500k, searching for property.", "Buyer"),
            ("Want to purchase a studio near downtown.", "Buyer"),
            ("Looking for off-market deals, cash buyer.", "Investor"),
            ("Interested in multi-family properties for portfolio.", "Investor"),
            ("Buying distressed properties for renovation.", "Investor"),
            ("Wholesale deal available, great ROI.", "Investor")
        ]
        X, y = zip(*training_data)
        X_vec = self.vectorizer.fit_transform(X)
        self.model.fit(X_vec, y)

    def classify(self, text):
        text_lower = text.lower()

        # Rule-based overrides for Investor
        investor_keywords = ['cash buyer', 'off-market', 'portfolio', 'distressed', 'wholesale', 'roi', 'multi-family']
        if any(kw in text_lower for kw in investor_keywords):
             return "Investor", 0.9

        X_vec = self.vectorizer.transform([text_lower])
        prediction = str(self.model.predict(X_vec)[0])
        probabilities = self.model.predict_proba(X_vec)[0]
        confidence = float(np.max(probabilities))

        return prediction, confidence

_classifier = IntentClassifier()

def classify_intent(text):
    return _classifier.classify(text)

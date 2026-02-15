import re
import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # Fallback if model is not downloaded
    nlp = None

def extract_phone(text):
    # Basic regex for phone numbers (supports various formats)
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3,4}[-.\s]?\d{4}'
    match = re.search(phone_pattern, text)
    return match.group(0) if match else None

def extract_email(text):
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(email_pattern, text)
    return match.group(0) if match else None

def extract_price(text):
    # Matches patterns like $500,000, 500k, 1.2M, etc.
    price_pattern = r'\$?\d{1,3}(?:,\d{3})*(?:\.\d+)?\s?[kKmMbB]?'
    match = re.search(price_pattern, text)
    if match:
        price_str = match.group(0).replace('$', '').replace(',', '').lower()
        try:
            if 'k' in price_str:
                return float(price_str.replace('k', '')) * 1000
            if 'm' in price_str:
                return float(price_str.replace('m', '')) * 1000000
            return float(price_str)
        except ValueError:
            return None
    return None

def extract_location(text):
    if not nlp:
        return "Unknown"
    doc = nlp(text)
    locations = [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC", "FAC"]]
    return ", ".join(locations) if locations else "Unknown"

def extract_entities(text):
    return {
        "phone": extract_phone(text),
        "email": extract_email(text),
        "price": extract_price(text),
        "location": extract_location(text)
    }

if __name__ == "__main__":
    test_text = "I am selling my house in New York for $500,000. Contact me at 123-456-7890 or test@example.com"
    print(extract_entities(test_text))

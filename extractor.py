import re
import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    nlp = None

def extract_phone(text):
    # Basic regex for phone numbers
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3,4}[-.\s]?\d{4}'
    matches = re.findall(phone_pattern, text)

    for match in matches:
        if isinstance(match, tuple):
            match = "".join(match)
        # Remove fake numbers like 555-xxxx
        if "555" in match:
            continue
        return match
    return None

def extract_email(text):
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(email_pattern, text)
    if match:
        email = match.group(0)
        # Basic validation
        if "example.com" in email or "test.com" in email:
            return None
        return email
    return None

def extract_price(text):
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

def normalize_location(text):
    if not nlp:
        return "Unknown"
    doc = nlp(text)
    locations = [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC", "FAC"]]
    if locations:
        # Simple normalization: capitalize first letter
        return ", ".join(set([loc.strip().title() for loc in locations]))
    return "Unknown"

def extract_entities(text):
    return {
        "phone": extract_phone(text),
        "email": extract_email(text),
        "price": extract_price(text),
        "location": normalize_location(text)
    }

def calculate_score(lead_data):
    score = 0
    description = lead_data.get('full_description', '').lower()

    # 1. Keyword Strength & Urgency (up to 40 points)
    urgency_keywords = ['urgent', 'immediately', 'must sell', 'now', 'asap', 'quick', 'fast']
    urgency_count = sum(1 for kw in urgency_keywords if kw in description)
    score += min(40, urgency_count * 15)

    # 2. Contact Availability (up to 30 points)
    if lead_data.get('phone'):
        score += 20
    if lead_data.get('email'):
        score += 10

    # 3. Price and Location detected (up to 20 points)
    if lead_data.get('price'):
        score += 10
    if lead_data.get('location') and lead_data.get('location') != "Unknown":
        score += 10

    # 4. Intent Confidence (up to 10 points)
    score += int(lead_data.get('intent_confidence', 0) * 10)

    return min(100, score)

if __name__ == "__main__":
    test_lead = {
        'full_description': 'Urgent sale! Must sell now. Beautiful house.',
        'phone': '1234567890',
        'email': 'test@test.com',
        'price': 500000,
        'location': 'New York',
        'intent_confidence': 1.0
    }
    print(f"Lead Score: {calculate_score(test_lead)}")

def calculate_score(lead_data):
    score = 0
    description = lead_data.get('description', '').lower()
    title = lead_data.get('title', '').lower()
    full_text = title + " " + description

    # 1. Urgent words (+30)
    urgent_keywords = ['urgent', 'asap', 'immediately', 'must sell', 'need to sell fast', 'quick sale']
    if any(kw in full_text for kw in urgent_keywords):
        score += 30

    # 2. Motivation words (+20)
    motivation_keywords = ['divorce', 'inherited', 'relocating', 'foreclosure', 'job transfer', 'distressed']
    if any(kw in full_text for kw in motivation_keywords):
        score += 20

    # 3. Financial signal (+15)
    financial_keywords = ['discount', 'below market', 'price mentioned', 'off-market', 'cash only']
    if any(kw in full_text for kw in financial_keywords) or lead_data.get('price'):
        score += 15

    # 4. Contact info present (+25)
    has_phone = bool(lead_data.get('phone'))
    has_email = bool(lead_data.get('email'))
    if has_phone and has_email:
        score += 25
    elif has_phone or has_email:
        score += 15

    # 5. Recent post (+10)
    # Defaulting to 10 as we scrape real-time.
    score += 10

    # Ensure score doesn't exceed 100
    score = min(score, 100)

    # Classification
    if score <= 40:
        level = "Low Intent"
    elif score <= 75:
        level = "Medium Intent"
    else:
        level = "High Intent"

    return score, level

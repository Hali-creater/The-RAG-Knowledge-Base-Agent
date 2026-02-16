def calculate_score(lead_data):
    score = 0
    description = lead_data.get('description', '').lower()
    title = lead_data.get('title', '').lower()
    full_text = title + " " + description

    # 1. Urgent words (+20)
    urgent_keywords = ['urgent', 'asap', 'immediately', 'must sell', 'need to sell fast']
    if any(kw in full_text for kw in urgent_keywords):
        score += 20

    # 2. Motivation words (+15)
    motivation_keywords = ['divorce', 'inherited', 'relocating', 'foreclosure', 'job transfer']
    if any(kw in full_text for kw in motivation_keywords):
        score += 15

    # 3. Financial signal (+10)
    financial_keywords = ['discount', 'below market', 'price mentioned']
    if any(kw in full_text for kw in financial_keywords) or lead_data.get('price'):
        score += 10

    # 4. Contact info present (+20)
    if lead_data.get('phone') or lead_data.get('email'):
        score += 20

    # 5. Recent post (+10)
    # Since we scrape in real-time, we can often assume posts we just found are recent.
    # If we have a timestamp and it's within 24h, we add 10.
    # For now, we'll give 10 as default if it was just scraped.
    score += 10

    # Classification
    if score <= 25:
        level = "Low Intent"
    elif score <= 50:
        level = "Medium Intent"
    else:
        level = "High Intent"

    return score, level

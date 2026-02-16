def calculate_score(lead_data):
    score = 0
    description = lead_data.get('description', '').lower()
    title = lead_data.get('title', '').lower()
    full_text = title + " " + description

    # 1. GOLD Urgent Signals (+45) - Increased to ensure high priority
    gold_keywords = [
        'divorce', 'inherited', 'foreclosure', 'behind on mortgage',
        'must sell', 'urgent sale', 'motivated seller', 'need to sell house quickly',
        'pre foreclosure', 'cash buyer needed', 'inherited property'
    ]
    if any(kw in full_text for kw in gold_keywords):
        score += 45

    # 2. Strong Intent Keywords (+20)
    intent_keywords = [
        'sell my house', 'fsbo', 'for sale by owner', 'selling my home',
        'looking to buy', 'relocating', 'moving to', 'first time home buyer',
        'owner financing', 'job transfer', 'quick sale', 'selling house'
    ]
    if any(kw in full_text for kw in intent_keywords):
        score += 20

    # 3. Financial & Quality Signals (+15)
    financial_keywords = [
        'discount', 'below market', 'price mentioned', 'off-market',
        'investment property', 'cash only', 'cash buyer'
    ]
    if any(kw in full_text for kw in financial_keywords) or lead_data.get('price'):
        score += 15

    # 4. Contact Availability (+20)
    has_phone = bool(lead_data.get('phone'))
    has_email = bool(lead_data.get('email'))
    if has_phone or has_email:
        score += 20
    if has_phone and has_email:
        score += 5 # Bonus for both

    # 5. Recency (+10)
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

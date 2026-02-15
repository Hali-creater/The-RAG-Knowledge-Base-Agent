def classify_intent(text):
    text = text.lower()

    seller_keywords = [
        'selling', 'urgent sale', 'owner selling', 'direct owner',
        'must sell', 'for sale', 'available for sale', 'listing my'
    ]

    buyer_keywords = [
        'looking to buy', 'need apartment', 'budget', 'searching for property',
        'want to purchase', 'interested in buying', 'buying', 'looking for'
    ]

    seller_score = sum(1 for kw in seller_keywords if kw in text)
    buyer_score = sum(1 for kw in buyer_keywords if kw in text)

    if seller_score > buyer_score:
        intent = "Seller"
        confidence = min(1.0, seller_score / (seller_score + buyer_score + 0.1) + 0.5)
    elif buyer_score > seller_score:
        intent = "Buyer"
        confidence = min(1.0, buyer_score / (seller_score + buyer_score + 0.1) + 0.5)
    else:
        if seller_score > 0: # Equal but not zero
             intent = "Both/Unclear"
             confidence = 0.5
        else:
             intent = "Unknown"
             confidence = 0.0

    return intent, confidence

if __name__ == "__main__":
    texts = [
        "I am selling my house urgently, direct owner.",
        "Looking to buy a 3 bedroom apartment within a budget of 500k.",
        "Just wanted to ask about the market."
    ]
    for t in texts:
        print(f"Text: {t} -> {classify_intent(t)}")

def detectPinch(hand, isPinching):
    thumb = hand[4]
    index = hand[8]
    distance = ((thumb.x - index.x) ** 2 + (thumb.y - index.y) ** 2) ** 0.5
    if isPinching:
        return distance < 0.08
    else:
        return distance < 0.05
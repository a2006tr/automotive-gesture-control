def detectPlaybackGesture(hand, isTouching):
    thumb = hand[4]
    ring = hand[16]
    distance = ((thumb.x - ring.x) ** 2 + (thumb.y - ring.y) ** 2) ** 0.5
    if distance < 0.05:
        return True
    return False
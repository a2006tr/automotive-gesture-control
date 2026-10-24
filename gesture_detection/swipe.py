#swipes register when fast and purposeful, cooldown of 1s
def detectSwipe(positions, currentTime, lastSwipeTime, cooldown):
    if len(positions)<2:
        return None, lastSwipeTime, None
    else:
        distance = positions[-1][0] - positions[0][0]
        timeElapsed = positions[-1][2] - positions[0][2]
        #verticalDistance = abs(positions[0][1] - positions[-1][1])
        if distance >= 500 and 0 < timeElapsed <= 0.5 and currentTime - lastSwipeTime >= cooldown: # and verticalDistance < 50:
            return "Left", currentTime, distance
        elif distance <= -500 and 0 < timeElapsed <= 0.5 and currentTime - lastSwipeTime >= cooldown: # and verticalDistance < 50:
            return "Right", currentTime, distance
        else:
            return None, lastSwipeTime, None
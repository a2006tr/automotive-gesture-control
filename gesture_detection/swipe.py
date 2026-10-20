#create position list
positions = [(100, 200, 5.0),
    (150, 200, 5.1),
    (250, 200, 5.2)]
currentTime= 5.2
lastSwipeTime = 3.5
cooldown = 1.0

if len(positions)<2:
    print("Not Enough Positions")
else:
    distance = positions[0][0] - positions[-1][0]
    timeElapsed = positions[-1][2] - positions[0][2]
    if distance >= 100 and timeElapsed <= 0.5 and currentTime - lastSwipeTime >= cooldown:
        print("Swipe Left")
        lastSwipeTime = currentTime
    elif distance <= -100 and timeElapsed <= 0.5 and currentTime - lastSwipeTime >= cooldown:
        print("Swipe Right")
        lastSwipeTime = currentTime
    else:
        print("No Swipe")

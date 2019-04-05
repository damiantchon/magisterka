def manhattan_distance(x,y):
    return sum(abs(a-b) for a,b in zip(x,y))

import math

# === Tools ===
def kt_to_mps(speed):
    return speed*1852/3600

def ft_to_m(alt):
    return alt*0.3048

def distance(p1x, p1y, p2x, p2y):
    return math.sqrt((p1x - p2x) ** 2 + (p1y - p2y) ** 2)
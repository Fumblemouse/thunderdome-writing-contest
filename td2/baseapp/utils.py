"""range of utils to use across site"""
from random import randrange

def sattolo_cycle(items):
    """assign list to random new position"""
    for i in range(len(items) - 1, 0, -1):
        j = randrange(i)  # 0 <= j <= i-1
        items[j], items[i] = items[i], items[j]
    return items

"""range of utils to use across site"""
import re
from random import randrange
from django.utils.html import strip_tags

def sattolo_cycle(items):
    """assign list to random new position (that isn't the old position"""
    for i in range(len(items) - 1, 0, -1):
        j = randrange(i)  # 0 <= j <= i-1
        items[j], items[i] = items[i], items[j]
    return items

def HTML_wordcount(string):
    words_to_count = strip_tags(string)
    wordcount = len(re.findall(r'\S+', words_to_count))
    return wordcount

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
    """Strips HTML tags for the purposes of getting wordcoutns of fields"""
    words_to_count = strip_tags(string)
    wordcount = len(re.findall(r'\S+', words_to_count))
    return wordcount

def check_story_permissions(request, story=0):
    """checks if user is author or staff
    failing that, checks to see if user has opened their work generally
    the if story has been opened to the public"""
    if story.author.pk == request.user.pk or request.user.is_staff:
        result = True
    elif story.access > 0 and request.user.is_authenticated:
        result = True
    elif story.access > 1:
        result = True
    else:
        result = False
    return result
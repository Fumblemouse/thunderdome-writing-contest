"""range of utils to use across site"""
import re
from random import randrange
from django.utils.html import strip_tags
from datetime import datetime

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
    and if the story has been opened to the public"""
    if story.author.pk == request.user.pk or request.user.is_staff:
        result = True
    elif story.author.private_profile:
        result = False
    elif story.access > 0 and request.user.is_authenticated:
        result = True
    elif story.access > 1:
        result = True
    else:
        result = False
    return result


def set_expirable_var(session, var_name, value, expire_at):
    session[var_name] = {'value': value, 'expire_at': expire_at.timestamp()}

def get_expirable_var(session, var_name, default=None):
    var = default
    if var_name in session:
        my_variable_dict = session.get(var_name, {})
        if my_variable_dict.get('expire_at', 0) > datetime.now().timestamp():
            var = my_variable_dict.get('value')
        else:
            del session[var_name]
    return var

def get_expirable_var_time_to_del(session, var_name):
    if var_name in session:
        my_variable_dict = session.get(var_name, {})
        return my_variable_dict.get('expire_at', 0) - datetime.now().timestamp()
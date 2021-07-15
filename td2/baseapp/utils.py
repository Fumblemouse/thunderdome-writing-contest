"""range of utils to use across site"""
import re
from random import randrange
from datetime import datetime
from django.utils.html import strip_tags


def sattolo_cycle(items):
    """assign list to random new position (that isn't the old position"""
    for i in range(len(items) - 1, 0, -1):
        j = randrange(i)  # 0 <= j <= i-1
        items[j], items[i] = items[i], items[j]
    return items


def html_wordcount(string):
    """Strips HTML tags for the purposes of getting wordcoutns of fields"""
    words_to_count = strip_tags(string)
    # ourcery
    # wordcount = len(re.findall(r'\S+', words_to_count))
    # return wordcount
    return len(re.findall(r"\S+", words_to_count))


def check_story_permissions(request, story=0):
    """checks if user is author or staff
    failing that, checks to see if user has opened their work generally
    and if the story has been opened to the public

    Returns:
        Boolean: Does the user have permission to view a story
    """
    if story.author.pk == request.user.pk or request.user.is_staff:
        return True
    elif story.author.private_profile:
        return False
    elif story.access > 0 and request.user.is_authenticated:
        return True
    elif story.access > 1:
        return True
    else:
        return False


def set_expirable_var(session, var_name, value, expire_at):
    """Sets a session variable that will expire in time

    Args:
        session (Session): User session
        var_name (String): name of session variable
        value (Misc): value of session variable
        expire_at (Date): Date variable can be stored until
    """
    session[var_name] = {"value": value, "expire_at": expire_at.timestamp()}


def get_expirable_var(session, var_name, default=None):
    """Retreives session variable that

    Args:
        session (Session): User session variable
        var_name (Str): name of variable to retrieve
        default (Misc, optional): What to use if there is no session variable. Defaults to None.

    Returns:
        Str: value stored in session variable
    """
    var = default
    if var_name in session:
        my_variable_dict = session.get(var_name, {})
        if my_variable_dict.get("expire_at", 0) > datetime.now().timestamp():
            var = my_variable_dict.get("value")
        else:
            del session[var_name]
    return var


def get_expirable_var_time_to_del(session, var_name):
    """Returns the deletion time of a a session variable

    Args:
        session (Session): Django session variable
        var_name (Str): Name of the variable to be retrieved from

    Returns:
        date: variables remaining storage life
    """
    if var_name in session:
        my_variable_dict = session.get(var_name, {})
        return my_variable_dict.get("expire_at", 0) - datetime.now().timestamp()

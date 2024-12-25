from django import template

register = template.Library()


@register.filter()
def censor(value):
    bad_words = ['редиска', 'дурак', 'идиот']

    if not isinstance(value, str):
        return value

    for word in bad_words:
        censored_word = word[0] + '*' * (len(word) - 1)

        value = value.replace(word, censored_word)
        value = value.replace(word.capitalize(), censored_word.capitalize())

    return value
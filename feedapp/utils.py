# Core import
import re

OPEN_HTML_TAG_HASH = '<a href="#!/search/{}/{}">'


def get_markup_text(raw_body):
    """
    Convert raw text body into hastag formatted text body.
    Takes the raw text body as the input string and convert it into
    string with html linked hashtag word. For example.
    "#hello go planner." ->
    "<a href='/search/hello/hashtag/>#hello<a> go planner."
    """
    result = []
    body_word_list = raw_body.split(' ')

    for word in body_word_list:

        if word[0] in ['#', '@']:
            cleaned_word = []
            full_word = re.findall('[\w]+', word)

            if word[0] == '#':
                opening_html_tag = OPEN_HTML_TAG_HASH.format(
                    full_word[0], 'hashtag')
                cleaned_word.append('#')
            else:
                opening_html_tag = OPEN_HTML_TAG_HASH.format(
                    full_word[0], 'person')
                cleaned_word.append('@')

            cleaned_word.insert(0, opening_html_tag)
            cleaned_word.append(full_word[0])
            closing_html_tag = '</a>'
            cleaned_word.append(closing_html_tag)

            if word[0] == '#':
                cleaned_word.append(word.replace('#' + full_word[0], ''))
            else:
                cleaned_word.append(word.replace('@' + full_word[0], ''))

            word = ''.join(cleaned_word)

        result.append(word)

    return ' '.join(result)

def get_first_simple_text(response):

    return response.data['template']['outputs'][0]['simpleText']['text']


def get_context(response):
    try:
        return response.data['context']['values']
    except KeyError:
        return None
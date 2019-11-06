def get_first_simple_text(response):
    return response.data['template']['outputs'][0]['simpleText']['text']

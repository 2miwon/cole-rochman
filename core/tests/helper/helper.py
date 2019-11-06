def get_first_simple_text(response):
    return response.data['template']['outputs'][0]['simpleText']['text']


def get_context(response):
    try:
        return response.data['context']['values']
    except KeyError:
        return None


def check_build_response_fallback_404_called(response):
    return response.content.decode().find('계정을 먼저 등록해주셔야 해요. 계정을 등록하러 가볼까요?') > 0


def message_in_response(response):
    return str(response.content.decode())

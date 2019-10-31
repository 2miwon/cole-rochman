class ResponseBuilder:
    version = '2.0'
    VALIDATION = 'validation'
    SKILL = 'skill'

    def __init__(self, response_type, status=None):
        """
        use status only when response_type is VALIDATION

        :param response_type: use ResponseBuilder.VALIDATION or ResponseBuilder.SKILL
        """
        if response_type not in [self.VALIDATION, self.SKILL]:
            raise ValueError('Response_type must be ResponseBuilder.VALIDATION or ResponseBuilder.SKILL')
        if response_type == self.VALIDATION and status not in ['FAIL', 'SUCCESS']:
            raise ValueError('Status must be "FAIL" or "SUCCESS" when response_type is VALIDATION')

        self.response_type = response_type

        if response_type == self.VALIDATION:
            self.status = status
            self.response = {
                'status': status
            }
        elif response_type == self.SKILL:
            self.response = {
                'version': self.version,
                'template': {
                    'outputs': []
                }
            }

    def __add_outputs(self, data: dict):
        """
        append data to self.response['template']['outputs']

        :param data: dict
        :return: None
        """
        if self.response_type != self.SKILL:
            raise ValueError('You cannot use this when response_type is ResponseBuilder.VALIDATION')

        self.response.get('template').get('outputs').append(data)

    def __add_quick_reply(self, data: dict):
        """
        append data to self.response['template']['quickReplies']

        :param data: dict
        :return: None
        """
        if self.response_type != self.SKILL:
            raise ValueError('You cannot use this when response_type is ResponseBuilder.VALIDATION')

        quick_replies = self.response.get('template').get('quickReplies')
        if quick_replies is None:
            self.response.get('template')['quickReplies'] = []

        self.response.get('template').get('quickReplies').append(data)

    def add_value(self, value):
        """
        append value to self.response

        :type value: string or int
        """
        if self.response_type != self.VALIDATION: raise ValueError(
            'You cannot use add_value() when response_type is ResponseBuilder.VALIDATION')
        if not (type(value) == int or type(value) == str): raise ValueError('value should be int or string.')

        self.response['value'] = value

    def add_simple_text(self, message: str):
        """
        append simpleText(dict) with message to self.response['template']['outputs']

        :param message: It can be up to 1,000 letters.
        :return: None

        (완성 예제)
        {
            "simpleText": {
                "text": "간단한 텍스트 요소입니다."
            }
        }
        """

        if not (type(message) == int or type(message) == str):
            raise ValueError('message should be int or string.')

        data = {
            'simpleText': {
                'text': message
            }
        }

        self.__add_outputs(data=data)

    def add_image(self, image_url: str, alt_text: str):
        """
        append simpleImage(dict) with image_url and alt_text to self.response['template']['outputs']

        :param image_url: URL
        :param alt_text: It can be up to 1,000 letters.
        :return: None

        (완성 예제)
        {
            "simpleImage": {
                "imageUrl": "http://k.kakaocdn.net/dn/83BvP/bl20duRC1Q1/lj3JUcmrzC53YIjNDkqbWK/i_6piz1p.jpg",
                "altText": "보물상자입니다"
            }
        }
        """
        if type(image_url) != str and 'http' not in image_url: raise ValueError('image_url should be string of URL.')
        if type(alt_text) != str: raise ValueError('alt_text should be string')

        data = {
            'simpleImage': {
                'imageUrl': image_url,
                'altText': alt_text
            }
        }
        self.__add_outputs(data=data)

    def add_quick_reply(self, action: str, label: str, block_id: str = None, message_text: str = None):
        """
        append quickReplies with action, label, or maybe block_id, message_text to self.response['template']['outputs']

        :type action: string. "block" or "message"
        :param label: string.
        :param block_id: string. It is necessary when action is "block"
        :param message_text: string.
        :return: None

        (완성 예제)
        {
            "action": "block",
            "label": "예",
            # "messageText": "예",
            "blockId": "5da5eac292690d0001a4"
        }
        or
        {
            "action": "message",
            "label": "아니요",
            "messageText": "아니요"
        }
        """
        if action is None or label is None: raise ValueError('action or label is None.')
        if action not in ['block', 'message']: raise ValueError('action should be block or message.')
        if action == 'block' and block_id is None: raise ValueError('block_id is necessary when action is "block".')
        if action == 'message' and message_text is None:
            raise ValueError('message_text is recommended when action is "message".')

        data = {
            'action': action,
            'label': label
        }

        if block_id:
            data['blockId'] = block_id

        if message_text:
            data['messageText'] = message_text

        self.__add_quick_reply(data=data)

    def set_quick_replies_yes_or_no(self, block: bool = True, block_id_for_yes: str = None,
                                    message_text_for_no: str = '아니요, 종료할게요.'):
        """
        Automaticaly add quick_replies for 예/아니요.
        Currently you can only set block_id for yes, and message_text for no.
        Use add_quick_reply() when you want other way.

        :param block: bool
        :param block_id_for_yes: str. It is necessary when block is True
        :param message_text_for_no: str. default is '아니요, 종료할게요.'
        :return: None
        """
        if block and block_id_for_yes is None:
            raise ValueError('block_id is necessary when action is "block".')

        self.add_quick_reply(action='block', label='예', block_id=block_id_for_yes)
        self.add_quick_reply(action='message', label='아니요', message_text=message_text_for_no)

    def get_response(self):
        """
        Return self.response

        :return: dict. self.response
        """
        return self.response

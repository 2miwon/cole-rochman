from django.http.request import HttpRequest
from rest_framework.test import APITestCase
from core.api.util.helper import find_nested_key_from_dict, Kakao


class FunctionTest(APITestCase):
    def test_find_key_from_dict_suceess(self):
        _dict = {
            'random': {'key': 'value'}
        }
        self.assertEqual(find_nested_key_from_dict(_dict, 'random.key'), 'value')

    def test_find_key_from_dict_fail(self):
        _dict = {
            'random': {'key2': 'value'}
        }
        self.assertEqual(find_nested_key_from_dict(_dict, 'random.key'), None)
    #
    # def test_check_nested_key_exist_success(self):
    #     _dict = {
    #         'random': {'key2': 'value'}
    #     }
    #     self.assertEqual(check_nested_key_exist(_dict, 'random.key'), False)
    #     _dict = {
    #         'random': 'value'
    #     }
    #     self.assertEqual(check_nested_key_exist(_dict, 'random'), True)


class KakaoTest(APITestCase):
    def test_parse_kakao_user_id(self):
        request = HttpRequest()
        data = {
            'userRequest': {
                'user': {
                    'id': 'test123'
                }
            }
        }
        setattr(request, 'data', data)

        kakao = Kakao()
        kakao.preprocess(request)
        kakao.parse_kakao_user_id()
        self.assertEqual(kakao.kakao_user_id, 'test123')
        self.assertEqual(kakao.kakao_user_id_parsed, True)

    def test_parse_params(self):
        request = HttpRequest()
        data = {
            'action': {
                'params': {'test_key': 'test_value'}
            }
        }
        setattr(request, 'data', data)

        kakao = Kakao()
        kakao.preprocess(request)
        self.assertEqual(kakao.params, {'test_key': 'test_value'})
        self.assertEqual(kakao.params_parsed, True)

    def test_parse_detail_params(self):
        request = HttpRequest()
        data = {
            'action': {
                'detailParams': {'test_key': {'origin': 'some_origin',
                                              'value': {'some_key': 'test_value'}}}
            }
        }
        setattr(request, 'data', data)

        kakao = Kakao()
        kakao.preprocess(request)
        self.assertEqual(kakao.detail_params, {'test_key': {'some_key': 'test_value'}})
        self.assertEqual(kakao.detail_params_parsed, True)

    def test_parse_detail_params_override(self):
        """
        override parse_detail_params() when params exists with same key
        """
        request = HttpRequest()
        data = {
            'action': {
                'params': {'test_key': {'some_key': 'not_value'}},
                'detailParams': {'test_key': {'origin': 'some_origin',
                                              'value': {'some_key': 'test_value'}}}
            }
        }
        setattr(request, 'data', data)

        kakao = Kakao()
        kakao.preprocess(request)
        self.assertEqual(kakao.detail_params, {'test_key': {'some_key': 'test_value'}})
        self.assertEqual(kakao.detail_params_parsed, True)
        self.assertEqual(kakao.data['test_key'], {'some_key': 'not_value'})

    def test_parse_patient_code(self):
        request = HttpRequest()
        data = {
            'action': {
                'params': {'patient_code': 'P12312345678'}
            }
        }
        setattr(request, 'data', data)

        kakao = Kakao()
        kakao.preprocess(request)
        kakao.parse_patient_code()
        self.assertEqual(kakao.patient_code, 'P12312345678')

"""
https://apidocs.ncloud.com/ko/common/ncpapi/#%EC%98%A4%EB%A5%98-%EC%B2%98%EB%A6%AC%ED%95%98%EA%B8%B0
"""


class NcloudBadRequestException:
    """
    protocol(https), endocing(UTF-8) 등 Request 에러
    """
    http_code = 400
    error_code = 100


class NcloudAuthenticationFailed:
    """
    인증 실패
    """
    http_code = 401
    error_code = 200


class NcloudPermissionDenied:
    """
    권한 없음
    """
    http_code = 401
    error_code = 210


class NcloudNotFoundException:
    """
    권한 없음
    """
    http_code = 404
    error_code = 300


class NcloudQuotaExceeded:
    """
    Quota 초과
    """
    http_code = 429
    error_code = 400


class NcloudThrottleLimited:
    """
    Rate 초과
    """
    http_code = 429
    error_code = 410


class NcloudRateLimited:
    """
    Rate 초과
    """
    http_code = 429
    error_code = 420


class NcloudRequestEntityTooLarge:
    """
    요청 엔티티 크기 초과
    """
    http_code = 413
    error_code = 430


class NcloudEndpointError:
    """
    엔드포인트 연결 에러
    """
    http_code = 503
    error_code = 500


class NcloudEndpointTimeout:
    """
    엔드포인트 연결 시간 초과
    """
    http_code = 504
    error_code = 510


class NcloudUnexpectedError:
    """
    예외 처리가 안된 에러
    """
    http_code = 500
    error_code = 900


exceptions = [
    NcloudBadRequestException,
    NcloudAuthenticationFailed,
    NcloudPermissionDenied,
    NcloudNotFoundException,
    NcloudQuotaExceeded,
    NcloudThrottleLimited,
    NcloudRateLimited,
    NcloudRequestEntityTooLarge,
    NcloudEndpointError,
    NcloudEndpointTimeout,
    NcloudUnexpectedError
]

exceptions = {x.code: x for x in exceptions}


def raise_exception(code: int):
    if type(code) == str:
        code = int(code)
    raise exceptions[code]

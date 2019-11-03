# cole-rochman
**Project**\
결핵 환자를 위한 카카오톡 챗봇 서버\
(연세대학교 디지털미디어랩)

# 주요 기능
크게 1) API 서버와 2) 대시보드 두가지로 볼 수 있습니다.
- 환자 등록
- 복약 관리/알림 기능
- 치료 관리/알림 기능
- 내원일 알림 기능
- 결핵 관련 정보 제공
- 병원 측 관리자 대시보드

# Spec
- **django** v2.2
- **django-rest-framework** v3.10
- Celery (예정)
- Redis (예정)
- Fabric3
- AWS 
    - EC2(Ubuntu 18.04)
    - RDS(PostgreSQL)
- Nginx, UWSGI

# Client
- [Kakao i 오픈빌더 베타](https://i.kakao.com/openbuilder)\
*베타이므로 개발자 등록이 필요합니다.*
- [오픈빌더 Document](https://i.kakao.com/docs/getting-started-overview)


# Before Start..
### 보안 관련 파일이 필요합니다.
- secrets.json (민감한 정보)
- deploy.json (배포 관련 환경변수)
- cole-rochman.pem (ssh 접속)

### Commit Rule
1. 최대한 작은 단위로 나눠서 커밋하도록 합니다.
2. Merge는 squash 방식을 지향합니다.
3. pyenv와 함께 virtualenv 사용을 권장합니다.
    - python version: v3.7.4
4. 아래 prefix를 붙여주세요.
    - 추가 : 기능 및 새로운 코드 추가
    - 수정 : 기존 코드 또는 로직의 수정
    - 리팩토링 : 리팩토링
    - 삭제 : 기존 코드 삭제

# Start
1. pip 설치
```
pip install -r requirements.txt
```
2. django runserver 확인

```
./manage.py runserver
```
3. test

```
./manage.py test --keepdb
```
4. 배포

```
fab deploy
```
5. 코드 변경없이 서버 리프레시만 하고자 할때

```
fab refresh
```

### Code
- API는 boilerplate를 줄이기 위해 아래 두 모듈을 사용합니다.
    - [helper](https://github.com/hanqyu/cole-rochman/blob/master/core/api/util/helper.py)
        - API 미들웨어 역할 (request parsing, user_id에 따른 patient 객체 준비 등)
    - [response_builder](https://github.com/hanqyu/cole-rochman/blob/master/core/api/util/response_builder.py)
        - Skill과 Validation 두가지 케이스
        - 오타로 인한 에러를 줄이기 위해 이 모듈을 사용하도록 합니다.

### Trouble Shooting
- uwsgi 관련 에러가 나는 경우
  - window 환경에서는 uwsgi를 설치할 수 없습니다. requirements.txt에서 uwsgi를 제거하고 진행하세요
  - uwsgi 환경은 별도로 돌아가고 있기 때문에 production에 영향을 미치지 않습니다.

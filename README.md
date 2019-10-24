# sns-scraping

# How to Run

## Facebook
- 중요 사항 : ChromeDriver를 구동 pc에 맞는 버젼으로 설치, 프로그램에 필요한 모듈 설치(.py 내에 있음.)
=> https://chromedriver.chromium.org/downloads
      
      
- Facebook scrap -
  1. facebook_scrap_db.sql를 먼저 실행하여, 테이블 생성
  2. facebook_scrap.py의 74 line의 chromedriver Path를 사용자가 저장한 path로 변경
  3. 423 line의 데이터베이스 연결 form 수정 (424 line의 주석 참조)
    * form : DATABASENAME://ID:PASSWORD@ADDRESS/SCHEMANAME?charset=utf8mb4
      (Ex. mysql://hwchoi96:1234@localhost/facebook_scrap?charset=utf8mb4
  4. scrap할 facebook Page ID 입력
    * Page ID = facebook 화면 왼쪽 상단의 검색 바에서 페이지를 검색하면 
      url에 www.facebook.com/PAGEID/가 뜨는데, PAGEID가 해당 페이지의 Page ID임.
  5. scrap를 하기 앞서, 먼저 scrap를 할 범위 입력
    * 1 scope = PageDown 키를 한 번 누른 범위
  6. 잠시 대기 후 결과 확인

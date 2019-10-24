'''
    Facebook Crawling Program

    1. 페이스북의 크롤링하고 싶은 페이지 id를 입력한다.
        - ex) JTBC NEWS를 크롤링하고 싶을 때, url에 https://www.facebook.com/jtbcnews/
              처럼 jtbcnews가 페이지 id가 된다.

    2. 스크롤링할 횟 수를 입력하여 그 범위만큼의 정보를 프로그램으로 가져온다.
        - 한 횟수만큼 스크롤링 범위 = page down키를 눌렀을 때, 나온 범위

    3. 잠시 기다리면 해당 페이지에 대한 요약 정보들이 출력된다.

    - 좋아요, 공유수, 댓글수 등은 엑셀 등의 프로그램에서 차트를 그리기 편하도록,
      정수형 데이터로 변환하여 저장하도록 함.

'''
# 필요한 모듈,
# pip install beautifulsoup4
# pip install selenium
# pip install sqlalchemy



# 크롤링 대상 - 특정 페이지의 게시물들의 반응
# 글 제목, 글 내용, 작성된 시간
# 좋아요 종류 - 좋아요, 최고예요, 웃겨요, 멋져요, 슬퍼요, 화나요
# 댓글 수, 공유 횟 수
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table


from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time



################ 페이지의 한 게시물 내용을 갖는 클래스###################
class Content:
    def __init__(self, id, author, time, contents, total_likes,
                 react, comment_count, share_count):
        super().__init__()
        self.id = id
        self.author = author
        self.time = time
        self.contents = contents
        self.total_likes = total_likes
        self.react = react
        self.comment_count = comment_count
        self.share_count = share_count

    def display_obj_info(self):
        print('>>>')
        print('\t글 고유 ID : ', self.id)
        print('\t글 작성자 : ', self.author)
        print('\t글 작성시간 : ', self.time)
        print('\t글 내용 : ', self.contents)
        print('\t글 좋아요 수 : ', self.total_likes)
        print('\t글 Best React 3. : ', self.react)
        print('\t글 댓글 수 : ', self.comment_count)
        print('\t글 공유 수 : ', self.share_count)


content_list = []
# 크롤링한 게시물을 저장할 리스트



print('Waiting for minute to program load complete')

driverPath = 'D:/ChromeDriver/chromedriver.exe'
# link to selenium chrome driver
# 구동 pc의 크롬 버젼에 맞는 driver를 설치하고 그 경로로 연결.
# https://chromedriver.chromium.org/downloads


driver = webdriver.Chrome(driverPath)
# selenium의 기능을 Chrome으로 연결


user_input = input('Facebook Page ID : ')
# Page ID를 입력받음.
url = 'https://www.facebook.com/' + user_input.strip() + '/'
url.strip()
driver.get(url)



############## Selenium 초기 세팅 #################
body = driver.find_element_by_tag_name('body')

def page_down(count = 100):
    i = 0
    while i < count:
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.05)
        i = i + 1
    print('done')
        # facebook 스크롤을 내려서 데이터를 불러옴으로서
        # JS로 이루어진 동적인 웹에 반응하도록 함.


def find_page_info():
    # 특정 페이지의 좋아요 개수, 팔로우 개수 출력
    page_info_list = []
    for i in range(0, len(page_community_info)):
        text = page_community_info[i].text
        if text.__contains__('좋아'):
            page_info_list.append(text)
            page_liker = text.split('명')[0].strip() # 페이지 좋아요 수 구하기.
            page_liker = page_liker.replace(',', '')
            # 100,000,000 처럼 , 삭제
            page_liker = int(page_liker)
        if text.__contains__('팔로우'):
            page_info_list.append(text)
            page_follower = text.split('명')[0].strip()
            page_follower = page_follower.replace(',', '')
            page_follower = int(page_follower)
    return page_info_list, page_liker, page_follower
################################################

num = input('Input the Scrolling page count : ').strip()
page_down(int(num))
# 사용자로 부터 스크롤링할 범위를 입력받음.

time.sleep(3)
# selenium에서 충분히 데이터가 로딩될 때까지 대기함.


total_page_text = driver.page_source

soup = BeautifulSoup(total_page_text, 'html.parser')
page_info = soup.find_all('div', attrs={'class':'_4-u2 _6590 _3xaf _4-u8'})
page_community_info = soup.find_all('div', attrs={'class':'_4bl9'})

page_info_list, page_liker, page_follower = find_page_info()
# 페이지에 관련된 좋아요, 팔로워 수를 가져옴

now = time.localtime()
current_time = "%04d-%02d-%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
print('크롤링 기준 시간 - ', current_time)


print('> Page Information <')
print('Page Name : ', user_input, '\t', page_info_list[0], '\t', page_info_list[1])
print('>>>>>>>> crawling result.')



######### 실제 게시물 크롤링 작업 #########
def search_information(content_list):
    # 실제 크롤링이 수행될 코드, content_list는 bs4으로 추출된 클래스 정보가 들어가 있음.

    list_count = 0

    for i in range(0, len(content_list)):
        one_id = '' # 글 고유 id값 -> + 크롤링 기준 시간으로 DB의 Primary key
        one_contents = ''  # 글 내용
        one_time = ''  # 글 작성시간
        one_total_likes = 0 # 글 총 좋아요 개수
        one_react = ''  # 글에 대한 좋아요 반응(Best React 3 종류 추출가능)
        one_comment_count = 0  # 글에 대한 댓글 수
        one_share_count = 0  # 글에 대한 공유 수



        one_list = content_list[i]
        # 한 게시물에 대한 정보


        try :
            # 한 페이지에 사진, 동영상 등을 모아놓은 클래스들도
            # 게시물과 같은 특징을 가지고, id값을 가지고 있으므로, 이는 건너뜀.
            if one_list['id'] is not None:
                continue
        except:
            pass

        #### 글 고유 ID값 뽑기 ####
        id = one_list.find_all('div', attrs={'class':'_4-u2 mbm _4mrt _5jmm _5pat _5v3q _7cqq _4-u8'})
        if id:
            one_id = id[0]['aria-describedby']


        #### 글 내용 뽑기 ####
        contents = one_list.find_all('div', attrs={'data-testid':'post_message'})
        # 글 내용은 무슨 태그든 post_message 속성을 가지고 있음.

        for i in range(0, len(contents)):
            # 글 내용 뽑아내기
            # 글 내용에는 바로 내용이 작성된 경우도 있지만,
            # 한 번 더 태그가 들어간 경우가 있어서 이 또한 검사해야함.
            if contents:
                deep = contents[i].find_all('div', attrs={'class':'text_exposed_root'})
                if deep:
                    for i in range(0, len(deep)):
                        one_contents = one_contents + deep[i].text
                else:
                    one_contents = one_contents + contents[i].text

            if len(one_contents) >= 1000:
                # DB에는 최대 1000글자까지 들어갈 수 있음.
                one_contents = one_contents[:999]




        #### 글 작성시간 뽑기 ####
        ## 시간은 local time이 달라 -4시간 정도의 오차가 남.
        time = one_list.find_all('abbr', attrs={'title' is not None})
        if time != [] or len(time) != 0:
            one_time = time[0]['title']


        ### 글 총 좋아요 개수 가지고 오기 ###
        total_likes = one_list.find_all('span', attrs={'class':'_81hb'})
        if total_likes:
            flag = '.'
            one_total_likes = total_likes[0].text
            # 총 좋아요 표시 양식은 5가지임.
            # ###, @@@ -> 특정 사람 이름.
            # 1. ###, @@@, 외 1.1만명
            # 2. ###, @@@, 외 1.1천명
            # 3. 1.1만
            # 4. 4.5천
            # 5. 562
            # 위의 케이스를 나눈 이유는 회원으로 크롤링하는 경우와,
            # 비회원으로 크롤링하는 경우 모두 동일하게 처리하기 위함.

            if one_total_likes.__contains__('외 '):
                # case 1, 2의 ###, @@@, 외 n.n%명에 해당하는 경우
                one_total_likes = one_total_likes.split('외 ')[1]
                if one_total_likes.__contains__('만'):
                    # case 1에 해당하는 경우.
                    one_total_likes = one_total_likes.replace('만명', '').strip()
                    if flag in one_total_likes:
                        # 3.4만명 처럼 소수점 표시가 있는 경우
                        likes = int(one_total_likes.split('.')[0]) * 10000
                        likes = likes + int(one_total_likes.split('.')[1]) * 1000
                    else:
                        # 3만명 처럼 소수점 표시가 없는 경우
                        likes = int(one_total_likes) * 10000
                    one_total_likes = likes
                elif one_total_likes.__contains__('천'):
                    # case 2에 해당하는 경우
                    one_total_likes = one_total_likes.replace('천명', '').strip()
                    if flag in one_total_likes:
                        # 3.4천명 처럼 소수점 표시가 있는 경우
                        likes = int(one_total_likes.split('.')[0]) * 1000
                        likes = likes + int(one_total_likes.split('.')[1]) * 100
                    else:
                        # 3천명 처럼 소수점 표시가 없는 경우
                        likes = int(one_total_likes) * 1000
                    one_total_likes = likes
            elif one_total_likes.__contains__('만'):
                one_total_likes = one_total_likes.replace('만', '').strip()
                # case 3에 해당하는 경우
                if flag in one_total_likes:
                    # 3.4만명 처럼 소수점 표시가 있는 경우
                    likes = int(one_total_likes.split('.')[0]) * 10000
                    likes = likes + int(one_total_likes.split('.')[1]) * 1000
                else:
                    # 3만명 처럼 소수점 표시가 없는 경우
                    likes = int(one_total_likes) * 10000
                one_total_likes = likes
            elif one_total_likes.__contains__('천'):
                one_total_likes = one_total_likes.replace('천', '').strip()
                # case 4에 해당하는 경우
                if flag in one_total_likes:
                    # 3.4천명 처럼 소수점 표시가 있는 경우
                    likes = int(one_total_likes.split('.')[0]) * 1000
                    likes = likes + int(one_total_likes.split('.')[1]) * 100
                else:
                    # 3천 처럼 소수점 표시가 없는 경우
                    likes = int(one_total_likes) * 1000
                one_total_likes = likes
            else:
                # case 5에 해당하는 경우
                one_total_likes = int(one_total_likes)
        else:
            # 아예 좋아요가 없는 경우
            one_total_likes = 0



        react = one_list.find_all('div', attrs={'class': '_68wo'})
        ### 게시물에 대한 반응은 최대 종류 3개까지 수집이 가능함.
        # 반응 = 좋아요 개수 및 종류, 댓글 개수, 공유 횟수에 관한 정보를 크롤링
        for i in range(0, len(react)):
            r = react[i].find_all('span', attrs={'aria-label' is not None})
            # aria-label에는 각 게시물에 관한 좋아요 정보가 들어가 있음.
            try:
                react1 = ''
                react2 = ''
                react3 = ''
                react1 = r[1].find_all('a', attrs={'aria-label' is not None})[0].attrs['aria-label']
                # Best 1
                react2 = r[3].find_all('a', attrs={'aria-label' is not None})[0].attrs['aria-label']
                # Best 2
                react3 = r[5].find_all('a', attrs={'aria-label' is not None})[0].attrs['aria-label']
                # Best 3
                str = react1 + ' ' + react2 + ' ' + react3
                one_react = str
                # 각 게시물의 최고 반응 3개를 추출하여 저장하는 과정
            except Exception:
                if react1 == '' and react2 == '' and react3 == '':
                    str = '0'
                # 좋아요가 달리지 않은 게시물에 대한 처리
                if react1 is not '':
                    str = react1
                if react2 is not '':
                    str = str + ' ' + react2
                if react3 is not '':
                    str = str + ' ' + react3
                one_react = str
            # 가끔씩 best 3 react가 없는 게시글도 있기 때문에 이 부분을 예외처리 하도록 함.




        #### 댓글 수를 가져오는 과정 ####
        comment_count = one_list.find_all('a', attrs={'class': '_3hg- _42ft'})
        if comment_count:
            flag = '.'
            one_comment_count = comment_count[0].text
            one_comment_count = one_comment_count.split(' ')[1].strip()
            # 결과로는 '댓글 40개'로 나오기 때문에, 숫자 데이터만 남길 필요가 있음.
            one_comment_count = one_comment_count[:-1]
            if one_comment_count.__contains__('천'):
                one_comment_count = one_comment_count.replace('천', '')
                if flag in one_comment_count:
                    # 1.3천처럼 소수점 단위가 있는 경우.
                    comments = int(one_comment_count.split('.')[0]) * 1000
                    comments = comments + int(one_comment_count.split('.')[1]) * 100
                else:
                    comments = int(one_comment_count.split('.')[0]) * 1000
                one_comment_count = comments
            elif one_comment_count.__contains__('만'):
                one_comment_count = one_comment_count.replace('만', '')
                if flag in one_comment_count:
                    # 3.4만처럼 소수점 단위가 있는 경우.
                    comments = int(one_comment_count.split('.')[0]) * 10000
                    comments = comments + int(one_comment_count.split('.')[1]) * 1000
                else:
                    comments = int(one_comment_count.split('.')[0]) * 10000
                one_comment_count = comments
            else:
                one_comment_count = int(one_comment_count)
        else:
            one_comment_count = 0



        #### 공유 수를 가져오는 과정 ####
        share_count = one_list.find_all('a', attrs={'class': '_3rwx _42ft'})
        if share_count:
            one_share_count = share_count[0].text
            one_share_count = one_share_count.split(' ')[1].strip()
            one_share_count = one_share_count[:-1]
            if one_share_count.__contains__('천'):
                one_share_count = one_share_count.replace('천', '').strip()
                if flag in one_share_count:
                    # 1.3천처럼 소수점 단위가 있는 경우.
                    shares = int(one_share_count.split('.')[0]) * 1000
                    shares = shares + int(one_share_count.split('.')[1]) * 100
                else:
                    shares = int(one_share_count.split('.')[0]) * 1000
                one_share_count = shares
            elif one_share_count.__contains__('만'):
                one_share_count = one_share_count.replace('만', '').strip()
                if flag in one_share_count:
                    # 3.4만처럼 소수점 단위가 있는 경우.
                    shares = int(one_share_count.split('.')[0]) * 10000
                    shares = shares + int(one_share_count.split('.')[1]) * 1000
                else:
                    shares = int(one_share_count.split('.')[0]) * 10000
                one_share_count = shares
            else:
                one_share_count = int(one_share_count)
        else:
            one_share_count = 0




        ## >>최종처리 과정<< ##
        if (one_contents != '') and (one_time != '') and (one_react != '') \
            and (one_comment_count != 0) and (one_share_count != 0):
            list_count = list_count + 1
            content = Content(one_id, user_input, one_time, one_contents, one_total_likes,
                              one_react, one_comment_count, one_share_count)
            crawling_list.append(content)

    return list_count


##### 크롤링 메소드 호출 부분 #####
count = 0
crawling_list = []

content_list = soup.find_all('div', attrs={'class':'_5va1 _427x'})
# 초기 추천 게시글에 대한 정보를 뽑아냄
count = search_information(content_list)

content_list = soup.find_all('div', attrs={'class':'_4-u2 _4-u8'})
count = count + search_information(content_list)

print('총 %d개의 게시글 발견.' % count)

for i in range(0, len(crawling_list)):
    crawling_list[i].display_obj_info()





############################# 데이터 베이스 연결 ############################

def get_engine():
    engine = create_engine('mysql://root:chl12055205@localhost/facebook?charset=utf8mb4',
                           convert_unicode=True)
    # create_engine('SQL종류://ID:PASSWORD@ADDRESS/TABLENAME?charset=utf8mb4)
    return engine

def init_db():
    Base.metadata.create_all(engine)

engine = get_engine()
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()
init_db()
#sqlalchemy insert init
conn = engine.connect()
metadata = MetaData(bind=engine)

conn.execute('SET NAMES utf8mb4;')
conn.execute('SET CHARACTER SET utf8mb4;')
conn.execute('SET character_set_connection=utf8mb4;')
# 한글 깨짐 문제를 최대한 예방하기 위한 코드


print('\n데이터 베이스에 삽입.')
influencer_table = Table('facebook_Influencer', metadata, autoload=True)
insert_table = influencer_table.insert()

insert_table.execute(username=user_input, scrap_time=current_time,
                     followers=page_follower, likers=page_liker)
# 먼저, 페이지에 대한 정보를 DB에 저장


post_table = Table('facebook_post', metadata, autoload=True)
insert_table=post_table.insert()

for data in crawling_list:
    insert_table.execute(id=data.id, scrap_time=current_time,
                         contents=data.contents, post_time=data.time,
                         username=user_input, likes=data.total_likes,
                         best3_react=data.react, comments=data.comment_count,
                         shares=data.share_count)
# 각 게시물에 대한 정보를 DB에 저장
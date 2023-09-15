import cv2 
import mediapipe as mp
import time
import pygame 
import sys 
from pygame.locals import *
import math 
import random 

# 상수 설정 
width = 600 
height = 400
white = (255, 255, 255)
black = (  0,   0,   0)
runCount = 0

#카메라 입력 설정 
cap = cv2.VideoCapture(cv2.CAP_DSHOW + 0) 

#pygame 창 설정
pygame.init() # pygame 초기화
pygame.display.set_caption('avoid_game') # 창 Title
screen = pygame.display.set_mode((width, height), 0, 32) #pygame을 띄울 창 설정
gulimfont = pygame.font.SysFont('굴림', 70) # pygame 내부에서 사용할 글씨체 설정
clock = pygame.time.Clock()

# 손인식 ------------------------------------------------------------------------------------------------------------------------------
mpHands = mp.solutions.hands # hand 처리를 위한 code 
hands = mpHands.Hands() # 손 감지 모델을 load 하고 사용하기 위한 code
mpDraw = mp.solutions.drawing_utils # hand 이미지 위에 랜드마크를 그리기 위한 code
ids = [4,8,12,16,20] # 각 손가락 맨 끝의 landmark를 리스트에 저장 

# 게임 내부에서 사용할 이미지 로드 
char = pygame.image.load("project/dora.png")
char1 = pygame.transform.scale(char,(50,50))
enemy = pygame.image.load("project/enemy1.png")
enemy1 = pygame.transform.scale(enemy,(50,50))
light = pygame.image.load("project/smalllight.png")
light1 = pygame.transform.scale(light,(50,50))

# 플레이어 설정
char1_x = width / 2 
char1_y = height /2
char1_speed = 5

# 처음 게임 상태 설정
game_over = False
score = 0

# 장애물 클래스 생성 
class Obstacle:
    def __init__(self, x, y, speed_x=0, speed_y=0):
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y

# 장애물이 생성되었을 때 장애물 하나하나를 저장하기 위한 list 
obstacle_list = []

# 손가락의 위치를 감지하는 함수 -----------------------------------------------------------------------------------------
def fingerPosition(image, handNo=0):
    lmList = []
    # 만약 랜드마크 정보가 감지 되었다면 
    if results.multi_hand_landmarks:
        # 그정보를 myHand에 저장 
        myHand = results.multi_hand_landmarks[handNo]
        # enumerate는 튜플을 생성함 
        # myHand 라는 랜드마크 정보의 인덱스를 id에 저장 요소 정보를 lm에 저장 
        for id, lm in enumerate(myHand.landmark):
            # 매개변수로 받아온 image 의 h(height), w(width), c(channel)정보를 가져옴
            h, w, c = image.shape
            # 요소정보 lm(랜드마크)의 x, y 위치정보와 width, height를 각각 곱한 정수를 cx, cy에 저장
            cx, cy = int(lm.x * w), int(lm.y * h)
            # 위에서 지정한 lmList라는 리스트에 인덱스와 cx, cy정보를 추가
            lmList.append([id, cx, cy])
    return lmList

#위 -> 아래 , 아래 -> 위로 움직이는 적 생성
def generate_upward_obstacle():
    x = random.randint(0, width - 50)
    y = 0 if random.randint(0, 1) == 0 else height - 50
    speed_y = 5 if y ==0 else -5
    obstacle_list.append(Obstacle(x, y, speed_y=speed_y))
    
    
# 좌 -> 우 , 우  -> 좌 로 움직이는 적 생성
def generate_sideways_obstacle():
    x = 0 if random.randint(0, 1) == 0 else width - 50
    y = random.randint(50, height - 50)
    speed_x = 5 if x == 0 else -5
    obstacle_list.append(Obstacle(x, y, speed_x=speed_x))

# 장애물 이동 함수
def move_obstacles():
    for obstacle in obstacle_list:
        obstacle.move()

# 장애물 그리기 함수
def draw_obstacles():
    for obstacle in obstacle_list:
        screen.blit(enemy1, (obstacle.x, obstacle.y))

# 충돌 판정 함수
def is_collision(char_x, char_y, obstacle):
    # math.sqrt = 제곱근 , ** -> 제곱
    distance = math.sqrt((char_x - obstacle.x) ** 2 + (char_y - obstacle.y) ** 2)
    if distance < 30:
        return True
    return False

# 초기값 설정 
modenum = 0
start_time = time.time()
startnum = 0 
tick_time = 0
boom = 1

#무한 반복문 시작 
while True:
    #카메라 읽어옴 (True or False 의 bool값 과 실제로 읽어온 frame)
    success, img = cap.read()
    # 게임 시작전 화면 구성 
    if startnum ==0:
        screen.fill(white)
        startPage1 = gulimfont.render(f"put on your hand", True, (255, 0, 0))
        screen.blit(startPage1, (width / 2 -200 , height / 2 -50))
        startPage2 = gulimfont.render(f"on screen", True, (255, 0, 0))
        screen.blit(startPage2, (width / 2 -100 , height / 2 ))
        pygame.display.update() 
        startnum = 1
    # 시작 화면에 손을 인식할 시 
    if startnum ==1:
        # game_over 가 True 라면 
        if game_over is True:
            screen.fill(white)
            retry = gulimfont.render(f"ReTry?", True, (255, 0, 0))
            screen.blit(retry, (width / 2 -150 , height / 2 -50))
            boom = 1
            modenum = 0
            enemy1 = pygame.transform.scale(enemy,(50,50))
            pygame.display.update() 
            cv2.waitKey()
            game_over = False
        #만약 pygame이 끝났다는 이벤트가 오면 game_over = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True

        # 게임 시간 계산 
        current_time = time.time()
        elapsed_time = current_time - start_time
        
        # game_over가 True 가 아니라면 
        if not game_over:
            # 카메라 얻어온 것을 BGR -> RGB로 바꿈
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            # 손을 감지 하고 추적함
            results = hands.process(imgRGB)
            list = fingerPosition(img)
            # 손을 인식하고 손의 landmark 8번에 설정한 색의 동그라미를 그림 (카메라 인식을 확인하기 위해 사용)
            if results.multi_hand_landmarks:
                for handLandmarks in results.multi_hand_landmarks:
                    for id, lm in enumerate(handLandmarks.landmark):
                        h, w, c = img.shape
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        #검지 끝
                        if id == 8:
                            cv2.circle(img, (cx, cy), 15, (90, 180, 0), cv2.FILLED)
            # 스크린을 반복문 돌 때마다 흰색으로 채워줌 (캐릭터와 적의 이동 전 이미지를 없앰)                          
            screen.fill(white)
            
            #폭탄의 초기설정
            boomnum = gulimfont.render("boom : %d" %boom, 1, (255,0,0))
            screen.blit(boomnum, (0, 0))  
            
            # char1의 위치를 얻음 
            char_rect = char1.get_rect()
            
            # 만약 손가락 2개를 인식하여 모드를 바꾼다면 Hard라는 텍스트를 띄움 
            if modenum == 1 :
                mode = gulimfont.render("Hard", 1, (255,0,0))
                screen.blit(mode, (480, 0))       
                
            # 손가락을 인식한 리스트의 개수가 0이 아니라면 손가락의 개수를 셈 
            if len(list) != 0:
                fingers = []
                for id in range(1, 5):
                    # ids는 각 손가락 끝을 저장한 list 
                    # 손 끝 랜드마크의 cy 가 해당 랜드마크의 -2 즉 두 마디 밑의 랜드마크 보다 작다면 손가락 리스트에 1을 더함 
                    if list[ids[id]][2] < list[ids[id] - 2][2]:
                        fingers.append(1)
                    if (list[ids[id]][2] > list[ids[id] - 2][2] ):
                        fingers.append(0)
                totalFingers = fingers.count(1)
                
                #만약 손가락 개수가 0이라면 폭탄을 터트려 모든 적을 없애고 0.04초 delay
                if totalFingers == 0 :
                    screen.blit(char1,[(600-cx),(cy-150)])
                    if boom > 0:
                        boom -= 1
                        screen.blit(char1,[(600-cx),(cy-150)])
                        obstacle_list = []
                        time.sleep(0.04)
                #만약 손가락 개수가 1이라면 캐릭터를 움직이고 그 좌표값을 다른 변수에 저장 
                elif totalFingers == 1:
                    screen.blit(char1,[(600-cx),(cy-150)])
                    char1_x = 600-cx
                    char1_y = cy-150
                #만약 손가락 개수가 2라면 검지위치에 라이트 이미지를 띄우고 적들의 크기를 키우며 modenum을 1로 바꿈 
                elif totalFingers == 2 :
                    modenum = 1
                    screen.blit(light1,[(600-cx),(cy-150)])
                    distance = math.sqrt((200 - obstacle.x) ** 2 + (300 - obstacle.y) ** 2)
                    if distance < 500:
                        enemy1 = pygame.transform.scale(enemy,(80,80))
                        tick_time = pygame.time.get_ticks()
                    time.sleep(0.5)
                # 랜덤 값을 통해 위,아래로 움직이는 장애물 생성 
                if random.randint(0, 100) < 10:
                    generate_upward_obstacle()
                # 랜덤 값을 통해 좌,우로 움직이는 장애물 생성
                if random.randint(0, 100) < 10:
                    generate_sideways_obstacle()
                # 적 이동 및 그리기
                move_obstacles()
                draw_obstacles()
                # 적과 충돌했는지를 계속 체크 
                for obstacle in obstacle_list:
                    if is_collision(char1_x, char1_y, obstacle):
                        game_over = True
                        break
                # 화면 크기로 설정한 width와 height보다 작고 0보다 큰 x,y 값을 지닌 적들을 리스트에 저장 하여 출력 
                obstacle_list = [obstacle for obstacle in obstacle_list if 0 <= obstacle.x <= width and 0 <= obstacle.y <= height]      
                pygame.display.update()
                # 게임의 fps를 60으로 설정 (초당 60번)
                clock.tick(60)
            # 게임 오버 화면 표시
            if game_over:            
                game_over_text = gulimfont.render("Game Over", 1, (255,0,0))
                text = gulimfont.render(f"survive time: {int(elapsed_time)} Sec", True, (255, 0, 0))
                screen.blit(text, (width // 2 -250, height // 2))
                screen.blit(game_over_text, (width // 2 - 150, height // 2 - 50))
                char1_x = width // 2 - 25
                obstacle_list = []
                pygame.display.update()  
                time.sleep(2)                
                start_time = time.time()
            # 캠 화면 띄움 
            img = cv2.flip(img,1)
            cv2.imshow("Image", img)
            cv2.waitKey(1)
        
    # pygame.quit()
    # sys.exit()

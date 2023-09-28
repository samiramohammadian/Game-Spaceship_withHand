# imports :
import pygame
import time
import random
import cv2
import mediapipe as mp
import numpy as np

# Initialize 
pygame.init()

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False,
            max_num_hands=1, 
            min_detection_confidence=0.5, 
            model_complexity = 0)


# Constants
BACKGROUND_IMAGE = "sky.jpg"
SPACESHIP_IMAGE = "spaceship.png"
SHOT_IMAGE = "shot.png"
OBSTACLE_IMAGES = ["obstacle1.png", "obstacle2.png", "obstacle3.png", "obstacle4.png", "obstacle5.png", "obstacle6.png", "obstacle7.png"]

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 0, 0)

SPACESHIP_WIDTH = 50
SPACESHIP_HEIGHT = 40

SHOT_WIDTH = 10
SHOT_HEIGHT = 30

#################################### we can use OBSTACLE instend of THING
THING_WIDTH = 50
THING_HEIGHT = 50

OBSTACLE_SPEED_INIT = 7

shooting = False 

frame_skip = 3
frame_count = 0

obstacle_speed = 7
num_obstacles = 5
# distance every object in y 
spacing = 150

# loading images and setting up
backgroundImg = pygame.image.load(BACKGROUND_IMAGE)
DISPLAY_WIDTH, DISPLAY_HEIGHT = backgroundImg.get_size()
gameDisplay = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
pygame.display.set_caption('Spaceship Game ... ')

spaceshipImg = pygame.transform.scale(pygame.image.load(SPACESHIP_IMAGE), (SPACESHIP_WIDTH, SPACESHIP_HEIGHT ))
shotImg = pygame.transform.scale(pygame.image.load(SHOT_IMAGE), (SHOT_WIDTH, SHOT_HEIGHT))


obstacle_images = []
for img in OBSTACLE_IMAGES:
    image = pygame.image.load(img)  # Load the image
    scaled_image = pygame.transform.scale(image, (THING_WIDTH, THING_HEIGHT))  # Scale the image
    obstacle_images.append(scaled_image)  # Append the scaled image to the list

# class for obstacle 
class Obstacle:
    def __init__(self, x, y, speed, image):
        self.x = x
        self.y = y
        self.speed = speed
        self.image = image

# class for shot 
class Shot:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed


# if obstacle collidin with spacehip return True 
def is_colliding(rect1,rect2):
    x1,y1,w1,h1 = rect1
    x2,y2,w2,h2 = rect2
    return (x1<x2+w2 and x1+w1>x2 and y1<y2+h2 and y1+h1>y2)
    
# display spaceship
def spaceship(x, y):
    gameDisplay.blit(spaceshipImg, (int(x),int( y)))

# display obstacle  
def things(obstacle):
    gameDisplay.blit(obstacle.image, (int(obstacle.x), int(obstacle.y)))

# if you collision with obstacle this function called
def game_over(score):
    
    gameDisplay.fill(WHITE)
    font = pygame.font.Font('freesansbold.ttf', 90)
    text = font.render("You Lose!", True, RED)
    gameDisplay.blit(text, (int(DISPLAY_WIDTH/4), int(DISPLAY_HEIGHT/3)))
    best_score = get_best_score()
    # for checking record 
    if score > best_score:
        save_best_score(score)
        show_new_record()
    else:
        pygame.display.update()
        time.sleep(3)  # Display the message for 3 seconds before quitting
    quit()

# displaying the player's score 
def show_score(score):
    font = pygame.font.SysFont(None, 35)  # default system font, Increased size from 25 to 35
    text = font.render("Score: " + str(score), True, WHITE)  # Changed color to WHITE
    gameDisplay.blit(text, (10, 10)) # loc


def get_best_score():
    try:
        #read from best_score.txt
        with open('best_score.txt', 'r') as file:
            return int(file.read())
    except FileNotFoundError:
        return 0
    
def save_best_score(score):
    # write in best_score.txt 
    with open('best_score.txt', 'w') as file:
        file.write(str(score))
        
# iif you set new record after you game over show you it 
def show_new_record():
    gameDisplay.fill(BLACK)  
    font = pygame.font.SysFont(None, 50)  
    text = font.render("You set a new record!", True, WHITE)
    textRect = text.get_rect() # location of rectangle
    textRect.center = (int(DISPLAY_WIDTH / 2), int(DISPLAY_HEIGHT / 2))
    gameDisplay.blit(text, textRect)
    pygame.display.update()  
    time.sleep(3)  

# when after 30 sec of satrting game show you it 
def show_speed_up():
    font = pygame.font.SysFont(None, 75)  # Make font size bigger, say 75
    text = font.render("Speed Up!", True, WHITE)
    textRect = text.get_rect()
    textRect.center = (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT / 2)  # Center the text
    gameDisplay.blit(text, textRect)


obstacles = []  # Initialize an empty list to store obstacles
for i in range(num_obstacles):
    # Generate random coordinates for the obstacle
    x = random.randrange(0, DISPLAY_WIDTH - THING_WIDTH)
    y = -i * spacing  # every obstacles be uper that next obstacles
    
    # Create an Obstacle instance and append it to the list
    obstacle = Obstacle(x, y, obstacle_speed, random.choice(obstacle_images))
    obstacles.append(obstacle)



#active_shots = []
shot_speed = -10
speed_up_display_duration = 3
speed_up_display_start_time = 0

def game_loop():
    global frame_count , shooting , speed_up_display_start_time
    
    x = (DISPLAY_WIDTH * 0.45)  # starting position of the spaceship 
    y = (DISPLAY_HEIGHT * 0.8)

    x_change = 0    # control horizontal movemen
    score = 0
    start_time = time.time()
    obstacle_speed = OBSTACLE_SPEED_INIT
    last_speed_increase_time = start_time

    active_shots = []
    obstacle_addition_interval = 25 # every 25 s
    gameExit = False

    while not gameExit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gameExit = True

        ret, frame = cap.read()
        frame_count += 1
        if ret and frame_count % frame_skip == 0 : # every 3 frame 
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame) # return a object that have landmarks 
            shooting = False 
            # Inside the game loop where hand tracking is performed
            if results.multi_hand_landmarks:
                for landmarks in results.multi_hand_landmarks:
                    index_tip = landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP] # the landmark about index  
                    middle_tip = landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]# the landmark about middle   

                    # Get the x-coordinate and y-coordinate of Landmark 8 (index finger tip)  pixel
                    index_x = int(index_tip.x * DISPLAY_WIDTH)
                    index_y = int(index_tip.y * DISPLAY_HEIGHT)
                    # Get the y-coordinate of Landmark 12 (middle finger tip) 
                    middle_y = int(middle_tip.y * DISPLAY_HEIGHT)    

                    # Adjust the spaceship's position based on the x-coordinate of Landmark 8
                    if index_x > DISPLAY_WIDTH * 0.6:  # You can adjust this threshold as needed
                        # Move the spaceship to the right
                        x_change = -9
                    elif index_x < DISPLAY_WIDTH * 0.4:
                        # Move the spaceship to the left
                        x_change = 9
                    else:
                        x_change = 0

                    if index_y < middle_y:
                        shooting = True
                        #print("strt")
                        # Shoot when index finger is above middle finger
                        
                    # else :
                    #     shooting = False 
                            # Create a new shot and add it to the active shots list
                if shooting:
                # Create a new shot and add it to the active shots list
                    new_shot = Shot(x + SPACESHIP_WIDTH / 2 - SHOT_WIDTH / 2, y, shot_speed)
                    active_shots.append(new_shot)
                        
        x += x_change
        
        if x > DISPLAY_WIDTH - SPACESHIP_WIDTH:
            x = DISPLAY_WIDTH - SPACESHIP_WIDTH
        elif x < 0:
            x = 0

        gameDisplay.blit(backgroundImg, (0, 0)) # showing background 


        shots_to_remove = []
        for shot in active_shots[:]:
            gameDisplay.blit(shotImg, (int(shot.x), int(shot.y))) # display shot
            shot.y += shot.speed

            if shot.y + SHOT_HEIGHT < 0: # out of screen 
                shots_to_remove.append(shot)

            for obstacle in obstacles[:]:
                if (shot.x + SHOT_WIDTH > obstacle.x and 
                    shot.x < obstacle.x + THING_WIDTH and 
                    shot.y + SHOT_HEIGHT > obstacle.y and 
                    shot.y < obstacle.y + THING_HEIGHT):

                    shots_to_remove.append(shot) # remove the shot 
                    obstacles.remove(obstacle)  # remove the hit obstacle
                    new_obstacle = Obstacle(random.randrange(0, DISPLAY_WIDTH - THING_WIDTH) 
                                            , 0 - THING_HEIGHT, 
                                            obstacle_speed, 
                                            random.choice(obstacle_images))
                    
                    obstacles.append(new_obstacle)  # add a new one at the top
                    score += 5

        # remove that shot collirsion to Obstacle
        for shot in shots_to_remove:
            if shot in active_shots:
                active_shots.remove(shot)

        for obstacle in obstacles:
            things(obstacle)
            obstacle.y += obstacle.speed
            if obstacle.y > DISPLAY_HEIGHT: # out of windows
                # create new obstacles
                obstacle.x = random.randrange(0, DISPLAY_WIDTH - THING_WIDTH)
                obstacle.y = 0 - THING_HEIGHT
                score += 1   # add score 1

        show_score(score)

        # speed of obstacle up 
        current_time = time.time()
        if current_time - last_speed_increase_time > obstacle_addition_interval:
            obstacle_speed += 2
            last_speed_increase_time = current_time
            speed_up_display_start_time = current_time

        #time for display speed up 3 sec
        if current_time - speed_up_display_start_time < speed_up_display_duration:
            show_speed_up()


        spaceship_rect = (x,y ,SPACESHIP_WIDTH , SPACESHIP_HEIGHT )
        for obstacle in obstacles:
            obstacle_rect = (obstacle.x , obstacle.y , THING_WIDTH , THING_HEIGHT )
            if is_colliding (spaceship_rect , obstacle_rect):
                print("Collision detected with obstacle!")
                game_over(score)

        spaceship(x, y)
        pygame.display.update()

cap = cv2.VideoCapture(0)
# cap.set(3, 640)
# cap.set(4, 480)
game_loop()



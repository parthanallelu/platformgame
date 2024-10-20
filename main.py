from typing import Any
import pygame
from pygame.locals import *

pygame.init()

clock = pygame.time.Clock()
fps = 90


SCREENWIDTH = 800
SCREENHEIGHT = 800

screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
pygame.display.set_caption("Platformer Game")

#define font
font_score = pygame.font.SysFont('Arial',20)

# Define game variables
tile_size = 40
game_over = 0
main_menu = True
score = 0

#define color
white = (255, 255, 255) 

# Load images
sun_img = pygame.image.load(
    "C:\\Users\\DELL\\Desktop\\python_projects\\Platformer\\img\\sun.png"
)
bg_img = pygame.image.load(
    "C:\\Users\\DELL\\Desktop\\python_projects\\Platformer\\img\\sky.png"
)
restart_img = pygame.image.load(
    "C:\\Users\\DELL\\Desktop\\python_projects\\Platformer\\img\\restart_btn.png"
)
exit_img = pygame.image.load(
    "C:\\Users\\DELL\\Desktop\\python_projects\\Platformer\\img\\exit_btn.png"
)
start_img = pygame.image.load(
    "C:\\Users\\DELL\\Desktop\\python_projects\\Platformer\\img\\start_btn.png"
)
you_win_img = pygame.image.load(
    "C:\\Users\\DELL\\Desktop\\python_projects\\Platformer\\img\\you_win.png"
)
you_lose_img = pygame.image.load(
    "C:\\Users\\DELL\\Desktop\\python_projects\\Platformer\\img\\you_lose.png"
)


#draw text function
def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))


# Resize the background image to fit the screen
bg_img = pygame.transform.scale(bg_img, (SCREENWIDTH, SCREENHEIGHT))
start_img = pygame.transform.scale(start_img, (start_img.get_width() // 1.5, start_img.get_height() // 1.5))
exit_img = pygame.transform.scale(exit_img, (exit_img.get_width() // 1.5, exit_img.get_height() // 1.5))

def reset_level(world_data):
    # Clear sprite groups
    blob_group.empty()
    platform_group.empty()
    coin_group.empty()
    lava_group.empty()
    exit_group.empty()

    # Reset player position
    player.reset(85, SCREENHEIGHT - 110)

    # Create a new world with the original world data
    world = World(world_data)

    score_coin = Coin(tile_size // 2, tile_size // 2)
    coin_group.add(score_coin)
    
    return world


class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False

        #get mouse position
        pos = pygame.mouse.get_pos()

        #check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
                

        #draw button
        screen.blit(self.image,self.rect)

        return action


class Player():
    def __init__(self, x, y):
        self.reset(x,y)



    def update(self,game_over):
        dx = 0
        dy = 0
        walk_cooldown = 10
        collision_factor = 20

        if game_over == 0:
        # To get key presses
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and not self.jumped and not self.in_air:
                self.vel_y = -14
                self.jumped = True
            if not key[pygame.K_SPACE]:
                self.jumped = False
            if key[pygame.K_LEFT] or key[pygame.K_a]:
                dx -= 4
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT] or key[pygame.K_d]:
                dx += 4
                self.counter += 1
                self.direction = 1
            if not (key[pygame.K_RIGHT] or key[pygame.K_LEFT] or key[pygame.K_a] or key[pygame.K_d]):
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]
    

        # To handle animation
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            # Checking for collision 
            self.in_air = True
            for tile in world.tile_list:
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #check if below the ground i.e. jumping
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
				    #check if above the ground i.e. falling
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom 
                        self.vel_y = 0
                        self.in_air = False


            #check for collision with enemies
            if pygame.sprite.spritecollide(self,blob_group,False):
                game_over = -1

            #check for collision with lava
            if pygame.sprite.spritecollide(self,lava_group,False):
                game_over = -1

            #check for collision with exit
            if pygame.sprite.spritecollide(self,exit_group,False):
                game_over = 1

            #check for collision with platform
            for platform in platform_group:
                #collision in the x direction
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
				#collision in the y direction
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
					#check if below platform
                    if abs((self.rect.top + dy) - platform.rect.bottom) < collision_factor:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top
					#check if above platform
                    elif abs((self.rect.bottom + dy) - platform.rect.top) < collision_factor:
                        self.rect.bottom = platform.rect.top - 1
                        self.in_air = False
                        dy = 0
					#move sideways with the platform
                    if platform.move_x != 0:
                        self.rect.x += platform.move_direction


            # Update player coordinates
            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1:
            self.image = self.dead_image
            if self.rect.y > 200:
                self.rect.y -= 5

        # To draw player on the screen
        screen.blit(self.image, self.rect)
        

        return game_over
    

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        
        for i in range(1, 5):
            img_right = pygame.image.load(f"C:\\Users\\DELL\\Desktop\\python_projects\\Platformer\\img\\guy{i}.png")
            img_right = pygame.transform.scale(img_right, (30, 60))
            img_left = pygame.transform.flip(img_right,True,False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.dead_image = pygame.image.load("C:\\Users\\DELL\\Desktop\\python_projects\\Platformer\\img\\ghost.png")
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True


class World():
    def __init__(self, data):
        self.tile_list = []

        # Load images
        dirt_img = pygame.image.load("C:\\Users\\DELL\\Desktop\\python_projects\\Platformer\\img\\dirt.png")
        grass_img = pygame.image.load("C:\\Users\\DELL\\Desktop\\python_projects\\Platformer\\img\\grass.png")

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    blob = Enemy(col_count*tile_size-2, row_count*tile_size + 5)
                    blob_group.add(blob)
                if tile == 4:
                    platform = PLatform(col_count*tile_size, row_count*tile_size, 1, 0)
                    platform_group.add(platform)
                if tile == 5:
                    platform = PLatform(col_count*tile_size, row_count*tile_size, 0, 1)
                    platform_group.add(platform)    
                if tile == 6:
                    lava = Lava(col_count*tile_size, row_count*tile_size + (tile_size/2))
                    lava_group.add(lava)
                if tile == 7:
                    coin = Coin(col_count*tile_size+(tile_size//2), row_count*tile_size + (tile_size/2))
                    coin_group.add(coin)
                if tile == 8:
                    exit = Exit(col_count*tile_size, row_count*tile_size - 20)
                    exit_group.add(exit)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("C:\\Users\\DELL\\Desktop\\python_projects\\Platformer\\img\\blob.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) >50:
            self.move_direction *= -1
            self.move_counter *= -1

class PLatform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("C:\\Users\\DELL\\Desktop\\python_projects\\Platformer\\img\\platform.png")
        self.image = pygame.transform.scale(img, (tile_size,tile_size//2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0
        self.move_x = move_x
        self.move_y = move_y

    def update(self):
        self.rect.x += self.move_direction * self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.move_counter += 1
        if abs(self.move_counter) >50:
            self.move_direction *= -1
            self.move_counter *= -1


class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("C:\\Users\\DELL\\Desktop\\python_projects\\Platformer\\img\\lava.png")
        self.image = pygame.transform.scale(img,(tile_size,tile_size//2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("C:\\Users\\DELL\\Desktop\\python_projects\\Platformer\\img\\coin.png")
        self.image = pygame.transform.scale(img,(tile_size/2,tile_size/2))
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        
        

class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("C:\\Users\\DELL\\Desktop\\python_projects\\Platformer\\img\\exit.png")
        self.image = pygame.transform.scale(img,(tile_size,int(tile_size*1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        

world_data = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 2, 2, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 7, 0, 5, 5, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 3, 0, 5, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 1],
    [1, 7, 0, 0, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 7, 0, 0, 0, 0, 1],
    [1, 0, 2, 0, 0, 7, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 2, 2, 0, 4, 4, 0, 0, 0, 0, 3, 0, 0, 3, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 7, 0, 0, 0, 0, 2, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 0, 2, 2, 2, 2, 2, 1],
    [1, 0, 0, 0, 0, 0, 2, 2, 2, 6, 6, 6, 6, 6, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]


player = Player(85,SCREENHEIGHT - 110)

blob_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

#create dummy coin for showing the score
score_coin = Coin(tile_size // 2, tile_size // 2)
coin_group.add(score_coin)

world = World(world_data)

#create buttons
restart_button = Button(SCREENWIDTH/2-50, SCREENHEIGHT/2+100, restart_img)
start_button = Button(SCREENWIDTH/2-300, SCREENHEIGHT/2, start_img)
exit_button = Button(SCREENWIDTH/2+100, SCREENHEIGHT/2, exit_img)

run = True
while run:

    clock.tick(fps)

    screen.blit(bg_img, (0, 0))
    screen.blit(sun_img, (80, 75))

    if main_menu == True:
        if exit_button.draw():
            run = False
        if start_button.draw():
            main_menu = False
    else:
        world.draw()

        if game_over ==0:
            blob_group.update()
            platform_group.update()
            #checking if a coin is collected
            if pygame.sprite.spritecollide(player, coin_group, True):
                score += 1
            draw_text('X ' + str(score), font_score, white, tile_size, 10)


        blob_group.draw(screen)
        platform_group.draw(screen)
        lava_group.draw(screen)
        coin_group.draw(screen)
        exit_group.draw(screen)

        game_over = player.update(game_over)

        if game_over == -1:
            screen.blit(you_lose_img, (SCREENWIDTH // 2 - you_lose_img.get_width() // 2, SCREENHEIGHT // 2 - you_lose_img.get_height() // 2 - 100))
            if restart_button.draw():
                world = reset_level(world_data)
                game_over = 0
                score = 0
                

        #if player has won
        if game_over == 1:
            screen.blit(you_win_img, (SCREENWIDTH // 2 - you_win_img.get_width() // 2, SCREENHEIGHT // 2 - you_win_img.get_height() // 2 - 100 ))
            #reset world
            if restart_button.draw():
                world = reset_level(world_data)
                game_over = 0
                score = 0
                

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                # Restart the level
                world = reset_level(world_data)
                game_over = 0
                score = 0    

    pygame.display.update()

pygame.quit()

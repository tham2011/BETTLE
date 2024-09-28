import pygame
import os
import random
from pygame import mixer

# Khởi tạo Pygame và mixer
pygame.init()
mixer.init()

# Tạo biến thời gian và tốc độ khung hình
clock = pygame.time.Clock()
fps = 60

# Kích thước cửa sổ game
bottom_panel = 150
screen_width = 800
screen_height = 400 + bottom_panel
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Battle')

# Load âm thanh
mixer.music.load("stranger-things-124008.mp3")
mixer.music.set_volume(0.5)
mixer.music.play(-1, 0.0, 5000)

sword_fx = mixer.Sound("sword.wav")
sword_fx.set_volume(0.5)
magic_fx = mixer.Sound("magic.wav")
magic_fx.set_volume(0.75)

# Biến game
current_fighter = 1
total_fighters = 3
action_cooldown = 0
action_wait_time = 90
attack = False
special_skill = False
potion = False
potion_effect = 15
clicked = False
game_over = 0

# Định nghĩa font chữ và màu sắc
font = pygame.font.SysFont('Times New Roman', 26)
red = (255, 0, 0)
green = (0, 255, 0)

# Load hình ảnh
background_img = pygame.image.load('img/Background/background.png').convert_alpha()
panel_img = pygame.image.load('img/Icons/panel.png').convert_alpha()
potion_img = pygame.image.load('img/Icons/potion.png').convert_alpha()
restart_img = pygame.image.load('img/Icons/restart.png').convert_alpha()
victory_img = pygame.image.load('img/Icons/victory.png').convert_alpha()
defeat_img = pygame.image.load('img/Icons/defeat.png').convert_alpha()
sword_img = pygame.image.load('img/Icons/sword.png').convert_alpha()
special_skill_img = pygame.image.load('img/Icons/special.png').convert_alpha()

# Vẽ chữ lên màn hình
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# Vẽ nền game
def draw_bg():
    screen.blit(background_img, (0, 0))

# Vẽ bảng thông tin bên dưới
def draw_panel():
    screen.blit(panel_img, (0, screen_height - bottom_panel))
    draw_text(f'{knight.name} HP: {knight.hp}', font, red, 100, screen_height - bottom_panel + 10)
    for count, i in enumerate(bandit_list):
        draw_text(f'{i.name} HP: {i.hp}', font, red, 550, (screen_height - bottom_panel + 10) + count * 60)

# Lớp Fighter (Chiến binh)
class Fighter():
    def __init__(self, x, y, name, max_hp, strength, potions):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.strength = strength
        self.potions = potions
        self.alive = True
        self.vel_x =0
        self.vel_y =0
        self.animation_list = []
        self.frame_index = 0
        self.action = 0  # 0:idle, 1:attack, 2:hurt, 3:dead
        self.update_time = pygame.time.get_ticks()
        self.exp =0
        self.lever =1
        self.exp_to_lever_up =100
        self.skill_points =0
        self.skilla = {'attack':1 , 'special':1}
        # Load các hình ảnh idle
        temp_list = []
        for i in range(8):
            img = pygame.image.load(f'img/{self.name}/Idle/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temp_list.append(img)
        self.animation_list.append(temp_list)

        # Load các hình ảnh attack
        temp_list = []
        for i in range(8):
            img = pygame.image.load(f'img/{self.name}/Attack/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temp_list.append(img)
        self.animation_list.append(temp_list)

        # Load các hình ảnh hurt
        temp_list = []
        for i in range(3):
            img = pygame.image.load(f'img/{self.name}/Hurt/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temp_list.append(img)
        self.animation_list.append(temp_list)

        # Load các hình ảnh death
        temp_list = []
        for i in range(10):
            img = pygame.image.load(f'img/{self.name}/Death/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temp_list.append(img)
        self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def upgrade_skill(self, skill_name):
        if skill_name in self.skills:
            self.skills[skill_name] +=1
            print(f'kỹ năng {skill_name} đã được lên cấp {self.skills[skill_name]}!')

    def gain_exp(self, amount):
       
        self.exp+= amount
        print(f'đã nhận được {amount} EXP.')
    
    def level_up(self):
        self.exp -= self.exp_to_level_up
        self.level += 1
        self.skill_points += 1
        print(f'Bạn đã được lên cấp {self.level}')

    def update(self):
        animation_cooldown = 100
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.idle()

        self.rect.x += self.vel_x
        

    def idle(self):
        self.action = 0
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        #khoảng cách nhân vật
    def attack(self, target):
        if abs (self.rect.centerx - target.rect.centerx) <=50:
            rand = random.randint(-5, 5)
            damage = self.strength + rand
            target.hp -= damage
            target.hurt()
            if target.hp < 1:
                target.hp = 0
                target.alive = False
                target.death()
            damage_text = DamageText(target.rect.centerx, target.rect.y, str(damage), red)
            damage_text_group.add(damage_text)
            self.action = 1
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
            sword_fx.play()

            if not target.alive:
                self.gain_exp(50) #nhập 50 xp khi tiêu diệt kẻ địch 
            else: 
                print(f"quá xa để tấn công {target.name}")

    def special_attack(self, target):
        skill_level = self.skilla['special']
        damage = self.strength * 2 + random.randint(-3, 3)
        target.hp -= damage
        target.hurt()
        if target.hp < 1:
            target.hp = 0
            target.death()
        damage_text = DamageText(target.rect.centerx, target.rect.y, str(damage), red)
        damage_text_group.add(damage_text)
        self.action = 1
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        magic_fx.play()

        if not target.alive:
            self.gain_exp(50)
   
    def hurt(self):
        self.action = 2
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def death(self):
        self.action = 3
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def draw(self):
        screen.blit(self.image, self.rect)
    
# Lớp thanh máu
class HealthBar():
    def __init__(self, x, y, hp, max_hp):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = max_hp

    def draw(self, hp):
        self.hp = hp
        ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, red, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, green, (self.x, self.y, 150 * ratio, 20))

# Lớp văn bản sát thương
class DamageText(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, colour):
        pygame.sprite.Sprite.__init__(self)
        self.image = font.render(damage, True, colour)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        self.rect.y -= 1
        self.counter += 1
        if self.counter > 30:
            self.kill()

# Nhóm văn bản sát thương
damage_text_group = pygame.sprite.Group()

# Chiến binh và kẻ địch
knight = Fighter(200, 260, 'Knight', 50, 10, 3)
bandit1 = Fighter(550, 270, 'Bandit', 30, 6, 1)
bandit2 = Fighter(700, 270, 'Bandit', 30, 6, 1)
bandit_list = [bandit1, bandit2]

# Thanh máu
knight_health_bar = HealthBar(100, screen_height - bottom_panel + 40, knight.hp, knight.max_hp)
bandit1_health_bar = HealthBar(550, screen_height - bottom_panel + 40, bandit1.hp, bandit1.max_hp)
bandit2_health_bar = HealthBar(550, screen_height - bottom_panel + 100, bandit2.hp, bandit2.max_hp)

# Lớp Button (Nút)
class Button():
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action
    def create_bandits():
        bandit1 = Fighter(550, 270, 'Bandit', 30, 6, 1)
        bandit2 = Fighter(700, 270, 'Bandit', 30, 6, 1)
        return [bandit1, bandit2]

# Khởi tạo kẻ địch
    bandit_list = create_bandits()

# Tạo các nút
potion_button = Button(100, screen_height - bottom_panel + 70, potion_img, 1)
attack_button = Button(200, screen_height - bottom_panel + 70, sword_img, 1.5)
special_skill_button = Button(300, screen_height - bottom_panel + 60, special_skill_img, 0.75)
restart_button = Button (300,150,  restart_img,0.5)

def reset_game():
    global current_fighter, action_cooldown, game_over
    knight.hp = knight.max_hp
    knight.alive = True

    for bandit in bandit_list:
        bandit.hp = bandit.max_hp
        bandit.alive = True

    current_fighter = 1
    action_cooldown = 0
    game_over = 0

    
# Game loop
run = True

while run:
    clock.tick(fps)
    draw_bg()
    draw_panel()
    knight_health_bar.draw(knight.hp)
    bandit1_health_bar.draw(bandit1.hp)
    bandit2_health_bar.draw(bandit2.hp)

    knight.update()
    knight.draw()

    for bandit in bandit_list:
        bandit.update()
        bandit.draw()

    damage_text_group.update()
    damage_text_group.draw(screen)

    attack = False
    potion = False
    special_skill = False
    target = None


    #banf phím di chuuyeenr nhân vật 
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        knight.vel_x =-5
    elif keys[pygame.K_RIGHT]:
        knight.vel_x =5
    else:
        knight.vel_x =0

    if knight.rect.left + knight.vel_x > 0 and knight.rect.right + knight.vel_x <screen_width:
            knight.rect.x += knight.vel_x

    # Kiểm tra người chơi nhấn nút nào
    if attack_button.draw():
        attack = True
        target = bandit1 if bandit1.alive else (bandit2 if bandit2.alive else None)
    # di chuyển đến mục tiêu
    if target and abs(knight.rect.centerx - target.rect.centerx) < 100:
        if knight.rect.centerx < target.rect.centerx:
            knight.vel_x =5
        elif knight.rect.centerx > target.rect.centerx:
            knight.vel_x =-5
    else:
        knight.vel_x =0
# đủ gần để tấn công 
    if attack and target and abs (knight.rect.centerx - target.rect.centerx) > 100:
        knight.attack(target)
        current_fighter += 1
        action_cooldown =0

    if potion_button.draw():
        potion = True

    if special_skill_button.draw():
        special_skill = True
        target = bandit1 if bandit1.alive else bandit2

    # Logic chiến đấu
    if game_over == 0:
        if knight.alive:
            if current_fighter == 1:
                action_cooldown += 1
                if action_cooldown >= action_wait_time:
                    if attack and target:
                        knight.attack(target)
                        current_fighter += 1
                        action_cooldown = 0
                    elif potion:
                        if knight.potions > 0:
                            knight.hp += potion_effect
                            if knight.hp > knight.max_hp:
                                knight.hp = knight.max_hp
                            knight.potions -= 1
                            current_fighter += 1
                            action_cooldown = 0
                    elif special_skill and target:
                        knight.special_attack(target)
                        current_fighter += 1
                        action_cooldown = 0
# kẻ địch tấn công 
        for count, bandit in enumerate(bandit_list):
            if current_fighter == 2 + count:
                if bandit.alive:
                    action_cooldown += 1
                    if action_cooldown >= action_wait_time:
                        bandit.attack(knight)
                        current_fighter += 1
                        action_cooldown = 0
                else:
                    current_fighter += 1

        if current_fighter > total_fighters:
            current_fighter = 1

    # Kiểm tra nếu tất cả kẻ địch đã chết thắng 
    alive_bandits = 0
    for bandit in bandit_list:
        if bandit.alive:
            alive_bandits += 1
    if alive_bandits == 0:
        game_over = 1
        # ktr nhân vật chết thua
    if  not knight.alive:
        game_over = -1 
# hàm hiển thị màn hình thắng hoặc thua 
    if game_over != 0:
        if game_over == 1:
            screen.blit(victory_img, (250, 50)) # thắng 
        if game_over == -1:
            screen.blit(defeat_img, (290, 50)) #thua cuộc 
            # nút restart để chơi lại
        if restart_button.draw():
            knight.hp = knight.max_hp # đặt lại nhân vật
            knight.alive = True
            # đặt lại kẻ địch
            for bandit in bandit_list:
                bandit.hp = bandit.max_hp
                bandit.alive = True

            current_fighter = 1
            action_cooldown = 0
            game_over = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
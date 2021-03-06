import pygame
import os
import time
import random

pygame.font.init()  # Carrega uma font

COMPRIMENTO, ALTURA = 750, 750
WIN = pygame.display.set_mode((COMPRIMENTO, ALTURA))  # Definir dimensoes do ecra
pygame.display.set_caption("Space Invaders")  # Titulo da Janela

# Carregar as imagens

NAVE_VERMELHA = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
NAVE_VERDE = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
NAVE_AZUL = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

NAVE_AMARELA = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# Lasers

LASER_VERMELHO = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
LASER_VERDE = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
LASER_AZUL = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
LASER_AMARELO = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# Background

BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (COMPRIMENTO, ALTURA))


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (height >= self.y >= 0)

    def collision(self, obj):
        return collide(obj, self)


class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(ALTURA):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = NAVE_AMARELA
        self.laser_img = LASER_AMARELO
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(ALTURA):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0),
                         (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0),
                         (self.x, self.y + self.ship_img.get_height() + 10,
                          self.ship_img.get_width() * (self.health / self.max_health), 10))




class Enemy(Ship):
    COLOR_MAP = {
        "red": (NAVE_VERMELHA, LASER_VERMELHO),
        "green": (NAVE_VERDE, LASER_VERDE),
        "blue": (NAVE_AZUL, LASER_AZUL),
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x - 10, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None


def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)
    player_vel = 5

    enemies = []
    wave_length = 5
    enemy_vel = 2
    laser_vel = 5

    player = Player(300, 630)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0, 0))  # ADICIONAMOS UMA IMAGEM DE FUNDO QUE COME??A NO CANTO SUPERIOR ESQUERDO (0,0)

        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (COMPRIMENTO - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("YOU LOST!!", 1, (255, 255, 255))
            WIN.blit(lost_label, (COMPRIMENTO / 2 - lost_label.get_width() / 2, 350))

        pygame.display.update()  # Refresca o screen

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, COMPRIMENTO - 100), random.randrange(-1500, -100),
                              random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():  # Verificamos se algum evento ocorreu
            if event.type == pygame.QUIT:  # Se clicarmos para fechar
                quit()

        keys = pygame.key.get_pressed()

        if keys[pygame.K_a] and player.x + player_vel > 0:  # Esquerda
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < COMPRIMENTO:  # Direita
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:  # Cima
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 10 < ALTURA:  # Baixo
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:  # [:] faz uma copia da lista
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2 * FPS) == 1:  # A cada segunda ?? probabilidade de 50% do inmigo disparar
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)

            elif enemy.y + enemy.get_height() > ALTURA:  # Se passar a altura do ecra
                lives -= 1  # Jogador perde 1 vida
                enemies.remove(enemy)  # Esse inimigo ?? removido da lista

        player.move_lasers(-laser_vel, enemies)

def main_menu():
    title_font = pygame.font.SysFont("comicsans",70)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("Pressione o rato para come??ar...",1 ,(255,255,255))
        WIN.blit(title_label, (COMPRIMENTO/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()

main_menu()


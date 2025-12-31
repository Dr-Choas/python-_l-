import pygame
import random
import time

IMAGE_PATH = 'imgs/'
screen_width = 800
screen_height = 560
GAMEOVER = False
LOG = '文件:{}中的方法:{}出错'.format(__file__, __name__)

RESOURCES = {
    'tushuguan': None,
    'shudian': None,
    'modian': None,
    'shijuan': None,
    'zombie': None,
    'zombie_walk_frames': []
}

class Map():
    map_names_list = [IMAGE_PATH + 'tushuguan.png']
    def __init__(self, x, y, img_index=0):
        self.image = RESOURCES['tushuguan']
        self.image = pygame.transform.scale(self.image, (80, 80))
        self.position = (x, y)
        self.can_grow = True

    def load_map(self):
        MainGame.window.blit(self.image, self.position)

class GameUnit(pygame.sprite.Sprite):
    def __init__(self):
        super(GameUnit, self).__init__()
        self.live = True

    def load_image(self):
        if hasattr(self, 'image') and hasattr(self, 'rect'):
            MainGame.window.blit(self.image, self.rect)
        else:
            print(LOG)

class Shudian(GameUnit):
    def __init__(self, x, y):
        super(Shudian, self).__init__()
        self.image = RESOURCES['shudian']
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.price = 50
        self.hp = 100
        self.time_count = 0

    def produce_money(self):
        self.time_count += 1
        if self.time_count == 25:
            MainGame.money += 5
            self.time_count = 0

    def display_shudian(self):
        MainGame.window.blit(self.image, self.rect)

class Modian(GameUnit):
    def __init__(self, x, y):
        super(Modian, self).__init__()
        self.image = RESOURCES['modian']
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.price = 50
        self.hp = 200
        self.shot_count = 0

    def shot(self):
        should_fire = False
        for zombie in MainGame.zombie_list:
            if zombie.rect.y == self.rect.y and zombie.rect.x < screen_width and zombie.rect.x > self.rect.x:
                should_fire = True
                break
        if self.live and should_fire:
            self.shot_count += 1
            if self.shot_count == 25:
                shijuan = Shijuan(self)
                MainGame.shijuan_list.append(shijuan)
                self.shot_count = 0

    def display_modian(self):
        MainGame.window.blit(self.image, self.rect)

class Shijuan(pygame.sprite.Sprite):
    def __init__(self, modian):
        self.live = True
        self.image = RESOURCES['shijuan']
        self.damage = 50
        self.speed = 10
        self.rect = self.image.get_rect()
        self.rect.x = modian.rect.x + 60
        self.rect.y = modian.rect.y + 15

    def move_shijuan(self):
        if self.rect.x < screen_width:
            self.rect.x += self.speed
        else:
            self.live = False

    def hit_zombie(self):
        for zombie in MainGame.zombie_list:
            if pygame.sprite.collide_rect(self, zombie):
                self.live = False
                zombie.hp -= self.damage
                if zombie.hp <= 0:
                    zombie.live = False
                    self.nextLevel()
                break

    def nextLevel(self):
        MainGame.score += 20
        MainGame.remnant_score -= 20
        for i in range(1, 100):
            if MainGame.score == 100 * i and MainGame.remnant_score == 0:
                MainGame.remnant_score = 100
                MainGame.shaoguan += 1
                MainGame.produce_zombie += 50
                break

    def display_shijuan(self):
        MainGame.window.blit(self.image, self.rect)

class Zombie(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Zombie, self).__init__()
        self.original_zombie = RESOURCES['zombie']
        self.walk_frames = RESOURCES['zombie_walk_frames']
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 15
        
        self.image = self.original_zombie
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hp = 1000
        self.damage = 2
        self.speed = 1
        self.live = True
        self.stop = False

    def update_zombie_animation(self):
        if self.live and not self.stop:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_speed:
                self.current_frame = (self.current_frame + 1) % 4
                self.image = self.walk_frames[self.current_frame]
                self.animation_timer = 0
        elif self.live and self.stop:
            self.image = self.original_zombie
            self.animation_timer = 0
            self.current_frame = 0

    def move_zombie(self):
        if self.live and not self.stop:
            self.rect.x -= self.speed
            if self.rect.x < -80:
                MainGame().gameOver()

    def hit_unit(self):
        for unit in MainGame.game_units_list:
            if pygame.sprite.collide_rect(self, unit):
                self.stop = True
                self.eat_unit(unit)
                break

    def eat_unit(self, unit):
        unit.hp -= self.damage
        if unit.hp <= 0:
            a = unit.rect.y // 80 - 1
            b = unit.rect.x // 80
            map_block = MainGame.map_list[a][b]
            map_block.can_grow = True
            unit.live = False
            self.stop = False

    def display_zombie(self):
        self.update_zombie_animation()
        MainGame.window.blit(self.image, self.rect)

class MainGame():
    shaoguan = 1
    score = 0
    remnant_score = 100
    money = 500
    map_points_list = []
    map_list = []
    game_units_list = []
    shijuan_list = []
    zombie_list = []
    count_zombie = 0
    produce_zombie = 100
    tushuguan_bg = None
    window = None
    game_speed = 1

    def init_window(self):
        pygame.display.init()
        MainGame.window = pygame.display.set_mode([screen_width, screen_height])
        pygame.display.set_caption("今天又在学习吗？")

    def draw_text(self, content, size, color, position=(0,0), center=False):
        pygame.font.init()
        font = pygame.font.SysFont('kaiti', size)
        text = font.render(content, True, color)
        if center:
            x = (screen_width - text.get_width()) // 2
            y = position[1]
            position = (x, y)
        MainGame.window.blit(text, position)
        return text.get_rect(topleft=position)

    def preload_resources(self):
        basic_resources = [
            ('tushuguan', IMAGE_PATH + 'tushuguan.png', (0,255,0)),
            ('shudian', 'imgs/shudian.png', (255,255,0)),
            ('modian', 'imgs/modian.png', (0,255,0)),
            ('shijuan', 'imgs/shijuan.png', (255,0,0)),
            ('zombie', 'imgs/zombie.png', (128,128,128))
        ]
        zombie_walk_paths = [
            IMAGE_PATH + 'zombie_walk1.png',
            IMAGE_PATH + 'zombie_walk2.png',
            IMAGE_PATH + 'zombie_walk3.png',
            IMAGE_PATH + 'zombie_walk4.png'
        ]
        total = len(basic_resources) + 1
        current_progress = 0

        for name, path, fallback_color in basic_resources:
            try:
                RESOURCES[name] = pygame.image.load(path)
            except pygame.error as e:
                print(f"加载{name}失败: {e}，使用备用色块")
                if name == 'zombie':
                    RESOURCES[name] = pygame.Surface((80, 120))
                else:
                    RESOURCES[name] = pygame.Surface((80, 80))
                RESOURCES[name].fill(fallback_color)
            current_progress += 1
            yield int((current_progress)/total * 100)
            time.sleep(0.2)

        fallback_surface = pygame.Surface((80, 120))
        fallback_surface.fill((128,128,128))
        for frame_path in zombie_walk_paths:
            try:
                frame = pygame.image.load(frame_path)
                frame = pygame.transform.scale(frame, (80, 120))
                RESOURCES['zombie_walk_frames'].append(frame)
            except pygame.error as e:
                print(f"加载僵尸行走帧{frame_path}失败: {e}，使用备用色块")
                RESOURCES['zombie_walk_frames'].append(fallback_surface.copy())
        current_progress += 1
        yield int((current_progress)/total * 100)
        time.sleep(0.2)

    def show_loading_screen(self):
        loading_done = False
        progress = 0
        loader = self.preload_resources()
        bg_color = (240, 248, 255)

        while not loading_done:
            MainGame.window.fill(bg_color)

            self.draw_text("游戏加载中...", 40, (0, 0, 255), center=True, position=(0, screen_height//2 - 80))

            bar_x = screen_width//2 - 200
            bar_y = screen_height//2
            pygame.draw.rect(MainGame.window, (100,100,100), (bar_x-2, bar_y-2, 404, 34), 2)

            fill_width = int(progress / 100 * 400)
            pygame.draw.rect(MainGame.window, (0, 200, 0), (bar_x, bar_y, fill_width, 30))

            self.draw_text(f"{progress}%", 24, (0,0,0), (screen_width//2 - 20, screen_height//2 + 40))

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            try:
                progress = next(loader)
            except StopIteration:
                loading_done = True

            pygame.display.update()
        time.sleep(0.5)

    def show_story_screen(self):
        story_done = False
        bg_color = (255, 248, 225)

        while not story_done:
            MainGame.window.fill(bg_color)

            self.draw_text("在攀登知识殿堂的高峰中，", 36, (139, 69, 19), center=True, position=(0, screen_height//2 - 100))
            self.draw_text("数电和模电始终阻止你进步。。。", 36, (139, 69, 19), center=True, position=(0, screen_height//2 - 50))
            self.draw_text('操作指南：左键创建数电 右键创建模电', 28, (0, 0, 255), center=True, position=(0, screen_height//2))
            self.draw_text("点击屏幕继续", 28, (0, 0, 255), center=True, position=(0, screen_height//2 + 60))

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    story_done = True

            pygame.display.update()

    def init_unit_points(self):
        for y in range(1, 7):
            points = []
            for x in range(10):
                point = (x, y)
                points.append(point)
            MainGame.map_points_list.append(points)

    def init_map(self):
        MainGame.tushuguan_bg = RESOURCES['tushuguan']
        MainGame.tushuguan_bg = pygame.transform.scale(MainGame.tushuguan_bg, (screen_width, screen_height))

        for points in MainGame.map_points_list:
            temp_map_list = []
            for point in points:
                x = point[0] * 80
                y = point[1] * 80
                map_block = Map(x, y, 0)
                temp_map_list.append(map_block)
            MainGame.map_list.append(temp_map_list)

    def load_map(self):
        MainGame.window.blit(MainGame.tushuguan_bg, (0, 0))

    def load_game_units(self):
        for unit in MainGame.game_units_list[:]:
            if unit.live:
                if isinstance(unit, Shudian):
                    unit.display_shudian()
                    unit.produce_money()
                elif isinstance(unit, Modian):
                    unit.display_modian()
                    unit.shot()
            else:
                MainGame.game_units_list.remove(unit)

    def load_shijuan(self):
        for s in MainGame.shijuan_list[:]:
            if s.live:
                s.display_shijuan()
                s.move_shijuan()
                s.hit_zombie()
            else:
                MainGame.shijuan_list.remove(s)

    def deal_events(self):
        eventList = pygame.event.get()
        for e in eventList:
            if e.type == pygame.QUIT:
                global GAMEOVER
                GAMEOVER = True
            elif e.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = e.pos
                if self.speed_btn_rect.collidepoint(mouse_pos):
                    MainGame.game_speed = 2 if MainGame.game_speed == 1 else 1
                else:
                    x = e.pos[0] // 80
                    y = e.pos[1] // 80
                    if 0 <= x < 10 and 0 <= y-1 < 6:
                        map_block = MainGame.map_list[y - 1][x]
                        if e.button == 1:
                            if map_block.can_grow and MainGame.money >= 50:
                                unit_x = x * 80
                                unit_y = y * 80
                                shudian = Shudian(unit_x, unit_y)
                                MainGame.game_units_list.append(shudian)
                                map_block.can_grow = False
                                MainGame.money -= 50
                        elif e.button == 3:
                            if map_block.can_grow and MainGame.money >= 50:
                                unit_x = x * 80
                                unit_y = y * 80
                                modian = Modian(unit_x, unit_y)
                                MainGame.game_units_list.append(modian)
                                map_block.can_grow = False
                                MainGame.money -= 50

    def init_zombies(self):
        for i in range(1, 7):
            dis = random.randint(1, 5) * 200
            zombie_x = screen_width + dis
            zombie_y = i * 80
            zombie = Zombie(zombie_x, zombie_y)
            MainGame.zombie_list.append(zombie)

    def load_zombies(self):
        for zombie in MainGame.zombie_list[:]:
            if zombie.live:
                zombie.display_zombie()
                zombie.move_zombie()
                zombie.hit_unit()
            else:
                MainGame.zombie_list.remove(zombie)

    def reset_game_state(self):
        global GAMEOVER
        GAMEOVER = False
        MainGame.shaoguan = 1
        MainGame.score = 0
        MainGame.remnant_score = 100
        MainGame.money = 500
        MainGame.game_units_list.clear()
        MainGame.shijuan_list.clear()
        MainGame.zombie_list.clear()
        MainGame.count_zombie = 0
        MainGame.produce_zombie = 100
        MainGame.game_speed = 1
        MainGame.map_points_list.clear()
        MainGame.map_list.clear()
        self.init_unit_points()
        self.init_map()
        self.init_zombies()

    def start_game(self):
        self.init_window()
        self.show_loading_screen()
        self.show_story_screen()
        self.init_unit_points()
        self.init_map()
        self.init_zombies()

        while not GAMEOVER:
            self.load_map()

            right_top_x = 600
            line1_y = 10
            line2_y = 40
            line3_y = 70
            line4_y = 100

            self.draw_text(f'知识$：{MainGame.money}', 26, (255, 0, 0), (right_top_x, line1_y))
            self.draw_text(f'关卡：{MainGame.shaoguan}', 26, (255, 0, 0), (right_top_x, line2_y))
            self.draw_text(f'得分：{MainGame.score} ',26, (255, 0, 0), (right_top_x, line3_y))
            self.draw_text(f'距下关还差：{MainGame.remnant_score}分', 26, (255, 0, 0), (right_top_x, line4_y))

            speed_text = "2倍加速" if MainGame.game_speed == 2 else "1倍加速"
            speed_color = (255, 165, 0) if MainGame.game_speed == 2 else (0, 255, 255)
            self.speed_btn_rect = self.draw_text(speed_text, 30, speed_color, (200, 20))

            self.load_game_units()
            self.load_shijuan()
            self.deal_events()
            self.load_zombies()

            MainGame.count_zombie += 1
            if MainGame.count_zombie == MainGame.produce_zombie:
                self.init_zombies()
                MainGame.count_zombie = 0

            delay_time = 10 // MainGame.game_speed
            pygame.time.wait(delay_time)
            pygame.display.update()

        self.game_over_loop()

    def gameOver(self):
        global GAMEOVER
        GAMEOVER = True
        print('游戏结束')

    def game_over_loop(self):
        while True:
            self.load_map()

            self.draw_text('游戏结束', 60, (255, 0, 0), center=True, position=(0, screen_height//2 - 100))
            self.draw_text(f'最终关数：{MainGame.shaoguan}  最终得分：{MainGame.score}',
                           36, (255, 255, 0), center=True, position=(0, screen_height//2 - 30))

            restart_rect = self.draw_text('重新开始', 40, (0, 255, 0), center=True, position=(0, screen_height//2 + 30))
            quit_rect = self.draw_text('退出游戏', 40, (255, 0, 0), center=True, position=(0, screen_height//2 + 100))

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    mouse_pos = e.pos
                    if restart_rect.collidepoint(mouse_pos):
                        self.reset_game_state()
                        self.start_game()
                    elif quit_rect.collidepoint(mouse_pos):
                        pygame.quit()
                        exit()

            pygame.display.update()
            pygame.time.wait(10)

if __name__ == '__main__':
    pygame.init()
    game = MainGame()
    game.start_game()
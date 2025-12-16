import pygame
import random
import os


pygame.init()


# === SCREEN ===
WIDTH, HEIGHT = 900, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Headball Voli UAS")


FPS = 60
GRAVITY = 1


# === ASSET LOADER (memanggil gambar & suara dari folder assets) ===
ASSET_DIR = "assets"


def load_image(name, size=None):
    # memuat gambar dari folder assets
    path = os.path.join(ASSET_DIR, name)
    img = pygame.image.load(path).convert_alpha()
    if size:
        img = pygame.transform.scale(img, size)  # resize jika diminta
    return img


def load_sound(name):
    # memuat file suara
    path = os.path.join(ASSET_DIR, name)
    return pygame.mixer.Sound(path)


# === LOAD GAMBAR & SUARA ===
background_img = load_image("background.jpg", (WIDTH, HEIGHT))
player1_img_raw = load_image("orang 1.png", (120, 120))
player2_img_raw = load_image("orang 2.png", (120, 120))
ball_img = load_image("bola voli.png", (70, 70))


jump_sound       = load_sound("jump.wav")
kick_sound       = load_sound("kick_sound.wav")
goal_bell        = load_sound("goal_bell.wav")
powerup_sound    = load_sound("powerup.wav")
game_over_sound  = load_sound("game_over.wav")



# =============== BASE OBJECT (SUPERCLASS) ===============
class GameObject:
    """Class dasar untuk semua objek (player, bola, powerup)."""
    def __init__(self, x: int, y: int, w: int, h: int):
        # private attributes → encapsulation
        self.__x = x
        self.__y = y
        self.__w = w
        self.__h = h

    # === Getter / Setter versi method ===
    def get_x(self):
        return self.__x

    def set_x(self, v):
        self.__x = v

    def get_y(self):
        return self.__y

    def set_y(self, v):
        self.__y = v

    def get_w(self):
        return self.__w

    def get_h(self):
        return self.__h


    def rect(self):
        # Menghasilkan area kotak untuk deteksi tabrakan
        return pygame.Rect(int(self.__x), int(self.__y), int(self.__w), int(self.__h))

    def draw(self):
        # harus dioverride oleh class anak
        raise NotImplementedError("draw() must be implemented by subclasses")



# =============== CHARACTER BASE (TURUNAN GameObject) ===============
class Character(GameObject):
    """Karakter dasar termasuk player."""
    def __init__(self, x, y, w, h, img):
        super().__init__(x, y, w, h)
        self._img_raw = img        # gambar asli
        self._img = img            # gambar yg telah di-scale saat lompat
        self.__vel_x = 5           # kecepatan horizontal
        self.__vel_y = 0           # kecepatan vertikal
        self.__can_jump = True     # boleh lompat atau tidak
        self.__jump_scale = 1.0    # efek squash/stretch
        self._smash = False        # status smash

    # === Getter / Setter velocity & status (method) ===
    def get_vel_x(self):
        return self.__vel_x

    def set_vel_x(self, v):
        self.__vel_x = v

    def get_vel_y(self):
        return self.__vel_y

    def set_vel_y(self, v):
        self.__vel_y = v

    def get_can_jump(self):
        return self.__can_jump

    def set_can_jump(self, v):
        self.__can_jump = v

    def get_jump_scale(self):
        return self.__jump_scale

    def set_jump_scale(self, v):
        self.__jump_scale = v



  
    def smash_active(self):
        return self._smash

    def movement(self):
        # movement default (kosong) → akan dioverride player
        pass

    def physics(self):
        """FISIKA KARAKTER: gravitasi, tabrak tanah, batasi area, efek lompat."""
        # gravitasi
        self.set_vel_y(self.get_vel_y() + GRAVITY)
        self.set_y(self.get_y() + self.get_vel_y())

        # efek squash/stretch saat lompat
        if not self.get_can_jump():
            self.set_jump_scale(1.15)
        else:
            if self.get_jump_scale() > 1.0:
                self.set_jump_scale(self.get_jump_scale() - 0.05)
            else:
                self.set_jump_scale(1.0)

        # tabrakan tanah
        if self.get_y() + self.get_h() >= HEIGHT - 20:
            self.set_y(HEIGHT - 20 - self.get_h())
            self.set_vel_y(0)
            self.set_can_jump(True)

        # batasi x supaya tidak keluar layar
        self.set_x(max(0, min(self.get_x(), WIDTH - self.get_w())))

        # update gambar sesuai scale lompat
        new_h = int(self.get_h() * self.get_jump_scale())
        self._img = pygame.transform.scale(self._img_raw, (self.get_w(), new_h))

    def draw(self):
        # gambar player dengan posisi kaki tetap di tanah
        screen.blit(
            self._img,
            (self.get_x(), self.get_y() - (self._img.get_height() - self.get_h()))
        )



# =============== PLAYER ===============
class Player(Character):
    def __init__(self, x, y, img, controls, name="Player"):
        super().__init__(x, y, 120, 120, img)
        self.controls = controls    # mapping tombol
        self.score = 0
        self.name = name

    def movement(self):
        """Override movement khusus player."""
        keys = pygame.key.get_pressed()

        # jalan kiri / kanan
        if keys[self.controls["left"]]:
            self.set_x(self.get_x() - self.get_vel_x())
        if keys[self.controls["right"]]:
            self.set_x(self.get_x() + self.get_vel_x())

        # lompat
        if keys[self.controls["jump"]] and self.get_can_jump():
            self.set_vel_y(-16)
            self.set_can_jump(False)
            jump_sound.play()

        # smash → aktif hanya jika di udara
        if keys[self.controls["smash"]] and not self.get_can_jump():
            self._smash = True
        else:
            self._smash = False

    def smash(self, power=None):
        """Contoh polymorphism (opsional power)."""
        if not self.get_can_jump():
            if power is None:
                self.set_vel_y(self.get_vel_y() + 3)      # smash biasa
            else:
                self.set_vel_y(self.get_vel_y() + power)  # smash lebih kuat

    def head_zone(self):
        # area kepala untuk hit detection
        r = self.rect()
        return pygame.Rect(r.x, r.y, r.width, r.height // 3)

    def draw(self):
        super().draw()



# =============== BALL ===============
class Ball(GameObject):
    def __init__(self):
        # posisi awal bola
        size = 70
        x = WIDTH // 2 - size // 2
        y = 100
        super().__init__(x, y, size, size)

        # kecepatan awal acak kiri/kanan
        self.__vel_x = 6 * random.choice([-1, 1])
        self.__vel_y = 0

    # getter/setter method
    def get_vel_x(self):
        return self.__vel_x

    def set_vel_x(self, v):
        self.__vel_x = v

    def get_vel_y(self):
        return self.__vel_y

    def set_vel_y(self, v):
        self.__vel_y = v


    def physics(self):
        """FISIKA BOLA: gravitasi, pantulan dinding, tabrakan net."""
        self.set_vel_y(self.get_vel_y() + GRAVITY)
        self.set_x(self.get_x() + self.get_vel_x())
        self.set_y(self.get_y() + self.get_vel_y())

        # pantulan dinding kiri/kanan
        if self.get_x() <= 0:
            self.set_x(0)
            self.set_vel_x(-self.get_vel_x())
        if self.get_x() + self.get_w() >= WIDTH:
            self.set_x(WIDTH - self.get_w())
            self.set_vel_x(-self.get_vel_x())

        # pantulan dinding atas
        if self.get_y() <= 0:
            self.set_y(0)
            self.set_vel_y(-self.get_vel_y())

        # area net
        net_rect = pygame.Rect(WIDTH//2 - 5, HEIGHT - 240, 10, 200)

        # jika bola menyentuh net
        if net_rect.colliderect(self.rect()):
            # arahkan bola menjauhi net
            if self.get_x() + self.get_w()/2 <= WIDTH//2:
                self.set_vel_x(-abs(self.get_vel_x()))
            else:
                self.set_vel_x(abs(self.get_vel_x()))

            # jika menyentuh bagian atas net
            if self.get_y() + self.get_h() < HEIGHT - 235:
                self.set_vel_y(-12)

    def collide(self, player: Player):
        """Interaksi bola dengan player."""
        player_r = player.rect()

        if player_r.colliderect(self.rect()):
            head_zone = pygame.Rect(player_r.x, player_r.y,
                                    player_r.width, player_r.height // 3)

            # hit kepala → pantulan kuat
            if head_zone.colliderect(self.rect()):
                self.set_vel_y(-24)
                # mengarahkan horizontal sesuai sisi pemain
                if self.get_x() + self.get_w()/2 < player.get_x() + player.get_w()/2:
                    self.set_vel_x(-abs(self.get_vel_x()))
                else:
                    self.set_vel_x(abs(self.get_vel_x()))
                self.set_vel_x(self.get_vel_x() * 1.05)
                kick_sound.play()
                return

            # smash
            if player.smash_active:
                self.set_vel_y(15)
                self.set_vel_x(self.get_vel_x() * 1.6)
                kick_sound.play()
                return

            # hit badan default
            self.set_vel_x(-self.get_vel_x())
            self.set_vel_y(-14)
            self.set_vel_y(self.get_vel_y() + 1)
            kick_sound.play()

    def reset(self):
        """Reset bola ke tengah."""
        self.__init__()

    def draw(self):
        screen.blit(ball_img, (int(self.get_x()), int(self.get_y())))



# =============== POWERUP ===============
class PowerUp(GameObject):
    """Buff speed acak yg muncul random."""
    def __init__(self):
        w, h = 40, 40
        x = random.randint(100, WIDTH - 100)
        y = HEIGHT - 100
        super().__init__(x, y, w, h)
        self.__active = False
        self.__timer = 0

    # getter/setter method untuk status aktif (kalau diperlukan nanti)
    def get_active(self):
        return self.__active

    def set_active(self, v):
        self.__active = v

    active = property(get_active, set_active)

    def spawn(self):
        # chance kecil untuk spawn
        if not self.__active and random.randint(1, 700) == 1:
            self.__active = True
            self.__timer = 500
            self.set_x(random.randint(100, WIDTH - 100))

    def draw(self):
        # kotak emas powerup
        if self.__active:
            pygame.draw.rect(
                screen,
                (255, 215, 0),
                (int(self.get_x()), int(self.get_y()), self.get_w(), self.get_h())
            )

    def collide(self, player: Player):
        # jika player menyentuh powerup
        if self.__active and player.rect().colliderect(self.rect()):
            powerup_sound.play()
            player.set_vel_x(player.get_vel_x() + 3)   # tambah speed
            self.__active = False

    def tick(self):
        # hitung mundur durasi aktif
        if self.__active:
            self.__timer -= 1
            if self.__timer <= 0:
                self.__active = False



# =============== UI / TEXT ===============
def draw_text(text, x, y, size=40, color=(255,255,255)):
    font = pygame.font.Font(None, size)
    label = font.render(text, True, color)
    screen.blit(label, (x, y))


def draw_winner(text):
    # muncul screen kemenangan
    screen.fill((0,0,0))
    label = pygame.font.Font(None, 80).render(text, True, (255,255,255))
    screen.blit(label, (WIDTH//2 - label.get_width()//2, HEIGHT//2 - 40))
    pygame.display.update()
    pygame.time.delay(3000)



# =============== GAME MANAGER ===============
class Game:
    def __init__(self):
        self.clock = pygame.time.Clock()

        # Player 1 (kontrol WASD)
        self.p1 = Player(
            150, HEIGHT - 200, player1_img_raw,
            {"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "smash": pygame.K_s},
            name="P1"
        )

        # Player 2 (kontrol arrow keys)
        self.p2 = Player(
            WIDTH - 300, HEIGHT - 200, player2_img_raw,
            {"left": pygame.K_LEFT, "right": pygame.K_RIGHT, "jump": pygame.K_UP, "smash": pygame.K_DOWN},
            name="P2"
        )

        self.ball = Ball()
        self.powerup = PowerUp()

        self.run = True

    def process_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.run = False

    def update(self):
        """Update semua objek per frame."""
        # movement + physics
        self.p1.movement()
        self.p2.movement()
        self.p1.physics()
        self.p2.physics()

        # bola
        self.ball.physics()

        # tabrakan bola dengan player
        self.ball.collide(self.p1)
        self.ball.collide(self.p2)

        # powerup
        self.powerup.spawn()
        self.powerup.tick()
        self.powerup.collide(self.p1)
        self.powerup.collide(self.p2)

        # skor jika bola jatuh
        if self.ball.get_y() > HEIGHT - 10:
            if self.ball.get_x() < WIDTH // 2:
                self.p2.score += 1
            else:
                self.p1.score += 1

            goal_bell.play()
            self.ball.reset()

        # win condition
        if self.p1.score >= 25:
            game_over_sound.play()
            draw_winner("PLAYER 1 MENANG!")
            self.run = False

        if self.p2.score >= 25:
            game_over_sound.play()
            draw_winner("PLAYER 2 MENANG!")
            self.run = False

    def draw(self):
        """Render semua objek ke layar."""
        screen.blit(background_img, (0, 0))

        # net
        pygame.draw.rect(screen, (255,255,255),
                         (WIDTH//2 - 5, HEIGHT - 240, 10, 200))

        # objek
        self.p1.draw()
        self.p2.draw()
        self.ball.draw()
        self.powerup.draw()

        # skor
        draw_text(f"P1: {self.p1.score}", 20, 20)
        draw_text(f"P2: {self.p2.score}", WIDTH - 160, 20)

        pygame.display.update()

    def run_loop(self):
        """Loop utama game."""
        while self.run:
            self.clock.tick(FPS)
            self.process_events()
            self.update()
            self.draw()

        pygame.quit()



# =============== ENTRY POINT ===============
if __name__ == "__main__":
    game = Game()
    game.run_loop()

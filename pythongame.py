import pygame
import sys
import time

pygame.init()

WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Binäreingabe Overlay")

BLACK   = (10, 10, 10)
WHITE   = (240, 240, 240)
GRAY    = (60, 60, 60)
LGRAY   = (120, 120, 120)
ACCENT  = (80, 160, 220)
GREEN   = (80, 200, 120)
AMBER   = (220, 170, 50)
RED     = (220, 80, 80)
DARK    = (20, 20, 25)
PANEL   = (28, 28, 35)
BORDER  = (50, 50, 65)

try:
    FONT_BIG   = pygame.font.SysFont("monospace", 72, bold=True)
    FONT_MED   = pygame.font.SysFont("monospace", 28)
    FONT_SM    = pygame.font.SysFont("monospace", 18)
    FONT_TINY  = pygame.font.SysFont("monospace", 13)
except:
    FONT_BIG  = pygame.font.Font(None, 72)
    FONT_MED  = pygame.font.Font(None, 28)
    FONT_SM   = pygame.font.Font(None, 18)
    FONT_TINY = pygame.font.Font(None, 13)

MORSE = {
    ".-": "A",   "-...": "B", "-.-.": "C", "-..": "D",  ".": "E",
    "..-.": "F", "--.": "G",  "....": "H", "..": "I",   ".---": "J",
    "-.-": "K",  ".-..": "L", "--": "M",   "-.": "N",   "---": "O",
    ".--.": "P", "--.-": "Q", ".-.": "R",  "...": "S",  "-": "T",
    "..-": "U",  "...-": "V", ".--": "W",  "-..-": "X", "-.--": "Y",
    "--..": "Z", "-----": "0","----": "1", "..---": "2","...--": "3",
    "....-": "4",".....-": "5","-....": "6","--...": "7","---..": "8",
    "----.": "9"
}

MODE_LETTER = 0
MODE_WORD   = 1
MODE_SENTENCE = 2
MODE_FILE   = 3
MODE_NAMES  = ["Buchstabe", "Wort", "Satz", "Datei"]

INPUT_1KEY  = 0
INPUT_2KEY  = 1

KEY_CONFIG_1 = [
    ("Links lang / Rechts kurz",  {pygame.K_LEFT: "-", pygame.K_RIGHT: "."}),
    ("Links kurz / Links lang",   {pygame.K_LEFT: ".", pygame.K_RIGHT: "-"}),
]
KEY_CONFIG_2 = [
    ("Links lang / Rechts kurz",  {pygame.K_LEFT: "-", pygame.K_RIGHT: "."}),
    ("Links kurz / Links lang",   {pygame.K_LEFT: ".", pygame.K_RIGHT: "-"}),
    ("Beide seltsam / Normal",    {pygame.K_LEFT: "-", pygame.K_RIGHT: "."}),
]

class Overlay:
    def __init__(self):
        self.mode = MODE_LETTER
        self.input_mode = INPUT_1KEY
        self.key_config_idx = 0
        self.current_seq = ""
        self.current_word = ""
        self.output_text = ""
        self.decoded_char = ""
        self.last_key_time = 0
        self.char_timeout = 1.2
        self.word_timeout = 2.5
        self.flash_alpha = 0
        self.flash_char = ""
        self.key_held = {}
        self.hold_start = {}
        self.HOLD_THRESHOLD = 0.4
        self.show_config = False
        self.dots = []
        self.status_msg = ""
        self.status_time = 0

        self.left_pressed = False
        self.right_pressed = False
        self.left_time = 0
        self.right_time = 0

    def get_key_map(self):
        configs = KEY_CONFIG_1 if self.input_mode == INPUT_1KEY else KEY_CONFIG_2
        idx = min(self.key_config_idx, len(configs) - 1)
        return configs[idx][1]

    def add_signal(self, signal):
        self.current_seq += signal
        self.last_key_time = time.time()
        self.dots.append({"val": signal, "t": time.time(), "x": 0})
        self.decoded_char = MORSE.get(self.current_seq, "?")

    def commit_char(self):
        if not self.current_seq:
            return
        ch = MORSE.get(self.current_seq, "")
        if ch:
            self.flash_char = ch
            self.flash_alpha = 255
            if self.mode == MODE_LETTER:
                self.output_text = ch
            elif self.mode == MODE_WORD:
                self.current_word += ch
                self.output_text = self.current_word
            elif self.mode in (MODE_SENTENCE, MODE_FILE):
                self.current_word += ch
                self.output_text = self.current_word
        else:
            self.set_status("?? unbekannte Sequenz: " + self.current_seq)
        self.current_seq = ""
        self.decoded_char = ""
        self.dots = []

    def commit_word(self):
        if self.mode in (MODE_SENTENCE, MODE_FILE):
            if self.current_word:
                self.output_text += " "
                self.current_word = ""
        elif self.mode == MODE_WORD:
            self.current_word = ""
            self.output_text = ""

    def backspace(self):
        if self.current_seq:
            self.current_seq = self.current_seq[:-1]
            self.decoded_char = MORSE.get(self.current_seq, "?") if self.current_seq else ""
            if self.dots:
                self.dots.pop()
        elif self.mode in (MODE_WORD, MODE_SENTENCE, MODE_FILE) and self.current_word:
            self.current_word = self.current_word[:-1]
            self.output_text = self.current_word
        elif self.output_text:
            self.output_text = self.output_text[:-1]

    def set_status(self, msg):
        self.status_msg = msg
        self.status_time = time.time()

    def update(self, dt):
        now = time.time()
        if self.current_seq and (now - self.last_key_time) > self.char_timeout:
            self.commit_char()
        if self.mode in (MODE_SENTENCE, MODE_FILE):
            if self.current_word and not self.current_seq and (now - self.last_key_time) > self.word_timeout:
                self.commit_word()
        if self.flash_alpha > 0:
            self.flash_alpha = max(0, self.flash_alpha - dt * 200)
        if self.status_msg and (now - self.status_time) > 3.0:
            self.status_msg = ""

    def draw(self, surf):
        surf.fill(DARK)

        self._draw_top_bar(surf)
        self._draw_main_display(surf)
        self._draw_mode_bar(surf)
        self._draw_seq_display(surf)
        self._draw_key_hints(surf)
        if self.show_config:
            self._draw_config_panel(surf)

    def _draw_top_bar(self, surf):
        bar = pygame.Rect(0, 0, WIDTH, 44)
        pygame.draw.rect(surf, PANEL, bar)
        pygame.draw.line(surf, BORDER, (0, 44), (WIDTH, 44), 1)

        title = FONT_SM.render("BINÄREINGABE OVERLAY", True, ACCENT)
        surf.blit(title, (16, 12))

        mode_label = FONT_SM.render(
            f"Eingabe: {'1 Taste' if self.input_mode == INPUT_1KEY else '2 Tasten'}  |  "
            f"Config #{self.key_config_idx + 1}",
            True, LGRAY
        )
        surf.blit(mode_label, (WIDTH - mode_label.get_width() - 16, 12))

    def _draw_main_display(self, surf):
        box = pygame.Rect(30, 60, 540, 280)
        pygame.draw.rect(surf, PANEL, box, border_radius=10)
        pygame.draw.rect(surf, BORDER, box, 1, border_radius=10)

        label = FONT_TINY.render("BILD / AUSGABE", True, LGRAY)
        surf.blit(label, (box.x + 12, box.y + 8))

        display_text = self.output_text or "—"
        if self.mode == MODE_LETTER:
            txt = FONT_BIG.render(display_text[-1] if display_text != "—" else "—", True, WHITE)
            surf.blit(txt, (box.centerx - txt.get_width() // 2, box.y + 60))
        else:
            words = display_text.split()
            y = box.y + 40
            line = ""
            for w in words:
                test = line + (" " if line else "") + w
                tw = FONT_MED.size(test)[0]
                if tw > box.width - 24:
                    t = FONT_MED.render(line, True, WHITE)
                    surf.blit(t, (box.x + 12, y))
                    y += 36
                    line = w
                else:
                    line = test
            if line:
                t = FONT_MED.render(line, True, WHITE)
                surf.blit(t, (box.x + 12, y))

        if self.decoded_char and self.decoded_char != "?":
            hint = FONT_MED.render(f"→ {self.decoded_char}", True, GREEN)
            surf.blit(hint, (box.x + 12, box.bottom - 40))

        if self.flash_alpha > 0:
            fa = int(self.flash_alpha)
            flash_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.rect(flash_surf, (80, 200, 120, fa), (0, 0, 60, 60), border_radius=8)
            fc = FONT_MED.render(self.flash_char, True, (255, 255, 255, fa))
            flash_surf.blit(fc, (10, 10))
            surf.blit(flash_surf, (box.right - 70, box.y + 10))

        sub_label = FONT_TINY.render(
            "Buchstabe Drücke Tasten  •  warte auf Timeout oder drücke SPACE",
            True, LGRAY
        )
        surf.blit(sub_label, (box.x + 12, box.bottom + 6))

    def _draw_mode_bar(self, surf):
        panel = pygame.Rect(590, 60, 280, 280)
        pygame.draw.rect(surf, PANEL, panel, border_radius=10)
        pygame.draw.rect(surf, BORDER, panel, 1, border_radius=10)

        label = FONT_TINY.render("MODUSWALL", True, LGRAY)
        surf.blit(label, (panel.x + 12, panel.y + 8))

        icons = ["A", "Hello", "Sätze", "Datei"]
        colors = [ACCENT, GREEN, AMBER, RED]
        for i, (name, icon, col) in enumerate(zip(MODE_NAMES, icons, colors)):
            bx = panel.x + 12 + i * 64
            by = panel.y + 30
            bw, bh = 56, 80
            br = pygame.Rect(bx, by, bw, bh)
            bg = col if self.mode == i else GRAY
            pygame.draw.rect(surf, bg, br, border_radius=6)
            pygame.draw.rect(surf, BORDER, br, 1, border_radius=6)

            ic = FONT_MED.render(icon[0] if i == 0 else icon[:3], True, WHITE)
            surf.blit(ic, (br.centerx - ic.get_width() // 2, br.y + 10))

            nm = FONT_TINY.render(name, True, WHITE)
            surf.blit(nm, (br.centerx - nm.get_width() // 2, br.bottom - 20))

        arrow_y = panel.y + 120
        pygame.draw.polygon(surf, ACCENT, [
            (panel.centerx - 10, arrow_y),
            (panel.centerx + 10, arrow_y),
            (panel.centerx, arrow_y + 20)
        ])

        hint = FONT_TINY.render("TAB = Modus wechseln", True, LGRAY)
        surf.blit(hint, (panel.x + 12, panel.bottom - 20))

    def _draw_seq_display(self, surf):
        box = pygame.Rect(30, 360, 540, 80)
        pygame.draw.rect(surf, PANEL, box, border_radius=8)
        pygame.draw.rect(surf, BORDER, box, 1, border_radius=8)

        label = FONT_TINY.render("AKTUELLE SEQUENZ", True, LGRAY)
        surf.blit(label, (box.x + 10, box.y + 6))

        x = box.x + 10
        for i, sig in enumerate(self.current_seq):
            col = ACCENT if sig == "." else AMBER
            if sig == ".":
                pygame.draw.circle(surf, col, (x + 10, box.centery + 5), 10)
                x += 30
            else:
                pygame.draw.rect(surf, col, (x, box.centery - 4, 34, 18), border_radius=4)
                x += 50

        if not self.current_seq:
            ph = FONT_SM.render("warte auf Eingabe…", True, GRAY)
            surf.blit(ph, (box.x + 10, box.centery - 10))

    def _draw_key_hints(self, surf):
        box = pygame.Rect(30, 455, 840, 120)

        keys = [
            ("LINKS  →  " + ("." if self.get_key_map().get(pygame.K_LEFT) == "." else "−"), ACCENT),
            ("RECHTS →  " + ("." if self.get_key_map().get(pygame.K_RIGHT) == "." else "−"), AMBER),
            ("SPACE  →  Buchstabe abschließen", WHITE),
            ("ENTER  →  Wort abschließen", WHITE),
            ("BACK   →  Löschen", RED),
            ("TAB    →  Modus", GREEN),
            ("C      →  Config", LGRAY),
            ("ESC    →  Beenden", LGRAY),
        ]

        for i, (text, col) in enumerate(keys):
            col_pos = i % 4
            row_pos = i // 4
            x = box.x + col_pos * 210
            y = box.y + row_pos * 24
            t = FONT_TINY.render(text, True, col)
            surf.blit(t, (x, y))

        if self.status_msg:
            st = FONT_SM.render(self.status_msg, True, RED)
            surf.blit(st, (30, HEIGHT - 28))

    def _draw_config_panel(self, surf):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surf.blit(overlay, (0, 0))

        panel = pygame.Rect(150, 100, 600, 380)
        pygame.draw.rect(surf, PANEL, panel, border_radius=12)
        pygame.draw.rect(surf, ACCENT, panel, 2, border_radius=12)

        title = FONT_MED.render("Moduswall — Eingabe-Konfiguration", True, ACCENT)
        surf.blit(title, (panel.x + 20, panel.y + 16))

        configs = KEY_CONFIG_1 if self.input_mode == INPUT_1KEY else KEY_CONFIG_2

        y = panel.y + 60
        for i, (name, km) in enumerate(configs):
            br = pygame.Rect(panel.x + 20, y, panel.width - 40, 50)
            bg = GREEN if i == self.key_config_idx else GRAY
            pygame.draw.rect(surf, bg, br, border_radius=6)
            t = FONT_SM.render(f"[{i+1}] {name}", True, WHITE)
            surf.blit(t, (br.x + 12, br.centery - t.get_height() // 2))
            y += 60

        close = FONT_SM.render("C oder ESC zum Schließen", True, LGRAY)
        surf.blit(close, (panel.x + 20, panel.bottom - 30))

    def handle_key(self, event):
        km = self.get_key_map()
        if event.type == pygame.KEYDOWN:
            if self.show_config:
                if event.key == pygame.K_c or event.key == pygame.K_ESCAPE:
                    self.show_config = False
                elif event.key == pygame.K_1:
                    self.key_config_idx = 0
                elif event.key == pygame.K_2:
                    self.key_config_idx = 1
                elif event.key == pygame.K_3 and self.input_mode == INPUT_2KEY:
                    self.key_config_idx = 2
                return

            if event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()
            elif event.key == pygame.K_c:
                self.show_config = not self.show_config
            elif event.key == pygame.K_TAB:
                self.commit_char()
                self.mode = (self.mode + 1) % 4
                self.output_text = ""
                self.current_word = ""
            elif event.key == pygame.K_i:
                self.commit_char()
                self.input_mode = 1 - self.input_mode
                self.key_config_idx = 0
                self.set_status(f"Eingabe: {'1 Taste' if self.input_mode == 0 else '2 Tasten'}")
            elif event.key == pygame.K_SPACE:
                self.commit_char()
            elif event.key == pygame.K_RETURN:
                self.commit_char()
                self.commit_word()
            elif event.key == pygame.K_BACKSPACE:
                self.backspace()
            elif event.key in km:
                sig = km[event.key]
                self.add_signal(sig)


def main():
    clock = pygame.time.Clock()
    ov = Overlay()

    while True:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            ov.handle_key(event)

        ov.update(dt)
        ov.draw(screen)
        pygame.display.flip()

if __name__ == "__main__":
    main()
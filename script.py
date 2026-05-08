import pygame
import sys
import time
import math

pygame.init()

WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
pygame.display.set_caption("Binäreingabe Overlay")

DARK = (14, 14, 18)
PANEL = (24, 24, 32)
PANEL2 = (32, 32, 44)
BORDER = (55, 55, 75)
ACCENT = (90, 160, 230)
GREEN = (80, 205, 120)
AMBER = (220, 175, 55)
RED = (215, 85, 80)
WHITE = (235, 235, 240)
LGRAY = (130, 130, 150)
GRAY = (65, 65, 80)

MONO = "monospace"
F72 = pygame.font.SysFont(MONO, 72, bold=True)
F48 = pygame.font.SysFont(MONO, 48, bold=True)
F32 = pygame.font.SysFont(MONO, 32, bold=True)
F22 = pygame.font.SysFont(MONO, 22)
F16 = pygame.font.SysFont(MONO, 16)
F13 = pygame.font.SysFont(MONO, 13)

MORSE_TABLE = {
    ".-": "A",
    "-...": "B",
    "-.-.": "C",
    "-..": "D",
    ".": "E",
    "..-.": "F",
    "--.": "G",
    "....": "H",
    "..": "I",
    ".---": "J",
    "-.-": "K",
    ".-..": "L",
    "--": "M",
    "-.": "N",
    "---": "O",
    ".--.": "P",
    "--.-": "Q",
    ".-.": "R",
    "...": "S",
    "-": "T",
    "..-": "U",
    "...-": "V",
    ".--": "W",
    "-..-": "X",
    "-.--": "Y",
    "--..": "Z",
    "-----": "0",
    "----": "1",
    "..---": "2",
    "...--": "3",
    "....-": "4",
    ".....": "5",
    "-....": "6",
    "--...": "7",
    "---..": "8",
    "----.": "9",
    ".-.-.-": ".",
    "--..--": ",",
    "..--..": "?",
}

# Panels: 0=Start, 1=Belegung, 2=Test, 3=Modus, 4=Eingabe
# Bei 1 Taste: Panel 1 (Belegung) wird übersprungen

MODE_NAMES = ["Buchstabe", "Wort", "Satz", "Online"]
MODE_COLORS = [ACCENT, GREEN, AMBER, RED]
MODE_DESCS = [
    "Ein Zeichen\npro Schritt",
    "Ein Wort\naufbauen",
    "Vollstaendige\nSaetze",
    "Online-\nModus",
]

KEY_CONFIGS = [
    ("Links lang / Rechts kurz", {pygame.K_LEFT: "-", pygame.K_RIGHT: "."}),
    ("Links kurz / Rechts lang", {pygame.K_LEFT: ".", pygame.K_RIGHT: "-"}),
    ("Beide: normale Eingabe", {pygame.K_LEFT: ".", pygame.K_RIGHT: "-"}),
]

# Funktionstest: Ziel-Sequenz für "A" = .- (kurz dann lang)
# Für 1 Taste wird nur 1 Taste erwartet; für 2 Tasten: Links (kurz) dann Rechts (lang)
TEST_TARGET = ".-"  # immer "A" = kurz + lang


def rrect(surf, col, r, radius=8):
    pygame.draw.rect(surf, col, r, border_radius=radius)


def rborder(surf, col, r, radius=8, w=1):
    pygame.draw.rect(surf, col, r, w, border_radius=radius)


def txt(surf, font, text, col, pos, center=False):
    s = font.render(text, True, col)
    p = (pos[0] - s.get_width() // 2, pos[1] - s.get_height() // 2) if center else pos
    surf.blit(s, p)
    return s.get_width()


def arrow_btn(surf, rect, direction, hover=False):
    bg = ACCENT if hover else PANEL2
    rrect(surf, bg, rect, 6)
    rborder(surf, ACCENT if not hover else WHITE, rect, 6)
    cx, cy = rect.centerx, rect.centery
    s = 9
    if direction == "right":
        pts = [(cx - s, cy - s), (cx + s, cy), (cx - s, cy + s)]
    else:
        pts = [(cx + s, cy - s), (cx - s, cy), (cx + s, cy + s)]
    pygame.draw.polygon(surf, WHITE if hover else ACCENT, pts)


def draw_mode_icon(surf, mode, cx, cy, size=80, col=None):
    if col is None:
        col = MODE_COLORS[mode]
    s = size

    if mode == 0:
        lw = max(3, s // 14)
        pygame.draw.line(surf, col, (cx - s // 3, cy + s // 2), (cx, cy - s // 2), lw)
        pygame.draw.line(surf, col, (cx, cy - s // 2), (cx + s // 3, cy + s // 2), lw)
        pygame.draw.line(
            surf, col, (cx - s // 5, cy + s // 8), (cx + s // 5, cy + s // 8), lw
        )

    elif mode == 1:
        lw = max(2, s // 18)
        gap = s // 5
        for i, length in enumerate([s * 2 // 3, s // 2, s * 3 // 5]):
            y = cy - s // 3 + i * gap
            pygame.draw.line(surf, col, (cx - s // 2, y), (cx - s // 2 + length, y), lw)

    elif mode == 2:
        lw = max(2, s // 18)
        r = pygame.Rect(cx - s // 2, cy - s // 2, s, s)
        rborder(surf, col, r, 6, lw)
        for i in range(3):
            y = cy - s // 4 + i * (s // 5)
            fw = s * 2 // 3 if i < 2 else s // 3
            pygame.draw.line(
                surf, col, (cx - s // 3, y), (cx - s // 3 + fw, y), max(1, lw - 1)
            )

    elif mode == 3:
        lw = max(2, s // 18)
        r = s // 2
        pygame.draw.circle(surf, col, (cx, cy), r, lw)
        pygame.draw.line(surf, col, (cx - r, cy), (cx + r, cy), lw)
        pygame.draw.line(surf, col, (cx, cy - r), (cx, cy + r), lw)
        for xoff in [-r // 2, r // 2]:
            pts = []
            for a in range(-90, 91, 10):
                rad = math.radians(a)
                px = cx + int(xoff * math.cos(rad))
                py = cy + int(r * math.sin(rad))
                pts.append((px, py))
            if len(pts) > 1:
                pygame.draw.lines(surf, col, False, pts, lw)


def draw_output_image(surf, mode, rect, char_or_text, col):
    cx = rect.centerx
    cy = rect.centery

    if mode == 0:
        draw_mode_icon(surf, 0, cx - 60, cy, size=100, col=col)
        if char_or_text and char_or_text != "—":
            ch = char_or_text[-1]
            t = F72.render(ch, True, WHITE)
            surf.blit(t, (cx + 20, cy - t.get_height() // 2))
        else:
            t = F32.render("?", True, GRAY)
            surf.blit(t, (cx + 20, cy - t.get_height() // 2))

    elif mode == 1:
        draw_mode_icon(surf, 1, cx - 120, cy, size=80, col=col)
        disp = char_or_text if char_or_text else "—"
        t = F32.render(disp, True, WHITE)
        surf.blit(t, (cx - 40, cy - t.get_height() // 2))

    elif mode == 2:
        draw_mode_icon(surf, 2, rect.x + 80, cy, size=80, col=col)
        disp = char_or_text if char_or_text else "—"
        words = disp.split()
        tx = rect.x + 160
        ty = rect.y + 20
        line = ""
        for w in words:
            test = (line + " " + w).strip()
            if F22.size(test)[0] > rect.right - tx - 10:
                t = F22.render(line, True, WHITE)
                surf.blit(t, (tx, ty))
                ty += 32
                line = w
            else:
                line = test
        if line:
            t = F22.render(line, True, WHITE)
            surf.blit(t, (tx, ty))

    elif mode == 3:
        draw_mode_icon(surf, 3, cx - 120, cy, size=80, col=col)
        disp = char_or_text if char_or_text else "—"
        t = F22.render(disp, True, WHITE)
        surf.blit(t, (cx - 40, cy - t.get_height() // 2))


def draw_key_symbol(surf, cx, cy, symbol, lit, size=64):
    """
    Zeichnet ein Tastensymbol (Punkt oder Strich) als großes Grafik-Element.
    lit=True: leuchtend (ACCENT), lit=False: gedimmt (GRAY)
    """
    col = ACCENT if lit else GRAY
    if symbol == ".":
        pygame.draw.circle(surf, col, (cx, cy), size // 2)
    else:  # "-"
        h = size // 3
        r = pygame.Rect(cx - size, cy - h // 2, size * 2, h)
        rrect(surf, col, r, h // 2)


def draw_test_visual(surf, cx, cy, seq, target, num_keys):
    """
    Großes Bild-Platzhalter-Visual für den Funktionstest.
    Zeigt die Ziel-Symbole mit Fortschritt.
    """
    slot_w = 140
    total_w = len(target) * slot_w
    x0 = cx - total_w // 2

    for i, sym in enumerate(target):
        sx = x0 + i * slot_w + slot_w // 2
        lit = i < len(seq)
        draw_key_symbol(surf, sx, cy, sym, lit, size=52)

    # Trennlinie zwischen den Slots
    for i in range(1, len(target)):
        lx = x0 + i * slot_w
        pygame.draw.line(surf, GRAY, (lx, cy - 60), (lx, cy + 60), 1)


class App:
    def __init__(self):
        self.panel = 0
        self.num_keys = 1
        self.key_config = 0
        self.mode = 0
        self.seq = ""
        self.word = ""
        self.output = ""
        self.decoded = ""
        self.last_t = 0
        self.CHAR_TO = 1.3
        self.WORD_TO = 2.5
        self.flash_ch = ""
        self.flash_a = 0.0
        self.status = ""
        self.status_t = 0
        self.slide_x = 0.0
        self.slide_dir = 1
        self.sliding = False

        # Funktionstest-Zustand
        self.test_seq = ""  # bisher gedrückte Test-Sequenz
        self.test_done = False  # Test erfolgreich abgeschlossen
        self.test_error = False  # falscher Tastendruck
        self.test_error_t = 0
        self.test_success_t = 0

        # 1-Taster-Chord-Tracking (beide Tasten gleichzeitig)
        self.chord_keys = set()  # aktuell gehaltene Tasten
        self.chord_press_t = 0.0  # Zeitpunkt des ersten chord-Drucks
        self.chord_active = False  # chord läuft gerade
        self.CHORD_LONG_T = 0.4  # Schwellwert kurz/lang in Sekunden

    # ── Panel-Navigation ──────────────────────────────────────────────────
    # Panels: 0=Start, 1=Belegung, 2=Test, 3=Modus, 4=Eingabe
    # Bei 1 Taste: Panel 1 (Belegung) übersprungen → 0→2→3→4

    def _next_panel(self, current):
        if current == 0:
            return 2 if self.num_keys == 1 else 1
        elif current == 1:
            return 2
        elif current == 2:
            return 3
        elif current == 3:
            return 4
        return current

    def _prev_panel(self, current):
        if current == 4:
            return 3
        elif current == 3:
            return 2
        elif current == 2:
            return 0 if self.num_keys == 1 else 1
        elif current == 1:
            return 0
        return current

    def go(self, target):
        if target < 0 or target > 4:
            return
        if target == 0:
            self.num_keys = 1
        if target == 2:
            # Test-Panel neu starten
            self.test_seq = ""
            self.test_done = False
            self.test_error = False
            self.chord_keys = set()
            self.chord_active = False
        self.slide_dir = 1 if target > self.panel else -1
        self.panel = target
        self.slide_x = float(WIDTH * self.slide_dir)
        self.sliding = True

    def go_next(self):
        self.go(self._next_panel(self.panel))

    def go_back(self):
        self.go(self._prev_panel(self.panel))

    def _btn_back(self):
        return pygame.Rect(14, HEIGHT // 2 - 32, 44, 64)

    def _btn_next(self):
        return pygame.Rect(WIDTH - 58, HEIGHT // 2 - 32, 44, 64)

    def _mode_btn(self, i):
        bw, bh = 200, 190
        gap = 26
        total = 4 * bw + 3 * gap
        x0 = WIDTH // 2 - total // 2
        return pygame.Rect(x0 + i * (bw + gap), 180, bw, bh)

    # ── Morse ──────────────────────────────────────────────────────────────
    def km(self):
        return KEY_CONFIGS[self.key_config][1]

    def add_sig(self, s):
        self.seq += s
        self.last_t = time.time()
        self.decoded = MORSE_TABLE.get(self.seq, "?")

    def commit_char(self):
        if not self.seq:
            return
        ch = MORSE_TABLE.get(self.seq, "")
        if ch:
            self.flash_ch = ch
            self.flash_a = 255.0
            if self.mode == 0:
                self.output = ch
            else:
                self.word += ch
                self.output = self.word
        else:
            self.status = f"Unbekannt: {self.seq}"
            self.status_t = time.time()
        self.seq = ""
        self.decoded = ""

    def commit_word(self):
        if self.mode >= 2:
            self.output = self.word + " "
            self.word = ""
        elif self.mode == 1:
            self.output = self.word
            self.word = ""

    def backspace(self):
        if self.seq:
            self.seq = self.seq[:-1]
            self.decoded = MORSE_TABLE.get(self.seq, "?") if self.seq else ""
        elif self.word:
            self.word = self.word[:-1]
            self.output = self.word
        elif self.output:
            self.output = self.output[:-1]

    # ── Funktionstest-Logik ────────────────────────────────────────────────
    def _test_expected_sym(self):
        """Gibt das Symbol zurück, das als nächstes im Test erwartet wird."""
        target = self._test_target()
        if len(self.test_seq) < len(target):
            return target[len(self.test_seq)]
        return None

    def _test_target(self):
        """Gibt die Ziel-Sequenz zurück (abhängig von Tastenbelegung)."""
        # Ziel ist immer ".-" (A) — kurz dann lang.
        # Wir übersetzen das in die aktuell konfigurierte Belegung.
        km = self.km()
        # Finde welche Taste kurz (.) und welche lang (-) ist
        # target[0]="." → welche Taste erzeugt "."?
        return TEST_TARGET

    def test_key(self, sig):
        """Verarbeitet einen Tastendruck im Test-Panel (2-Taster-Modus)."""
        if self.test_done:
            return
        target = self._test_target()
        expected = (
            target[len(self.test_seq)] if len(self.test_seq) < len(target) else None
        )
        if expected is None:
            return
        if sig == expected:
            self.test_seq += sig
            self.test_error = False
            if self.test_seq == target:
                self.test_done = True
                self.test_success_t = time.time()
        else:
            self.test_error = True
            self.test_error_t = time.time()
            self.test_seq = ""

    def test_chord_down(self, key):
        """Beide Tasten gleichzeitig: KEYDOWN für 1-Taster-Test."""
        if self.test_done:
            return
        if key not in (pygame.K_LEFT, pygame.K_RIGHT):
            return
        if not self.chord_active:
            self.chord_active = True
            self.chord_press_t = time.time()
        self.chord_keys.add(key)

    def test_chord_up(self, key):
        """KEYUP — Loslassen beendet den Chord und wertet Dauer aus."""
        if self.test_done or not self.chord_active:
            return
        if key not in (pygame.K_LEFT, pygame.K_RIGHT):
            return
        self.chord_keys.discard(key)
        if len(self.chord_keys) == 0:
            # Beide Tasten losgelassen → Signal auswerten
            duration = time.time() - self.chord_press_t
            sig = "-" if duration >= self.CHORD_LONG_T else "."
            self.chord_active = False
            # Jetzt in Test-Sequenz eintragen
            target = self._test_target()
            if len(self.test_seq) < len(target):
                expected = target[len(self.test_seq)]
                if sig == expected:
                    self.test_seq += sig
                    self.test_error = False
                    if self.test_seq == target:
                        self.test_done = True
                        self.test_success_t = time.time()
                else:
                    self.test_error = True
                    self.test_error_t = time.time()
                    self.test_seq = ""

    # ── Update ─────────────────────────────────────────────────────────────
    def update(self, dt):
        now = time.time()
        if self.seq and (now - self.last_t) > self.CHAR_TO:
            self.commit_char()
        if (
            self.mode >= 2
            and self.word
            and not self.seq
            and (now - self.last_t) > self.WORD_TO
        ):
            self.commit_word()
        if self.flash_a > 0:
            self.flash_a = max(0.0, self.flash_a - dt * 220)
        if self.status and (now - self.status_t) > 3:
            self.status = ""
        if self.test_error and (now - self.test_error_t) > 0.8:
            self.test_error = False
        # Auto-Weiter nach erfolgreichem Test
        if self.test_done and not self.sliding and (now - self.test_success_t) > 1.2:
            self.go_next()
            self.test_done = False
        if self.sliding:
            speed = WIDTH * dt * 7
            if self.slide_dir == 1:
                self.slide_x = max(0.0, self.slide_x - speed)
            else:
                self.slide_x = min(0.0, self.slide_x + speed)
            if abs(self.slide_x) < 2:
                self.slide_x = 0.0
                self.sliding = False

    # ── Events ─────────────────────────────────────────────────────────────
    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            self._key(event)
        if event.type == pygame.KEYUP:
            self._key_up(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._click(event.pos)

    def _key(self, ev):
        if self.sliding:
            return
        if ev.key == pygame.K_q and (pygame.key.get_mods() & pygame.KMOD_CTRL):
            pygame.quit()
            sys.exit()

        if self.panel == 4:
            km = self.km()
            if ev.key == pygame.K_ESCAPE:
                self.go_back()
            elif ev.key == pygame.K_SPACE:
                self.commit_char()
            elif ev.key == pygame.K_RETURN:
                self.commit_char()
                self.commit_word()
            elif ev.key == pygame.K_BACKSPACE:
                self.backspace()
            elif ev.key in km:
                self.add_sig(km[ev.key])

        elif self.panel == 2:
            # Funktionstest
            km = self.km()
            if ev.key == pygame.K_ESCAPE:
                self.go_back()
            elif ev.key == pygame.K_RETURN and self.test_done:
                self.go_next()
            elif ev.key == pygame.K_RETURN and not self.test_done:
                self.go_next()
            elif self.num_keys == 1:
                # 1-Taster: Chord-Tracking (KEYDOWN-Seite)
                self.test_chord_down(ev.key)
            elif ev.key in km:
                # 2-Taster: direkte Signalauswertung
                self.test_key(km[ev.key])

    def _key_up(self, ev):
        if self.sliding:
            return
        if self.panel == 2 and self.num_keys == 1:
            self.test_chord_up(ev.key)

        else:
            if ev.key == pygame.K_ESCAPE:
                if self.panel > 0:
                    self.go_back()
                else:
                    pygame.quit()
                    sys.exit()
            elif ev.key == pygame.K_RETURN:
                self.go_next()

    def _click(self, pos):
        if self.sliding:
            return
        mx, my = pos
        if self.panel > 0 and self._btn_back().collidepoint(mx, my):
            self.go_back()
            return
        if self.panel < 4 and self._btn_next().collidepoint(mx, my):
            self.go_next()
            return

        if self.panel == 0:
            for i, r in enumerate(
                [
                    pygame.Rect(WIDTH // 2 - 230, 200, 200, 100),
                    pygame.Rect(WIDTH // 2 + 30, 200, 200, 100),
                ]
            ):
                if r.collidepoint(mx, my):
                    self.num_keys = i + 1
                    self.go_next()
                    return

        elif self.panel == 1:
            for i in range(len(KEY_CONFIGS)):
                r = pygame.Rect(WIDTH // 2 - 320, 170 + i * 100, 640, 82)
                if r.collidepoint(mx, my):
                    self.key_config = i
                    self.go_next()
                    return

        elif self.panel == 3:
            for i in range(4):
                if self._mode_btn(i).collidepoint(mx, my):
                    self.mode = i
                    self.go_next()
                    return

    # ── Draw ───────────────────────────────────────────────────────────────
    def draw(self, surf):
        surf.fill(DARK)
        mx, my = pygame.mouse.get_pos()
        ox = int(self.slide_x)

        old_clip = surf.get_clip()
        surf.set_clip(pygame.Rect(60, 55, WIDTH - 120, HEIGHT - 65))
        [self._p0, self._p1, self._p2, self._p3, self._p4][self.panel](surf, ox)
        surf.set_clip(old_clip)

        self._progress(surf)

        if not self.sliding:
            if self.panel > 0:
                br = self._btn_back()
                arrow_btn(surf, br, "left", br.collidepoint(mx, my))
            if self.panel < 4:
                nr = self._btn_next()
                arrow_btn(surf, nr, "right", nr.collidepoint(mx, my))

        if self.status:
            t = F16.render(self.status, True, RED)
            surf.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT - 26))

    def _progress(self, surf):
        if self.num_keys == 1:
            steps = [(0, "Start"), (2, "Test"), (3, "Modus"), (4, "Eingabe")]
        else:
            steps = [
                (0, "Start"),
                (1, "Belegung"),
                (2, "Test"),
                (3, "Modus"),
                (4, "Eingabe"),
            ]
        y = 28
        n = len(steps)
        step_w = 180
        x0 = WIDTH // 2 - (n - 1) * step_w // 2
        for idx, (panel_id, name) in enumerate(steps):
            cx = x0 + idx * step_w
            active = panel_id == self.panel
            done = panel_id < self.panel
            col = ACCENT if active else (GREEN if done else GRAY)
            r = 9 if active else 6
            pygame.draw.circle(surf, col, (cx, y), r)
            if active:
                pygame.draw.circle(surf, WHITE, (cx, y), 4)
            tc = WHITE if active else (LGRAY if done else GRAY)
            txt(surf, F13, name, tc, (cx, y + 16), center=True)
            if idx < n - 1:
                nx = x0 + (idx + 1) * step_w
                lc = GREEN if done else GRAY
                pygame.draw.line(surf, lc, (cx + r + 2, y), (nx - r - 2, y), 2)

    # ── Panel 0: Start ─────────────────────────────────────────────────────
    def _p0(self, surf, ox):
        cx = WIDTH // 2 + ox
        txt(surf, F32, "Wie viele Tasten?", WHITE, (cx, 140), center=True)
        txt(surf, F16, "Wähle deine Eingabemethode", LGRAY, (cx, 178), center=True)
        mx, my = pygame.mouse.get_pos()
        for i, (n, desc) in enumerate(
            [
                ("1 Taste", "← oder →"),
                ("2 Tasten", "← und →"),
            ]
        ):
            col = ACCENT
            r = pygame.Rect(cx - 230 + i * 260, 200, 200, 100)
            hov = r.collidepoint(mx, my)
            active = self.num_keys == i + 1
            bg = col if active else (PANEL2 if not hov else GRAY)
            rrect(surf, bg, r, 12)
            rborder(surf, col, r, 12, 2 if active else 1)
            draw_mode_icon(
                surf,
                i,
                r.centerx,
                r.centery - 10,
                size=36,
                col=WHITE if active else col,
            )
            txt(surf, F16, n, WHITE, (r.centerx, r.centery + 22), center=True)
            txt(
                surf,
                F13,
                desc,
                (WHITE if active else LGRAY),
                (r.centerx, r.centery + 44),
                center=True,
            )
        txt(
            surf,
            F13,
            "Klicke eine Option an oder drücke Weiter →",
            LGRAY,
            (cx, 350),
            center=True,
        )

    # ── Panel 1: Belegung ──────────────────────────────────────────────────
    def _p1(self, surf, ox):
        cx = WIDTH // 2 + ox
        txt(surf, F32, "Tastenbelegung", WHITE, (cx, 100), center=True)
        txt(surf, F16, "Wie ist Links/Rechts belegt?", LGRAY, (cx, 138), center=True)
        mx, my = pygame.mouse.get_pos()
        for i, (name, km) in enumerate(KEY_CONFIGS):
            r = pygame.Rect(cx - 320, 170 + i * 100, 640, 82)
            hov = r.collidepoint(mx, my)
            active = i == self.key_config
            bg = ACCENT if active else (PANEL2 if not hov else GRAY)
            rrect(surf, bg, r, 8)
            rborder(surf, ACCENT if active else BORDER, r, 8, 2 if active else 1)
            lv = km[pygame.K_LEFT]
            rv = km[pygame.K_RIGHT]
            ls = "LANG (−)" if lv == "-" else "KURZ (.)"
            rs = "LANG (−)" if rv == "-" else "KURZ (.)"
            txt(
                surf,
                F16,
                f"←  {ls}     |     →  {rs}",
                WHITE,
                (r.centerx, r.centery - 12),
                center=True,
            )
            txt(
                surf,
                F13,
                name,
                WHITE if active else LGRAY,
                (r.centerx, r.centery + 14),
                center=True,
            )
        txt(
            surf,
            F13,
            "Klicke eine Belegung oder drücke Weiter →",
            LGRAY,
            (cx, 480),
            center=True,
        )

    # ── Panel 2: Funktionstest ─────────────────────────────────────────────
    def _p2(self, surf, ox):
        cx = WIDTH // 2 + ox
        km = self.km()
        target = self._test_target()
        n = self.num_keys

        # ── Titel ──
        txt(surf, F32, "Funktionstest", WHITE, (cx, 82), center=True)

        # ── Großes Bild-Visual (obere Hälfte) ─────────────────────────────
        vis_rect = pygame.Rect(cx - 420, 105, 840, 280)
        rrect(surf, PANEL, vis_rect, 14)
        rborder(surf, BORDER, vis_rect, 14)

        if self.test_done:
            # Erfolgs-Anzeige
            rrect(surf, (20, 55, 30), vis_rect, 14)
            rborder(surf, GREEN, vis_rect, 14, 2)
            t = F72.render("A", True, GREEN)
            surf.blit(
                t,
                (cx - t.get_width() // 2 - 60, vis_rect.centery - t.get_height() // 2),
            )
            t2 = F48.render(".-", True, GREEN)
            surf.blit(t2, (cx + 20, vis_rect.centery - t2.get_height() // 2))
            t3 = F22.render("✓  Erfolgreich!", True, GREEN)
            surf.blit(t3, (cx - t3.get_width() // 2, vis_rect.bottom - 44))
        elif self.test_error:
            rrect(surf, (55, 20, 20), vis_rect, 14)
            rborder(surf, RED, vis_rect, 14, 2)
            t = F32.render("Falsche Taste — nochmal!", True, RED)
            surf.blit(
                t, (cx - t.get_width() // 2, vis_rect.centery - t.get_height() // 2)
            )
        elif n == 1:
            # 1-Taster: beide Tasten gleichzeitig → zeige ←+→ Symbol + Schritt-Fortschritt
            vis_cx = vis_rect.centerx
            vis_cy = vis_rect.centery - 10

            # Tastenpaar-Symbol (beide Pfeile + Plus)
            key_r = pygame.Rect(vis_cx - 220, vis_cy - 50, 90, 90)
            both_lit = self.chord_active
            key_col = ACCENT if both_lit else GRAY
            rrect(surf, PANEL2 if not both_lit else (30, 60, 100), key_r, 12)
            rborder(surf, key_col, key_r, 12, 2)
            t = F32.render("←", True, key_col)
            surf.blit(
                t,
                (
                    key_r.centerx - t.get_width() // 2,
                    key_r.centery - t.get_height() // 2,
                ),
            )

            txt(surf, F32, "+", LGRAY, (vis_cx - 100, vis_cy - 16), center=True)

            key_r2 = pygame.Rect(vis_cx - 60, vis_cy - 50, 90, 90)
            rrect(surf, PANEL2 if not both_lit else (30, 60, 100), key_r2, 12)
            rborder(surf, key_col, key_r2, 12, 2)
            t2 = F32.render("→", True, key_col)
            surf.blit(
                t2,
                (
                    key_r2.centerx - t2.get_width() // 2,
                    key_r2.centery - t2.get_height() // 2,
                ),
            )

            # Pfeil rechts
            txt(surf, F32, "→", LGRAY, (vis_cx + 60, vis_cy - 16), center=True)

            # Fortschritt: zwei Slot-Symbole rechts
            for i, sym in enumerate(target):
                sx = vis_cx + 120 + i * 130
                lit = i < len(self.test_seq)
                slot_r = pygame.Rect(sx - 50, vis_cy - 50, 100, 90)
                rrect(surf, PANEL2, slot_r, 10)
                rborder(surf, ACCENT if lit else BORDER, slot_r, 10, 2 if lit else 1)
                draw_key_symbol(surf, sx, vis_cy - 10, sym, lit, size=34)
                lbl = "KURZ" if sym == "." else "LANG"
                txt(
                    surf,
                    F13,
                    lbl,
                    ACCENT if lit else LGRAY,
                    (sx, vis_cy + 34),
                    center=True,
                )
                if i < len(target) - 1:
                    pygame.draw.polygon(
                        surf,
                        GRAY,
                        [
                            (sx + 58, vis_cy - 10),
                            (sx + 72, vis_cy),
                            (sx + 58, vis_cy + 10),
                        ],
                    )

            # Fortschritts-Zähler
            prog_txt = f"{len(self.test_seq)} / {len(target)}"
            t = F16.render(prog_txt, True, LGRAY)
            surf.blit(t, (vis_rect.right - t.get_width() - 14, vis_rect.bottom - 30))
        else:
            # Fortschritts-Visual: Symbole der Ziel-Sequenz
            vis_cx = vis_rect.centerx
            vis_cy = vis_rect.centery - 20

            # Ziel-Symbole groß darstellen
            slot_w = 160
            total_w = len(target) * slot_w
            x0 = vis_cx - total_w // 2

            for i, sym in enumerate(target):
                sx = x0 + i * slot_w + slot_w // 2
                lit = i < len(self.test_seq)

                # Slot-Hintergrund
                slot_r = pygame.Rect(sx - 60, vis_cy - 56, 120, 112)
                rrect(surf, PANEL2, slot_r, 10)
                rborder(surf, ACCENT if lit else BORDER, slot_r, 10, 2 if lit else 1)

                # Symbol zeichnen
                draw_key_symbol(surf, sx, vis_cy, sym, lit, size=44)

                # Bezeichnung unter dem Symbol
                label = "KURZ (.)" if sym == "." else "LANG (−)"
                label_col = ACCENT if lit else LGRAY
                txt(surf, F13, label, label_col, (sx, vis_cy + 70), center=True)

                # Trennpfeil zwischen Slots
                if i < len(target) - 1:
                    ax = x0 + (i + 1) * slot_w
                    pygame.draw.polygon(
                        surf,
                        GRAY,
                        [
                            (ax - 10, vis_cy - 10),
                            (ax + 10, vis_cy),
                            (ax - 10, vis_cy + 10),
                        ],
                    )

            # Fortschrittsanzeige (Schrittanzahl)
            prog_txt = f"{len(self.test_seq)} / {len(target)}"
            t = F16.render(prog_txt, True, LGRAY)
            surf.blit(t, (vis_rect.right - t.get_width() - 14, vis_rect.bottom - 30))

        # ── Instruktionen (untere Hälfte) ──────────────────────────────────
        instr_y = vis_rect.bottom + 24

        if not self.test_done:
            if n == 1:
                # 1-Taster: beide Tasten gleichzeitig, Haltezeit = kurz/lang
                step1_done = len(self.test_seq) >= 1
                step2_done = len(self.test_seq) >= 2
                step1_active = not step1_done
                step2_active = step1_done and not step2_done

                txt(
                    surf,
                    F22,
                    "Drücke ← und → gleichzeitig:",
                    WHITE,
                    (cx, instr_y),
                    center=True,
                )

                # Live-Haltezeit-Balken (wenn chord gerade aktiv)
                now = time.time()
                bar_y = instr_y + 26
                bar_r = pygame.Rect(cx - 200, bar_y, 400, 10)
                rrect(surf, PANEL2, bar_r, 5)
                if self.chord_active:
                    held = min(
                        time.time() - self.chord_press_t, self.CHORD_LONG_T * 1.5
                    )
                    prog = min(held / self.CHORD_LONG_T, 1.0)
                    fw = int(400 * prog)
                    if fw > 0:
                        bar_col = (
                            RED if prog >= 1.0 else (AMBER if prog > 0.5 else ACCENT)
                        )
                        rrect(surf, bar_col, pygame.Rect(bar_r.x, bar_r.y, fw, 10), 5)
                    # Schwellwert-Markierung
                    mx_mark = bar_r.x + 400 * 1 // 1  # immer am Ende = 100%
                    pygame.draw.line(
                        surf,
                        AMBER,
                        (bar_r.x + 400, bar_r.y - 4),
                        (bar_r.x + 400, bar_r.y + 14),
                        2,
                    )
                else:
                    rborder(surf, BORDER, bar_r, 5)

                # Schwellwert-Linie in der Mitte (visuell: nach CHORD_LONG_T = voll)
                thresh_x = bar_r.x + int(
                    400 * (self.CHORD_LONG_T / (self.CHORD_LONG_T * 1.5))
                )
                pygame.draw.line(
                    surf, AMBER, (thresh_x, bar_r.y - 5), (thresh_x, bar_r.y + 15), 2
                )
                txt(surf, F13, "LANG", AMBER, (thresh_x + 6, bar_r.y + 2))

                # Schritt-Karten
                step1_col = GREEN if step1_done else (ACCENT if step1_active else LGRAY)
                step2_col = GREEN if step2_done else (ACCENT if step2_active else LGRAY)

                r1 = pygame.Rect(cx - 320, instr_y + 48, 280, 72)
                rrect(surf, PANEL2, r1, 10)
                rborder(surf, step1_col, r1, 10, 2)
                mark1 = "✓" if step1_done else ("▶" if step1_active else " ")
                txt(
                    surf,
                    F22,
                    f"{mark1}  ← + →  kurz  →  KURZ (.)",
                    step1_col,
                    (r1.centerx, r1.centery),
                    center=True,
                )

                r2 = pygame.Rect(cx + 40, instr_y + 48, 280, 72)
                rrect(surf, PANEL2, r2, 10)
                rborder(surf, step2_col, r2, 10, 2)
                mark2 = "✓" if step2_done else ("▶" if step2_active else " ")
                txt(
                    surf,
                    F22,
                    f"{mark2}  ← + →  lang  →  LANG (−)",
                    step2_col,
                    (r2.centerx, r2.centery),
                    center=True,
                )

                txt(
                    surf,
                    F13,
                    f"Kurz = loslassen vor dem Balken  |  Lang = halten bis Balken voll  ({int(self.CHORD_LONG_T*1000)} ms)",
                    LGRAY,
                    (cx, instr_y + 134),
                    center=True,
                )

            else:
                # 2-Tasten: Erst Links dann Rechts
                lv = km[pygame.K_LEFT]
                rv = km[pygame.K_RIGHT]
                step1_sym = target[0]
                step2_sym = target[1]

                # Welche Taste für Schritt 1?
                key1_name = "←" if lv == step1_sym else "→"
                key2_name = "←" if lv == step2_sym else "→"

                txt(
                    surf,
                    F22,
                    "Drücke die Tasten nacheinander:",
                    WHITE,
                    (cx, instr_y),
                    center=True,
                )

                step1_col = (
                    ACCENT
                    if len(self.test_seq) == 0
                    else (GREEN if len(self.test_seq) >= 1 else LGRAY)
                )
                step2_col = (
                    ACCENT
                    if len(self.test_seq) == 1
                    else (GREEN if len(self.test_seq) >= 2 else LGRAY)
                )

                # Schritt 1: linke Taste
                r1 = pygame.Rect(cx - 310, instr_y + 32, 270, 68)
                rrect(surf, PANEL2, r1, 10)
                rborder(surf, step1_col, r1, 10, 2)
                s1_label = "KURZ (.)" if step1_sym == "." else "LANG (−)"
                txt(
                    surf,
                    F22,
                    f"1.  {key1_name}  →  {s1_label}",
                    step1_col,
                    (r1.centerx, r1.centery),
                    center=True,
                )

                # Pfeil
                pygame.draw.polygon(
                    surf,
                    GRAY,
                    [
                        (cx - 22, instr_y + 66),
                        (cx + 2, instr_y + 80),
                        (cx - 22, instr_y + 94),
                    ],
                )

                # Schritt 2: rechte Taste
                r2 = pygame.Rect(cx + 40, instr_y + 32, 270, 68)
                rrect(surf, PANEL2, r2, 10)
                rborder(surf, step2_col, r2, 10, 2)
                s2_label = "KURZ (.)" if step2_sym == "." else "LANG (−)"
                txt(
                    surf,
                    F22,
                    f"2.  {key2_name}  →  {s2_label}",
                    step2_col,
                    (r2.centerx, r2.centery),
                    center=True,
                )

                txt(
                    surf,
                    F13,
                    "Ziel-Zeichen:  A  =  .-  (kurz, dann lang)",
                    LGRAY,
                    (cx, instr_y + 120),
                    center=True,
                )
        else:
            txt(
                surf,
                F22,
                "Weiter mit ENTER oder warte kurz…",
                LGRAY,
                (cx, instr_y + 40),
                center=True,
            )

    # ── Panel 3: Moduswahl ────────────────────────────────────────────────
    def _p3(self, surf, ox):
        cx = WIDTH // 2 + ox
        txt(surf, F32, "Modus wählen", WHITE, (cx, 100), center=True)
        txt(surf, F16, "Was möchtest du eingeben?", LGRAY, (cx, 138), center=True)
        mx, my = pygame.mouse.get_pos()
        for i in range(4):
            r = self._mode_btn(i)
            r = pygame.Rect(r.x + ox, r.y, r.w, r.h)
            hov = r.collidepoint(mx, my)
            active = i == self.mode
            col = MODE_COLORS[i]
            bg = col if active else (PANEL2 if not hov else GRAY)
            rrect(surf, bg, r, 12)
            rborder(surf, col, r, 12, 2 if active else 1)
            draw_mode_icon(
                surf, i, r.centerx, r.y + 68, size=60, col=WHITE if active else col
            )
            txt(surf, F16, MODE_NAMES[i], WHITE, (r.centerx, r.y + 118), center=True)
            for j, line in enumerate(MODE_DESCS[i].split("\n")):
                txt(
                    surf,
                    F13,
                    line,
                    (WHITE if active else LGRAY),
                    (r.centerx, r.y + 142 + j * 18),
                    center=True,
                )
        txt(
            surf,
            F13,
            "Klicke einen Modus oder drücke Weiter →",
            LGRAY,
            (cx, 410),
            center=True,
        )

    # ── Panel 4: Eingabe ──────────────────────────────────────────────────
    def _p4(self, surf, ox):
        cx = WIDTH // 2 + ox
        col = MODE_COLORS[self.mode]

        txt(surf, F22, f"Modus: {MODE_NAMES[self.mode]}", col, (cx, 72), center=True)
        km = self.km()
        ls = "LANG" if km[pygame.K_LEFT] == "-" else "KURZ"
        rs = "LANG" if km[pygame.K_RIGHT] == "-" else "KURZ"
        txt(
            surf,
            F13,
            f"←={ls}   →={rs}   SPACE=Zeichen abschließen   ENTER=Wort   BACK=löschen",
            LGRAY,
            (cx, 98),
            center=True,
        )

        out = pygame.Rect(cx - 460, 115, 920, 210)
        rrect(surf, PANEL, out, 12)
        rborder(surf, col, out, 12)
        txt(surf, F13, "AUSGABE", LGRAY, (out.x + 12, out.y + 8))

        disp = self.output or (self.word if self.word else "")
        draw_output_image(
            surf,
            self.mode,
            pygame.Rect(out.x + 12, out.y + 24, out.w - 24, out.h - 32),
            disp,
            col,
        )

        if self.flash_a > 0:
            fa = int(self.flash_a)
            fs = pygame.Surface((80, 80), pygame.SRCALPHA)
            pygame.draw.rect(fs, (*GREEN, fa), (0, 0, 80, 80), border_radius=10)
            draw_mode_icon(fs, self.mode, 40, 40, size=44, col=(255, 255, 255))
            surf.blit(fs, (out.right - 90, out.y + 10))

        seq_r = pygame.Rect(cx - 460, 338, 920, 72)
        rrect(surf, PANEL, seq_r, 8)
        rborder(surf, BORDER, seq_r, 8)
        txt(surf, F13, "AKTUELLE SEQUENZ", LGRAY, (seq_r.x + 12, seq_r.y + 6))
        x = seq_r.x + 16
        for sig in self.seq:
            if sig == ".":
                pygame.draw.circle(surf, ACCENT, (x + 12, seq_r.centery + 4), 12)
                x += 34
            else:
                pygame.draw.rect(
                    surf, AMBER, (x, seq_r.centery - 8, 40, 22), border_radius=4
                )
                x += 56
        if self.decoded and self.decoded != "?":
            dt = F22.render(f"→ {self.decoded}", True, GREEN)
            surf.blit(dt, (seq_r.right - dt.get_width() - 14, seq_r.centery - 11))
        if not self.seq:
            txt(
                surf,
                F16,
                "warte auf Eingabe…",
                GRAY,
                (seq_r.x + 16, seq_r.centery - 10),
            )

        now = time.time()
        if self.seq:
            prog = min((now - self.last_t) / self.CHAR_TO, 1.0)
            br = pygame.Rect(cx - 460, 415, 920, 7)
            rrect(surf, GRAY, br, 3)
            fw = int(920 * prog)
            if fw > 0:
                fc = GREEN if prog < 0.6 else (AMBER if prog < 0.85 else RED)
                rrect(surf, fc, pygame.Rect(br.x, br.y, fw, 7), 3)

        txt(surf, F13, "REFERENZ:", LGRAY, (cx - 460, 432))
        refs = [
            ("A", ".-"),
            ("E", "."),
            ("I", ".."),
            ("M", "--"),
            ("N", "-."),
            ("O", "---"),
            ("S", "..."),
            ("T", "-"),
            ("U", "..-"),
            ("R", ".-."),
        ]
        for j, (ch, sq) in enumerate(refs):
            txt(surf, F13, f"{ch}:{sq}", LGRAY, (cx - 360 + j * 80, 432))


def main():
    clock = pygame.time.Clock()
    app = App()
    while True:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            app.handle(event)
        app.update(dt)
        app.draw(screen)
        pygame.display.flip()


if __name__ == "__main__":
    main()

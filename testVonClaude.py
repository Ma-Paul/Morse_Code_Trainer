"""
Morse Eingabegerät – CustomTkinter GUI
Raspberry Pi 3B · Python 3

Installation:
    pip install customtkinter

Starten:
    python morse_gui.py
"""

import customtkinter as ctk

# ── Erscheinungsbild ──────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

FONT_TITLE  = ("Courier New", 22, "bold")
FONT_SUB    = ("Courier New", 13)
FONT_BTN    = ("Courier New", 14, "bold")
FONT_MONO   = ("Courier New", 28, "bold")
FONT_SMALL  = ("Courier New", 11)

COLOR_ACCENT  = "#00e5ff"
COLOR_GREEN   = "#39ff8f"
COLOR_MUTED   = "#4a5568"
COLOR_SURFACE = "#1a1d26"
COLOR_BG      = "#0d0f14"


# ═══════════════════════════════════════════════════════════════════
class MorseApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Morse Eingabegerät")
        self.geometry("480x520")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BG)

        # Zustand
        self.taste_anzahl = None   # "1" oder "2"
        self.modus        = None   # nur bei 2 Tasten
        self.morse_puffer = ""

        # Haupt-Container (alle Screens leben hier)
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=24, pady=20)

        self.screens = {}
        for ScreenClass in (Screen1Tasten, Screen2Modus, Screen3Bestaetigen, Screen4Bereit):
            name = ScreenClass.__name__
            frame = ScreenClass(self.container, app=self)
            frame.grid(row=0, column=0, sticky="nsew")
            self.screens[name] = frame

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.zeige_screen("Screen1Tasten")

    # ── Navigation ────────────────────────────────────────────────
    def zeige_screen(self, name: str):
        self.screens[name].tkraise()
        self.screens[name].on_enter()

    def weiter_von_screen1(self, anzahl: str):
        self.taste_anzahl = anzahl
        if anzahl == "1":
            self.zeige_screen("Screen3Bestaetigen")
        else:
            self.zeige_screen("Screen2Modus")

    def weiter_von_screen2(self, modus: str):
        self.modus = modus
        self.zeige_screen("Screen3Bestaetigen")

    def starten(self):
        self.zeige_screen("Screen4Bereit")

    def neu_konfigurieren(self):
        self.taste_anzahl = None
        self.modus        = None
        self.morse_puffer = ""
        self.zeige_screen("Screen1Tasten")


# ═══════════════════════════════════════════════════════════════════
class BaseScreen(ctk.CTkFrame):
    """Basis-Klasse für alle Screens."""
    def __init__(self, parent, app: MorseApp):
        super().__init__(parent, fg_color=COLOR_SURFACE, corner_radius=14)
        self.app = app

    def on_enter(self):
        """Wird aufgerufen, wenn der Screen sichtbar wird."""
        pass

    def _header(self, schritt: str, titel: str, untertitel: str):
        ctk.CTkLabel(self, text=schritt,
                     font=FONT_SMALL, text_color=COLOR_MUTED).pack(anchor="w", padx=20, pady=(18, 0))
        ctk.CTkLabel(self, text=titel,
                     font=FONT_TITLE, text_color="white").pack(anchor="w", padx=20, pady=(4, 0))
        ctk.CTkLabel(self, text=untertitel,
                     font=FONT_SUB, text_color=COLOR_MUTED, wraplength=380).pack(anchor="w", padx=20, pady=(2, 12))
        ctk.CTkFrame(self, height=1, fg_color="#1e2530").pack(fill="x", padx=20, pady=(0, 14))


# ═══════════════════════════════════════════════════════════════════
class Screen1Tasten(BaseScreen):
    """Schritt 1: 1 oder 2 Tasten wählen."""

    def __init__(self, parent, app):
        super().__init__(parent, app)
        self._header(
            "SCHRITT 1 / SETUP",
            "Wie viele Tasten?",
            "Wähle die Hardware-Konfiguration deines Geräts."
        )
        self._btn("◉   1 Taste",
                  "Punkt & Strich durch Druckdauer unterschieden",
                  lambda: app.weiter_von_screen1("1"))
        self._btn("◉◉  2 Tasten",
                  "Je eine Taste für Punkt  /  Strich",
                  lambda: app.weiter_von_screen1("2"))

        ctk.CTkLabel(self,
                     text="ℹ  Bei 1 Taste entfällt die Modusauswahl.",
                     font=FONT_SMALL, text_color=COLOR_MUTED).pack(anchor="w", padx=24, pady=(14, 0))

    def _btn(self, label, sub, cmd):
        frame = ctk.CTkFrame(self, fg_color=COLOR_BG, corner_radius=10)
        frame.pack(fill="x", padx=20, pady=5)

        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(inner, text=label, font=FONT_BTN, text_color="white",
                     anchor="w").pack(fill="x")
        ctk.CTkLabel(inner, text=sub, font=FONT_SMALL, text_color=COLOR_MUTED,
                     anchor="w").pack(fill="x")

        ctk.CTkButton(frame, text="Wählen  →", font=FONT_BTN,
                      fg_color=COLOR_ACCENT, text_color=COLOR_BG,
                      hover_color="#00b8cc", corner_radius=8,
                      width=110, command=cmd).pack(anchor="e", padx=14, pady=(0, 10))

    def on_enter(self):
        pass


# ═══════════════════════════════════════════════════════════════════
class Screen2Modus(BaseScreen):
    """Schritt 2: Modus wählen (nur bei 2 Tasten)."""

    MODI = [
        ("⚡  Iambic A",        "Abwechselnd · / —  beim gleichzeitigen Drücken"),
        ("⚡⚡ Iambic B",        "Wie A, aber letztes Zeichen wird noch gesendet"),
        ("⬛  Straight / Paddle","Linke = Punkt, Rechte = Strich  (vollmanuell)"),
    ]

    def __init__(self, parent, app):
        super().__init__(parent, app)
        self._header(
            "SCHRITT 2 / MODUS  ·  nur bei 2 Tasten",
            "Welchen Modus?",
            "Wähle, wie die zwei Tasten interpretiert werden."
        )
        self.modus_var = ctk.StringVar(value="")

        for label, sub in self.MODI:
            self._radio(label, sub, label)

        ctk.CTkButton(self, text="← Zurück", font=FONT_BTN,
                      fg_color="transparent", border_width=1,
                      border_color=COLOR_MUTED, text_color=COLOR_MUTED,
                      hover_color="#1e2530",
                      command=lambda: app.zeige_screen("Screen1Tasten")).pack(
                          anchor="w", padx=20, pady=(14, 4))

    def _radio(self, label, sub, value):
        row = ctk.CTkFrame(self, fg_color=COLOR_BG, corner_radius=10)
        row.pack(fill="x", padx=20, pady=4)

        ctk.CTkRadioButton(
            row, text=label, variable=self.modus_var, value=value,
            font=FONT_BTN, text_color="white",
            fg_color=COLOR_ACCENT, hover_color="#00b8cc",
            command=lambda v=value: self.app.weiter_von_screen2(v)
        ).pack(anchor="w", padx=16, pady=(10, 2))

        ctk.CTkLabel(row, text=sub, font=FONT_SMALL,
                     text_color=COLOR_MUTED, anchor="w").pack(
                         anchor="w", padx=40, pady=(0, 10))

    def on_enter(self):
        self.modus_var.set("")


# ═══════════════════════════════════════════════════════════════════
class Screen3Bestaetigen(BaseScreen):
    """Schritt 3: Konfiguration bestätigen."""

    def __init__(self, parent, app):
        super().__init__(parent, app)
        self._header(
            "SCHRITT 3 / BESTÄTIGEN",
            "Konfiguration prüfen",
            "Stimmt alles? Dann starte das Gerät."
        )
        # Zusammenfassung
        summ = ctk.CTkFrame(self, fg_color=COLOR_BG, corner_radius=10)
        summ.pack(fill="x", padx=20, pady=4)

        self.lbl_taste = self._zeile(summ, "Tasten")
        self.lbl_modus = self._zeile(summ, "Modus")
        self._zeile(summ, "Gerät", "Raspberry Pi 3B", static=True)

        # Buttons
        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.pack(fill="x", padx=20, pady=(16, 0))

        ctk.CTkButton(nav, text="← Zurück", font=FONT_BTN,
                      fg_color="transparent", border_width=1,
                      border_color=COLOR_MUTED, text_color=COLOR_MUTED,
                      hover_color="#1e2530", width=100,
                      command=self._zurueck).pack(side="left")

        ctk.CTkButton(nav, text="▶  Starten", font=FONT_BTN,
                      fg_color=COLOR_ACCENT, text_color=COLOR_BG,
                      hover_color="#00b8cc", corner_radius=8,
                      command=app.starten).pack(side="right")

    def _zeile(self, parent, key, value="—", static=False):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=5)
        ctk.CTkLabel(row, text=key, font=FONT_SMALL,
                     text_color=COLOR_MUTED, anchor="w", width=80).pack(side="left")
        lbl = ctk.CTkLabel(row, text=value, font=FONT_BTN,
                           text_color=COLOR_GREEN, anchor="e")
        lbl.pack(side="right")
        return None if static else lbl

    def _zurueck(self):
        if self.app.taste_anzahl == "2":
            self.app.zeige_screen("Screen2Modus")
        else:
            self.app.zeige_screen("Screen1Tasten")

    def on_enter(self):
        self.lbl_taste.configure(text=self.app.taste_anzahl or "—")
        if self.app.taste_anzahl == "2":
            self.lbl_modus.configure(text=self.app.modus or "—", text_color=COLOR_GREEN)
        else:
            self.lbl_modus.configure(text="nicht benötigt", text_color=COLOR_MUTED)


# ═══════════════════════════════════════════════════════════════════
class Screen4Bereit(BaseScreen):
    """Schritt 4: Gerät aktiv – Morse-Eingabe."""

    def __init__(self, parent, app):
        super().__init__(parent, app)
        self._header(
            "SCHRITT 4 / AKTIV",
            "Gerät bereit ✔",
            "Morse-Eingabe läuft. Tasten drücken zum Senden."
        )
        # Morse-Ausgabe
        self.morse_lbl = ctk.CTkLabel(
            self, text="· · ·  — — —  · · ·",
            font=FONT_MONO, text_color=COLOR_ACCENT,
            fg_color=COLOR_BG, corner_radius=10
        )
        self.morse_lbl.pack(fill="x", padx=20, pady=6, ipady=14)

        # Tasten-Container (wird in on_enter gebaut)
        self.tasten_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.tasten_frame.pack(pady=8)

        # Löschen
        ctk.CTkButton(self, text="⌫  Löschen", font=FONT_SMALL,
                      fg_color="transparent", border_width=1,
                      border_color=COLOR_MUTED, text_color=COLOR_MUTED,
                      hover_color="#1e2530", width=120,
                      command=self._loeschen).pack(pady=(0, 4))

        # Neu konfigurieren
        ctk.CTkButton(self, text="⟳  Neu konfigurieren", font=FONT_BTN,
                      fg_color="transparent", border_width=1,
                      border_color=COLOR_MUTED, text_color=COLOR_MUTED,
                      hover_color="#1e2530",
                      command=app.neu_konfigurieren).pack(pady=(6, 0))

    def on_enter(self):
        # Alte Tasten entfernen
        for w in self.tasten_frame.winfo_children():
            w.destroy()
        self.morse_lbl.configure(text="…")

        if self.app.taste_anzahl == "1":
            self._taste_btn("●  TASTE", self._punkt)
        else:
            self._taste_btn("·  PUNKT", self._punkt)
            self._taste_btn("—  STRICH", self._strich)

    def _taste_btn(self, label, cmd):
        btn = ctk.CTkButton(
            self.tasten_frame, text=label, font=FONT_BTN,
            fg_color=COLOR_BG, border_width=2, border_color=COLOR_ACCENT,
            text_color=COLOR_ACCENT, hover_color="#00e5ff",
            width=130, height=70, corner_radius=10,
            command=cmd
        )
        btn.pack(side="left", padx=10)

    def _punkt(self):
        self.app.morse_puffer += "· "
        self._aktualisieren()

    def _strich(self):
        self.app.morse_puffer += "— "
        self._aktualisieren()

    def _loeschen(self):
        self.app.morse_puffer = ""
        self.morse_lbl.configure(text="…")

    def _aktualisieren(self):
        self.morse_lbl.configure(text=self.app.morse_puffer.strip() or "…")


# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = MorseApp()
    app.mainloop()
import tkinter as tk
import subprocess

def umwandeln():
    text = eingabe_feld.get()

    try:
        # main.py starten und Text als Eingabe übergeben
        result = subprocess.run(
            ["python", "main.py"],
            input=text,
            text=True,
            capture_output=True
        )

        # Ausgabe anzeigen
        ausgabe_label.config(text=result.stdout.strip())

    except Exception as e:
        ausgabe_label.config(text=f"Fehler: {e}")


# Fenster erstellen
fenster = tk.Tk()
fenster.title("Morsecode-Generator")
fenster.geometry("500x250")

# Überschrift
titel = tk.Label(fenster, text="Morsecode-Generator", font=("Arial", 16))
titel.grid(row=0, column=0, columnspan=2, pady=10)

# Eingabe
eingabe_text = tk.Label(fenster, text="Text eingeben:")
eingabe_text.grid(row=1, column=0, padx=10, pady=10)

eingabe_feld = tk.Entry(fenster, width=40)
eingabe_feld.grid(row=1, column=1, padx=10, pady=10)

# Button
button = tk.Button(fenster, text="In Morsecode umwandeln", command=umwandeln)
button.grid(row=2, column=0, columnspan=2, pady=10)

# Ausgabe
ausgabe_titel = tk.Label(fenster, text="Morsecode:")
ausgabe_titel.grid(row=3, column=0, pady=10)

ausgabe_label = tk.Label(fenster, text="", font=("Courier", 12), wraplength=400)
ausgabe_label.grid(row=3, column=1, pady=10)

fenster.mainloop()
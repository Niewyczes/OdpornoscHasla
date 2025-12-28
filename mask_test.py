import time
import tkinter as tk
from tkinter import messagebox
from threading import Thread
from itertools import product

#Co sie kryje pod znakami
MASK_CHARSETS = {
    "?l": "abcdefghijklmnopqrstuvwxyz",
    "?u": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "?d": "0123456789",
    "?s": "!@#$%^&*()_+-=[]{}|;:,.<>/?"
}


def start_mask(self):
    """Rozpoczyna atak maski"""
    password = self.password_entry.get()
    if not password:
        messagebox.showwarning("Brak hasła", "Wprowadź hasło do testu.")
        return

    self.testing = True
    self.stop_event.clear()
    self.start_time = time.time()

    self.result_text.delete(1.0, tk.END)
    self.gui_safe(self.result_text.insert, tk.END,
                  "Test mask attack (Etap 3)\n")

    thread = Thread(target=self.run_mask, args=(password,), daemon=True)
    thread.start()


def run_mask(self, password):
    """Symuluje atak bruteforce z maską"""
    # Generowanie maski
    mask = ""
    for ch in password:
        if ch.islower(): mask += "?l"
        elif ch.isupper(): mask += "?u"
        elif ch.isdigit(): mask += "?d"
        else: mask += "?s"

    # Tworzenie listy z charsetów
    charsets = [MASK_CHARSETS[m] for m in [mask[i:i+2] for i in range(0, len(mask), 2)]]

    # Obliczanie liczby kombinacji
    total = 1
    for cs in charsets:
        total *= len(cs)

    self.gui_safe(self.result_text.insert, tk.END,
                  f"Maska: {mask}\n"
                  f"Liczba kombinacji: {total:,}\n"
                  f"Rozpoczynam mask attack...\n\n")

    MAX_TIME = 10  #Limit czasu dla symulacji 10 sekund

    attempts = 0
    for combo in product(*charsets):

        #  STOP TEST
        if self.stop_event.is_set():
            break

        # LIMIT CZASU
        if time.time() - self.start_time > MAX_TIME:
            break

        attempts += 1
        guess = "".join(combo)

        # Pasek postępu
        if attempts % 5000 == 0:
            progress = (attempts / total) * 100
            self.progress_var.set(progress)

        # Wyświetlanie co jakiś czas
        if attempts % 100000 == 0:
            self.gui_safe(self.result_text.insert, tk.END,
                          f"Próba {attempts:,}: {guess}\n")

        # Trafienie hasła
        if guess == password:
            elapsed = time.time() - self.start_time
            return self.finish_mask(mask, elapsed, found=True, attempts=attempts)

    elapsed = time.time() - self.start_time
    self.finish_mask(mask, elapsed, found=False, attempts=attempts)


def finish_mask(self, mask, elapsed_time, found, attempts):
    """Raport ataku maskowego"""
    self.result_text.insert(tk.END, f"\n{'=' * 60}\n")
    self.result_text.insert(tk.END, "WYNIK MASK ATTACK:\n")
    self.result_text.insert(tk.END, f"{'=' * 60}\n")

    self.result_text.insert(tk.END, f"Maska: {mask}\n")
    self.result_text.insert(tk.END, f"Liczba prób: {attempts:,}\n")
    self.result_text.insert(tk.END, f"Czas testu: {elapsed_time:.2f} sekund\n")
    self.result_text.insert(tk.END, f"Hasło znalezione: {'TAK' if found else 'NIE'}\n")

    # Znaleziono hasło
    if found:
        self.result_text.insert(tk.END, "\n⚠️ Hasło zostało złamane mask attack!\n")

    # Test został zatrzymany
    elif self.stop_event.is_set():
        self.result_text.insert(tk.END, "\n⛔ Test zatrzymany przez użytkownika.\n")

    # Test zakończył się limit symulacji/hasło nieznalezione
    else:
        self.result_text.insert(tk.END, "\n✓ Mask attack zakończony — hasła nie znaleziono.\n")

    self.testing = False
    self.stop_button.config(state=tk.DISABLED)
    self.progress_var.set(100)

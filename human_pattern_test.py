import time
import tkinter as tk
from tkinter import messagebox
from threading import Thread
import random


def start_human_pattern_test(self):
    """"Rozpoczyna test human pattern"""
    password = self.password_entry.get()
    if not password:
        messagebox.showwarning("Brak hasła", "Wprowadź hasło do testu.")
        return

    self.update_stats(password)
    self.testing = True
    self.stop_test = False
    self.stop_event.clear()
    self.start_time = time.time()
    self.attempts = 0
    self.last_scroll = 0
    self.last_progress_update = 0   # 🔥 KLUCZOWE — bez tego pasek nie działa

    self.stop_button.config(state=tk.NORMAL)
    self.result_text.delete(1.0, tk.END)
    self.gui_safe(self.result_text.insert, tk.END,
                  "Test Schematyczności Hasła (Human Pattern Test)\n")

    thread = Thread(target=self.run_human_pattern_test, args=(password,), daemon=True)
    thread.start()


def run_human_pattern_test(self, password):
    """Wykonuje test sprawdza najpopularniejsze schematy"""
    hybrid = self.load_hybrid_passwords()

    names = hybrid['names']
    adjs = hybrid['adjectives']
    specs = hybrid['special']

    MAX_TIME = 10
    start = time.time()
    found = False
    matched_pattern = None

    while time.time() - start < MAX_TIME and not self.stop_event.is_set() and not self.stop_test:

        name = random.choice(names)
        adj = random.choice(adjs)
        spec = random.choice(specs)
        year = str(random.randint(1990, 2025))
        num = str(random.randint(1, 9))

        patterns = [
            f"{name}123",
            f"{name}{year}",
            f"{name}!",
            f"{name}{name}",
            f"{name}*{name}",
            f"{name}{spec}{adj}",
            f"{adj}{spec}{name}",
            f"{name}{num}",
            f"{name}!{num}",
            f"{name}{adj}",
        ]

        for p in patterns:

            if self.stop_event.is_set() or self.stop_test:
                break

            self.attempts += 1

            # 🔥 Aktualizacja paska co 50 ms
            now = time.time()
            if now - self.last_progress_update > 0.05:
                progress = ((now - start) / MAX_TIME) * 100
                self.gui_safe(self.progress_var.set, min(progress, 100))
                self.last_progress_update = now

            # Logowanie co 200k prób
            if self.attempts % 200000 == 0:
                self.gui_safe(self.result_text.insert, tk.END,
                              f"Próba {self.attempts:,}: {p}\n")
                self.result_text.see(tk.END)

                if now - self.last_scroll > 0.4:
                    self.gui_safe(lambda: self.result_text.see(tk.END))
                    self.last_scroll = now

            if p == password:
                found = True
                matched_pattern = p
                break

        if found:
            break

    elapsed = time.time() - start
    self.finish_human_pattern_test(password, found, matched_pattern, elapsed)


def finish_human_pattern_test(self, password, found, matched_pattern, elapsed_time):
    """Kończy test i generuje raport"""
    self.result_text.insert(tk.END, f"\n{'=' * 60}\n")
    self.result_text.insert(tk.END, "WYNIK TESTU SCHEMATYCZNOŚCI:\n")
    self.result_text.insert(tk.END, f"{'=' * 60}\n")

    self.result_text.insert(tk.END, f"Czas testu: {elapsed_time:.2f} sekund\n")
    self.result_text.insert(tk.END, f"Liczba prób: {self.attempts:,}\n")
    self.result_text.insert(tk.END, f"Hasło schematyczne: {'TAK' if found else 'NIE'}\n")

    if found:
        self.result_text.insert(tk.END,
            f"\n⚠️ Twoje hasło pasuje do popularnego schematu:\n   → {matched_pattern}\n"
        )
    elif self.stop_event.is_set() or self.stop_test:
        self.result_text.insert(tk.END, "\n⛔ Test zatrzymany przez użytkownika.\n")
    else:
        self.result_text.insert(tk.END,
            "\n✓ Hasło nie pasuje do 10 najpopularniejszych schematów ludzkich.\n"
        )

    self.testing = False
    self.stop_button.config(state=tk.DISABLED)
    self.progress_var.set(100)

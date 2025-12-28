#dodać nowe metody
#pasek postępu wyrzucić? moim zdaniem niech zostanie, zawesze to jakiś bajer. Tylko przy brute-force dziwne działa(tak na logikę to ciężko go będzie zaprogramować z brute-forcem)
#poprawić pasek siły hasła?
#czemu metodą słownikową nie odczytuje alfabetycznie?
import tkinter as tk
from concurrent.futures.process import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
from tkinter import ttk, messagebox, scrolledtext
import time
import itertools
import string
from itertools import permutations, product
from datetime import timedelta
import threading
from threading import Thread
#import requests
from urllib.parse import urlparse
import re
import queue
#Zainportowane moduły
#------------------------
from hybrid_dictionary import (
    start_hybrid_dictionary,
    run_hybrid_dictionary,
    hybrid_dictionary_worker,
    on_done_hybrid_dictionary,
    finish_hybrid_dictionary
)

from human_pattern_test import (
    start_human_pattern_test,
    run_human_pattern_test,
    finish_human_pattern_test
)

from mask_test import (
    start_mask,
    run_mask,
    finish_mask
)
#----------------------------

class PasswordStrengthAnalyzer:
    def __init__(self, root):
        #Dodanie wywoływań modułów
        # --- HYBRID DICTIONARY ---
        self.start_hybrid_dictionary = start_hybrid_dictionary.__get__(self)
        self.run_hybrid_dictionary = run_hybrid_dictionary.__get__(self)
        self.hybrid_dictionary_worker = hybrid_dictionary_worker.__get__(self)
        self.on_done_hybrid_dictionary = on_done_hybrid_dictionary.__get__(self)
        self.finish_hybrid_dictionary = finish_hybrid_dictionary.__get__(self)

        # --- HUMAN PATTERN TEST ---
        self.start_human_pattern_test = start_human_pattern_test.__get__(self)
        self.run_human_pattern_test = run_human_pattern_test.__get__(self)
        self.finish_human_pattern_test = finish_human_pattern_test.__get__(self)

        # --- MASK ---
        self.start_mask = start_mask.__get__(self)
        self.run_mask = run_mask.__get__(self)
        self.finish_mask = finish_mask.__get__(self)

        self.root = root
        self.root.title("Analizator Siły Hasła")
        self.root.geometry("700x650")
        self.root.resizable(True, True)

        # Stylizacja
        self.setup_styles()

        # Słowniki haseł (można rozbudować)
        self.common_passwords = self.load_common_passwords()

        # Zmienne
        self.testing = False
        self.stop_test = False
        self.stop_event=threading.Event()

        #Widżety GUI
        self.create_widgets()

        #Dodanie kolejki
        self.stage1_queue = queue.Queue()
    def setup_styles(self):
        """Konfiguruje style dla aplikacji"""
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Kolory
        self.colors = {
            'very_weak': '#ff0000',
            'weak': '#ff6666',
            'medium': '#ffcc00',
            'strong': '#66cc66',
            'very_strong': '#006600'
        }

    def load_common_passwords(self):
        """Ładuje listę popularnych haseł"""
        common = [
            '123456', 'password', '12345678', 'qwerty', '123456789',
            '12345', '1234', '111111', '1234567', 'smok',
            '123123', 'pilka', 'abc123', 'football', 'monkey',
            'wpuscmnie', '696969', 'cien', 'master', '666666',
            'qwertyuiop', '123321', 'mustang', '1234567890',
            'michal', '654321', 'superman', '1qaz2wsx', '7777777',
            'password1', 'wolnosc', 'admin', 'login', 'welcome'
        ]

        # Próba załadowania z pliku
        try:
            with open('common_passwords.txt', 'r', encoding='utf-8') as f:
                common += [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            pass

        return set(common)
    #Ładuje pliki i skleja je i zwraca jeden słownik
    def load_hybrid_passwords(self):
        #Tworzenie słownika
        hybrid_dict={
            'names':[],
            'adjectives':[],
            'special':[]
        }
        #Szukanie po nazwie pliku i próba otworzenia go
        for category in hybrid_dict.keys():
            filename=f"{category}.txt"
            try:
                with open (filename, "r", encoding="utf-8") as f:
                    hybrid_dict[category]=[line.strip().strip("'").strip('"')
                        for line in f
                        if line.strip()]
            except FileNotFoundError:
                print(f"Brak pliku {filename}")
        return hybrid_dict

    def create_widgets(self):
        """Tworzy wszystkie elementy GUI"""
        # Ramka główna
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Konfiguracja grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Sekcja wprowadzania hasła
        ttk.Label(main_frame, text="Wprowadź hasło do analizy:",
                  font=('Arial', 11, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky=tk.W)

        ttk.Label(main_frame, text="Hasło:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.password_entry = ttk.Entry(main_frame, show="•", width=40)
        self.password_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)

        # Przycisk pokaż/ukryj hasło
        self.show_var = tk.BooleanVar()
        self.show_check = ttk.Checkbutton(main_frame, text="Pokaż hasło",
                                          variable=self.show_var,
                                          command=self.toggle_password_visibility)
        self.show_check.grid(row=1, column=2, padx=(10, 0))

        # Przyciski analizy
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)

        ttk.Button(button_frame, text="Analizuj Siłę",
                   command=self.analyze_strength).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Analiza ZXCVBN",
                   command=self.analyze_password_strength_zxcvbn).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Test Brute-Force",
                   command=self.start_brute_force_test).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Test Słownikowy",
                   command=self.start_dictionary_test).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Test Hybrydowy-Słownikowy",
                   command=self.start_hybrid_dictionary).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Test Schematyczności",
                   command=self.start_human_pattern_test).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Test Maski",
                   command=self.start_mask).pack(side=tk.LEFT, padx=5)
        # Pasek postępu
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var,
                                            maximum=100, length=300)
        self.progress_bar.grid(row=3, column=0, columnspan=3, pady=(10, 5), sticky=(tk.W, tk.E))

        # Przycisk stop
        self.stop_button = ttk.Button(main_frame, text="Stop Test",
                                      command=self.stop_test_func, state=tk.DISABLED)
        self.stop_button.grid(row=4, column=0, columnspan=3, pady=(0, 10))

        # Notatnik wyników
        ttk.Label(main_frame, text="Wyniki Analizy:",
                  font=('Arial', 11, 'bold')).grid(row=5, column=0, columnspan=3, pady=(10, 5), sticky=tk.W)

        self.result_text = scrolledtext.ScrolledText(main_frame, width=70, height=15,
                                                     wrap=tk.WORD, font=('Courier', 9))
        self.result_text.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Wskaźnik siły hasła
        self.strength_frame = ttk.LabelFrame(main_frame, text="Siła Hasła", padding="5")
        self.strength_frame.grid(row=7, column=0, columnspan=3, pady=(10, 0), sticky=(tk.W, tk.E))

        self.strength_label = ttk.Label(self.strength_frame, text="Nieocenione", font=('Arial', 10))
        self.strength_label.pack()

        self.strength_meter = tk.Canvas(self.strength_frame, height=20, bg='white')
        self.strength_meter.pack(fill=tk.X, pady=5)

        # Statystyki
        stats_frame = ttk.Frame(main_frame)
        stats_frame.grid(row=8, column=0, columnspan=3, pady=(10, 0), sticky=(tk.W, tk.E))

        self.stats_labels = {}
        stats = [
            ("Długość", "length"),
            ("Duże litery", "uppercase"),
            ("Małe litery", "lowercase"),
            ("Cyfry", "digits"),
            ("Znaki specjalne", "special"),
      #      ("Czas łamania (BF)", "bf_time")
        ]

        for i, (name, key) in enumerate(stats):
            ttk.Label(stats_frame, text=f"{name}:").grid(row=i // 3, column=(i % 3) * 2, sticky=tk.W, padx=(0, 5))
            label = ttk.Label(stats_frame, text="-", font=('Arial', 9, 'bold'))
            label.grid(row=i // 3, column=(i % 3) * 2 + 1, sticky=tk.W, padx=(0, 20))
            self.stats_labels[key] = label

    def toggle_password_visibility(self):
        """Przełącza widoczność hasła"""
        if self.show_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="•")

    def calculate_password_strength(self, password):
        """Oblicza siłę hasła"""
        if not password:
            return 0, "Brak hasła"

        score = 0
        length = len(password)

        # Punkty za długość
        score += min(length * 4, 40)

        # Punkty za różnorodność znaków
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)

        char_types = sum([has_upper, has_lower, has_digit, has_special])
        score += (char_types - 1) * 10

        # Kara za kolejne znaki
        if length > 2:
            for i in range(2, length):
                if password[i] == password[i - 1] == password[i - 2]:
                    score -= 5

        # Sprawdzenie w słowniku
        if password.lower() in self.common_passwords:
            score = max(0, score - 50)

        # Normalizacja wyniku
        score = max(0, min(score, 100))

        # Określenie poziomu siły
        if score < 20:
            strength = "Bardzo słabe"
        elif score < 40:
            strength = "Słabe"
        elif score < 60:
            strength = "Średnie"
        elif score < 80:
            strength = "Silne"
        else:
            strength = "Bardzo silne"

        return score, strength
    def gui_safe(self, func, *args,**kwargs):
        self.root.after(0,lambda:func(*args,**kwargs))

    def split_into_chunks(self,lst, n):
        """Dzieli listę na części"""
        if not lst:
            return [[] for _ in range(n)]
        k, m = divmod(len(lst), n)
        return [lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]

    def estimate_crack_time(self, password):
        """Szacuje czas potrzebny do złamania hasła"""
        if not password:
            return "N/A"

        # Zakładana szybkość łamania (prób na sekundę)
        bf_speed = 1000000000  # 1 miliard prób/sekundę
        dict_speed = 10000000  # 10 milionów prób/sekundę

        length = len(password)
        char_types = []

        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)

        # Obliczenie przestrzeni kluczy
        charset_size = 0
        if has_lower:
            charset_size += 26
        if has_upper:
            charset_size += 26
        if has_digit:
            charset_size += 10
        if has_special:
            charset_size += 32  # typowe znaki specjalne

        if charset_size == 0:
            return "Natychmiastowo"

        # Szacowanie dla brute-force
        total_combinations = sum(charset_size ** i for i in range(1, length + 1))
        bf_seconds = total_combinations / bf_speed

        # Sprawdzenie słownikowe
        dict_time = len(self.common_passwords) / dict_speed

        # Wybór krótszego czasu
        seconds = min(bf_seconds, dict_time)

        # Formatowanie czasu
        if seconds < 1:
            return "Mniej niż sekunda"
        elif seconds < 60:
            return f"{seconds:.1f} sekund"
        elif seconds < 3600:
            return f"{seconds / 60:.1f} minut"
        elif seconds < 86400:
            return f"{seconds / 3600:.1f} godzin"
        elif seconds < 2592000:
            return f"{seconds / 86400:.1f} dni"
        elif seconds < 31536000:
            return f"{seconds / 2592000:.1f} miesięcy"
        else:
            return f"{seconds / 31536000:.1f} lat"

    def analyze_strength(self):
        """Analizuje siłę wprowadzonego hasła"""
        password = self.password_entry.get()

        if not password:
            messagebox.showwarning("Brak hasła", "Wprowadź hasło do analizy.")
            return

        # Obliczanie siły
        score, strength = self.calculate_password_strength(password)

        # Aktualizacja wskaźnika
        self.update_strength_meter(score, strength)

        # Aktualizacja statystyk
        self.update_stats(password)

        # Wyświetlenie wyników
        self.result_text.delete(1.0, tk.END)

        report = f"""
{'=' * 60}
ANALIZA HASŁA
{'=' * 60}
Hasło: {'*' * len(password)}
Długość: {len(password)} znaków
Siła: {strength} ({score}/100)
Szacowany czas łamania: {self.estimate_crack_time(password)}

ANALIZA SKŁADU:
• Duże litery: {'✓' if any(c.isupper() for c in password) else '✗'}
• Małe litery: {'✓' if any(c.islower() for c in password) else '✗'}
• Cyfry: {'✓' if any(c.isdigit() for c in password) else '✗'}
• Znaki specjalne: {'✓' if any(not c.isalnum() for c in password) else '✗'}

OCENA:
"""

        if score < 40:
            report += "• Hasło jest zbyt słabe! Użyj dłuższego hasła z różnymi typami znaków.\n"
            report += "• Unikaj popularnych haseł i sekwencji.\n"
        elif score < 60:
            report += "• Hasło jest akceptowalne, ale można je poprawić.\n"
            report += "• Dodaj więcej znaków specjalnych i cyfr.\n"
        elif score < 80:
            report += "• Hasło jest dobre.\n"
            report += "• Rozważ użycie jeszcze dłuższego hasła.\n"
        else:
            report += "• Doskonałe! Hasło jest bardzo silne.\n"
            report += "• Pamiętaj, aby nie używać go na wielu stronach.\n"

        report += f"\nWskazówka: Użyj menedżera haseł do generowania i przechowywania silnych haseł."

        self.result_text.insert(1.0, report)
        # Wstępnie dodany zxcvbn
    def calculate_password_strength_zxcvbn(self, password):
            "Oblicza siłę hasła za pomocą ZXCVBN-like"
            length = len(password)
            score_100 = 0
            problems = []
            # Dodaje punkty za długość hasła
            score_100 += min(length * 5, 50)
            if length < 10:
                problems.append("Zbyt krótkie hasło (potrzeba więcej znaków niż 10)")
            # Dodaje punkty za różnorodne znaki
            char_types = 0
            if any(c.islower() for c in password): char_types += 1
            if any(c.isupper() for c in password): char_types += 1
            if any(c.isdigit() for c in password): char_types += 1
            if any(not c.isalnum() for c in password): char_types += 1
            score_100 += char_types * 10
            lower_password = password.lower()
            # Sprawdza czy hasło znajduje się w słowniku
            if hasattr(self, 'common_passwords') and self.common_passwords:
                for word in self.common_passwords:
                    if len(word) > 3 and word in lower_password:
                        score_100 -= 40
                        problems.append(f"Zawiera hasło słownikowe: '{word}' ")
                        break
            # Sprawdza powtarzające się sekwencje
            common_squences = ['123', 'qwer', 'asdf', 'aaaa', 'eeee', 'abc', 'zyxw']
            for squence in common_squences:
                if squence in lower_password:
                    score_100 -= 15
                    problems.append(f"Zawiera prostą sekwencje/powtórzenie '{squence}'")
                    break
            # Sprawdza czy hasło zawiera rok z przedziału (1900-2026)
            for year in range(1900, 2026):
                if str(year) in password:
                    score_100 -= 10
                    problems.append(f"Zawiera rok lub datę: '{year}'.")
                    break
            #Ustawianie granicy , aby nie dawało wysokiego wyniku hasłom z błedami
            if problems and score_100 > 60:
                score_100 = 60
            # Zamiana wyniku z skali 0 do 100 na skale od 0 do 4
            final_score_100 = max(0, min(100, score_100))
            if final_score_100 >= 80:
                score_zxcvbn = 4
            elif final_score_100 >= 60:
                score_zxcvbn = 3
            elif final_score_100 >= 40:
                score_zxcvbn = 2
            elif final_score_100 >= 20:
                score_zxcvbn = 1
            else:
                score_zxcvbn = 0
            return score_zxcvbn, problems

    def analyze_password_strength_zxcvbn(self):
            "Analizuje siłę hasła za pomocą ZXCVBN-like (0-4) i tworzy raport"
            password = self.password_entry.get()
            if not password:
                messagebox.showwarning("Brak hasła", "Wprowadź hasło do analizy.")
                return
            self.update_stats(password)
            score_4, problems = self.calculate_password_strength_zxcvbn(password)
            ###Łączenie powtarzających się znaków specjalnych, liter oraz cyfr np: "aaaaa" w "a"
            crack_test_password = re.sub(r'(.)\1+', r'\1', password)
            if len(crack_test_password) < len(password):
                estimated_time = self.estimate_crack_time(crack_test_password)
            else:
                estimated_time = self.estimate_crack_time(password)
            strength_map = {
                0: " Bardzo Słabe",
                1: " Słabe",
                2: " Umiarkowane",
                3: " Silne",
                4: " Bardzo silne"
            }
            strength = strength_map[score_4]
            score_100 = score_4 * 25
            self.update_strength_meter(score_100, strength)
            self.result_text.delete(1.0, tk.END)
            report = f"""
{'=' * 60}
ANALIZA HASŁA (METODA ZXCVBN-LIKE)
{'=' * 60}
Hasło: {'*' * len(password)}
Długość: {len(password)} znaków
Siła: {strength} ({score_4}/4)
Szacowany czas łamania: {estimated_time}
ANALIZA SKŁADU:
• Duże litery: {'✓' if any(c.isupper() for c in password) else '✗'}
• Małe litery: {'✓' if any(c.islower() for c in password) else '✗'}
• Cyfry: {'✓' if any(c.isdigit() for c in password) else '✗'}
• Znaki specjalne: {'✓' if any(not c.isalnum() for c in password) else '✗'}
OCENA:
"""
            report += "\nWYKRYTE PROBLEMY ORAZ KARY ZA WZORCE:\n"
            if problems:
                for p in problems:
                    report += f"{p}\n"
            else:
                report += "\nNie wykryto żadnych problemów\n"
            report += "\nOCENA KOŃCOWA I WSKAZÓWKI:\n"
            if score_4 <= 1:
                report += "• Hasło jest zbyt słabe! Użyj dłuższego hasła z różnymi typami znaków.\n"
                report += "• Unikaj popularnych haseł i sekwencji.\n"
            elif score_4 == 2:
                report += "• Hasło jest akceptowalne, ale można je poprawić.\n"
                report += "• Dodaj więcej znaków specjalnych i cyfr.\n"
            elif score_4 == 3:
                report += "• Hasło jest dobre.\n"
                report += "• Rozważ użycie jeszcze dłuższego hasła.\n"
            else:
                report += "• Doskonałe! Hasło jest bardzo silne.\n"
                report += "• Pamiętaj, aby nie używać go na wielu stronach.\n"
            report += f"\nWskazówka: Użyj menedżera haseł do generowania i przechowywania silnych haseł."
            self.result_text.insert(1.0, report)

    def update_strength_meter(self, score, strength):
        """Aktualizuje wskaźnik siły hasła"""
        self.strength_label.config(text=f"{strength} ({score}/100)")

        # Ustawienie koloru
        if score < 20:
            color = self.colors['very_weak']
        elif score < 40:
            color = self.colors['weak']
        elif score < 60:
            color = self.colors['medium']
        elif score < 80:
            color = self.colors['strong']
        else:
            color = self.colors['very_strong']

        # Rysowanie wskaźnika
        self.strength_meter.delete("all")
        width = self.strength_meter.winfo_width()
        if width < 10:
            width = 200

        fill_width = (score / 100) * width
        self.strength_meter.create_rectangle(0, 0, fill_width, 20, fill=color, outline="")
        self.strength_meter.create_rectangle(0, 0, width, 20, outline="black")

    def update_stats(self, password):
        """Aktualizuje statystyki hasła"""
        self.stats_labels['length'].config(text=str(len(password)))
        self.stats_labels['uppercase'].config(text=str(sum(1 for c in password if c.isupper())))
        self.stats_labels['lowercase'].config(text=str(sum(1 for c in password if c.islower())))
        self.stats_labels['digits'].config(text=str(sum(1 for c in password if c.isdigit())))
        self.stats_labels['special'].config(text=str(sum(1 for c in password if not c.isalnum())))

    def brute_force_test(self, password):
        """Symuluje atak brute-force"""
        self.testing = True
        self.stop_test = False
        self.progress_var.set(0)
        self.update_stats(password)
        chars = ''
        if any(c.islower() for c in password):
            chars += string.ascii_lowercase
        if any(c.isupper() for c in password):
            chars += string.ascii_uppercase
        if any(c.isdigit() for c in password):
            chars += string.digits
        if any(not c.isalnum() for c in password):
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"

        length = len(password)
        total_combinations = len(chars) ** length if chars else 0

        start_time = time.time()
        found = False
        attempts = 0

        # Ograniczona symulacja dla demonstracji
        max_demo_attempts = min(100000, total_combinations)

        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, f"Rozpoczynanie testu brute-force...\n")
        self.result_text.insert(tk.END, f"Długość hasła: {length}\n")
        self.result_text.insert(tk.END, f"Zestaw znaków: {chars}\n")
        self.result_text.insert(tk.END, f"Teoretyczna liczba kombinacji: {total_combinations:,}\n")
        self.result_text.insert(tk.END, f"{'=' * 60}\n")

        # Symulacja dla demonstracji
        for i in range(1, length + 1):
            if self.stop_test:
                break

            for combo in itertools.product(chars, repeat=i):
                if self.stop_test:
                    break

                attempts += 1
                test_pass = ''.join(combo)

                # Aktualizacja postępu
                if max_demo_attempts > 0:
                    progress = (attempts / max_demo_attempts) * 100
                    self.progress_var.set(min(progress, 100))

                if attempts % 1000 == 0:
                    self.result_text.insert(tk.END, f"Próba {attempts:,}: {test_pass}\n")
                    self.result_text.see(tk.END)
                    self.root.update()

                if test_pass == password:
                    found = True
                    break

            if found or self.stop_test:
                break

        elapsed_time = time.time() - start_time

        # Wyświetlenie wyników
        self.result_text.insert(tk.END, f"\n{'=' * 60}\n")
        self.result_text.insert(tk.END, "WYNIK TESTU BRUTE-FORCE:\n")
        self.result_text.insert(tk.END, f"{'=' * 60}\n")
        self.result_text.insert(tk.END, f"Czas testu: {elapsed_time:.2f} sekund\n")
        self.result_text.insert(tk.END, f"Liczba prób: {attempts:,}\n")
        self.result_text.insert(tk.END, f"Hasło znalezione: {'TAK' if found else 'NIE (test zatrzymany)'}\n")

        if not found and not self.stop_test:
            self.result_text.insert(tk.END,
                                    f"\nSzacowany czas pełnego przeszukania: {self.estimate_crack_time(password)}\n")
            self.result_text.insert(tk.END, f"Zalecenie: {self.get_recommendation(password)}\n")

        self.testing = False
        self.stop_button.config(state=tk.DISABLED)
        self.progress_var.set(100)

    def dictionary_test(self, password):
        """Symuluje atak słownikowy"""
        self.testing = True
        self.stop_test = False
        self.progress_var.set(0)
        self.update_stats(password)
        start_time = time.time()
        found = False
        attempts = 0

        # Rozszerzenie słownika o proste modyfikacje
        test_passwords = list(self.common_passwords)

        # Dodanie wariacji
        variations = []
        for pwd in self.common_passwords:
            variations.append(pwd + "123")
            variations.append(pwd + "!")
            variations.append(pwd.upper())
            variations.append(pwd + "2024")

        test_passwords.extend(variations)

        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, f"Rozpoczynanie testu słownikowego...\n")
        self.result_text.insert(tk.END, f"Rozmiar słownika: {len(test_passwords):,} haseł\n")
        self.result_text.insert(tk.END, f"{'=' * 60}\n")

        for i, test_pass in enumerate(test_passwords):
            if self.stop_test:
                break

            attempts += 1

            # Aktualizacja postępu
            progress = (i / len(test_passwords)) * 100
            self.progress_var.set(progress)

            if attempts % 100 == 0:
                self.result_text.insert(tk.END, f"Próba {attempts:,}: {test_pass}\n")
                self.result_text.see(tk.END)
                self.root.update()

            if test_pass == password:
                found = True
                break

        elapsed_time = time.time() - start_time

        # Wyświetlenie wyników
        self.result_text.insert(tk.END, f"\n{'=' * 60}\n")
        self.result_text.insert(tk.END, "WYNIK TESTU SŁOWNIKOWEGO:\n")
        self.result_text.insert(tk.END, f"{'=' * 60}\n")
        self.result_text.insert(tk.END, f"Czas testu: {elapsed_time:.2f} sekund\n")
        self.result_text.insert(tk.END, f"Liczba prób: {attempts:,}\n")
        self.result_text.insert(tk.END, f"Hasło znalezione w słowniku: {'TAK' if found else 'NIE'}\n")

        if found:
            self.result_text.insert(tk.END, f"\n⚠️  UWAGA: Twoje hasło znajduje się w słowniku popularnych haseł!\n")
            self.result_text.insert(tk.END, f"Zalecenie: Natychmiast zmień to hasło na bardziej unikalne.\n")
        else:
            self.result_text.insert(tk.END, f"\n✓ Hasło nie znajduje się w słowniku popularnych haseł.\n")

        self.testing = False
        self.stop_button.config(state=tk.DISABLED)
        self.progress_var.set(100)

    def start_brute_force_test(self):
        """Uruchamia test brute-force w osobnym wątku"""
        password = self.password_entry.get()

        if not password:
            messagebox.showwarning("Brak hasła", "Wprowadź hasło do testu.")
            return

        if self.testing:
            messagebox.showwarning("Test w toku", "Poczekaj na zakończenie obecnego testu.")
            return

        self.stop_button.config(state=tk.NORMAL)
        thread = Thread(target=self.brute_force_test, args=(password,), daemon=True)
        thread.start()
    def start_dictionary_test(self):
        """Uruchamia test słownikowy w osobnym wątku"""
        password = self.password_entry.get()

        if not password:
            messagebox.showwarning("Brak hasła", "Wprowadź hasło do testu.")
            return

        if self.testing:
            messagebox.showwarning("Test w toku", "Poczekaj na zakończenie obecnego testu.")
            return

        self.stop_button.config(command=self.stop_test_func,state=tk.NORMAL)
        thread = Thread(target=self.dictionary_test, args=(password,), daemon=True)
        thread.start()

    def stop_test_func(self):
        """Zatrzymuje aktualnie wykonywany test"""
        self.stop_test = True

    def get_recommendation(self, password):
        """Zwraca rekomendacje dotyczące hasła"""
        length = len(password)
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)

        recommendations = []

        if length < 12:
            recommendations.append("użyj dłuższego hasła (min. 12 znaków)")

        char_types = sum([has_upper, has_lower, has_digit, has_special])
        if char_types < 3:
            recommendations.append("dodaj więcej rodzajów znaków")

        if not has_special:
            recommendations.append("dodaj znaki specjalne")

        if password.lower() in self.common_passwords:
            recommendations.append("unikaj popularnych haseł")

        if recommendations:
            return "Zalecenia: " + ", ".join(recommendations)
        return "Hasło spełnia podstawowe wymagania bezpieczeństwa."


def main():
    root = tk.Tk()
    app = PasswordStrengthAnalyzer(root)

    # Centrowanie okna
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    root.mainloop()


if __name__ == "__main__":

    main()
import secrets
import tkinter as tk
import random
import string
from tkinter import ttk
import pandas as pd


def open_password_generator_window(self):
    """"Otwiera okienko generatora hasła"""
    #Wczytywanie plików z CSV
    self.pairs_df = pd.read_csv("pairs.csv")
    self.pairs_dict = dict(zip(self.pairs_df["from"], self.pairs_df["to"]))

    #Tworzenie okna generatora
    win = tk.Toplevel(self.root)
    win.title("Generator hasła")
    win.geometry("600x500")

    strength_meter = None

    ttk.Label(
        win,
        text="Generator hasła",
        font=('Arial', 16, 'bold')
    ).pack(pady=(10, 0), anchor="center")

    notebook = ttk.Notebook(win)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    standard_tab = ttk.Frame(notebook)
    corporate_tab = ttk.Frame(notebook)
    personalized_tab = ttk.Frame(notebook)

    notebook.add(standard_tab, text="Tryb standardowy")
    notebook.add(corporate_tab, text="Tryb korporacyjny")
    notebook.add(personalized_tab, text="Tryb personalizacji")

    def on_tab_change(event):
        """Chowa pasek siły przy zmienianiu zakładki z standardowej na inną"""
        nonlocal strength_meter
        active = notebook.index(notebook.select())

        if active != 0 and strength_meter is not None:
            strength_meter.pack_forget()
    notebook.bind("<<NotebookTabChanged>>", on_tab_change)
    #Zmienne
    length_standard_var = tk.IntVar(value=8)
    length_corp_var = tk.IntVar(value=12)
    result_var = tk.StringVar()

    def copy_to_clipboard(*args, **kwargs):
        """Uniwersalna funkcja do kopiowania hasła do schowka"""
        if args:
            value = args[0]
        else:
            value = kwargs.get('value')
        if value:
            win.clipboard_clear()
            win.clipboard_append(value)
            win.update()

    def update_strength_meter(password):
        """Funkcja rysująca pasek z tekstem"""
        nonlocal strength_meter
        if strength_meter is None:
            return
        strength_meter.update_idletasks()
        score, strength = self.calculate_password_strength(password)

        if score < 40:
            color = "red"
        elif score < 60:
            color = "orange"
        else:
            color = "green"

        strength_meter.delete("all")
        width = int((score / 100) * strength_meter.winfo_width())

        strength_meter.create_rectangle(0, 0, width, 20, fill=color, width=0)
        strength_meter.create_text(
            strength_meter.winfo_width() // 2,
            10,
            text=f"Siła hasła:{strength} ({score}%)",
            fill="white",
            font=('Arial', 10, 'bold')
        )

    def generate():
        """Przekazuje dane do generatora hasła"""
        nonlocal strength_meter
        active_tab = notebook.index(notebook.select())
        if active_tab == 0:
            length = max(length_standard_var.get(), 8)
        else:
            length = max(length_corp_var.get(), 12)
        #Dla trybu standardowego
        if active_tab == 0:
            pwd = generate_password(
                length,
                lower_var.get(),
                upper_var.get(),
                digit_var.get(),
                special_var.get(),
                remove_similar_var.get(),
                remove_sequence_var.get(),
                self.pairs_dict
            )
            if strength_meter is None:
                strength_meter = tk.Canvas(win, height=20, bg="#b3b3b3")
            strength_meter.pack(fill="x", padx=10, pady=(5, 10))
            update_strength_meter(pwd)

        #Dla trybu korporacyjnego
        elif active_tab == 1:
            pwd = generate_corporate_password(length, self.pairs_dict)
            if strength_meter is not None:
                strength_meter.pack_forget()

        result_var.set(pwd)

    #Tryb standardowy
    result_frame = ttk.Frame(standard_tab)
    result_frame.grid(row=7, column=0, columnspan=3, pady=10)

    tk.Entry(result_frame, textvariable=result_var, width=30).pack(side="left", padx=(0, 10))
    tk.Button(result_frame, text="Generuj hasło", command=generate).pack(side="left")
    tk.Button(result_frame, text="Kopiuj", command=lambda: copy_to_clipboard(result_var.get())).pack(side="left")

    tk.Label(standard_tab, text="Długość:").grid(row=0, column=0)
    length_label = tk.Label(standard_tab, text=str(length_standard_var.get()))
    length_label.grid(row=0, column=2, padx=5)

    def update_length(value):
        """Obsługuje suwak długości hasła"""
        length_label.config(text=value)

    tk.Scale(
        standard_tab,
        from_=8,
        to=60,
        orient="horizontal",
        variable=length_standard_var,
        command=update_length,
        length=150
    ).grid(row=0, column=1, pady=5)

    lower_var = tk.BooleanVar(value=True)
    upper_var = tk.BooleanVar(value=True)
    digit_var = tk.BooleanVar(value=True)
    special_var = tk.BooleanVar(value=True)
    remove_similar_var = tk.BooleanVar(value=True)
    remove_sequence_var = tk.BooleanVar(value=True)

    tk.Checkbutton(standard_tab, text="Małe litery", variable=lower_var).grid(row=1, column=0, sticky="w")
    tk.Checkbutton(standard_tab, text="Duże litery", variable=upper_var).grid(row=2, column=0, sticky="w")
    tk.Checkbutton(standard_tab, text="Cyfry", variable=digit_var).grid(row=3, column=0, sticky="w")
    tk.Checkbutton(standard_tab, text="Znaki specjalne", variable=special_var).grid(row=4, column=0, sticky="w")
    tk.Checkbutton(standard_tab, text="Wyklucz podobne znaki (0/O, S/5 itd.) ", variable=remove_similar_var).grid(row=5, column=0, sticky="w")
    tk.Checkbutton(standard_tab, text="Bez powtarzających się sekwencji znaków", variable=remove_sequence_var).grid(row=6, column=0, sticky="w")

    #Tryb korporacyjny
    tk.Label(corporate_tab, text="Długość:").grid(row=0, column=0)
    tk.Scale(corporate_tab, from_=12, to=60, orient="horizontal",
             variable=length_corp_var, command=lambda v: length_label.config(text=v), length=150).grid(row=0, column=1, pady=5)

    tk.Label(corporate_tab,
             text="Tworzy hasło które zawiera: Duże litery, Małe litery, Cyfry, Znaki specjalne",
             font=('Arial', 10, 'bold')).grid(row=2, column=0, columnspan=2, sticky="w")

    result_frame_corp = ttk.Frame(corporate_tab)
    result_frame_corp.grid(row=3, column=0, columnspan=3, pady=10)

    tk.Entry(result_frame_corp, textvariable=result_var, width=30).pack(side="left", padx=(0, 10))
    tk.Button(result_frame_corp, text="Generuj hasło", command=generate).pack(side="left")
    tk.Button(result_frame_corp, text="Kopiuj", command=lambda: copy_to_clipboard(result_var.get())).pack(side="left")

    #Tryb personalizacji

    tk.Label(personalized_tab, text="Wklej swoje hasło", font=('Arial', 10, 'bold')).grid(
        row=0, column=0, padx=5, pady=5)

    user_pwd_var = tk.StringVar()
    tk.Entry(personalized_tab, textvariable=user_pwd_var, width=30).grid(row=0, column=1, padx=5, pady=5)

    leets_var = tk.BooleanVar()
    reverse_var = tk.BooleanVar()
    shuffle_var = tk.BooleanVar()
    custom_chars_var = tk.StringVar()

    tk.Checkbutton(personalized_tab, text="Zmień na leetspeak", variable=leets_var).grid(row=1, column=0, sticky="w")
    tk.Checkbutton(personalized_tab, text="Odwróć hasło", variable=reverse_var).grid(row=2, column=0, sticky="w")
    tk.Checkbutton(personalized_tab, text="Wymieszaj hasło", variable=shuffle_var).grid(row=3, column=0, sticky="w")

    tk.Label(personalized_tab, text="Dodaj własne znaki:", font=('Arial', 10)).grid(row=4, column=0, sticky="w")
    tk.Entry(personalized_tab, textvariable=custom_chars_var, width=30).grid(row=5, column=0, padx=5, pady=5)

    tk.Label(personalized_tab, text="Zmodyfikowane hasło:", font=('Arial', 10)).grid(
        row=6, column=0, sticky="w", pady=(10, 0))

    personalized_var = tk.StringVar()
    tk.Entry(personalized_tab, textvariable=personalized_var, width=30).grid(
        row=6, column=1, padx=5, pady=(10, 0))

    tk.Button(personalized_tab, text="Kopiuj", command=lambda: copy_to_clipboard(personalized_var.get())).grid(row=6, column=2, padx=5)

    def personalized_password():
        pwd = user_pwd_var.get()
        if not pwd:
            personalized_var.set("Brak hasła")
            return
        #Zmienia na leetspeak
        if leets_var.get():
            if any(c in self.pairs_dict.values() for c in pwd):
                reverse_map = {v: k for k, v in self.pairs_dict.items()}
                pwd = remove_similar_chars(pwd, reverse_map)
            else:
                pwd = remove_similar_chars(pwd, self.pairs_dict)
        #Dodaje dodatkowe znaki
        extra_chars = custom_chars_var.get()
        if extra_chars:
            pwd += extra_chars
        #Odwraca hasło
        if reverse_var.get():
            pwd = pwd[::-1]
        #Miesza hasło
        if shuffle_var.get():
            pwd = ''.join(random.sample(pwd, len(pwd)))
        personalized_var.set(pwd)

    tk.Button(personalized_tab, text="Modyfikuj", command=personalized_password).grid(row=7, column=3, pady=10)

    def send_to_analysis():
        """Wysyła hasło do analizy jego siły"""
        pwd = personalized_var.get()
        if pwd:
            self.password_entry.delete(0, tk.END)
            self.password_entry.insert(0, pwd)
            self.analyze_strength()

    tk.Button(personalized_tab, text="Wyślij do analizy siły hasła",
              command=send_to_analysis).grid(row=8, column=3, pady=10)

    #Zamknij
    close_frame = ttk.Frame(win)
    close_frame.pack(side="bottom", anchor="e", padx=10, pady=10)
    tk.Button(close_frame, text="Zamknij", command=win.destroy).pack()

def remove_similar_chars(pwd, mapping):
    changed = True
    while changed:
        changed = False
        new_pwd = ""
        for c in pwd:
            new_c = mapping.get(c, c)
            if new_c != c:
                changed = True
            new_pwd += new_c
        pwd = new_pwd
    return pwd


def remove_repeated_sequences(pwd: str, max_repeat: int = 3) -> str:
    """Usuwa powtarzające się sekwencje znaków dłuższe niż max"""
    if not pwd:
        return pwd
    cleaned = []
    for char in pwd:
        if len(cleaned) < max_repeat or cleaned[-max_repeat] != char:
            cleaned.append(char)
    return "".join(cleaned)


def generate_corporate_password(length=12, mapping=None):
    """Generuje hasło korporacyjne zawiera conajmniej
    1 duża litere, 1 cyfre oraz 1 znak specjalny"""
    sets = [
        string.ascii_uppercase,
        string.ascii_lowercase,
        string.digits,
        "!@#$%^&*()-_=+[]{};:,.<>?"
    ]
    sets = [remove_similar_chars(s, mapping) for s in sets]
    upper, lower, digits, specials = sets

    required = [
        secrets.choice(upper),
        secrets.choice(lower),
        secrets.choice(digits),
        secrets.choice(specials)
    ]

    all_chars = upper + lower + digits + specials
    required += [secrets.choice(all_chars) for _ in range(length - 4)]

    secrets.SystemRandom().shuffle(required)
    return "".join(required)


def generate_password(length, lower, upper, digit, special, remove_similar, remove_sequence, mapping):
    """Generuje hasło na podstawie wyboru użytkownika"""
    chars = ""
    if lower:
        chars += string.ascii_lowercase
    if upper:
        chars += string.ascii_uppercase
    if digit:
        chars += string.digits
    if special:
        chars += string.punctuation

    if remove_similar:
        chars = remove_similar_chars(chars, mapping)

    if remove_sequence:
        chars = remove_repeated_sequences(chars)
    #Tu jeśli nic nie wybierze
    if not chars:
        return ""

    return "".join(random.choice(chars) for i in range(length))

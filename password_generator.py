import secrets
import tkinter as tk
import random
import string
from tkinter import ttk

def open_password_generator_window(self):
    """"Otwiera okienko generatora hasła"""
    win = tk.Toplevel(self.root)
    win.title("Generator hasła")
    win.geometry("600x500")

    ttk.Label(
        win,
        text="Generator hasła",
        font=('Arial', 16, 'bold')
    ).pack(pady=(10,0), anchor="center")

    notebook=ttk.Notebook(win)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    standard_tab=ttk.Frame(notebook)
    corporate_tab=ttk.Frame(notebook)

    notebook.add(standard_tab, text="Tryb standardowy")
    notebook.add(corporate_tab, text="Tryb korporacyjny")

    length_var = tk.IntVar(value=12)

    #Tryb standardowy
    tk.Label(standard_tab, text="Długość:").grid(row=0, column=0)
    length_label=tk.Label(standard_tab, text=str(length_var.get()))
    length_label.grid(row=0,column=2,padx=5)

    def update_length(value):
        """Obsługuje suwak długości hasła"""
        length_label.config(text=value)

    tk.Scale(
            standard_tab,
            from_=8,
            to=60,
            orient="horizontal",
            variable=length_var,
            command=update_length,
            length=150
        ).grid(row=0,column=1,pady=5)

    lower_var = tk.BooleanVar(value=True)
    upper_var = tk.BooleanVar(value=True)
    digit_var = tk.BooleanVar(value=True)
    special_var = tk.BooleanVar(value=True)
    remove_similar_var=tk.BooleanVar(value=True)
    remove_sequence_var=tk.BooleanVar(value=True)

    tk.Checkbutton(standard_tab, text="Małe litery", variable=lower_var).grid(row=1, column=0, sticky="w")
    tk.Checkbutton(standard_tab, text="Duże litery", variable=upper_var).grid(row=2, column=0, sticky="w")
    tk.Checkbutton(standard_tab, text="Cyfry", variable=digit_var).grid(row=3, column=0, sticky="w")
    tk.Checkbutton(standard_tab, text="Znaki specjalne", variable=special_var).grid(row=4, column=0, sticky="w")
    tk.Checkbutton(standard_tab, text="Wyklucz podobne znaki (0/O, S/5 itd.) ", variable=remove_similar_var).grid(row=5,column=0,sticky="w")
    tk.Checkbutton(standard_tab, text="Bez powtarzających się sekwencji znaków", variable=remove_sequence_var).grid(row=6,column=0,sticky="w")

    #Tryb korporacyjny
    tk.Label(corporate_tab,text="Długość:").grid(row=0,column=0)
    tk.Scale(corporate_tab,from_=12, to=60, orient="horizontal",
             variable=length_var,command=update_length,length=150).grid(row=0,column=1,pady=5)
    tk.Label(corporate_tab, text="Tworzy hasło które zawiera: Duże litery\n Małe litery\n Cyfry\n Znaki specjalne\n",
             font=('Arial', 10, 'bold')).grid(row=2, column=0, columnspan=2, sticky="w")

    result_var = tk.StringVar()
    def generate():
        """Przekazuje dane do generatora hasła"""
        active_tab = notebook.index(notebook.select())
        #Dla trybu standardowego
        if active_tab==0:
            pwd = generate_password(
                length_var.get(),
                lower_var.get(),
                upper_var.get(),
                digit_var.get(),
                special_var.get(),
                remove_similar_var.get(),
                remove_sequence_var.get()
            )
            score, strength=self.calculate_password_strength(pwd)
            if score<40:
                color="red"
            elif score<60:
                color="orange"
            else:
                color="green"
            strength_var.set(f"Siła hasła: {strength} ({score/100}")
            strength_label.config(foreground=color)
        #Dla trybu korporacyjnego
        else:
            pwd=generate_corporate_password(length_var.get())
            strength_var.set("")
            strength_label.config(foreground="black")
        result_var.set(pwd)
    #Ramka z polem hasła i przyciskiem generuj
    result_frame=ttk.Frame(win)
    result_frame.pack(pady=10)
    #Podgląd siły hasła dla trybu standardowego
    strength_var=tk.StringVar(value="")
    strength_label=ttk.Label(win,textvariable=strength_var, font=('Arial',10))
    strength_label.pack()
    tk.Entry(result_frame, textvariable=result_var, width=30).pack(side="left", padx=(0, 10))
    tk.Button(result_frame, text="Generuj hasło", command=generate).pack(side="left")

    #Ramka z przyciskiem zamknij
    close_frame=ttk.Frame(win)
    close_frame.pack(side="bottom",anchor="e",padx=10,pady=10)
    tk.Button(close_frame, text="Zamknij",command=win.destroy).pack()
def remove_similar_chars(chars:str)->str:
    """Funkcja wyłapująca znaki podobne """
    #Pary podobnych znaków
    pairs=[
            ("O","0"),
            ("l","1"),
            ("S", "5"),
            ("a","@"),
            ("E","3"),
            ("Z","2"),
            ("G","6"),
            ("U","V"),
            ("g","q"),
            ("i","!"),
            ("B","8"),
    ]
    filtered=set(chars)
    #Jeśli znajdzie podobny element to go odrzuca z puli do hasła
    for first,second in pairs:
        if first in filtered or second in filtered:
                filtered.discard(first)
                filtered.add(second)
    return "".join(sorted(filtered))
def remove_repeated_sequances(pwd:str,max_repeat: int=3)->str:
    "Usuwa powtarzające się sekwencje znaków dłuższe niż max"
    if not pwd:
        return pwd
    cleaned=[]
    for char in pwd:
        if len(cleaned)<max_repeat or cleaned[-max_repeat]!=char:
            cleaned.append(char)
    return "".join(cleaned)
def generate_corporate_password(length=12):
    """Generuje hasło korporacyjne zawiera conajmniej
    1 duża litere, 1 cyfre oraz 1 znak specjalny"""
    sets=[
       string.ascii_uppercase,
       string.ascii_lowercase,
       string.digits,
        "!@#$%^&*()-_=+[]{};:,.<>?"
        ]
    sets=[remove_similar_chars(s) for s in sets]
    upper,lower,digits,specials=sets
    required=[
       secrets.choice(upper),
       secrets.choice(lower),
       secrets.choice(digits),
       secrets.choice(specials)
    ]
    all_chars=upper+lower+digits+specials
    required+=[secrets.choice(all_chars) for _ in range(length-4)]
    secrets.SystemRandom().shuffle(required)
    return "".join(required)
def generate_password(length, lower,upper,digit,special,remove_similar,remove_sequence):
    """Generuje hasło na podstawie wyboru użytkownika"""

    chars=""
    if lower:
        chars +=string.ascii_lowercase
    if upper:
        chars+=string.ascii_uppercase
    if digit:
        chars+=string.digits
    if special:
        chars+=string.punctuation
    if remove_similar:
        chars=remove_similar_chars(chars)
    if remove_sequence:
        chars=remove_repeated_sequances(chars)
    if not chars:
        return ""
    return "".join(random.choice(chars) for i in range(length))



#wyklucz powtarzające się znaki wskażnik sił hasła oraz kopiowanie do schowka. typowe hasło korporacyjne ,leety
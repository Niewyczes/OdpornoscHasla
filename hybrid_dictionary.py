import itertools
import time
import tkinter as tk
from tkinter import messagebox
from threading import Thread
from concurrent.futures import ThreadPoolExecutor

from itertools import product
##Roboczo on the fly
def on_the_fly_variant(word):
    """Generuje warianty liter on_the_fly"""
    for pattern in product([0, 1], repeat=len(word)):
        yield ''.join(
            c.upper() if bit else c.lower()
            for c, bit in zip(word, pattern)
        )
def start_hybrid_dictionary(self):
    password = self.password_entry.get()
    if not password:
        messagebox.showwarning("Brak hasła", "Wprowadź hasło do testu.")
        return

    self.testing = True
    self.stop_event.clear()
    self.start_time = time.time()
    self.attempts = 0

    self.result_text.delete(1.0, tk.END)
    self.gui_safe(self.result_text.insert, tk.END,
                  "Test hybrid_dictionary (Etap 1)\n")

    thread = Thread(target=self.run_hybrid_dictionary, args=(password,), daemon=True)
    thread.start()


def run_hybrid_dictionary(self, password):
    hybrid_dict = self.load_hybrid_passwords()

    name_variants = []
    adj_variants = []

    for name in hybrid_dict['names']:
        name_variants.extend([name, name.lower(), name.upper(), name.capitalize()])

    for adj in hybrid_dict['adjectives']:
        adj_variants.extend([adj, adj.lower(), adj.upper(), adj.capitalize()])

    specs = hybrid_dict['special']
    target_length = len(password)

    self.executor = ThreadPoolExecutor(max_workers=1)
    self.futures_dict = []

    future = self.executor.submit(
        self.hybrid_dictionary_worker,
        password,
        name_variants,
        adj_variants,
        specs,
        target_length,
        self.stop_event
    )
    future.add_done_callback(self.on_done_hybrid_dictionary)
    self.futures_dict.append(future)


def hybrid_dictionary_worker(self, password, names, adjs, specs, target_length, stop_event):
    start_time = time.time()
    local_attempts = 0

    max_spec_len = max(len(s) for s in specs)
    polish_chars = "ąćęłńóśżź"

    for name in names:
        if stop_event.is_set():
            break
        if any(ch in name and ch not in password for ch in polish_chars):
            continue

        for adj in adjs:
            if stop_event.is_set():
                break
            if any(ch in adj and ch not in password for ch in polish_chars):
                continue

            if abs(len(name) + len(adj) - target_length) > max_spec_len:
                continue

            for spec in specs:
                if stop_event.is_set():
                    break

                if len(name) + len(adj) + len(spec) != target_length:
                    continue

                parts = [name, adj, spec]

                for combo_tuple in itertools.permutations(parts):
                    if stop_event.is_set():
                        break

                    combo = "".join(combo_tuple)
                    local_attempts += 1

                    if combo == password:
                        elapsed = time.time() - start_time
                        return ("found", combo, local_attempts, elapsed)

    elapsed = time.time() - start_time
    return ("done", None, local_attempts, elapsed)


def on_done_hybrid_dictionary(self, future):
    try:
        status, match, attempts, elapsed = future.result()

        self.finish_hybrid_dictionary(
            found=(status == "found"),
            match=match if match else "",
            attempts=attempts,
            elapsed_time=elapsed
        )

    except Exception as e:
        print("Błąd hybrid_dictionary:", e)

    self.testing = False


def finish_hybrid_dictionary(self, found, match, attempts, elapsed_time):
    self.result_text.insert(tk.END, f"\n{'=' * 60}\n")
    self.result_text.insert(tk.END, "WYNIK TESTU HYBRID_DICTIONARY:\n")
    self.result_text.insert(tk.END, f"{'=' * 60}\n")

    self.result_text.insert(tk.END, f"Czas testu: {elapsed_time:.2f} sekund\n")
    self.result_text.insert(tk.END, f"Liczba prób: {attempts:,}\n")
    self.result_text.insert(tk.END, f"Hasło znalezione: {'TAK' if found else 'NIE'}\n")

    if found:
        self.result_text.insert(tk.END,
            f"\n⚠️  Hasło znalezione: {match}\n"
            "Zalecenie: zmień hasło na silniejsze.\n"
        )
    else:
        self.result_text.insert(tk.END,
            "\n✓ Hasło nie zostało znalezione w hybrid_dictionary.\n"
        )

    self.testing = False
    self.stop_button.config(command=self.stop_test_func,state=tk.NORMAL)
    self.progress_var.set(100)

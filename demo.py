"""
PGP projekat - MOCK GUI demo sa placeholder podacima.

Ovo NIJE finalna aplikacija - ovde nema stvarne kriptografije, sve vrednosti
(potpisi, kljucevi, statusi verifikacije) su izmisljene da bi se videlo kako
bi izgledao tok kroz ekrane:
    - izbor trenutnog korisnika
    - prikaz prstena javnih i privatnih kljuceva
    - slanje poruke (dijalog sa checkboxovima, radio dugmićima, file pickerom)
    - prijem poruke (dijalog sa file pickerom i placeholder rezultatima)
    - uvoz/izvoz kljuca iz/u .pem fajl (file picker demo)
    - generisanje novog para kljuceva (forma)

Kada se logika (core/) zavrsi, ovi placeholderi se zamenjuju pravim pozivima
ka AppController-u.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import datetime


# =====================================================================
# PLACEHOLDER PODACI (u finalnoj verziji bi dolazili iz AppControllera,
# koji ih ucitava iz JSON fajlova / keyring objekata)
# =====================================================================

USERS = {
    "alice": {
        "display_name": "Alice Petrović",
        "email": "alice@example.com",
        "private_keys": [
            {"key_id": "A1B2C3D4", "given_name": "Alice - lični ključ (2048)",
             "size": 2048, "timestamp": "2026-03-01 10:15"},
            {"key_id": "E5F6A7B8", "given_name": "Alice - test ključ (1024)",
             "size": 1024, "timestamp": "2026-05-12 09:02"},
        ],
        "public_keys": [
            {"key_id": "A1B2C3D4", "given_name": "Alice - lični ključ (2048)",
             "owner": "Alice Petrović", "size": 2048},
            {"key_id": "9F8E7D6C", "given_name": "Bob - uvezen ključ",
             "owner": "Bob Jovanović", "size": 2048},
        ],
    },
    "bob": {
        "display_name": "Bob Jovanović",
        "email": "bob@example.com",
        "private_keys": [
            {"key_id": "9F8E7D6C", "given_name": "Bob - lični ključ",
             "size": 2048, "timestamp": "2026-02-20 14:40"},
        ],
        "public_keys": [
            {"key_id": "9F8E7D6C", "given_name": "Bob - lični ključ",
             "owner": "Bob Jovanović", "size": 2048},
            {"key_id": "A1B2C3D4", "given_name": "Alice - uvezen ključ",
             "owner": "Alice Petrović", "size": 2048},
        ],
    },
    "carol": {
        "display_name": "Carol Nikolić",
        "email": "carol@example.com",
        "private_keys": [],
        "public_keys": [
            {"key_id": "A1B2C3D4", "given_name": "Alice - uvezen ključ",
             "owner": "Alice Petrović", "size": 2048},
        ],
    },
}


# =====================================================================
# KEYRING PRIKAZ (Treeview sa dva taba - privatni / javni kljucevi)
# =====================================================================

class KeyringFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        # --- Tab: privatni kljucevi ---
        priv_tab = ttk.Frame(notebook)
        notebook.add(priv_tab, text="Privatni ključevi")

        self.priv_tree = ttk.Treeview(
            priv_tab, columns=("given_name", "key_id", "size", "timestamp"),
            show="headings", height=6
        )
        self.priv_tree.heading("given_name", text="Naziv")
        self.priv_tree.heading("key_id", text="Key ID")
        self.priv_tree.heading("size", text="Veličina")
        self.priv_tree.heading("timestamp", text="Kreiran")
        self.priv_tree.column("given_name", width=220)
        self.priv_tree.column("key_id", width=100)
        self.priv_tree.column("size", width=80, anchor="center")
        self.priv_tree.column("timestamp", width=140)
        self.priv_tree.pack(fill="both", expand=True, padx=5, pady=5)

        # --- Tab: javni kljucevi ---
        pub_tab = ttk.Frame(notebook)
        notebook.add(pub_tab, text="Javni ključevi")

        self.pub_tree = ttk.Treeview(
            pub_tab, columns=("given_name", "key_id", "owner", "size"),
            show="headings", height=6
        )
        self.pub_tree.heading("given_name", text="Naziv")
        self.pub_tree.heading("key_id", text="Key ID")
        self.pub_tree.heading("owner", text="Vlasnik")
        self.pub_tree.heading("size", text="Veličina")
        self.pub_tree.column("given_name", width=200)
        self.pub_tree.column("key_id", width=100)
        self.pub_tree.column("owner", width=160)
        self.pub_tree.column("size", width=80, anchor="center")
        self.pub_tree.pack(fill="both", expand=True, padx=5, pady=5)

    def refresh(self, user_data):
        self.priv_tree.delete(*self.priv_tree.get_children())
        for k in user_data["private_keys"]:
            self.priv_tree.insert("", "end", values=(
                k["given_name"], k["key_id"], f'{k["size"]} bita', k["timestamp"]
            ))

        self.pub_tree.delete(*self.pub_tree.get_children())
        for k in user_data["public_keys"]:
            self.pub_tree.insert("", "end", values=(
                k["given_name"], k["key_id"], k["owner"], f'{k["size"]} bita'
            ))


# =====================================================================
# DIJALOG: SLANJE PORUKE
# =====================================================================

class SendMessageDialog(tk.Toplevel):
    def __init__(self, parent, user_data):
        super().__init__(parent)
        self.title("Slanje poruke")
        self.geometry("460x480")
        self.resizable(True, True)
        self.user_data = user_data

        # --- Poruka koju kucamo ---
        tk.Label(self, text="Poruka:").pack(anchor="w", padx=10, pady=(10, 0))
        self.message_text = tk.Text(self, height=5)
        self.message_text.pack(fill="x", padx=10)
        self.message_text.insert("1.0", "Ovo je placeholder sadržaj poruke...")

        # --- Potpisivanje ---
        tk.Label(self, text="Privatni ključ za potpisivanje:").pack(
            anchor="w", padx=10, pady=(12, 0))
        self.priv_var = tk.StringVar()
        priv_values = [k["given_name"] for k in user_data["private_keys"]]
        self.priv_dropdown = ttk.Combobox(
            self, textvariable=self.priv_var, values=priv_values, state="readonly")
        self.priv_dropdown.pack(fill="x", padx=10)
        if priv_values:
            self.priv_dropdown.current(0)

        # --- Enkripcija ---
        tk.Label(self, text="Javni ključ primaoca (za enkripciju):").pack(
            anchor="w", padx=10, pady=(10, 0))
        self.pub_var = tk.StringVar()
        pub_values = [k["given_name"] for k in user_data["public_keys"]]
        self.pub_dropdown = ttk.Combobox(
            self, textvariable=self.pub_var, values=pub_values, state="readonly")
        self.pub_dropdown.pack(fill="x", padx=10)
        if pub_values:
            self.pub_dropdown.current(0)

        # --- Checkboxovi ---
        opts_frame = tk.LabelFrame(self, text="Opcije obrade")
        opts_frame.pack(fill="x", padx=10, pady=(12, 0))

        self.opt_encrypt = tk.BooleanVar(value=True)
        self.opt_sign = tk.BooleanVar(value=True)
        self.opt_compress = tk.BooleanVar(value=False)
        self.opt_radix64 = tk.BooleanVar(value=True)

        tk.Checkbutton(opts_frame, text="Enkripcija (tajnost)",
                        variable=self.opt_encrypt).pack(anchor="w", padx=10)
        tk.Checkbutton(opts_frame, text="Potpisivanje (autentičnost)",
                        variable=self.opt_sign).pack(anchor="w", padx=10)
        tk.Checkbutton(opts_frame, text="Kompresija (ZIP)",
                        variable=self.opt_compress).pack(anchor="w", padx=10)
        tk.Checkbutton(opts_frame, text="Radix-64 konverzija",
                        variable=self.opt_radix64).pack(anchor="w", padx=10)

        # --- Radio dugmici za algoritam ---
        algo_frame = tk.LabelFrame(self, text="Simetrični algoritam")
        algo_frame.pack(fill="x", padx=10, pady=(10, 0))

        self.algo_var = tk.StringVar(value="AES128")
        tk.Radiobutton(algo_frame, text="AES128", variable=self.algo_var,
                        value="AES128").pack(anchor="w", padx=10)
        tk.Radiobutton(algo_frame, text="TripleDES", variable=self.algo_var,
                        value="3DES").pack(anchor="w", padx=10)

        # --- Izlazni fajl ---
        tk.Label(self, text="Sačuvaj kao:").pack(anchor="w", padx=10, pady=(12, 0))
        out_frame = tk.Frame(self)
        out_frame.pack(fill="x", padx=10)
        self.out_path_var = tk.StringVar()
        tk.Entry(out_frame, textvariable=self.out_path_var,
                  state="readonly").pack(side="left", fill="x", expand=True)
        tk.Button(out_frame, text="Sačuvaj kao...",
                   command=self.browse_output).pack(side="left", padx=(5, 0))

        # --- Dugme za slanje ---
        tk.Button(self, text="Pošalji poruku", command=self.do_send,
                    bg="#2e7d32", fg="white").pack(pady=16)

    def browse_output(self):
        path = filedialog.asksaveasfilename(
            title="Sačuvaj poruku kao",
            defaultextension=".pgp",
            filetypes=[("PGP fajlovi", "*.pgp"), ("Svi fajlovi", "*.*")]
        )
        if path:
            self.out_path_var.set(path)

    def do_send(self):
        if not self.out_path_var.get():
            messagebox.showerror("Greška", "Izaberite gde da sačuvate poruku.")
            return
        if self.opt_encrypt.get() and not self.pub_var.get():
            messagebox.showerror("Greška", "Izaberite javni ključ primaoca.")
            return
        if self.opt_sign.get() and not self.priv_var.get():
            messagebox.showerror("Greška", "Izaberite privatni ključ za potpisivanje.")
            return

        # U pravoj aplikaciji bi ovde isao poziv:
        # controller.send_message(text, priv_key, pub_key, opts, algo, out_path)
        summary = (
            f"Potpisano: {'da (' + self.priv_var.get() + ')' if self.opt_sign.get() else 'ne'}\n"
            f"Enkriptovano: {'da (' + self.pub_var.get() + ')' if self.opt_encrypt.get() else 'ne'}\n"
            f"Kompresija: {'da' if self.opt_compress.get() else 'ne'}\n"
            f"Radix-64: {'da' if self.opt_radix64.get() else 'ne'}\n"
            f"Algoritam: {self.algo_var.get()}\n"
            f"Fajl: {self.out_path_var.get()}"
        )
        messagebox.showinfo("Poruka sačuvana (placeholder)", summary)
        self.destroy()


# =====================================================================
# DIJALOG: PRIJEM PORUKE
# =====================================================================

class ReceiveMessageDialog(tk.Toplevel):
    def __init__(self, parent, user_data):
        super().__init__(parent)
        self.title("Prijem poruke")
        self.geometry("460x420")
        self.resizable(True, True)
        self.user_data = user_data
        self.loaded = False

        tk.Label(self, text="Fajl sa porukom:").pack(anchor="w", padx=10, pady=(10, 0))
        in_frame = tk.Frame(self)
        in_frame.pack(fill="x", padx=10)
        self.in_path_var = tk.StringVar()
        tk.Entry(in_frame, textvariable=self.in_path_var,
                  state="readonly").pack(side="left", fill="x", expand=True)
        tk.Button(in_frame, text="Otvori...",
                   command=self.browse_input).pack(side="left", padx=(5, 0))

        self.result_frame = tk.LabelFrame(self, text="Rezultat obrade")
        self.result_frame.pack(fill="both", expand=True, padx=10, pady=(15, 0))

        self.status_label = tk.Label(self.result_frame, text="(učitajte fajl)",
                                       fg="gray")
        self.status_label.pack(anchor="w", padx=10, pady=10)

        self.save_btn = tk.Button(self, text="Sačuvaj originalnu poruku...",
                                    command=self.save_decrypted, state="disabled")
        self.save_btn.pack(pady=12)

    def browse_input(self):
        path = filedialog.askopenfilename(
            title="Izaberite fajl sa porukom",
            filetypes=[("PGP fajlovi", "*.pgp"), ("Svi fajlovi", "*.*")]
        )
        if not path:
            return
        self.in_path_var.set(path)
        self.process_file(path)

    def process_file(self, path):
        # PLACEHOLDER - u pravoj verziji ovde ide:
        # result = controller.receive_message(path, self.user_data)
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        signer = self.user_data["public_keys"][0]["owner"] if \
            self.user_data["public_keys"] else "nepoznat"

        tk.Label(self.result_frame, text="✓ Potpis uspešno verifikovan",
                  fg="#2e7d32").pack(anchor="w", padx=10, pady=(10, 2))
        tk.Label(self.result_frame, text=f"Autor potpisa: {signer}").pack(
            anchor="w", padx=10)
        tk.Label(self.result_frame, text="Enkripcija: AES128").pack(
            anchor="w", padx=10)
        tk.Label(self.result_frame, text="Kompresija: ne").pack(
            anchor="w", padx=10)
        tk.Label(self.result_frame,
                  text=f"Vreme prijema: {datetime.datetime.now():%Y-%m-%d %H:%M}").pack(
            anchor="w", padx=10, pady=(0, 10))

        self.loaded = True
        self.save_btn.config(state="normal")

    def save_decrypted(self):
        path = filedialog.asksaveasfilename(
            title="Sačuvaj originalnu poruku",
            defaultextension=".txt",
            filetypes=[("Tekstualni fajlovi", "*.txt"), ("Svi fajlovi", "*.*")]
        )
        if path:
            messagebox.showinfo("Sačuvano (placeholder)", f"Poruka bi bila sačuvana u:\n{path}")


# =====================================================================
# DIJALOG: UVOZ KLJUČA IZ .pem
# =====================================================================

class ImportKeyDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Uvoz ključa")
        self.geometry("420x300")
        self.resizable(False, False)

        tk.Label(self, text="Šta uvozite:").pack(anchor="w", padx=10, pady=(10, 0))
        self.import_type = tk.StringVar(value="public")
        tk.Radiobutton(self, text="Samo javni ključ", variable=self.import_type,
                        value="public", command=self.update_password_state).pack(
            anchor="w", padx=20)
        tk.Radiobutton(self, text="Ceo par (javni i privatni)", variable=self.import_type,
                        value="pair", command=self.update_password_state).pack(
            anchor="w", padx=20)

        tk.Label(self, text=".pem fajl:").pack(anchor="w", padx=10, pady=(12, 0))
        file_frame = tk.Frame(self)
        file_frame.pack(fill="x", padx=10)
        self.pem_path_var = tk.StringVar()
        tk.Entry(file_frame, textvariable=self.pem_path_var,
                  state="readonly").pack(side="left", fill="x", expand=True)
        tk.Button(file_frame, text="Izaberi fajl...",
                   command=self.browse_pem).pack(side="left", padx=(5, 0))

        tk.Label(self, text="Naziv za prikaz (given name):").pack(
            anchor="w", padx=10, pady=(12, 0))
        self.given_name_var = tk.StringVar()
        tk.Entry(self, textvariable=self.given_name_var).pack(fill="x", padx=10)

        tk.Label(self, text="Lozinka privatnog ključa:").pack(
            anchor="w", padx=10, pady=(10, 0))
        self.password_entry = tk.Entry(self, show="*", state="disabled")
        self.password_entry.pack(fill="x", padx=10)

        tk.Button(self, text="Uvezi", command=self.do_import,
                    bg="#2e7d32", fg="white").pack(pady=16)

    def update_password_state(self):
        if self.import_type.get() == "pair":
            self.password_entry.config(state="normal")
        else:
            self.password_entry.delete(0, "end")
            self.password_entry.config(state="disabled")

    def browse_pem(self):
        path = filedialog.askopenfilename(
            title="Izaberite .pem fajl",
            filetypes=[("PEM fajlovi", "*.pem"), ("Svi fajlovi", "*.*")]
        )
        if path:
            self.pem_path_var.set(path)

    def do_import(self):
        if not self.pem_path_var.get():
            messagebox.showerror("Greška", "Izaberite .pem fajl.")
            return
        if self.import_type.get() == "pair" and not self.password_entry.get():
            messagebox.showerror("Greška", "Unesite lozinku privatnog ključa.")
            return

        kind = "ceo par ključeva" if self.import_type.get() == "pair" else "javni ključ"
        messagebox.showinfo(
            "Uvezeno (placeholder)",
            f"Uvezen {kind} iz:\n{self.pem_path_var.get()}\n\n"
            f"Naziv: {self.given_name_var.get() or '(nije unet)'}"
        )
        self.destroy()


# =====================================================================
# GLAVNI PROZOR
# =====================================================================

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PGP alat - demo")
        self.geometry("640x520")

        self.current_user_id = None

        # --- Izbor korisnika ---
        top_frame = tk.Frame(self)
        top_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(top_frame, text="Trenutni korisnik:").pack(side="left")

        self.user_display_to_id = {v["display_name"]: k for k, v in USERS.items()}
        self.user_var = tk.StringVar()
        self.user_dropdown = ttk.Combobox(
            top_frame, textvariable=self.user_var,
            values=list(self.user_display_to_id.keys()), state="readonly", width=30
        )
        self.user_dropdown.pack(side="left", padx=(5, 0))
        self.user_dropdown.bind("<<ComboboxSelected>>", self.on_user_change)

        # --- Keyring prikaz ---
        self.keyring_frame = KeyringFrame(self)
        self.keyring_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # --- Dugmici za akcije ---
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))

        tk.Button(btn_frame, text="Generiši novi par ključeva",
                   command=self.generate_new_key).pack(side="left", padx=(0, 5))
        tk.Button(btn_frame, text="Uvezi iz .pem",
                   command=self.open_import_dialog).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Pošalji poruku",
                   command=self.open_send_dialog, bg="#1565c0", fg="white").pack(
            side="right", padx=5)
        tk.Button(btn_frame, text="Primi poruku",
                   command=self.open_receive_dialog, bg="#1565c0", fg="white").pack(
            side="right", padx=(5, 0))

        # Postavi prvog korisnika kao pocetnog
        self.user_dropdown.current(0)
        self.on_user_change()

    def on_user_change(self, event=None):
        display_name = self.user_var.get()
        self.current_user_id = self.user_display_to_id[display_name]
        user_data = USERS[self.current_user_id]
        self.keyring_frame.refresh(user_data)

    def open_send_dialog(self):
        user_data = USERS[self.current_user_id]
        SendMessageDialog(self, user_data)

    def open_receive_dialog(self):
        user_data = USERS[self.current_user_id]
        ReceiveMessageDialog(self, user_data)

    def open_import_dialog(self):
        ImportKeyDialog(self)

    def generate_new_key(self):
        # Jednostavan placeholder dijalog za generisanje - forma
        win = tk.Toplevel(self)
        win.title("Generisanje novog para ključeva")
        win.geometry("360x300")
        win.resizable(False, False)

        tk.Label(win, text="Ime:").pack(anchor="w", padx=10, pady=(10, 0))
        name_entry = tk.Entry(win)
        name_entry.pack(fill="x", padx=10)

        tk.Label(win, text="Email:").pack(anchor="w", padx=10, pady=(10, 0))
        email_entry = tk.Entry(win)
        email_entry.pack(fill="x", padx=10)

        tk.Label(win, text="Veličina ključa:").pack(anchor="w", padx=10, pady=(10, 0))
        size_var = tk.StringVar(value="2048")
        tk.Radiobutton(win, text="1024 bita", variable=size_var, value="1024").pack(
            anchor="w", padx=20)
        tk.Radiobutton(win, text="2048 bita", variable=size_var, value="2048").pack(
            anchor="w", padx=20)

        tk.Label(win, text="Lozinka za privatni ključ:").pack(
            anchor="w", padx=10, pady=(10, 0))
        pass_entry = tk.Entry(win, show="*")
        pass_entry.pack(fill="x", padx=10)

        def do_generate():
            if not name_entry.get() or not email_entry.get() or not pass_entry.get():
                messagebox.showerror("Greška", "Popunite sva polja.")
                return
            messagebox.showinfo(
                "Generisano (placeholder)",
                f"Novi par ključeva ({size_var.get()} bita) za:\n"
                f"{name_entry.get()} <{email_entry.get()}>"
            )
            win.destroy()

        tk.Button(win, text="Generiši", command=do_generate,
                    bg="#2e7d32", fg="white").pack(pady=16)


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
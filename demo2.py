"""
PGP projekat - MOCK GUI demo sa placeholder podacima.

Ovo NIJE finalna aplikacija - nema stvarne kriptografije, sve vrednosti
(kljucevi, potpisi, statusi verifikacije) su izmisljene da bi se videlo
kako bi izgledao tok kroz ekrane:
    - prikaz private i public keyring-a (dva odvojena, ravna spiska)
    - generisanje novog para kljuceva (dodaje se u OBA keyringa)
    - uvoz kljuca iz .pem fajla (samo javni deo, ili ceo par)
    - slanje poruke (potpis iz private keyring-a, enkripcija javnim iz
      public keyring-a, checkboxovi, radio dugmici, file picker)
    - prijem poruke (file picker + placeholder rezultat verifikacije)

Ovo predstavlja JEDNU PGP instalaciju: nema korisnika/naloga u aplikaciji,
samo dva prstena kljuceva koje sam bira ko potpisuje/enkriptuje.

Kada logika (core/) bude gotova, placeholderi se zamenjuju pravim pozivima.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import datetime
import os
import binascii


# =====================================================================
# "JSON BAZA" - dva ravna spiska, kao dva odvojena fajla na disku
# (npr. private_keyring.json i public_keyring.json). Ovde su hardkodirani
# radi demonstracije, ali oblik odgovara onome sto bi json.load() vratio.
#
# PRIVATE_KEYRING - moji sopstveni parovi kljuceva (imam i privatni deo)
# PUBLIC_KEYRING  - javni kljucevi: i moji sopstveni (mirror iz privatnog
#                   keyring-a) i tudji uvezeni (imaju "owner" polje)
# =====================================================================

PRIVATE_KEYRING = [
    {
        "key_id": "A1B2C3D4",
        "given_name": "Moj lični ključ (2048)",
        "name": "Alice Petrović",
        "email": "alice@example.com",
        "key_size": 2048,
        "timestamp": "2026-03-01T10:15:00",
        "public_key_pem": "-----BEGIN PUBLIC KEY-----\n...(placeholder)...\n-----END PUBLIC KEY-----\n",
        "private_key_pem": "-----BEGIN ENCRYPTED PRIVATE KEY-----\n...(placeholder)...\n-----END ENCRYPTED PRIVATE KEY-----\n",
    },
    {
        "key_id": "E5F6A7B8",
        "given_name": "Test ključ (1024)",
        "name": "Alice Petrović",
        "email": "alice@example.com",
        "key_size": 1024,
        "timestamp": "2026-05-12T09:02:00",
        "public_key_pem": "-----BEGIN PUBLIC KEY-----\n...(placeholder)...\n-----END PUBLIC KEY-----\n",
        "private_key_pem": "-----BEGIN ENCRYPTED PRIVATE KEY-----\n...(placeholder)...\n-----END ENCRYPTED PRIVATE KEY-----\n",
    },
]

PUBLIC_KEYRING = [
    {
        "key_id": "A1B2C3D4",
        "given_name": "Moj lični ključ (2048)",
        "owner": "Alice Petrović",
        "email": "alice@example.com",
        "key_size": 2048,
        "public_key_pem": "-----BEGIN PUBLIC KEY-----\n...(placeholder)...\n-----END PUBLIC KEY-----\n",
    },
    {
        "key_id": "E5F6A7B8",
        "given_name": "Test ključ (1024)",
        "owner": "Alice Petrović",
        "email": "alice@example.com",
        "key_size": 1024,
        "public_key_pem": "-----BEGIN PUBLIC KEY-----\n...(placeholder)...\n-----END PUBLIC KEY-----\n",
    },
    {
        "key_id": "9F8E7D6C",
        "given_name": "Bob - uvezen ključ",
        "owner": "Bob Jovanović",
        "email": "bob@example.com",
        "key_size": 2048,
        "public_key_pem": "-----BEGIN PUBLIC KEY-----\n...(placeholder)...\n-----END PUBLIC KEY-----\n",
    },
    {
        "key_id": "3C4D5E6F",
        "given_name": "Carol - uvezen ključ",
        "owner": "Carol Nikolić",
        "email": "carol@example.com",
        "key_size": 2048,
        "public_key_pem": "-----BEGIN PUBLIC KEY-----\n...(placeholder)...\n-----END PUBLIC KEY-----\n",
    },
]

#from keyring import PublicKeyring, PrivateKeyring
from utils.rsa_generation import generateKeys
#privateKeyring = PrivateKeyring()
#publicKeyring = PublicKeyring()
from app_core import publicKeyring, privateKeyring


# def new_key_id():
#     """Placeholder generisanje key_id-a - u pravoj verziji npr. poslednjih
#     8 bajtova SHA-1 hash-a javnog kljuca (kao u pravom PGP-u)."""
#     return binascii.hexlify(os.urandom(4)).decode().upper()


# =====================================================================
# KEYRING PRIKAZ (Treeview sa dva taba - private / public keyring)
# =====================================================================

class KeyringFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)
        self.notebook = notebook

        # --- Tab: private keyring ---
        priv_tab = ttk.Frame(notebook)
        notebook.add(priv_tab, text="Private keyring")

        self.priv_tree = ttk.Treeview(
            priv_tab, columns=("given_name", "key_id", "size", "timestamp", "pub_preview"),
            show="headings", height=8
        )
        self.priv_tree.heading("pub_preview", text="Public key (preview)")
        self.priv_tree.column("pub_preview", width=220)
        self.priv_tree.heading("given_name", text="Naziv")
        self.priv_tree.heading("key_id", text="Key ID")
        self.priv_tree.heading("size", text="Veličina")
        self.priv_tree.heading("timestamp", text="Kreiran")
        self.priv_tree.column("given_name", width=220)
        self.priv_tree.column("key_id", width=100)
        self.priv_tree.column("size", width=80, anchor="center")
        self.priv_tree.column("timestamp", width=140)
        self.priv_tree.pack(fill="both", expand=True, padx=5, pady=5)

        # --- Tab: public keyring ---
        pub_tab = ttk.Frame(notebook)
        notebook.add(pub_tab, text="Public keyring")

        self.pub_tree = ttk.Treeview(
            pub_tab, columns=("given_name", "key_id", "owner", "size", "pub_preview"),
            show="headings", height=8
        )
        self.pub_tree.heading("pub_preview", text="Public key (preview)")
        self.pub_tree.column("pub_preview", width=220)
        self.pub_tree.heading("given_name", text="Naziv")
        self.pub_tree.heading("key_id", text="Key ID")
        self.pub_tree.heading("owner", text="Vlasnik")
        self.pub_tree.heading("size", text="Veličina")
        self.pub_tree.column("given_name", width=200)
        self.pub_tree.column("key_id", width=100)
        self.pub_tree.column("owner", width=160)
        self.pub_tree.column("size", width=80, anchor="center")
        self.pub_tree.pack(fill="both", expand=True, padx=5, pady=5)

        self.priv_tree.bind("<Double-1>", self._on_priv_double_click)
        self.pub_tree.bind("<Double-1>", self._on_pub_double_click)
        self.refresh()

    def get_selected(self):
        """Vraca (kind, entry) za trenutno selektovan red u aktivnom tabu.
            kind je 'private' ili 'public'. (None, None) ako nista nije selektovano."""
        tab_idx = self.notebook.index(self.notebook.select())
        if tab_idx == 0:
            sel = self.priv_tree.selection()
            if sel:
                return "private", self._priv_entries.get(sel[0])
        else:
            sel = self.pub_tree.selection()
            if sel:
                return "public", self._pub_entries.get(sel[0])
        return None, None

    def refresh(self):
        self.priv_tree.delete(*self.priv_tree.get_children())
        self._priv_entries = {}
        for k in privateKeyring.getAll():
            preview = k.get_public_key_pem().splitlines()[1][:30] + "..."
            iid = self.priv_tree.insert("", "end", values=(
                k.given_name, k.key_id, f"{k.public_key.key_size} bita", k.timestamp, preview
            ))
            self._priv_entries[iid] = k

        self.pub_tree.delete(*self.pub_tree.get_children())
        self._pub_entries = {}
        for k in publicKeyring.getAll():
            preview = k.get_public_key_pem().splitlines()[1][:30] + "..."
            iid = self.pub_tree.insert("", "end", values=(
                k.given_name, k.key_id, k.user_id, f"{k.public_key.key_size} bita", preview
            ))
            self._pub_entries[iid] = k

    def _on_priv_double_click(self, event):
        iid = self.priv_tree.identify_row(event.y)
        entry = self._priv_entries.get(iid)
        if entry:
            KeyDetailsDialog(
                self, f"Ključ: {entry.given_name}",
                public_pem=entry.get_public_key_pem(),
                private_pem=entry.get_encrypted_private_key_pem(),
            )

    def _on_pub_double_click(self, event):
        iid = self.pub_tree.identify_row(event.y)
        entry = self._pub_entries.get(iid)
        if entry:
            KeyDetailsDialog(
                self, f"Ključ: {entry.given_name}",
                public_pem=entry.get_public_key_pem(),
            )

class KeyDetailsDialog(tk.Toplevel):
    def __init__(self, parent, title, public_pem, private_pem=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("560x480")

        tk.Label(self, text="Public key (PEM):", font=("TkDefaultFont", 9, "bold")).pack(
            anchor="w", padx=10, pady=(10, 0))
        pub_text = tk.Text(self, height=10, wrap="none")
        pub_text.insert("1.0", public_pem)
        pub_text.config(state="disabled")
        pub_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        if private_pem is not None:
            tk.Label(self, text="Encrypted private key (PEM):",
                     font=("TkDefaultFont", 9, "bold")).pack(anchor="w", padx=10)
            priv_text = tk.Text(self, height=10, wrap="none")
            priv_text.insert("1.0", private_pem)
            priv_text.config(state="disabled")
            priv_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        tk.Button(self, text="Zatvori", command=self.destroy).pack(pady=8)


# =====================================================================
# DIJALOG: SLANJE PORUKE
# =====================================================================

class SendMessageDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Slanje poruke")
        self.geometry("600x600")
        self.resizable(True, True)

        # --- Poruka koju kucamo ---
        tk.Label(self, text="Poruka:").pack(anchor="w", padx=10, pady=(10, 0))
        self.message_text = tk.Text(self, height=5)
        self.message_text.pack(fill="x", padx=10)
        self.message_text.insert("1.0", "Ovo je placeholder sadržaj poruke...")

        # --- Potpisivanje - bira se iz PRIVATE keyring-a ---
        tk.Label(self, text="Privatni ključ za potpisivanje (private keyring):").pack(
            anchor="w", padx=10, pady=(12, 0))
        self.priv_var = tk.StringVar()
        priv_values = [k["given_name"] for k in PRIVATE_KEYRING]
        self.priv_dropdown = ttk.Combobox(
            self, textvariable=self.priv_var, values=priv_values, state="readonly")
        self.priv_dropdown.pack(fill="x", padx=10)
        if priv_values:
            self.priv_dropdown.current(0)
        tk.Label(self, text="Lozinka za privatni ključ:").pack(
            anchor="w", padx=10, pady=(6, 0))
        self.priv_password_entry = tk.Entry(self, show="*")
        self.priv_password_entry.pack(fill="x", padx=10)

        # --- Enkripcija - bira se iz PUBLIC keyring-a ---
        tk.Label(self, text="Javni ključ primaoca (public keyring):").pack(
            anchor="w", padx=10, pady=(10, 0))
        self.pub_var = tk.StringVar()
        pub_values = [f'{k["given_name"]} ({k["owner"]})' for k in PUBLIC_KEYRING]
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
        if self.opt_sign.get() and not self.priv_password_entry.get():
            messagebox.showerror("Greška", "Unesite lozinku za privatni ključ.")
            return

        # U pravoj aplikaciji ovde ide poziv:
        # controller.send_message(text, priv_key, pub_key, opts, algo, out_path)
        password = self.priv_password_entry.get()
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
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Prijem poruke")
        self.geometry("460x420")
        self.resizable(False, False)
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
        # result = controller.receive_message(path)
        # (pretraga PRIVATE_KEYRING po key_id iz session key packeta,
        #  pretraga PUBLIC_KEYRING po key_id iz pgp_flow_utils packeta)
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        signer = PUBLIC_KEYRING[0]["owner"] if PUBLIC_KEYRING else "nepoznat"

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
            defaultextension=".bin",
            filetypes=[("Svi fajlovi", "*.*")]
        )
        if path:
            messagebox.showinfo("Sačuvano (placeholder)", f"Poruka bi bila sačuvana u:\n{path}")


# =====================================================================
# DIJALOG: UVOZ KLJUČA IZ .pem  (dodaje u PUBLIC_KEYRING, i opciono
# i u PRIVATE_KEYRING ako se uvozi ceo par)
# =====================================================================

from utils.pem_utils import import_public_key, import_private_key

class ImportKeyDialog(tk.Toplevel):
    def __init__(self, parent, on_imported):
        super().__init__(parent)
        self.title("Uvoz ključa")
        self.geometry("600x400")
        self.resizable(False, False)
        self.on_imported = on_imported

        tk.Label(self, text="Šta uvozite:").pack(anchor="w", padx=10, pady=(10, 0))
        self.import_type = tk.StringVar(value="public")
        tk.Radiobutton(self, text="Samo javni ključ", variable=self.import_type,
                        value="public", command=self.update_password_state).pack(
            anchor="w", padx=20)
        tk.Radiobutton(self, text="Ceo par (javni i privatni)", variable=self.import_type,
                        value="pair", command=self.update_password_state).pack(
            anchor="w", padx=20)

        tk.Label(self, text=".pem fajl za javni kljuc:").pack(anchor="w", padx=10, pady=(12, 0))
        file_frame = tk.Frame(self)
        file_frame.pack(fill="x", padx=10)
        self.pem_path_var = tk.StringVar()
        tk.Entry(file_frame, textvariable=self.pem_path_var,
                  state="readonly").pack(side="left", fill="x", expand=True)
        tk.Button(file_frame, text="Izaberi fajl...",
                   command=self.browse_pem).pack(side="left", padx=(5, 0))

        tk.Label(self, text=".pem fajl za privatni kljuc:").pack(anchor="w", padx=10, pady=(12, 0))
        file_frame_private = tk.Frame(self)
        file_frame_private.pack(fill="x", padx=10)
        self.pem_private_path_var = tk.StringVar()
        tk.Entry(file_frame_private, textvariable=self.pem_private_path_var,
                 state="readonly").pack(side="left", fill="x", expand=True)
        tk.Button(file_frame_private, text="Izaberi fajl...",
                  command=self.browse_pem2).pack(side="left", padx=(5, 0))

        tk.Label(self, text="Naziv za prikaz (given name):").pack(
            anchor="w", padx=10, pady=(12, 0))
        self.given_name_var = tk.StringVar()
        tk.Entry(self, textvariable=self.given_name_var).pack(fill="x", padx=10)

        tk.Label(self, text="Vlasnik (email):").pack(
            anchor="w", padx=10, pady=(10, 0))
        self.owner_var = tk.StringVar()
        tk.Entry(self, textvariable=self.owner_var).pack(fill="x", padx=10)

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

    def browse_pem2(self):
        path = filedialog.askopenfilename(
            title="Izaberite .pem fajl",
            filetypes=[("PEM fajlovi", "*.pem"), ("Svi fajlovi", "*.*")]
        )
        if path:
            self.pem_private_path_var.set(path)

    def do_import(self):
        if not self.pem_path_var.get():
            messagebox.showerror("Greška", "Izaberite .pem fajl.")
            return
        if not self.given_name_var.get() or not self.owner_var.get():
            messagebox.showerror("Greška", "Unesite naziv i vlasnika ključa.")
            return
        if self.import_type.get() == "pair" and not self.password_entry.get():
            messagebox.showerror("Greška", "Unesite lozinku privatnog ključa.")
            return

        public_key = import_public_key(self.pem_path_var.get())
        #key_id = new_key_id()
        given_name = self.given_name_var.get()
        email = self.owner_var.get()
        publicKeyring.add(public_key, email, given_name)
        password = self.password_entry.get()

        # Javni deo uvek ide u PUBLIC_KEYRING
        # PUBLIC_KEYRING.append({
        #     "key_id": key_id,
        #     "given_name": given_name,
        #     "owner": owner,
        #     "email": "",
        #     "key_size": 2048,
        #     "public_key_pem": f"-----BEGIN PUBLIC KEY-----\n...(učitano iz {self.pem_path_var.get()})...\n-----END PUBLIC KEY-----\n",
        # })

        # Ako se uvozi ceo par, privatni deo ide i u PRIVATE_KEYRING
        if self.import_type.get() == "pair":
            private_key = import_private_key(self.pem_private_path_var.get(), password)
            privateKeyring.add(email, public_key, private_key, password, given_name)
            # PRIVATE_KEYRING.append({
            #     "key_id": key_id,
            #     "given_name": given_name,
            #     "name": owner,
            #     "email": "",
            #     "key_size": 2048,
            #     "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
            #     "public_key_pem": PUBLIC_KEYRING[-1]["public_key_pem"],
            #     "private_key_pem": f"-----BEGIN ENCRYPTED PRIVATE KEY-----\n...(učitano, zaštićeno unetom lozinkom)...\n-----END ENCRYPTED PRIVATE KEY-----\n",
            # })

        kind = "ceo par ključeva" if self.import_type.get() == "pair" else "javni ključ"
        messagebox.showinfo(
            "Uvezeno (placeholder)",
            f"Uvezen {kind} iz:\n{self.pem_path_var.get()}\n\nNaziv: {given_name}\n"
        )
        self.on_imported()
        self.destroy()


# =====================================================================
# DIJALOG: GENERISANJE NOVOG PARA KLJUČEVA (dodaje u OBA keyring-a)
# =====================================================================

class GenerateKeyDialog(tk.Toplevel):
    def __init__(self, parent, on_generated):
        super().__init__(parent)
        self.title("Generisanje novog para ključeva")
        self.geometry("500x500")
        self.resizable(True, True)
        self.on_generated = on_generated

        tk.Label(self, text="Ime i prezime:").pack(anchor="w", padx=10, pady=(10, 0))
        self.name_entry = tk.Entry(self)
        self.name_entry.pack(fill="x", padx=10)

        tk.Label(self, text="Email:").pack(anchor="w", padx=10, pady=(10, 0))
        self.email_entry = tk.Entry(self)
        self.email_entry.pack(fill="x", padx=10)

        tk.Label(self, text="Naziv za prikaz (given name):").pack(
            anchor="w", padx=10, pady=(10, 0))
        self.given_name_entry = tk.Entry(self)
        self.given_name_entry.pack(fill="x", padx=10)

        tk.Label(self, text="Veličina ključa:").pack(anchor="w", padx=10, pady=(10, 0))
        self.size_var = tk.StringVar(value="2048")
        tk.Radiobutton(self, text="1024 bita", variable=self.size_var, value=1024).pack(
            anchor="w", padx=20)
        tk.Radiobutton(self, text="2048 bita", variable=self.size_var, value=2048).pack(
            anchor="w", padx=20)

        tk.Label(self, text="Lozinka za privatni ključ:").pack(
            anchor="w", padx=10, pady=(10, 0))
        self.pass_entry = tk.Entry(self, show="*")
        self.pass_entry.pack(fill="x", padx=10)

        tk.Button(self, text="Generiši", command=self.do_generate,
                    bg="#2e7d32", fg="white").pack(pady=16)

    def do_generate(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        given_name = self.given_name_entry.get().strip() or f"Ključ ({self.size_var.get()})"

        if not name or not email or not self.pass_entry.get():
            messagebox.showerror("Greška", "Popunite ime, email i lozinku.")
            return

        # key_id = new_key_id()
        timestamp = datetime.datetime.now().isoformat(timespec="seconds")
        size = int(self.size_var.get())
        password = self.pass_entry.get().strip()

        public_pem = f"-----BEGIN PUBLIC KEY-----\n...(novogenerisan, {size} bita)...\n-----END PUBLIC KEY-----\n"
        private_pem = "-----BEGIN ENCRYPTED PRIVATE KEY-----\n...(zaštićeno unetom lozinkom)...\n-----END ENCRYPTED PRIVATE KEY-----\n"

        '''PRIVATE_KEYRING.append({
            "key_id": key_id, "given_name": given_name, "name": name, "email": email,
            "key_size": size, "timestamp": timestamp,
            "public_key_pem": public_pem, "private_key_pem": private_pem,
        })
        PUBLIC_KEYRING.append({
            "key_id": key_id, "given_name": given_name, "owner": name, "email": email,
            "key_size": size, "public_key_pem": public_pem,
        })'''

        generateKeys(size, password, email, given_name, publicKeyring, privateKeyring)

        messagebox.showinfo(
            "Generisano (placeholder)",
            f"Novi par ključeva ({size} bita)\nVlasnik: {name} <{email}>"
        )
        self.on_generated()
        self.destroy()


# =====================================================================
# GLAVNI PROZOR
# =====================================================================

from utils.pem_utils import export_public_key, export_private_key

class ExportKeyDialog(tk.Toplevel):
    """
    kind: "private" ili "public" - iz kog keyring-a je ključ selektovan.
    entry: PrivateKeyringEntry ili PublicKeyEntry.
    """
    def __init__(self, parent, kind, entry):
        super().__init__(parent)
        self.title("Izvoz ključa")
        self.geometry("460x320")
        self.resizable(False, False)
        self.kind = kind
        self.entry = entry

        tk.Label(self, text=f"Ključ: {entry.given_name}  (Key ID: {entry.key_id})").pack(
            anchor="w", padx=10, pady=(10, 0))

        tk.Label(self, text="Šta izvozite:").pack(anchor="w", padx=10, pady=(12, 0))
        self.export_type = tk.StringVar(value="public")
        tk.Radiobutton(self, text="Samo javni ključ", variable=self.export_type,
                        value="public").pack(anchor="w", padx=20)

        both_state = "normal" if kind == "private" else "disabled"
        tk.Radiobutton(self, text="Javni i privatni ključ (ceo par)", variable=self.export_type,
                        value="pair", state=both_state).pack(anchor="w", padx=20)

        if kind == "public":
            tk.Label(self, text="(Ključ je iz public keyring-a - nema privatnog dela.)",
                      fg="gray").pack(anchor="w", padx=20, pady=(0, 5))

        tk.Label(self, text="Folder za izvoz:").pack(anchor="w", padx=10, pady=(12, 0))
        folder_frame = tk.Frame(self)
        folder_frame.pack(fill="x", padx=10)
        self.folder_var = tk.StringVar()
        tk.Entry(folder_frame, textvariable=self.folder_var, state="readonly").pack(
            side="left", fill="x", expand=True)
        tk.Button(folder_frame, text="Izaberi folder...",
                   command=self.browse_folder).pack(side="left", padx=(5, 0))

        tk.Label(self, text="Naziv fajla (bez ekstenzije):").pack(anchor="w", padx=10, pady=(12, 0))
        self.filename_var = tk.StringVar(value=entry.given_name.replace(" ", "_"))
        tk.Entry(self, textvariable=self.filename_var).pack(fill="x", padx=10)

        tk.Button(self, text="Izvezi", command=self.do_export,
                    bg="#2e7d32", fg="white").pack(pady=16)

    def browse_folder(self):
        path = filedialog.askdirectory(title="Izaberite folder za izvoz")
        if path:
            self.folder_var.set(path)

    def do_export(self):
        folder = self.folder_var.get()
        filename = self.filename_var.get().strip()

        if not folder:
            messagebox.showerror("Greška", "Izaberite folder za izvoz.")
            return
        if not filename:
            messagebox.showerror("Greška", "Unesite naziv fajla.")
            return

        public_path = os.path.join(folder, f"{filename}_public.pem")
        try:
            export_public_key(self.entry.public_key, public_path)
        except OSError as e:
            messagebox.showerror("Greška", f"Ne mogu da sačuvam javni ključ:\n{e}")
            return

        written = [public_path]

        if self.export_type.get() == "pair":
            if self.kind != "private":
                messagebox.showerror("Greška", "Ovaj ključ nema privatni deo za izvoz.")
                return
            private_path = os.path.join(folder, f"{filename}_private.pem")
            try:
                export_private_key(self.entry.encrypted_private_key, private_path)
            except OSError as e:
                messagebox.showerror("Greška", f"Ne mogu da sačuvam privatni ključ:\n{e}")
                return
            written.append(private_path)

        messagebox.showinfo("Izvezeno", "Sačuvano:\n" + "\n".join(written))
        self.destroy()

import traceback

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PGP alat - demo (private / public keyring)")
        self.geometry("640x520")

        tk.Label(
            self, text="Private keyring i Public keyring ove instalacije:",
            font=("TkDefaultFont", 10, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 0))

        # --- Keyring prikaz ---
        self.keyring_frame = KeyringFrame(self)
        self.keyring_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        # --- Dugmici za akcije ---
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))

        tk.Button(btn_frame, text="Generiši novi par ključeva",
                   command=self.open_generate_dialog).pack(side="left", padx=(0, 5))
        tk.Button(btn_frame, text="Uvezi iz .pem",
                   command=self.open_import_dialog).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Izvezi ključeve",
                  command=self.open_export_dialog).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Pošalji poruku",
                   command=self.open_send_dialog, bg="#1565c0", fg="white").pack(
            side="right", padx=5)
        tk.Button(btn_frame, text="Primi poruku",
                   command=self.open_receive_dialog, bg="#1565c0", fg="white").pack(
            side="right", padx=(5, 0))
        self.report_callback_exception = self.handle_exception

    def open_send_dialog(self):
        SendMessageDialog(self)

    def open_receive_dialog(self):
        ReceiveMessageDialog(self)

    def open_import_dialog(self):
        ImportKeyDialog(self, on_imported=self.keyring_frame.refresh)

    def open_export_dialog(self):
        kind, entry = self.keyring_frame.get_selected()
        if entry is None:
            messagebox.showerror(
                "Greška",
                "Izaberite ključ klikom na red u tabeli (private ili public keyring) koji želite da izvezete."
            )
            return
        ExportKeyDialog(self, kind, entry)

    def open_generate_dialog(self):
        GenerateKeyDialog(self, on_generated=self.keyring_frame.refresh)

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        error_text = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        print(error_text)  # i dalje ispiši u konzolu, korisno za debug
        messagebox.showerror("Greška", f"{exc_type.__name__}: {exc_value}")


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
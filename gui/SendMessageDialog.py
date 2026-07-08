from pgp_flow.send_flow import send_message
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from app_core import publicKeyring, privateKeyring, save_keyrings, delete_key

class SendMessageDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Slanje poruke")
        self.geometry("600x600")
        self.resizable(True, True)

        # Poruka koju kucamo
        tk.Label(self, text="Poruka:").pack(anchor="w", padx=10, pady=(10, 0))
        self.message_text = tk.Text(self, height=5)
        self.message_text.pack(fill="x", padx=10)
        self.message_text.insert("1.0", "Ovo je placeholder sadržaj poruke...")

        # Potpisivanje - bira se iz privatnog keyring-a
        tk.Label(self, text="Privatni ključ za potpisivanje (private keyring):").pack(
            anchor="w", padx=10, pady=(12, 0))
        self.priv_var = tk.StringVar()
        priv_values = [k.given_name for k in privateKeyring.getAll()]
        self.priv_entries = list(privateKeyring.getAll())
        self.priv_dropdown = ttk.Combobox(
            self, textvariable=self.priv_var, values=priv_values, state="readonly")
        self.priv_dropdown.pack(fill="x", padx=10)
        if priv_values:
            self.priv_dropdown.current(0)
        tk.Label(self, text="Lozinka za privatni ključ:").pack(
            anchor="w", padx=10, pady=(6, 0))
        self.priv_password_entry = tk.Entry(self, show="*")
        self.priv_password_entry.pack(fill="x", padx=10)

        # Enkripcija - bira se iz PUBLIC keyring-a
        tk.Label(self, text="Javni ključ primaoca (public keyring):").pack(
            anchor="w", padx=10, pady=(10, 0))
        self.pub_var = tk.StringVar()
        pub_values = [f'{k.given_name} ({k.user_id})' for k in publicKeyring.getAll()]
        self.public_entries = list(publicKeyring.getAll())
        self.pub_dropdown = ttk.Combobox(
            self, textvariable=self.pub_var, values=pub_values, state="readonly")
        self.pub_dropdown.pack(fill="x", padx=10)
        if pub_values:
            self.pub_dropdown.current(0)

        # Checkboxovi
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

        # Radio dugmici za algoritam
        algo_frame = tk.LabelFrame(self, text="Simetrični algoritam")
        algo_frame.pack(fill="x", padx=10, pady=(10, 0))

        self.algo_var = tk.StringVar(value="AES128")
        tk.Radiobutton(algo_frame, text="AES128", variable=self.algo_var,
                        value="AES128").pack(anchor="w", padx=10)
        tk.Radiobutton(algo_frame, text="TripleDES", variable=self.algo_var,
                        value="3DES").pack(anchor="w", padx=10)

        # Izlazni fajl
        tk.Label(self, text="Sačuvaj kao:").pack(anchor="w", padx=10, pady=(12, 0))
        out_frame = tk.Frame(self)
        out_frame.pack(fill="x", padx=10)
        self.out_path_var = tk.StringVar()
        tk.Entry(out_frame, textvariable=self.out_path_var,
                  state="readonly").pack(side="left", fill="x", expand=True)
        tk.Button(out_frame, text="Sačuvaj kao...",
                   command=self.browse_output).pack(side="left", padx=(5, 0))

        # Dugme za slanje
        tk.Button(self, text="Pošalji poruku", command=self.do_send,
                    bg="#2e7d32", fg="white").pack(pady=16)

    def get_selected_priv_entry(self):
        id = self.priv_dropdown.current()
        if id == -1:
            return None
        return self.priv_entries[id]

    def get_selected_public_entry(self):
        id = self.pub_dropdown.current()
        if id == -1:
            return None
        return self.public_entries[id]

    def browse_output(self):
        path = filedialog.asksaveasfilename(
            title="Sačuvaj poruku kao",
            defaultextension=".pgp",
            filetypes=[("PGP fajlovi", "*.pgp"), ("Svi fajlovi", "*.*")]
        )
        if path:
            self.out_path_var.set(path)

    def do_send(self):
        message = self.message_text.get("1.0", "end-1c")
        if not message:
            messagebox.showerror("Greška", "Morate uneti poruku.")
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

        password = self.priv_password_entry.get()
        publicEntry = self.get_selected_public_entry()
        privateEntry = self.get_selected_priv_entry()
        privateKey = privateEntry.get_private_key(password) if (privateEntry and self.opt_sign.get()) else None
        sign_key_id = privateEntry.key_id if privateEntry else None
        encrypt_key_id = publicEntry.key_id if publicEntry else None
        publicKey = publicEntry.public_key if publicEntry else None
        options = dict()
        options["signed"] = self.opt_sign.get()
        options["compressed"] = self.opt_compress.get()
        options["encrypted"] = self.opt_encrypt.get()
        options["radix"] = self.opt_radix64.get()
        algorithm = self.algo_var.get().strip()
        out_path = self.out_path_var.get().strip()
        send_message(out_path, message, options, algorithm, privateKey, publicKey, sign_key_id, encrypt_key_id)
        self.destroy()

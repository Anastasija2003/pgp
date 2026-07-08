from utils.pem_utils import import_public_key, import_private_key
from pgp_flow.send_flow import send_message
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from app_core import publicKeyring, privateKeyring, save_keyrings, delete_key
import datetime
from utils.rsa_generation import generateKeys

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

        generateKeys(size, password, email, given_name, publicKeyring, privateKeyring)

        messagebox.showinfo(
            "Generisano (placeholder)",
            f"Novi par ključeva ({size} bita)\nVlasnik: {name} <{email}>"
        )
        self.on_generated()
        self.destroy()
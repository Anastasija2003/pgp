from utils.pem_utils import import_public_key, import_private_key
from pgp_flow.send_flow import send_message
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from app_core import publicKeyring, privateKeyring, save_keyrings, delete_key

class ImportKeyDialog(tk.Toplevel):
    def __init__(self, parent, on_imported):
        super().__init__(parent)
        self.title("Uvoz ključa")
        self.geometry("600x400")
        self.resizable(True, True)
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
        given_name = self.given_name_var.get()
        email = self.owner_var.get()
        publicKeyring.add(public_key, email, given_name)
        password = self.password_entry.get()

        # Javni deo uvek ide u publicKeyring

        # Ako se uvozi ceo par, privatni deo ide i u privateKeyring
        if self.import_type.get() == "pair":
            private_key = import_private_key(self.pem_private_path_var.get(), password)
            privateKeyring.add(email, public_key, private_key, password, given_name)

        kind = "ceo par ključeva" if self.import_type.get() == "pair" else "javni ključ"
        messagebox.showinfo(
            "Uvezeno (placeholder)",
            f"Uvezen {kind} iz:\n{self.pem_path_var.get()}\n\nNaziv: {given_name}\n"
        )
        self.on_imported()
        self.destroy()
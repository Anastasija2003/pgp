from utils.pem_utils import export_public_key, export_private_key
from utils.pem_utils import import_public_key, import_private_key
from pgp_flow.send_flow import send_message
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from app_core import publicKeyring, privateKeyring, save_keyrings, delete_key
import os

class ExportKeyDialog(tk.Toplevel):
    """
    kind: "private" ili "public" - iz kog keyring-a je ključ selektovan.
    entry: PrivateKeyringEntry ili PublicKeyEntry.
    """
    def __init__(self, parent, kind, entry):
        super().__init__(parent)
        self.title("Izvoz ključa")
        self.geometry("460x320")
        self.resizable(True, True)
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
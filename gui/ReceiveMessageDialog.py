from pgp_flow.send_flow import send_message
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from app_core import publicKeyring, privateKeyring, save_keyrings, delete_key
from pgp_flow.receive_flow import start_receive, finish_receive, UnknownKeyError
import datetime

class ReceiveMessageDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Prijem poruke")
        self.geometry("460x420")
        self.resizable(True, True)
        self.loaded = False
        self.message_bytes = None

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
        with open(path, "rb") as f:
            file_bytes = f.read()

        try:
            context = start_receive(file_bytes, privateKeyring)
        except UnknownKeyError:
            messagebox.showerror("Greška", "Ova poruka nije namenjena nijednom od vaših ključeva.")
            return
        except Exception as e:
            messagebox.showerror("Greška", f"Fajl nije validna PGP poruka:\n{e}")
            return

        password = None
        if context.needs_password():
            password = simpledialog.askstring(
                "Lozinka",
                f"Unesite lozinku za ključ: {context.private_key_entry.given_name}",
                show="*",
                parent=self,
            )
            if password is None:
                return

        try:
            filename, message_bytes, signer_entry, signature_valid = finish_receive(
                context, password, publicKeyring
            )
        except ValueError:
            messagebox.showerror("Greška", "Pogrešna lozinka.")
            return
        except UnknownKeyError:
            messagebox.showerror("Greška", "Potpisnik poruke nije poznat (nema ga u public keyring-u).")
            return
        except Exception as e:
            messagebox.showerror("Greška", f"Dekripcija/verifikacija nije uspela:\n{e}")
            return

        self.show_result(filename, message_bytes, signer_entry, signature_valid)

    def show_result(self, filename, message_bytes, signer_entry, signature_valid):
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        if signer_entry is not None:
            if signature_valid:
                tk.Label(self.result_frame, text="✓ Potpis uspešno verifikovan",
                          fg="#2e7d32").pack(anchor="w", padx=10, pady=(10, 2))
            else:
                tk.Label(self.result_frame, text="✗ Potpis NIJE validan",
                          fg="#c62828").pack(anchor="w", padx=10, pady=(10, 2))
            tk.Label(self.result_frame,
                      text=f"Autor potpisa: {signer_entry.given_name} ({signer_entry.user_id})").pack(
                anchor="w", padx=10)
        else:
            tk.Label(self.result_frame, text="(poruka nije potpisana)", fg="gray").pack(
                anchor="w", padx=10, pady=(10, 2))

        tk.Label(self.result_frame, text=f"Fajl: {filename}").pack(anchor="w", padx=10)
        tk.Label(self.result_frame,
                  text=f"Vreme prijema: {datetime.datetime.now():%Y-%m-%d %H:%M}").pack(
            anchor="w", padx=10, pady=(0, 10))

        self.message_bytes = message_bytes
        self.loaded = True
        self.save_btn.config(state="normal")

    def save_decrypted(self):
        path = filedialog.asksaveasfilename(
            title="Sačuvaj originalnu poruku",
            defaultextension=".txt",
            filetypes=[("Tekstualni fajlovi", "*.txt"), ("Svi fajlovi", "*.*")]
        )
        if path:
            with open(path, "wb") as f:
                f.write(self.message_bytes)
            messagebox.showinfo("Sačuvano", f"Poruka je sačuvana u:\n{path}")
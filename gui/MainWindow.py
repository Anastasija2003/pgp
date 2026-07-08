import traceback
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from app_core import publicKeyring, privateKeyring, save_keyrings, delete_key
from gui.KeyringFrame import KeyringFrame
from gui.SendMessageDialog import SendMessageDialog
from gui.ReceiveMessageDialog import ReceiveMessageDialog
from gui.ImportKeyDialog import ImportKeyDialog
from gui.ExportKeyDialog import ExportKeyDialog
from gui.GenerateKeyDialog import GenerateKeyDialog

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PGP alat")
        self.geometry("640x520")

        tk.Label(
            self, text="Private keyring i Public keyring ove instalacije:",
            font=("TkDefaultFont", 10, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 0))

        # Keyring prikaz
        self.keyring_frame = KeyringFrame(self)
        self.keyring_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        # Dugmici za akcije
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))

        tk.Button(btn_frame, text="Generiši novi par ključeva",
                   command=self.open_generate_dialog).pack(side="left", padx=(0, 5))
        tk.Button(btn_frame, text="Uvezi iz .pem",
                   command=self.open_import_dialog).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Izvezi ključeve",
                  command=self.open_export_dialog).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Obriši ključ",
                  command=self.delete_selected_key).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Pošalji poruku",
                   command=self.open_send_dialog, bg="#1565c0", fg="white").pack(
            side="right", padx=5)
        tk.Button(btn_frame, text="Primi poruku",
                   command=self.open_receive_dialog, bg="#1565c0", fg="white").pack(
            side="right", padx=(5, 0))
        self.report_callback_exception = self.handle_exception
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        save_keyrings()
        self.destroy()

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

    def delete_selected_key(self):
        kind, entry = self.keyring_frame.get_selected()
        if entry is None:
            messagebox.showerror(
                "Greška",
                "Izaberite ključ klikom na red u tabeli (private ili public keyring) koji želite da obrišete."
            )
            return

        confirmed = messagebox.askyesno(
            "Potvrda brisanja",
            f"Da li ste sigurni da želite da obrišete ključ '{entry.given_name}'?\n"
            "Ova akcija je nepovratna."
        )
        if not confirmed:
            return

        delete_key(entry.key_id)
        self.keyring_frame.refresh()

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        error_text = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        print(error_text)
        messagebox.showerror("Greška", f"{exc_type.__name__}: {exc_value}")
import tkinter as tk

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

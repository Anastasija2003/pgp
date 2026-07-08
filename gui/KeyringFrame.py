import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from app_core import publicKeyring, privateKeyring, save_keyrings, delete_key
from gui.KeyDetailsDialog import KeyDetailsDialog


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
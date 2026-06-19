# Tkinter GUI

"""Tkinter-based GUI application."""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import getpass
import os
from vault import auth, file_manager


class VaultGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Secure File Vault")
        self.geometry("700x500")
        
        self.key = None  #AES key after authentication
        
        # Setup UI
        self._setup_auth_frame()
        self._setup_main_frame()
        
        # Try to auto-open vault
        try:
            self.key = auth.open_vault()
            self._show_main_view()
        except ValueError:
            self._show_auth_view()
    
    def _setup_auth_frame(self):
        """Setup authentication frame."""
        self.auth_frame = tk.Frame(self)
        
        tk.Label(
            self.auth_frame,
            text="Secure File Vault",
            font=("Helvetica", 24, "bold")
        ).pack(pady=40)
        
        tk.Label(
            self.auth_frame,
            text="Enter master password to access vault",
            font=("Helvetica", 12)
        ).pack(pady=10)
        
        self.password_entry = tk.Entry(
            self.auth_frame,
            show="*",
            font=("Helvetica", 14),
            width=30
        )
        self.password_entry.pack(pady=15)
        self.password_entry.bind("<Return>", lambda e: self._authenticate())
        
        tk.Button(
            self.auth_frame,
            text="Open Vault",
            font=("Helvetica", 12),
            command=self._authenticate,
            bg="#4CAF50",
            fg="white"
        ).pack(pady=10)
        
        tk.Button(
            self.auth_frame,
            text="Initialize New Vault",
            font=("Helvetica", 10),
            command=self._init_vault,
            bg="#2196F3",
            fg="white"
        ).pack(pady=5)
    
    def _setup_main_frame(self):
        """Setup main vault frame."""
        self.main_frame = tk.Frame(self)
        
        # Title
        tk.Label(
            self.main_frame,
            text="My Vault",
            font=("Helvetica", 18, "bold")
        ).pack(pady=10)
        
        # File list (Treeview)
        list_frame = tk.Frame(self.main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("id", "filename", "size", "created")
        self.file_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        self.file_tree.heading("id", text="ID")
        self.file_tree.heading("filename", text="Filename")
        self.file_tree.heading("size", text="Size")
        self.file_tree.heading("created", text="Created")
        
        self.file_tree.column("id", width=50)
        self.file_tree.column("filename", width=300)
        self.file_tree.column("size", width=100)
        self.file_tree.column("created", width=150)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Search bar
        search_frame = tk.Frame(self.main_frame)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        
        self.search_entry = tk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_entry.bind("<Return>", lambda e: self._search_files())
        
        tk.Button(
            search_frame,
            text="Search",
            command=self._search_files
        ).pack(side=tk.LEFT)
        
        # Buttons
        btn_frame = tk.Frame(self.main_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            btn_frame,
            text="➕ Add File",
            command=self._add_file,
            bg="#4CAF50",
            fg="white",
            width=12
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            btn_frame,
            text="🔓 Decrypt",
            command=self._decrypt_file,
            bg="#2196F3",
            fg="white",
            width=12
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            btn_frame,
            text="🗑️ Remove",
            command=self._remove_file,
            bg="#f44336",
            fg="white",
            width=12
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            btn_frame,
            text="📋 Logs",
            command=self._show_logs,
            width=12
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            btn_frame,
            text="✖ Close",
            command=self.close,
            width=12
        ).pack(side=tk.RIGHT, padx=2)
    
    def _show_auth_view(self):
        """Show authentication view."""
        self.auth_frame.pack(fill=tk.BOTH, expand=True)
        self.main_frame.pack_forget()
        self.password_entry.focus()
    
    def _show_main_view(self):
        """Show main vault view."""
        self.auth_frame.pack_forget()
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self._refresh_file_list()
    
    def _authenticate(self):
        """Authenticate user."""
        password = self.password_entry.get()
        
        if not password:
            messagebox.showerror("Error", "Password is required")
            return
        
        try:
            self.key = auth.open_vault()
            self.password_entry.delete(0, tk.END)
            self._show_main_view()
        except ValueError as e:
            messagebox.showerror("Authentication Failed", str(e))
    
    def _init_vault(self):
        """Initialize new vault."""
        if messagebox.askyesno("Initialize Vault", "Create a new vault? (Existing vault will be overwritten)"):
            try:
                auth.init_vault()
                messagebox.showinfo("Success", "Vault initialized!")
                self.key = auth.open_vault()
                self._show_main_view()
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def _refresh_file_list(self):
        """Refresh file list in Treeview."""
        # Clear existing items
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # Add files
        files = file_manager.list_files()
        for f in files:
            size_kb = f['filesize'] / 1024 if f['filesize'] else 0
            self.file_tree.insert("", tk.END, values=(
                f['id'],
                f['filename'],
                f"{size_kb:.1f} KB",
                f['created_at']
            ))
    
    def _add_file(self):
        """Add file to vault."""
        path = filedialog.askopenfilename(title="Select file to encrypt")
        
        if not path:
            return
        
        try:
            file_id = file_manager.add_file(path, self.key)
            messagebox.showinfo("Success", f"File encrypted and added (ID: {file_id})")
            self._refresh_file_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _decrypt_file(self):
        """Decrypt selected file."""
        selected = self.file_tree.selection()
        
        if not selected:
            messagebox.showwarning("Warning", "Select a file to decrypt")
            return
        
        item = self.file_tree.item(selected[0])
        filename = item['values'][1]
        
        output_dir = filedialog.askdirectory(title="Select output directory")
        
        if not output_dir:
            return
        
        try:
            output_path = file_manager.decrypt_file(filename, self.key, output_dir)
            messagebox.showinfo("Success", f"Decrypted to:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _remove_file(self):
        """Remove selected file."""
        selected = self.file_tree.selection()
        
        if not selected:
            messagebox.showwarning("Warning", "Select a file to remove")
            return
        
        item = self.file_tree.item(selected[0])
        filename = item['values'][1]
        
        if not messagebox.askyesno("Remove File", f"Delete '{filename}' from vault?"):
            return
        
        try:
            file_manager.remove_file(filename, self.key)
            messagebox.showinfo("Success", f"'{filename}' removed")
            self._refresh_file_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _search_files(self):
        """Search files."""
        keyword = self.search_entry.get()
        
        if not keyword:
            self._refresh_file_list()
            return
        
        files = file_manager.search_files(keyword)
        
        # Clear and show results
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        for f in files:
            size_kb = f['filesize'] / 1024 if f['filesize'] else 0
            self.file_tree.insert("", tk.END, values=(
                f['id'],
                f['filename'],
                f"{size_kb:.1f} KB",
                f['created_at']
            ))
    
    def _show_logs(self):
        """Show activity logs."""
        from vault import db
        logs = db.get_logs(20)
        
        if not logs:
            messagebox.showinfo("Logs", "No activity logs.")
            return
        
        log_text = "\n".join([
            f"[{log['timestamp']}] {log['action']} (ID: {log['file_id'] or '-'})"
            for log in logs
        ])
        
        messagebox.showinfo("Recent Activity", log_text)


def main():
    """GUI entry point."""
    app = VaultGUI()
    app.mainloop()


if __name__ == '__main__':
    main()

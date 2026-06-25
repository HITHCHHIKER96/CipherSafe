import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from vault import auth, file_manager, db

class VaultGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Secure File Vault")
        self.geometry("600x400")
        self.key = None

        self.lbl = tk.Label(self, text="Secure File Vault", font=("Arial", 18, "bold"))
        self.lbl.pack(pady=10)

        self.btn_init = tk.Button(self, text="Initialize Vault", command=self.init_vault)
        self.btn_init.pack(pady=5)

        self.btn_open = tk.Button(self, text="Open Vault", command=self.open_vault)
        self.btn_open.pack(pady=5)

        self.btn_add = tk.Button(self, text="Add File", command=self.add_file, state="disabled")
        self.btn_add.pack(pady=5)

        self.btn_list = tk.Button(self, text="List Files", command=self.list_files, state="disabled")
        self.btn_list.pack(pady=5)

        self.txt = tk.Text(self, height=10, width=70)
        self.txt.pack(pady=10)

    def init_vault(self):
        try:
            self.key = auth.init_vault()
            self.btn_add.config(state="normal")
            self.btn_list.config(state="normal")
            messagebox.showinfo("Success", "Vault initialized")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def open_vault(self):
        try:
            self.key = auth.open_vault()
            self.btn_add.config(state="normal")
            self.btn_list.config(state="normal")
            messagebox.showinfo("Success", "Vault opened")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_file(self):
        if not self.key:
            messagebox.showwarning("Warning", "Open vault first")
            return
        path = filedialog.askopenfilename()
        if path:
            try:
                file_manager.add_file(path, self.key)
                messagebox.showinfo("Success", "File added")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def list_files(self):
        self.txt.delete("1.0", tk.END)
        rows = file_manager.list_files()
        for r in rows:
            self.txt.insert(tk.END, f"{r['id']}  {r['filename']}  {r['created_at']}\n")

def main():
    app = VaultGUI()
    app.mainloop()
import os
import sys
import shutil
import string
import threading
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox

APP_NAME = "ML Installer"

def resource_path(name: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / name

def find_minecraft_content():
    # Search all mounted drive letters for the exact XboxGames installation path.
    for letter in string.ascii_uppercase:
        root = Path(f"{letter}:\\")
        candidate = root / "XboxGames" / "Minecraft for Windows" / "Content"
        try:
            if candidate.is_dir():
                return candidate
        except OSError:
            pass
    return None

def safe_copy(source: Path, destination: Path):
    if not source.is_file():
        raise FileNotFoundError(f"Не найден файл программы: {source.name}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = destination.with_name(destination.name + f".backup-{stamp}")
        shutil.copy2(destination, backup)
    shutil.copy2(source, destination)
    if not destination.is_file() or destination.stat().st_size != source.stat().st_size:
        raise OSError(f"Проверка копирования не пройдена: {destination}")

class Installer:
    def __init__(self, root):
        self.root = root
        root.title("ML — Установщик")
        root.geometry("560x410")
        root.minsize(500, 380)
        root.configure(bg="#101010")
        root.option_add("*Font", ("Segoe UI", 10))

        self.title = tk.Label(root, text="ML INSTALLER", bg="#101010", fg="white",
                              font=("Segoe UI", 22, "bold"))
        self.title.pack(pady=(24, 4))
        tk.Label(root, text="Автоматическая установка файлов Minecraft Bedrock",
                 bg="#101010", fg="#bdbdbd").pack(pady=(0, 18))

        self.path_var = tk.StringVar(value="Поиск Minecraft...")
        tk.Label(root, textvariable=self.path_var, bg="#1c1c1c", fg="#e8e8e8",
                 wraplength=500, justify="left", padx=12, pady=12).pack(fill="x", padx=24)

        tk.Button(root, text="Выбрать папку Content вручную", command=self.choose_folder,
                  bg="#303030", fg="white", activebackground="#454545",
                  activeforeground="white", relief="flat", padx=12, pady=9).pack(pady=12)

        self.install_btn = tk.Button(root, text="УСТАНОВИТЬ", command=self.install,
                                     bg="white", fg="black", activebackground="#dddddd",
                                     relief="flat", font=("Segoe UI", 12, "bold"),
                                     padx=28, pady=12)
        self.install_btn.pack(pady=8)

        self.status = tk.Label(root, text="Готово к установке", bg="#101010",
                               fg="#9e9e9e", wraplength=500)
        self.status.pack(pady=12)
        tk.Label(root, text="При замене существующих файлов создаётся резервная копия.",
                 bg="#101010", fg="#777777", font=("Segoe UI", 8)).pack(side="bottom", pady=12)

        self.content_dir = find_minecraft_content()
        self.refresh_path()

    def refresh_path(self):
        if self.content_dir:
            self.path_var.set(f"Папка Minecraft: {self.content_dir}")
        else:
            self.path_var.set("Папка Minecraft не найдена. Выберите папку Content вручную.")

    def choose_folder(self):
        selected = filedialog.askdirectory(title="Выберите папку Minecraft for Windows\\Content")
        if selected:
            p = Path(selected)
            if p.name.lower() != "content" or not (p.parent / "Minecraft for Windows").exists():
                if not messagebox.askyesno("Проверка пути", "Выбранная папка не похожа на Minecraft\\Content. Использовать её?"):
                    return
            self.content_dir = p
            self.refresh_path()

    def install(self):
        if not self.content_dir or not self.content_dir.is_dir():
            messagebox.showwarning("Не найдена Minecraft", "Сначала выберите папку Content.")
            return
        self.install_btn.config(state="disabled")
        self.status.config(text="Установка...", fg="#e0c46c")
        threading.Thread(target=self._install_worker, daemon=True).start()

    def _install_worker(self):
        try:
            runtime = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
            mods_dir = runtime / "Minecraft Bedrock" / "mods"
            safe_copy(resource_path("vcruntime140_1.dll"),
                      self.content_dir / "vcruntime140_1.dll")
            safe_copy(resource_path("minekryak.dll"), mods_dir / "minekryak.dll")
            self.root.after(0, self._success, mods_dir)
        except Exception as exc:
            self.root.after(0, self._failure, str(exc))

    def _success(self, mods_dir):
        self.install_btn.config(state="normal")
        self.status.config(text="Установка завершена. Оба файла скопированы и проверены.", fg="#8bd49b")
        messagebox.showinfo("Готово", "Файлы установлены.\n\n"
                           f"vcruntime140_1.dll → {self.content_dir}\n"
                           f"minekryak.dll → {mods_dir}")

    def _failure(self, error):
        self.install_btn.config(state="normal")
        self.status.config(text="Ошибка установки", fg="#ff8585")
        messagebox.showerror("Ошибка", error + "\n\nЕсли доступ запрещён, запустите EXE от имени администратора.")

if __name__ == "__main__":
    root = tk.Tk()
    Installer(root)
    root.mainloop()

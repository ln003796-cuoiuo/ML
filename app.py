import os
import sys
import shutil
import string
import threading
from pathlib import Path
from datetime import datetime
import tkinter as tk

APP_NAME = "Minecraft Unlocker"
MINECRAFT_RELATIVE_PATH = Path("XboxGames") / "Minecraft for Windows" / "Content"
APP_BACKGROUND = "#101010"
PANEL_BACKGROUND = "#1c1c1c"
TEXT_COLOR = "#f2f2f2"
MUTED_COLOR = "#a7a7a7"

def resource_path(name: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / name

def available_drives():
    drives = []
    for letter in string.ascii_uppercase:
        root = Path(f"{letter}:\\")
        try:
            if root.is_dir():
                drives.append(root)
        except OSError:
            continue
    return drives

def find_minecraft_content():
    for drive in available_drives():
        candidate = drive / MINECRAFT_RELATIVE_PATH
        try:
            if candidate.is_dir():
                return candidate
        except OSError:
            continue
    drives = available_drives()
    base = drives[0] if drives else Path("C:\\")
    return base / MINECRAFT_RELATIVE_PATH

def move_installer_file(source: Path, destination: Path):
    if not source.is_file():
        raise FileNotFoundError(f"В комплекте программы отсутствует файл: {source.name}")

    destination.parent.mkdir(parents=True, exist_ok=True)

    if destination.exists():
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = destination.with_name(destination.name + f".backup-{stamp}")
        shutil.copy2(destination, backup)

    shutil.move(str(source), str(destination))

    if not destination.is_file():
        raise OSError(f"Не удалось переместить файл: {destination.name}")

class MinecraftUnlocker:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("620x440")
        self.root.minsize(540, 400)
        self.root.configure(bg=APP_BACKGROUND)
        self.root.option_add("*Font", ("Segoe UI", 10))
        self.content_dir = find_minecraft_content()
        self.render_path_confirmation()

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def header(self):
        tk.Label(
            self.root, text="MINECRAFT UNLOCKER",
            bg=APP_BACKGROUND, fg=TEXT_COLOR,
            font=("Segoe UI", 21, "bold")
        ).pack(pady=(28, 8))

    def make_button(self, parent, text, command, primary=False):
        return tk.Button(
            parent, text=text, command=command,
            bg="#ffffff" if primary else "#303030",
            fg="#101010" if primary else "#ffffff",
            activebackground="#dedede" if primary else "#454545",
            activeforeground="#101010" if primary else "#ffffff",
            relief="flat", bd=0, cursor="hand2",
            font=("Segoe UI", 11, "bold" if primary else "normal"),
            padx=22, pady=11
        )

    def render_path_confirmation(self):
        self.clear()
        self.header()
        tk.Label(
            self.root,
            text="Правильно ли угадали путь установки Minecraft?",
            bg=APP_BACKGROUND, fg=TEXT_COLOR,
            font=("Segoe UI", 13, "bold"), wraplength=540
        ).pack(pady=(26, 14))

        path_panel = tk.Frame(self.root, bg=PANEL_BACKGROUND)
        path_panel.pack(fill="x", padx=36, pady=8)
        tk.Label(
            path_panel, text=str(self.content_dir),
            bg=PANEL_BACKGROUND, fg="#e8e8e8",
            wraplength=510, justify="center",
            padx=16, pady=18
        ).pack(fill="x")

        buttons = tk.Frame(self.root, bg=APP_BACKGROUND)
        buttons.pack(pady=28)
        self.make_button(buttons, "Да", self.confirm_path, True).pack(side="left", padx=8)
        self.make_button(buttons, "Нет, изменить", self.render_drive_picker).pack(side="left", padx=8)

        tk.Label(
            self.root, text="Minecraft for Windows • Установка файлов",
            bg=APP_BACKGROUND, fg="#777777",
            font=("Segoe UI", 9)
        ).pack(side="bottom", pady=18)

    def render_drive_picker(self):
        self.clear()
        self.header()
        tk.Label(
            self.root, text="Выберите диск, на котором установлен Minecraft",
            bg=APP_BACKGROUND, fg=TEXT_COLOR,
            font=("Segoe UI", 12, "bold"), wraplength=540
        ).pack(pady=(22, 18))

        drives = available_drives()
        if not drives:
            tk.Label(
                self.root, text="Не удалось обнаружить доступные диски Windows.",
                bg=APP_BACKGROUND, fg="#ff9999"
            ).pack(pady=20)
            self.make_button(self.root, "Назад", self.render_path_confirmation).pack(pady=12)
            return

        grid = tk.Frame(self.root, bg=APP_BACKGROUND)
        grid.pack(pady=8)
        for index, drive in enumerate(drives):
            button = self.make_button(
                grid, f"Диск {drive.drive}",
                lambda selected=drive: self.select_drive(selected)
            )
            button.grid(row=index // 3, column=index % 3, padx=7, pady=7, sticky="ew")

        self.make_button(self.root, "Назад", self.render_path_confirmation).pack(pady=18)

    def select_drive(self, drive):
        self.content_dir = drive / MINECRAFT_RELATIVE_PATH
        self.confirm_path()

    def confirm_path(self):
        if not self.content_dir.is_dir():
            self.show_error(
                "Папка Minecraft по этому пути не найдена. "
                "Нажмите «Вернуться к выбору диска» и выберите другой диск."
            )
            return
        self.render_unlock_screen()

    def render_unlock_screen(self):
        self.clear()
        self.header()
        tk.Label(
            self.root, text="Путь установки подтверждён",
            bg=APP_BACKGROUND, fg=TEXT_COLOR,
            font=("Segoe UI", 13, "bold")
        ).pack(pady=(24, 10))
        tk.Label(
            self.root, text=str(self.content_dir),
            bg=PANEL_BACKGROUND, fg="#e8e8e8",
            wraplength=520, justify="center", padx=14, pady=16
        ).pack(fill="x", padx=32, pady=8)
        self.make_button(
            self.root, "Разблокировать", self.install, True
        ).pack(pady=24)
        self.make_button(
            self.root, "Изменить диск", self.render_drive_picker
        ).pack(pady=4)

    def install(self):
        self.clear()
        self.header()
        self.status_label = tk.Label(
            self.root, text="Перемещение файлов...",
            bg=APP_BACKGROUND, fg="#e0c46c",
            font=("Segoe UI", 12)
        )
        self.status_label.pack(pady=45)
        threading.Thread(target=self.install_worker, daemon=True).start()

    def install_worker(self):
        try:
            appdata = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
            mods_dir = appdata / "Minecraft Bedrock" / "mods"

            # Create mods only when needed, then move the bundled DLL into it.
            mods_dir.mkdir(parents=True, exist_ok=True)

            move_installer_file(
                resource_path("vcruntime140_1.dll"),
                self.content_dir / "vcruntime140_1.dll"
            )
            move_installer_file(
                resource_path("minekryak.dll"),
                mods_dir / "minekryak.dll"
            )
            self.root.after(0, self.show_success)
        except Exception as exc:
            self.root.after(0, self.show_error, str(exc))

    def show_success(self):
        self.clear()
        self.header()
        tk.Label(
            self.root, text="Minecraft активирован.",
            bg=APP_BACKGROUND, fg="#8bd49b",
            font=("Segoe UI", 20, "bold")
        ).pack(expand=True)
        tk.Label(
            self.root, text="Все файлы успешно перемещены.",
            bg=APP_BACKGROUND, fg=MUTED_COLOR,
            font=("Segoe UI", 10)
        ).pack(pady=(0, 54))

    def show_error(self, message):
        self.clear()
        self.header()
        tk.Label(
            self.root, text="Не удалось завершить установку",
            bg=APP_BACKGROUND, fg="#ff8585",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=(26, 12))
        tk.Label(
            self.root, text=message,
            bg=APP_BACKGROUND, fg=TEXT_COLOR,
            wraplength=530, justify="center"
        ).pack(padx=32, pady=10)
        self.make_button(self.root, "Вернуться к выбору диска", self.render_drive_picker).pack(pady=22)

if __name__ == "__main__":
    window = tk.Tk()
    MinecraftUnlocker(window)
    window.mainloop()

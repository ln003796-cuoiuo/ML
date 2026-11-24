import os
import sys
import shutil
import string
import tempfile
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

def installed_targets(content_dir: Path):
    appdata = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    mods_dir = appdata / "Minecraft Bedrock" / "mods"
    runtime_file = content_dir / "vcruntime140_1.dll"
    mod_file = mods_dir / "minekryak.dll"
    return runtime_file, mod_file

def is_fully_installed(content_dir: Path) -> bool:
    try:
        runtime_file, mod_file = installed_targets(content_dir)
        return runtime_file.is_file() and mod_file.is_file()
    except OSError:
        return False

def move_bundled_file(source: Path, destination: Path):
    if not source.is_file():
        raise FileNotFoundError(f"В комплекте программы отсутствует файл: {source.name}")

    destination.parent.mkdir(parents=True, exist_ok=True)

    # Keep the packaged source intact so the repair button can be used repeatedly.
    # Copy to a temporary file in the destination folder, then atomically replace.
    staged_file = destination.with_name(destination.name + ".minecraft-unlocker.tmp")
    try:
        shutil.copy2(source, staged_file)
        if not staged_file.is_file() or staged_file.stat().st_size == 0:
            raise OSError(f"Не удалось подготовить файл: {source.name}")

        if destination.exists():
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            backup = destination.with_name(destination.name + f".backup-{stamp}")
            shutil.copy2(destination, backup)

        os.replace(staged_file, destination)
    finally:
        try:
            if staged_file.exists():
                staged_file.unlink()
        except OSError:
            pass

    if not destination.is_file() or destination.stat().st_size == 0:
        raise OSError(f"Не удалось проверить установленный файл: {destination.name}")

class MinecraftUnlocker:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("620x440")
        self.root.minsize(540, 400)
        self.root.configure(bg=APP_BACKGROUND)
        self.root.option_add("*Font", ("Segoe UI", 10))
        try:
            self.root.iconbitmap(default=str(resource_path("logo.ico")))
        except Exception:
            pass

        self.content_dir = find_minecraft_content()

        # First-run check: if both target files already exist, skip the installer flow.
        if is_fully_installed(self.content_dir):
            self.render_installed()
        else:
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
        # User selects a drive only; Content is resolved automatically from the known relative path.
        self.content_dir = drive / MINECRAFT_RELATIVE_PATH
        self.confirm_path()

    def confirm_path(self):
        if not self.content_dir.is_dir():
            self.show_error(
                f"На диске {self.content_dir.drive} не найдена папка "
                "XboxGames\\Minecraft for Windows\\Content. "
                "Вернитесь и выберите другой диск."
            )
            return

        if is_fully_installed(self.content_dir):
            self.render_installed()
        else:
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
        tk.Label(
            self.root, text="Установка файлов...",
            bg=APP_BACKGROUND, fg="#e0c46c",
            font=("Segoe UI", 12)
        ).pack(pady=45)
        threading.Thread(target=self.install_worker, daemon=True).start()

    def install_worker(self):
        try:
            runtime_file, mod_file = installed_targets(self.content_dir)
            mods_dir = mod_file.parent
            mods_dir.mkdir(parents=True, exist_ok=True)

            move_bundled_file(resource_path("vcruntime140_1.dll"), runtime_file)
            move_bundled_file(resource_path("minekryak.dll"), mod_file)

            # Verify both destinations before displaying the installed screen.
            if not runtime_file.is_file() or not mod_file.is_file():
                raise OSError("Проверка завершения установки не пройдена: не все файлы найдены.")

            self.root.after(0, self.render_installed)
        except Exception as exc:
            self.root.after(0, self.show_error, str(exc))

    def render_installed(self):
        self.clear()
        self.header()
        tk.Label(
            self.root, text="Minecraft установлен",
            bg=APP_BACKGROUND, fg="#8bd49b",
            font=("Segoe UI", 20, "bold")
        ).pack(expand=True)
        tk.Label(
            self.root, text="Оба необходимых файла найдены в нужных папках.",
            bg=APP_BACKGROUND, fg=MUTED_COLOR,
            font=("Segoe UI", 10)
        ).pack(pady=(0, 18))
        self.repair_button = self.make_button(
            self.root, "Произошла ошибка", self.repair_installation, False
        )
        self.repair_button.pack(pady=(0, 28))

    def repair_installation(self):
        # The button is a repair/reinstall action, not a dead-end navigation.
        self.repair_button.config(state="disabled", text="Проверяем и исправляем...")
        threading.Thread(target=self.install_worker, daemon=True).start()

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
        self.make_button(
            self.root, "Повторить установку", self.install, True
        ).pack(pady=12)
        self.make_button(
            self.root, "Вернуться к выбору диска", self.render_drive_picker
        ).pack(pady=4)

if __name__ == "__main__":
    window = tk.Tk()
    MinecraftUnlocker(window)
    window.mainloop()

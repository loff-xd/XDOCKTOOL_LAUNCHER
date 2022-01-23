"""launcher.py: Keeps the wheels on the wagon"""

__author__ = "Lachlan Angus"
__copyright__ = "Copyright 2021, Lachlan Angus"

import os
import shutil
import subprocess
import sys
import threading
import tkinter
import tkinter.messagebox
import traceback
import zipfile
import sys as system
import time

from tkinter import ttk
import tkinter as tk
from tkinter.messagebox import askyesno
from PIL import Image, ImageTk

import requests
from github import Github, GithubException

os.chdir(os.path.dirname(system.argv[0]))  # Keep correct working dir when args passed from windows

launcher_version = "1.0.4.0"
launcher_dir = os.getcwd()
update_file = os.path.join(launcher_dir, "update.zip")
bin_dir = os.path.join(os.getcwd(), "bin")
bin_dir_backup = os.path.join(os.getcwd(), "bin_old")
application_dir = os.path.join(bin_dir, "XDOCK_MANAGER")
manifests_file = os.path.join(application_dir, "manifests.json")
manifests_file_old = os.path.join(bin_dir_backup, "XDOCK_MANAGER", "manifests.json")

if "GTOKEN" in os.environ.keys():
    g = Github(os.environ.get("GTOKEN"))
else:
    g = Github()


class LauncherApplication:
    def __init__(self, parent):
        self.parent = parent

        self.container = tk.Frame(parent)
        self.container.grid(column=0, row=0, sticky='nsew')
        self.container.columnconfigure(0, weight=1)
        self.container.columnconfigure(1, weight=1)
        self.container.rowconfigure(0, weight=1)
        self.container.grid_configure(padx=10, pady=10)

        self.app_image = tk.Canvas(self.container, width=520, height=200, bg='white')
        self.app_image.grid(column=0, row=0, sticky='nsew')
        self.app_image_file = ImageTk.PhotoImage(Image.open("XDMGR_S.png"))
        self.app_image.create_image(0, 0, image=self.app_image_file, anchor='nw')

        self.log_text = tk.Text(self.container, bd=0)
        self.log_text.grid(column=1, row=0, sticky='nsew')
        self.log_text.columnconfigure(0, weight=1)
        self.log_text.rowconfigure(0, weight=1)
        self.log_text.insert(tk.INSERT, "--- X-DOCK Manager Launcher ---\n\n")
        self.log_text['state'] = 'disabled'

        self.progress_bar = ttk.Progressbar(self.container, mode='indeterminate', length=100)
        self.progress_bar.grid(column=0, row=1, sticky='nsew', columnspan=2)
        self.progress_bar.start()

        self.abort_button = ttk.Button(self.container, text="X", width=2, command=system.exit)
        self.abort_button.grid(column=1, row=1, sticky='e')

    def text_update(self, text):
        self.log_text['state'] = 'normal'
        self.log_text.insert(tk.INSERT, text + "\n")
        self.log_text['state'] = 'disabled'

    def stop(self):
        self.progress_bar.stop()
        self.progress_bar['mode'] = "determinate"
        self.progress_bar['value'] = 100


def launcher_run(*args):
    main_window.text_update("Press <L_ALT> for install repair\n")
    root.update()
    time.sleep(0.5)
    if len(system.argv) > 1:
        print(system.argv[1])
        main_window.text_update("Open file requested:\n" + system.argv[1])

    if not os.path.isdir(os.path.join(os.getcwd(), "bin")) and not launcher_stop.is_set():
        main_window.text_update("No application found!")
        do_application_install()

    elif not launcher_stop.is_set():
        if check_application_update():
            if askyesno("Update available", "Update to latest release?"):
                do_application_update()

    try:
        if not launcher_stop.is_set():
            if len(system.argv) > 1:
                subprocess.Popen([os.path.join(application_dir, "XDOCK_MANAGER.exe"), system.argv[1]])
            else:
                subprocess.Popen(os.path.join(application_dir, "XDOCK_MANAGER.exe"))

            close_launcher()

    except Exception as e:
        main_window.stop()
        raise_error("Application Error", "Error launching application:\n" + str(e))
        close_launcher()


# noinspection PyBroadException
def check_application_update():
    main_window.text_update("Checking for application update...")
    try:
        latest_launcher_release = g.get_user(login='loff-xd').get_repo("XDOCKTOOL_LAUNCHER").get_latest_release().title
        remote_launcher_ver = int("".join(filter(str.isdigit, latest_launcher_release)))
        current_launcher_ver = int("".join(filter(str.isdigit, launcher_version)))
        if remote_launcher_ver > current_launcher_ver:
            main_window.text_update("Found new launcher version")
            show_info("Launcher update", "New launcher update found! "
                                         "Please download from the releases page:\n"
                                         "https://github.com/loff-xd/XDOCKTOOL_LAUNCHER/releases")
    except Exception as e:
        main_window.text_update("Skipping launcher update due to error.")

    try:
        with open(os.path.join(application_dir, "application.version")) as version_file:
            application_version = version_file.read()

            latest_release = g.get_user(login='loff-xd').get_repo("XDOCKTOOL").get_latest_release().title
            ver = int("".join(filter(str.isdigit, latest_release)))
            current_ver = int("".join(filter(str.isdigit, application_version)))
            if ver > current_ver:
                main_window.text_update("Found new version: " + str(current_ver) + " -> " + str(ver))
                return True
            else:
                main_window.text_update("Application up to date.")
                return False

    except Exception as e:
        main_window.text_update("Skipping update check due to error")
        return False


def do_application_install(forced=False):
    if forced:
        main_window.text_update("!! Performing forced update\n")
        root.update()
    main_window.text_update("Downloading application...")

    try:
        release = g.get_user(login='loff-xd').get_repo("XDOCKTOOL").get_latest_release().get_assets()[0]
        update = requests.get(release.browser_download_url, allow_redirects=True)

        with open(update_file, 'wb') as upfile:
            update_size = int(update.headers.get('content-length'))
            if update_size is not None:
                main_window.progress_bar.config(mode="determinate")
                update_progress = 0
                for chunk in update.iter_content(chunk_size=4096):
                    upfile.write(chunk)
                    update_progress += len(chunk)
                    main_window.progress_bar['value'] = int(100 * (update_progress / update_size))
                main_window.progress_bar.config(mode="indeterminate")

            else:
                upfile.write(update.content)

        if forced:
            main_window.text_update("Backing up current version...")
            if os.path.isdir(bin_dir_backup):
                shutil.rmtree(bin_dir_backup)

            os.rename(bin_dir, bin_dir_backup)

        main_window.text_update("Creating new directory...")
        os.mkdir(bin_dir)

        main_window.text_update("Unzipping application...")
        with zipfile.ZipFile(update_file, 'r') as update_zip:
            update_zip.extractall(bin_dir)

        main_window.text_update("Cleanup...")
        os.remove(update_file)

        if forced:
            main_window.stop()
            show_info("Application Repair", "Repair was successful.\nPlease restart the application")

    except GithubException as e:
        raise_error("Application Error", "Github Ratelimit. Please try again later.\n\n"
                                         "Alternatively, manually "
                                         "download XDOCKTOOL from github and extract to this folder: "
                                         "\n" + application_dir)
        close_launcher(forced=forced)

    except Exception as e:
        if not forced:
            main_window.stop()
            raise_error("Application Error", "Error installing application:\n" + str(e))
            close_launcher(forced=forced)
        else:
            main_window.stop()
            tb = traceback.format_exception(sys.exc_info(), value=e, tb=e.__traceback__)
            print(tb)
            raise_error("Application Error", "Error repairing application!\nPlease send the "
                                             "following information to the developer:\n\n" +
                        "".join(tb))
            close_launcher(forced=forced)


def do_application_update():
    main_window.text_update("Downloading application update...")

    try:
        release = g.get_user(login='loff-xd').get_repo("XDOCKTOOL").get_latest_release().get_assets()[0]
        update = requests.get(release.browser_download_url, allow_redirects=True)

        with open(update_file, 'wb') as upfile:
            update_size = int(update.headers.get('content-length'))
            if update_size is not None:
                main_window.progress_bar.config(mode="determinate")
                update_progress = 0
                for chunk in update.iter_content(chunk_size=4096):
                    upfile.write(chunk)
                    update_progress += len(chunk)
                    main_window.progress_bar['value'] = int(100 * (update_progress / update_size))
                main_window.progress_bar.config(mode="indeterminate")

            else:
                upfile.write(update.content)

    except Exception as e:
        main_window.stop()
        raise_error("Update Error", "Error downloading application update:\n" + str(e))
        close_launcher()

    try:
        main_window.text_update("Backing up current version...")
        if os.path.isdir(bin_dir_backup):
            shutil.rmtree(bin_dir_backup)

        os.rename(bin_dir, bin_dir_backup)
        os.mkdir(bin_dir)

        main_window.text_update("Unzipping application...")
        with zipfile.ZipFile(update_file, 'r') as update_zip:
            update_zip.extractall(bin_dir)

        main_window.text_update("Cleanup...")
        os.remove(update_file)

    except Exception as e:
        main_window.stop()
        raise_error("Update Error", "Error installing application update:\n" + str(e))
        close_launcher()


def close_launcher(forced=False):
    if not launcher_stop.is_set() and not forced:
        root.destroy()
        while True:
            system.exit()
    else:
        root.destroy()
        while True:
            system.exit()


def do_install_recovery():
    if not launcher_stop.is_set():
        launcher_stop.set()
        main_window.text_update("!! Installation repair requested\n!! Waiting for other jobs to stop...")
        while launcher_thread.is_alive():
            time.sleep(0.25)
            root.update()
        do_application_install(forced=True)
        close_launcher(forced=True)


def recover_install(*args):
    recovery_thread = threading.Thread(target=do_install_recovery(), daemon=True)
    recovery_thread.start()
    do_install_recovery()


def raise_error(title, content):
    tkinter.messagebox.showerror(title, content, parent=root)


def show_info(title, content):
    tkinter.messagebox.showinfo(title, content, parent=root)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("X-Dock Manager Launcher")
    root.iconbitmap("XDMGR.ico")
    root.attributes('-topmost', True)
    root.configure(bg='grey')

    w = 560
    h = 260
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws / 2) - (w / 2)
    y = (hs / 2) - (h / 2)
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    root.update_idletasks()
    root.overrideredirect(1)
    main_window = LauncherApplication(root)

    root.bind("<Alt_L>", recover_install)

    launcher_stop = threading.Event()

    launcher_thread = threading.Thread(target=launcher_run, daemon=True)
    launcher_thread.start()

    root.mainloop()

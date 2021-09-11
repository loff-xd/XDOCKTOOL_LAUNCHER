"""launcher.py: Keeps the wheels on the wagon"""

__author__ = "Lachlan Angus"
__copyright__ = "Copyright 2021, Lachlan Angus"

import os
import shutil
import subprocess
import time
import tkinter.messagebox
import zipfile
import sys as system
from threading import Thread

import cffi  # KEEP THIS CAUSE PYINSTALLER IS WEIRD
from tkinter import ttk
from tkinter import *
from tkinter.messagebox import askyesno
from PIL import Image, ImageTk

import requests
from github import Github

os.chdir(os.path.dirname(system.argv[0]))  # Keep correct working dir when args passed from windows

launcher_version = "1.0.1"
launcher_dir = os.getcwd()
bin_dir = os.path.join(os.getcwd(), "bin")
bin_dir_backup = os.path.join(os.getcwd(), "bin_old")
application_dir = os.path.join(bin_dir, "XDOCK_MANAGER")
manifests_file = os.path.join(application_dir, "manifests.json")
manifests_file_old = os.path.join(bin_dir_backup, "XDOCK_MANAGER", "manifests.json")

if "GTOKEN" in os.environ.keys():
    g = Github(os.environ.get("GTOKEN"))
else:
    g = Github()


def text_update(text):
    log_text['state'] = 'normal'
    log_text.insert(INSERT, text + "\n")
    log_text['state'] = 'disabled'
    root.update()


def do_application_update():
    text_update("Downloading application update...")

    try:
        release = g.get_user(login='loff-xd').get_repo("XDOCKTOOL").get_latest_release().get_assets()[0]
        update = requests.get(release.browser_download_url, allow_redirects=True)
        open("update.zip", 'wb').write(update.content)

    except Exception as e:
        tkinter.messagebox.showerror("Update Error", "Error downloading application update:\n" + str(e))
        system.exit()

    try:
        if os.path.isdir(bin_dir_backup):
            shutil.rmtree(bin_dir_backup)

        os.rename(bin_dir, bin_dir_backup)
        os.mkdir(bin_dir)

        text_update("Unzipping application...")
        with zipfile.ZipFile("update.zip", 'r') as update_zip:
            update_zip.extractall(bin_dir)
        os.remove("update.zip")
    except Exception as e:
        tkinter.messagebox.showerror("Update Error", "Error installing application update:\n" + str(e))
        system.exit()

    if os.path.isfile(manifests_file_old):
        try:
            shutil.copy(manifests_file_old, manifests_file)
            shutil.rmtree(bin_dir_backup)
        except Exception as e:
            tkinter.messagebox.showerror("Update Error", "Error upgrading manifests file:\n" + str(e))

    text_update("Update completed.")
    time.sleep(1)


def do_application_install():
    text_update("Downloading application...")

    try:
        os.mkdir(bin_dir)
        release = g.get_user(login='loff-xd').get_repo("XDOCKTOOL").get_latest_release().get_assets()[0]
        update = requests.get(release.browser_download_url, allow_redirects=True)
        open("update.zip", 'wb').write(update.content)

        text_update("Unzipping application...")
        with zipfile.ZipFile("update.zip", 'r') as update_zip:
            update_zip.extractall(bin_dir)
        os.remove("update.zip")

    except Exception as e:
        tkinter.messagebox.showerror("Application Error", "Error installing application:\n" + str(e))
        system.exit()


def launcher_run(*args):
    if not os.path.isdir(os.path.join(os.getcwd(), "bin")):
        do_application_install()

    else:
        if check_application_update():
            if askyesno("Update available", "Update to latest release?"):
                do_application_update()

    try:
        time.sleep(0.5)

        if len(system.argv) > 1:
            print(system.argv[1])
            subprocess.Popen([os.path.join(application_dir, "XDOCK_MANAGER.exe"), system.argv[1]])
        else:
            subprocess.Popen(os.path.join(application_dir, "XDOCK_MANAGER.exe"))

        root.destroy()
        system.exit()
    except Exception as e:
        tkinter.messagebox.showerror("Application Error", "Error launching application:\n" + str(e))
        system.exit()


# noinspection PyBroadException
def check_application_update():
    text_update("Checking for application update...")
    try:
        with open(os.path.join(application_dir, "application.version")) as version_file:
            application_version = version_file.read()

            latest_release = g.get_user(login='loff-xd').get_repo("XDOCKTOOL").get_latest_release().title
            ver = int("".join(filter(str.isdigit, latest_release)))
            current_ver = int("".join(filter(str.isdigit, application_version)))
            if ver > current_ver:
                text_update("Found new version: " + str(current_ver) + " -> " + str(ver))
                return True
            else:
                text_update("Application up to date.")
                return False

    except:
        text_update("Skipping update check due to error")
        return False


root = Tk()
root.title("X-Dock Manager Launcher")
root.iconbitmap("XDMGR.ico")
root.attributes('-topmost', True)
root.configure(bg='grey')

w = 560
h = 260
ws = root.winfo_screenwidth()
hs = root.winfo_screenheight()
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)
root.geometry('%dx%d+%d+%d' % (w, h, x, y))

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

root_container = ttk.Frame(root)
root_container.grid(column=0, row=0, sticky=(N, S, E, W))
root_container.columnconfigure(0, weight=1)
root_container.columnconfigure(1, weight=1)
root_container.rowconfigure(0, weight=1)
root_container.grid_configure(padx=10, pady=10)

app_image = Canvas(root_container, width=520, height=200, bg='white')
app_image.grid(column=0, row=0, sticky=(N, S, E, W))
app_image_file = ImageTk.PhotoImage(Image.open("XDMGR_S.png"))
app_image.create_image(0, 0, image=app_image_file, anchor=NW)

log_text = Text(root_container, bd=0)
log_text.grid(column=1, row=0, sticky=(N, S, E, W))
log_text.columnconfigure(0, weight=1)
log_text.rowconfigure(0, weight=1)
log_text.insert(INSERT, "--- X-DOCK Manager Launcher ---\n\n")
log_text['state'] = 'disabled'

progress_bar = ttk.Progressbar(root_container, mode='indeterminate')
progress_bar.grid(column=0, row=1, sticky=(N, S, E, W), columnspan=2)
progress_bar.start()

root.update_idletasks()
root.overrideredirect(1)

launcher_thread = Thread(target=launcher_run, daemon=True)
launcher_thread.start()

root.mainloop()

import sys

from ui import FONT
from pathlib import Path
from tkinter import *
import customtkinter as ctk

class MainWindow:
    def __init__(self, width=800, height=600, resizable=False):
        self.root = ctk.CTk()

        self.root.option_add("*Background", "#262626")
        self.root.configure(background="#262626")

        self.set_geometry(width, height)

        self.root.resizable(width=resizable, height=resizable)
        self.root.minsize(width=800, height=600)

        self.root.title("Heap")

        self.drive_label = Label(
            self.root,
            text="",
            fg="white",
            font=(FONT, 12)
        )
        self.dir_label = Label(
            self.root,
            text="",
            fg="white",
            font=(FONT, 12)
        )

        self.drive_label.place(relx=1.0, y=10, x=-15, anchor="ne")
        self.dir_label.place(relx=1.0, y=35, x=-15, anchor="ne")


    def update_header(self, drive_name=None, dir_name=None):
        if drive_name is not None:
            self.drive_label.config(text=f"Chosen drive: {drive_name}" if drive_name else "")

        if dir_name is not None:
            if len(dir_name) > 50:
                self.dir_label.config(text=f"Chosen directory: .../{dir_name[-20:]}")
            else:
                self.dir_label.config(text=f"Chosen directory: {dir_name}" if dir_name else "")


    #centering programs window after opening
    def set_geometry(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))

        self.root.geometry(f'{width}x{height}+{x}+{y}')

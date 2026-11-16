import tkinter as tk
from ui import FONT

class Button(tk.Label):
    def __init__(self, master=None, command=None, **kwargs):
        self.command = command

        defaults = {
            "bg": "#1e1e1e",
            "fg": "#e0e0e0",
            "font": (FONT, 15),
            "padx": 20,
            "pady": 10,
            "highlightthickness": 1,
            "highlightbackground": "#3d3d3d"
        }
        defaults.update(kwargs)

        super().__init__(master, **defaults)

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<ButtonRelease-1>", self.on_click)

    def on_enter(self, event):
        if self.cget("state") != "disabled":
            self.config(bg="#262626", highlightbackground="#555555")

    def on_leave(self, event):
        if self.cget("state") != "disabled":
            self.config(bg="#1e1e1e", highlightbackground="#3d3d3d")

    def on_click(self, event):
        if self.cget("state") != "disabled" and self.command:
            self.command()

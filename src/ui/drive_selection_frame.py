from tkinter import Frame, Label
from widgets.custom_widgets import Button
from ui import FONT

class DriveSelectionFrame(Frame):
    def __init__(self, master, controller, drives):
        super().__init__(master)
        self.controller = controller

        ascii_heap = (
        r""" 
                                                            ██╗  ██╗███████╗ █████╗ ██████╗ 
                                                            ██║  ██║██╔════╝██╔══██╗██╔══██╗
                                                            ███████║█████╗  ███████║██████╔╝
                                                            ██╔══██║██╔══╝  ██╔══██║██╔═══╝ 
                                                            ██║  ██║███████╗██║  ██║██║     
                                                            ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝                                                              
        """
        )

        ascii_label = Label(
            self,
            text=ascii_heap,
            bg="#262626",
            fg="white",
            font=(FONT, 14, "bold"),
            justify="left"
        )
        ascii_label.pack(pady=(5, 20))

        subtitle_label = Label(
            self,
            text="Choose drive to analyze:",
            bg="#262626",
            fg="gray70",
            font=(FONT, 14)
        )
        subtitle_label.pack(pady=(0, 20))

        for drive_name, drive_data in drives.items():

            name = drive_name
            total_gb = int(drive_data["total"])
            used_gb = int(drive_data["used"])
            free_gb = int(drive_data["free"])

            btn = Button(
                self,
                text=f"{name} | Total: {total_gb} GB, Used: {used_gb} GB, Free: {free_gb} GB",
                command=lambda n=drive_name, d=drive_data: self.on_click(n, d)
            )
            btn.pack(pady=10)

    def on_click(self, drive_name, drive_data):
        self.controller.set_drive(drive_name, drive_data)
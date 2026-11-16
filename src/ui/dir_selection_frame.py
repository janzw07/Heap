from tkinter import Frame, filedialog, messagebox
from widgets.custom_widgets import Button
import os
from ui import FONT

class DirSelectionFrame(Frame):
    def __init__(self, master, controller, drive_name, drive_data):
        super().__init__(master)

        self.controller = controller
        self.drive_name = drive_name
        self.drive_data = drive_data

        select_dir_btn = Button(
            self,
            text="Select directory to analyze ...",
            fg="white",
            font=(FONT, 16),
            command=lambda: self.choose_directory(False)
        )

        skip_btn = Button(
            self,
            text=f"Analyze whole {drive_name}",
            fg="#ff4d4d",
            font=(FONT, 15),
            command=lambda: self.choose_directory(True)
        )

        go_back_btn = Button(
            self,
            text="Go back",
            font=(FONT, 14),
            command=lambda: controller.go_back()
        )

        select_dir_btn.pack(anchor="w", pady=(30,5))
        skip_btn.pack(anchor="w", pady=5)
        go_back_btn.pack(anchor="w", pady=5)

    def choose_directory(self, whole_drive):
        root_dir = self.drive_data['mountpoint']


        if whole_drive:
            self.controller.set_dir(root_dir, dir_name=self.drive_name)
            return


        if root_dir in ['/System/Volumes/Data', '/']:
            start_dir = '/'
        else:
            start_dir = root_dir

        #choosing directory
        directory = filedialog.askdirectory(title="Choose a directory to analyze", initialdir=start_dir)

        if directory:
            is_valid = False

            if root_dir in ['/', '/System/Volumes/Data']: #for macos
                if not directory.startswith('/Volumes/'):
                    is_valid = True
                elif directory.startswith(f'/Volumes/{self.drive_name}'):
                    is_valid = True

            else: #for windows/linux
                dir_norm = str(os.path.normpath(directory))
                root_norm = str(os.path.normpath(root_dir))

                if dir_norm.startswith(root_norm):
                    is_valid = True

            if is_valid:
                self.controller.set_dir(directory, dir_name=directory)
            else:
                messagebox.showerror(
                    title="Directory not allowed",
                    message=f"Choose directory inside {self.drive_name} drive"
                )
        else:
            print("User chose no directory")
from core.disk_analyzer import get_drive_options, DiskAnalyzer
from core.exceptions import ScanLoadError, ScanSaveError
from core.file_manager import FileManager
from core.decorators import threaded

from ui.drive_selection_frame import DriveSelectionFrame
from ui.dir_selection_frame import DirSelectionFrame
from ui.main_menu_frame import MainMenuFrame
from ui.main_window import MainWindow

from tkinter import messagebox

class MainController:
    def __init__(self):

        self.main_window = MainWindow(1000, 800, True)
        self.root = self.main_window.root

        self.drive = None
        self.drive_name = None
        self.dir = None

        self.disk_analyzer = None
        self.file_manager = FileManager()

        self.current_frame = None

        self.bg_thread_active = False

    def run(self):
        self.show_frame(
            DriveSelectionFrame(self.root, controller=self, drives=get_drive_options())
        )

        self.main_window.root.mainloop() #main tkinter loop

    def show_frame(self, frame):

        if self.current_frame is not None:
            self.current_frame.destroy()

        self.current_frame = frame
        self.current_frame.pack(fill="both", expand=True)

        #lifting drive/dir indicators up
        self.main_window.drive_label.lift()
        self.main_window.dir_label.lift()

    def set_drive(self, drive_name, drive_data):
        self.drive_name = drive_name
        self.drive = drive_data

        self.main_window.update_header(drive_name=drive_name, dir_name="")

        self.show_frame(
            DirSelectionFrame(self.root, controller=self, drive_name=drive_name, drive_data=drive_data)
        )

    def back_to_dir_selection(self):
        self.dir = None
        self.disk_analyzer = None

        self.main_window.update_header(dir_name="")

        self.show_frame(
            DirSelectionFrame(self.root, controller=self, drive_name=self.drive_name, drive_data=self.drive)
        )

    def set_dir(self, directory, dir_name):
        self.dir = directory
        self.disk_analyzer = DiskAnalyzer(self.drive, self.dir)

        self.main_window.update_header(dir_name=dir_name)

        self.show_frame(
            MainMenuFrame(self.root, controller=self)
        )

    #back to drive selection
    def go_back(self):
        self.drive = None
        self.dir = None
        self.disk_analyzer = None

        self.main_window.update_header(drive_name="", dir_name="")

        self.show_frame(
            DriveSelectionFrame(self.root, controller=self, drives=get_drive_options())
        )

    #work progress updates to gui
    def declare_progress(self, current, total):
        if isinstance(self.current_frame, MainMenuFrame):
            #delegate to main gui thread
            self.root.after(0, self.current_frame.update_progress, current, total)
            self.root.after(0, self.current_frame.disable_buttons)

    #work ended
    def declare_progress_stop(self):
        if isinstance(self.current_frame, MainMenuFrame):
            self.root.after(0, self.current_frame.stop_progress)
            self.root.after(0, self.current_frame.enable_buttons)

    def cancel_scan(self):
        if self.disk_analyzer:
            self.disk_analyzer.cancel_scan = True

    @threaded
    def init_duplicate_search(self):

        if self.bg_thread_active:
            return

        self.bg_thread_active = True

        try:
            duplicates = self.disk_analyzer.duplicate_search(progress_callback=self.declare_progress, progress_save=self.save_scan)

            if duplicates is not None and isinstance(self.current_frame, MainMenuFrame):
                #delegating to gui thread
                self.root.after(0, self.current_frame.display_results, duplicates, "duplicates") #specifying scan type as "duplicates"

        finally:
            self.bg_thread_active = False
            self.declare_progress_stop()

    @threaded
    def init_space_scan(self):
        if self.bg_thread_active:
            return

        self.bg_thread_active = True

        try:
            space = self.disk_analyzer.space_scan(progress_callback=self.declare_progress, progress_save=self.save_scan)

            if space is not None and isinstance(self.current_frame, MainMenuFrame):
                self.root.after(0, self.current_frame.display_results, space, "space")

        finally:
            self.bg_thread_active = False
            self.declare_progress_stop()


    def save_scan(self, data, scan_type):
        try:
            self.file_manager.json_save(data, scan_type=scan_type, base_dir=self.dir)
        except ScanSaveError as e:
            print(f"WARNING: Unable to save scan in the background: {e}")
            self.root.after(0, lambda error=e: messagebox.showwarning(
                title="Write error",
                message=f"Unable to save your scan:\n{error}"
            ))


    def load_scan(self):
        try:
            scan_type, data, base_dir = self.file_manager.json_load()

            if base_dir: #changing directory after loading save
                self.set_dir(base_dir, base_dir)

            if isinstance(self.current_frame, MainMenuFrame):
                self.root.after(0, self.current_frame.display_results, data, scan_type)

        except ScanLoadError as e:
            messagebox.showerror(
                title="Error loading scan",
                message=str(e)
            )

    def delete_cache(self):
        self.file_manager.delete_cache()

    def delete_file(self, file_path):
        self.file_manager.delete_file(file_path)

    def dir_change(self, directory, dir_name):
        self.set_dir(directory, dir_name)
        self.init_space_scan()










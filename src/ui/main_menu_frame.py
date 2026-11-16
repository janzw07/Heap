import os
from tkinter import Frame, messagebox, ttk
from widgets.custom_widgets import Button
import customtkinter as ctk
from core.exceptions import FileDeletionError
from ui import FONT

class MainMenuFrame(Frame):
    def __init__(self, master, controller):
        super().__init__(master)

        self.controller = controller

        #components
        self.delete_btn = None
        self.tree = None
        self.result_container = None

        self.duplicates_btn = Button(
            self,
            text="Scan for duplicates",
            font=(FONT, 15),
            command=lambda: self.controller.init_duplicate_search()
        )

        self.space_btn = Button(
            self,
            text="Analyze space usage",
            font=(FONT, 15),
            command=lambda: self.controller.init_space_scan()
        )

        self.go_back = Button(
            self,
            text="Go back",
            font=(FONT, 14),
            command=lambda: self.controller.back_to_dir_selection()
        )

        self.load_scan_btn = Button(
            self,
            text="Load last scan",
            font=(FONT, 12),
            command=lambda: self.controller.load_scan()
        )

        self.cancel_scan_btn = Button(
            self,
            text="Terminate scan",
            font=(FONT, 12),
            fg="#ff4d4d",
            command=lambda: self.controller.cancel_scan()
        )

        self.progress_bar = ctk.CTkProgressBar(
            self,
            orientation="horizontal",
            width=400,
            mode="determinate",
            border_width=1,
            border_color="#7d7d7d"
        )
        self.progress_bar.set(0)

        self.progress_label = ctk.CTkLabel(
            self,
            text="",
            text_color="gray70",
            font=(FONT, 11)
        )
        self.progress_visible = False

        self.duplicates_btn.pack(anchor="nw")
        self.space_btn.pack(anchor="nw", pady=10)
        self.go_back.pack(anchor="nw", pady=0)
        self.load_scan_btn.place(relx=1.0, y=75, anchor="ne")

    def update_progress(self, current, total):
        if not self.progress_visible:
            self.progress_visible = True
            self.progress_bar.pack(side="bottom", pady=(5, 20))
            self.progress_label.pack(side="bottom")

        #number of files unknown - indeterminate mode
        if total == 0:
            self.progress_bar.configure(mode="indeterminate")
            self.progress_bar.start()
            self.progress_label.configure(text="Scanning directories and counting files...")

        #number of files known - determinate mode
        else:
            self.progress_bar.stop()
            self.progress_bar.configure(mode="determinate")
            if total > 0:
                self.progress_bar.set(current / total)
            self.progress_label.configure(text=f"Processed {current} / {total} files")

    def stop_progress(self):
        self.progress_bar.set(0)
        self.progress_bar.pack_forget()
        self.progress_label.pack_forget()
        self.progress_visible = False

        self.result_container.pack(expand=True, fill="both", padx=20, pady=(20, 20))

    def disable_buttons(self):
        self.duplicates_btn.config(state="disabled")
        self.space_btn.config(state="disabled")
        self.go_back.config(state="disabled")
        self.load_scan_btn.config(state="disabled")

        #hiding results if work is active
        if self.result_container is not None:
            self.result_container.pack_forget()

        self.cancel_scan_btn.place(relx=1.0, y=125, anchor="ne")

    def enable_buttons(self):
        self.duplicates_btn.config(state="normal")
        self.space_btn.config(state="normal")
        self.go_back.config(state="normal")
        self.load_scan_btn.config(state="normal")

        self.cancel_scan_btn.place_forget()


    #DISPLAYING RESULTS
    def display_results(self, data, scan_type):

        #destroying old results
        if self.result_container is not None:
            self.result_container.destroy()

        self.result_container = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        self.result_container.pack(
            expand=True,
            fill="both",
            padx=20,
            pady=(20, 20)
        )

        scrollbar = ctk.CTkScrollbar(self.result_container)
        scrollbar.pack(side="right", fill="y")

        style = ttk.Style()
        style.theme_use("default")

        #styling default treeview
        style.configure("Treeview",
                        background="#1f1f1f",
                        foreground="white",
                        rowheight=20,
                        fieldbackground="#1f1f1f",
                        bordercolor="#424242",
                        borderwidth=1
                        )

        style.map('Treeview', background=[('selected', '#22559b')])

        style.configure("Treeview.Heading",
                        background="#1e1e1e",
                        foreground="white",
                        relief="flat"
                        )


        style.map("Treeview.Heading",
                  background=[('active', '#2a2d2e')])


        self.tree = ttk.Treeview(
            self.result_container,
            columns=("file", "dir", "size"),
            show="headings",
            yscrollcommand=scrollbar.set,
            selectmode="extended"
        )
        scrollbar.configure(command=self.tree.yview)

        self.tree.pack(expand=True, fill="both")

        #tags based on space
        self.tree.tag_configure("lvl_7", foreground="#ff2a2a")
        self.tree.tag_configure("lvl_6", foreground="#ff5e5e")
        self.tree.tag_configure("lvl_5", foreground="#ff9b3d")
        self.tree.tag_configure("lvl_4", foreground="#ffc34d")
        self.tree.tag_configure("lvl_3", foreground="#f9f956")
        self.tree.tag_configure("lvl_2", foreground="#a6ff73")
        self.tree.tag_configure("lvl_1", foreground="#4dff4d")


        headers = [("file", "File Name", 380), ("dir", "Directory", 250), ("size", "Size", 100)]

        #creating headers
        for col, col_name, width in headers:
            self.tree.heading(col, text=col_name, anchor="w")
            self.tree.column(col, width=width, anchor="w")


        #INSERTING DATA DEPENDING ON search_type
        limit = 1000
        if scan_type == "duplicates":

            count = 0

            for (size, _), files in data.items():

                if count >= limit:
                    break

                size_str, size_tag = self.determine_color(size)

                for path in files:

                    if count >= limit:
                        break

                    self.tree.insert(
                        "",
                        "end",
                        iid=path,
                        values=(os.path.basename(path), os.path.dirname(path), size_str),
                        tags=size_tag
                    )
                    count+=1
        elif scan_type == "space":

            count = 0

            for size, files in data.items():

                if count >= limit:
                    break

                size_str, row_tag = self.determine_color(size)

                for path in files:

                    if count >= limit:
                        break

                    self.tree.insert(
                        "",
                        "end",
                        iid=path,
                        values=(os.path.basename(path), os.path.dirname(path), size_str),
                        tags=row_tag
                    )
                    count+=1

        else:
            messagebox.showerror(
                "ERROR",
                "Unknown scan type specified, try restarting the application."
            )


        self.delete_btn = ctk.CTkButton(
            self.result_container,
            text="Delete selected: 0",
            command=self.delete_selected,
            fg_color="transparent",
            border_width=1,
            border_color="#cc0000",
            text_color="#ff4d4d",
            hover_color="#303030",
            corner_radius=1,
            font=(FONT, 12)
        )
        self.delete_btn.pack(pady=(15, 0), ipadx=20)

        self.tree.bind(
            "<<TreeviewSelect>>",
            lambda e: self.delete_btn.configure(
                text=f"Delete selected: {len([item for item in self.tree.selection()])}"
            )
        )
        self.tree.bind(
            "<Double-1>",
            self.on_item_double_click
        )

    def delete_selected(self):

        selected_paths = [path for path in self.tree.selection()]

        if not selected_paths:
            return

        file_count = 0
        dir_count = 0

        for file_path in selected_paths:
            if os.path.isdir(file_path):
                dir_count += 1
            else:
                file_count += 1

        confirm = messagebox.askyesno(
            "Confirmation of deletion",
            f"Are you sure you want to permanently delete:\n"
            f" \t {dir_count} directories\n"
            f" \t {file_count} files\n\n"
            "This operation cannot be undone!"
        )

        if not confirm:
            return

        failed_deletes = []
        successful_deletes = 0

        for file_path in selected_paths:
            try:
                self.controller.delete_file(file_path)

                self.tree.delete(file_path)
                successful_deletes += 1
            except FileDeletionError as e:
                error_msg = str(e)

                if error_msg == "not_found":
                    failed_deletes.append((file_path, "File no longer exists"))
                    self.tree.delete(file_path)
                else:
                    failed_deletes.append((file_path, error_msg))

        if failed_deletes:
            msg = f"Unable to delete {len(failed_deletes)} files. They could be in use or no longer exist."
            messagebox.showwarning("WARNING", msg)

        if successful_deletes > 0:
            self.controller.delete_cache()
            messagebox.showinfo(
                "INFO",
                f"Successfully deleted: {successful_deletes}"
            )

        valid_selection = [item for item in self.tree.selection()]
        self.delete_btn.configure(text=f"Delete selected: {len(valid_selection)}")


    def on_item_double_click(self, event):
        selected_paths = self.tree.selection()
        if not selected_paths:
            return

        path=selected_paths[0]

        if os.path.isdir(path):
            self.controller.dir_change(path, path)

    def determine_color(self, size):
        kb, mb, gb = 1024, 1024 ** 2, 1024 ** 3

        if size >= 5 * gb:         return f"██████  {size / gb:.2f} GB", "lvl_7"
        elif size >= 2.5 * gb:     return f"█████  {size / gb:.2f} GB", "lvl_6"
        elif size >= gb:           return f"████  {size / gb:.2f} GB", "lvl_5"
        elif size >= 250 * mb:     return f"███  {size / mb:.2f} MB", "lvl_4"
        elif size >= 50 * mb:      return f"██  {size / mb:.2f} MB", "lvl_3"
        elif size >= mb:           return f"█  {size / mb:.2f} MB", "lvl_2"
        else:                      return f"|  {size / kb:.2f} KB", "lvl_1"





import customtkinter as ctk
import os
import threading
import tksvg
from tkinter import filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES

try:
    from .engine import convert
except (ImportError, ValueError):
    from engine import convert

class TkDnD(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

class PyctureApp:
    def __init__(self):
        ctk.set_appearance_mode("dark")  
        ctk.set_default_color_theme("blue")

        self.app = TkDnD()
        self.app.geometry("450x550") 
        self.app.title("PyctureConverter")

        self.selected_file_path = ""

        self.camera_icon = self._load_icon("camera.svg")
        if self.camera_icon:
            self.app.wm_iconphoto(False, self.camera_icon)
        self.image_icon = self._load_icon("image.svg")
        self.magic_wand_icon = self._load_icon("magic-wand.svg")
        self.prohibit_icon = self._load_icon("prohibit.svg")
        self.hourglass_icon = self._load_icon("hourglass.svg")
        self.upload_icon = self._load_icon("upload-simple.svg", scale=2.0) 

        self.title_label = ctk.CTkLabel(
            self.app, 
            text=" PyctureConverter", 
            font=("Arial", 24, "bold"),
            image=self.camera_icon,
            compound="left"
        )
        self.title_label.pack(pady=(20, 10))

        self.upload_frame = ctk.CTkFrame(
            self.app, 
            width=350, 
            height=200, 
            fg_color="transparent",
            border_width=2,
            border_color="#555555" 
        )
        self.upload_frame.pack(pady=20, padx=20, fill="both", expand=True)
        self.upload_frame.pack_propagate(False)

        self.drop_label = ctk.CTkLabel(
            self.upload_frame,
            text="\n\nClick to Select an Image\n(or drag & drop here)",
            image=self.upload_icon,
            compound="top",
            text_color="gray",
            font=("Arial", 14)
        )
        self.drop_label.pack(expand=True, fill="both")

        self.drop_label.bind("<Button-1>", lambda e: self.select_image())
        self.drop_label.bind("<Enter>", lambda e: self.app.config(cursor="hand2"))
        self.drop_label.bind("<Leave>", lambda e: self.app.config(cursor=""))

        self.upload_frame.drop_target_register(DND_FILES)
        self.upload_frame.dnd_bind('<<Drop>>', self.handle_drop)
        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind('<<Drop>>', self.handle_drop)

        self.status_label = ctk.CTkLabel(
            self.app, 
            text="No image selected.", 
            text_color="gray",
            image=self.prohibit_icon,
            compound="left"
        )
        self.status_label.pack(pady=(0, 10))

        self.control_frame = ctk.CTkFrame(self.app, fg_color="transparent")
        self.control_frame.pack(pady=10)

        self.format_label = ctk.CTkLabel(self.control_frame, text="Convert to:")
        self.format_label.pack(side="left", padx=(0, 10))

        self.format_var = ctk.StringVar(value="SVG") 
        self.format_dropdown = ctk.CTkOptionMenu(
            self.control_frame, 
            variable=self.format_var, 
            values=["SVG", "PNG", "JPEG", "WEBP", "ICO"]
        )
        self.format_dropdown.pack(side="left")

        self.convert_button = ctk.CTkButton(
            self.app, 
            text="Convert!", 
            command=self.start_conversion, 
            fg_color="#2FA572", 
            hover_color="#1D7850",
            image=self.magic_wand_icon,
            compound="left",
            height=40, 
            font=("Arial", 16, "bold")
        )
        self.convert_button.pack(pady=(10, 20))

    def _load_icon(self, filename, color="white", scale=0.8):
        assets_path = os.path.join(os.path.dirname(__file__), "..", "assets", filename)
        if not os.path.exists(assets_path):
            assets_path = os.path.join(os.path.dirname(__file__), "assets", filename)
            if not os.path.exists(assets_path):
                assets_path = os.path.join("assets", filename)

        try:
            with open(assets_path, "r") as f:
                svg_data = f.read()
            svg_data = svg_data.replace('fill="#000000"', f'fill="{color}"')
            return tksvg.SvgImage(data=svg_data, scale=scale) 
        except Exception as e:
            print(f"Warning: Could not load icon {filename}: {e}")
            return None

    def handle_drop(self, event):
        files = self.app.tk.splitlist(event.data)
        if files:
            file_path = files[0]
            self.selected_file_path = file_path
            file_name = os.path.basename(file_path)
            self.status_label.configure(text=f"Ready: {file_name}", text_color="white", image=self.image_icon)

    def select_image(self):
        file_path = filedialog.askopenfilename(
            title="Select a Pycture",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.webp;*.bmp")]
        )
        if file_path:
            self.selected_file_path = file_path
            file_name = os.path.basename(file_path)
            self.status_label.configure(text=f"Ready: {file_name}", text_color="white", image=self.image_icon)

    def start_conversion(self):
        if not self.selected_file_path:
            self.status_label.configure(text="Please choose an image first!", text_color="red", image=self.prohibit_icon)
            return

        target_format = self.format_var.get()
        self.status_label.configure(text="Converting...", text_color="yellow", image=self.hourglass_icon)

        self.convert_button.configure(state="disabled")

        threading.Thread(target=self._run_conversion_thread, args=(self.selected_file_path, target_format), daemon=True).start()

    def _run_conversion_thread(self, file_path, target_format):
        try:
            output_path = convert(file_path, target_format)
            self._update_status_success(output_path)
        except Exception as e:
            self._update_status_error(str(e))
        finally:
            def reenable_button():
                self.convert_button.configure(state="normal")
            self.app.after(0, reenable_button)

    def _update_status_success(self, output_path):
        filename = os.path.basename(output_path)

        def update_ui():
            self.status_label.configure(text=f"Success! Saved: {filename}", text_color="#2FA572", image=self.image_icon)
            messagebox.showinfo("Success", f"Saved: {output_path}")

        self.app.after(0, update_ui)

    def _update_status_error(self, error_message):
        def update_ui():
            self.status_label.configure(text=f"Error: {error_message}", text_color="red", image=self.prohibit_icon)
            
        self.app.after(0, update_ui)

    def run(self):
        self.app.mainloop()

if __name__ == "__main__":
    app = PyctureApp()
    app.run()

# app.py
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
from extractor import VideoExtractor
import threading
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class VideoFrameApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🎞 Video Frame Extractor")
        self.geometry("1200x760")
        self.minsize(1100, 720)

        self.extractor = None
        self.output_dir = None
        self.in_time = 0.0
        self.out_time = 0.0
        self.preview_image = None

        self._build_ui()

    # ================= UI =================
    def _build_ui(self):
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)

        # ===== HEADER =====
        header = ctk.CTkFrame(self, height=60)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=15, pady=(15, 8))
        header.grid_columnconfigure(2, weight=1)

        ctk.CTkButton(
            header, text="📂 Abrir video", width=150,
            command=self.load_video
        ).grid(row=0, column=0, padx=15, pady=12)

        # --- Switch sistema ---
        self.system_var = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(
            header,
            text="Modo sistema",
            variable=self.system_var,
            command=self.toggle_system_mode
        ).grid(row=0, column=1, padx=10)

        self.info = ctk.CTkLabel(header, text="Ningún video cargado", anchor="w")
        self.info.grid(row=0, column=2, sticky="w")

        # ===== LEFT: VIDEO =====
        video_panel = ctk.CTkFrame(self)
        video_panel.grid(row=1, column=0, sticky="nsew", padx=(15, 8), pady=10)
        video_panel.grid_rowconfigure(1, weight=1)
        video_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            video_panel, text="Preview",
            font=("Segoe UI", 16, "bold")
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(12, 6))

        self.preview = ctk.CTkLabel(
            video_panel,
            text="Cargue un video",
            corner_radius=12,
            fg_color="#1f1f1f"
        )
        self.preview.grid(row=1, column=0, sticky="nsew", padx=15, pady=15)

        # ===== RIGHT: CONTROLS =====
        controls = ctk.CTkFrame(self)
        controls.grid(row=1, column=1, sticky="nsew", padx=(8, 15), pady=10)
        controls.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            controls, text="Controles",
            font=("Segoe UI", 16, "bold")
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(12, 15))

        # --- IN ---
        ctk.CTkLabel(controls, text="⏱ Inicio (segundos)").grid(
            row=1, column=0, sticky="w", padx=15
        )

        self.in_slider = ctk.CTkSlider(
            controls, from_=0, to=100, command=self.on_in_change
        )
        self.in_slider.grid(row=2, column=0, sticky="ew", padx=15)

        self.in_label = ctk.CTkLabel(controls, text="0.00 s")
        self.in_label.grid(row=3, column=0, sticky="e", padx=15, pady=(0, 10))

        # --- OUT ---
        ctk.CTkLabel(controls, text="⏱ Fin (segundos)").grid(
            row=4, column=0, sticky="w", padx=15
        )

        self.out_slider = ctk.CTkSlider(
            controls, from_=0, to=100, command=self.on_out_change
        )
        self.out_slider.grid(row=5, column=0, sticky="ew", padx=15)

        self.out_label = ctk.CTkLabel(controls, text="0.00 s")
        self.out_label.grid(row=6, column=0, sticky="e", padx=15, pady=(0, 15))

        # --- EXPORT ---
        ctk.CTkLabel(controls, text="Exportación").grid(
            row=7, column=0, sticky="w", padx=15, pady=(10, 6)
        )

        ctk.CTkButton(
            controls, text="📁 Carpeta de salida",
            command=self.select_output
        ).grid(row=8, column=0, sticky="ew", padx=15, pady=5)

        self.prefix = ctk.CTkEntry(controls)
        self.prefix.insert(0, "frame_")
        self.prefix.grid(row=9, column=0, sticky="ew", padx=15, pady=5)

        self.start_index = ctk.CTkEntry(controls)
        self.start_index.insert(0, "1")
        self.start_index.grid(row=10, column=0, sticky="ew", padx=15, pady=5)

        self.save_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            controls, text="Guardar imágenes",
            variable=self.save_var
        ).grid(row=11, column=0, sticky="w", padx=15, pady=10)

        ctk.CTkButton(
            controls, text="🚀 Procesar rango",
            height=40, command=self.process
        ).grid(row=12, column=0, sticky="ew", padx=15, pady=(10, 20))

        self.progress = ctk.CTkProgressBar(controls)
        self.progress.set(0)
        self.progress.grid(
            row=13, column=0,
            sticky="ew", padx=15, pady=(0, 15)
        )

        # ===== FOOTER =====
        footer = ctk.CTkFrame(self, height=36)
        footer.grid(row=2, column=0, columnspan=2, sticky="ew")

        ctk.CTkLabel(
            footer, text="IngSystemCix · Video Tools",
            text_color="gray"
        ).pack(pady=6)

    # ================= LOGIC =================
    def toggle_system_mode(self):
        mode = "system" if self.system_var.get() else "dark"
        ctk.set_appearance_mode(mode)

    def load_video(self):
        path = filedialog.askopenfilename(
            filetypes=[("Videos", "*.mp4 *.avi *.mkv *.mov")]
        )
        if not path:
            return

        self.extractor = VideoExtractor(path)
        duration = self.extractor.duration

        self.in_slider.configure(to=duration)
        self.out_slider.configure(to=duration)
        self.out_slider.set(duration)

        self.in_time = 0.0
        self.out_time = duration

        self.in_label.configure(text="0.00 s")
        self.out_label.configure(text=f"{duration:.2f} s")

        self.info.configure(
            text=f"{os.path.basename(path)} · {duration:.2f}s · {self.extractor.fps:.2f} FPS"
        )

        self.show_frame(0)

    def show_frame(self, seconds):
        if not self.extractor:
            return

        frame = self.extractor.get_frame_by_time(seconds)
        if frame is None:
            return

        img = Image.fromarray(frame)
        img.thumbnail((900, 520))

        self.preview_image = ctk.CTkImage(light_image=img, size=img.size)
        self.preview.configure(image=self.preview_image, text="")

    def on_in_change(self, value):
        self.in_time = float(value)

        if self.in_time > self.out_time:
            self.out_time = self.in_time
            self.out_slider.set(self.out_time)
            self.out_label.configure(text=f"{self.out_time:.2f} s")

        self.in_label.configure(text=f"{self.in_time:.2f} s")
        self.show_frame(self.in_time)

    def on_out_change(self, value):
        self.out_time = float(value)

        if self.out_time < self.in_time:
            self.in_time = self.out_time
            self.in_slider.set(self.in_time)
            self.in_label.configure(text=f"{self.in_time:.2f} s")

        self.out_label.configure(text=f"{self.out_time:.2f} s")
        self.show_frame(self.out_time)

    def select_output(self):
        self.output_dir = filedialog.askdirectory()

    def process(self):
        if not self.extractor or not self.output_dir:
            self.info.configure(text="❌ Falta cargar video o carpeta")
            return

        start = self.in_time
        end = self.out_time

        self.progress.set(0)

        def update_progress(value):
            # value viene de 0.0 a 1.0
            self.progress.set(value)
            percent = int(value * 100)
            self.info.configure(text=f"Procesando… {percent}%")

        def task():
            self.extractor.extract_range( # type: ignore
                start_sec=start,
                end_sec=end,
                output_dir=self.output_dir,
                prefix=self.prefix.get(),
                start_index=int(self.start_index.get()),
                save=self.save_var.get(),
                progress_callback=update_progress
            )
            self.info.configure(text="✔ Proceso completado")
            self.progress.set(1)

        threading.Thread(target=task, daemon=True).start()



if __name__ == "__main__":
    VideoFrameApp().mainloop()

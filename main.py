import os
import sys
import shutil
import tempfile
import webbrowser
import threading
import subprocess
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageFilter, ImageDraw

import customtkinter as ctk

# Configuración inicial de CustomTkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class GlassButton(ctk.CTkButton):
    """Botón con estilo Liquid Glass (Efecto Cristal)"""
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            corner_radius=16,
            fg_color="#2A2D3E",
            hover_color="#3B3E54",
            border_width=1.5,
            border_color="#4A4E69",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            **kwargs
        )


class NetComApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("NetCom - Limpiador Digital")
        self.geometry("900x600")
        self.minsize(850, 550)

        # Cargar imagen de logo si existe
        self.logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
        self.logo_image = None
        if os.path.exists(self.logo_path):
            img = Image.open(self.logo_path)
            self.logo_image = ctk.CTkImage(light_image=img, dark_image=img, size=(60, 60))

        # Fondo degradado difuminado (Rojo, Verde y Azul)
        self.canvas_bg = tk.Canvas(self, highlightthickness=0)
        self.canvas_bg.pack(fill="both", expand=True)
        self.bind("<Configure>", self._draw_gradient_background)

        # Contenedor principal superpuesto al canvas
        self.main_container = ctk.CTkFrame(self.canvas_bg, fg_color="transparent")
        self.main_container.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Menú Lateral Izquierdo (Panel Glass)
        self.sidebar = ctk.CTkFrame(
            self.main_container,
            width=220,
            corner_radius=20,
            fg_color="#0F0F19",
            border_width=1,
            border_color="#33334D"
        )
        self.sidebar.pack(side="left", fill="y", padx=15, pady=15)
        self.sidebar.pack_propagate(False)

        # Header con Logo y Nombre de la app
        if self.logo_image:
            self.lbl_logo = ctk.CTkLabel(self.sidebar, image=self.logo_image, text="")
            self.lbl_logo.pack(pady=(20, 5))

        self.lbl_title = ctk.CTkLabel(
            self.sidebar, text="NetCom",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color="#FFFFFF"
        )
        self.lbl_title.pack(pady=(0, 20))

        # Botones de navegación lateral
        self.btn_nav_cleaner = GlassButton(
            self.sidebar,
            text="🧹  Limpiador",
            command=self.show_cleaner_page
        )
        self.btn_nav_cleaner.pack(fill="x", padx=15, pady=10)

        self.btn_nav_cetcom = GlassButton(
            self.sidebar,
            text="🌐  CETCOM",
            command=self.open_cetcom_website
        )
        self.btn_nav_cetcom.pack(fill="x", padx=15, pady=10)

        # Contenido Central
        self.content_frame = ctk.CTkFrame(
            self.main_container,
            corner_radius=20,
            fg_color="#141423",
            border_width=1,
            border_color="#33334D"
        )
        self.content_frame.pack(side="right", fill="both", expand=True, padx=(0, 15), pady=15)

        self.setup_cleaner_ui()

    def _draw_gradient_background(self, event=None):
        """Genera un fondo degradado difuminado en tonos Rojo, Verde y Azul"""
        width = self.winfo_width()
        height = self.winfo_height()

        if width <= 1 or height <= 1:
            return

        img = Image.new("RGB", (width, height), "#0a0a12")
        draw = ImageDraw.Draw(img)

        # Esferas de luz de colores Rojo, Verde y Azul
        draw.ellipse([-width*0.2, -height*0.2, width*0.6, height*0.6], fill=(180, 30, 60))    # Rojo
        draw.ellipse([width*0.4, height*0.3, width*1.2, height*1.1], fill=(20, 140, 80))     # Verde
        draw.ellipse([width*0.1, height*0.5, width*0.8, height*1.2], fill=(30, 80, 200))     # Azul

        blurred_img = img.filter(ImageFilter.GaussianBlur(radius=80))
        self.bg_photo = ImageTk.PhotoImage(blurred_img)

        self.canvas_bg.delete("all")
        self.canvas_bg.create_image(0, 0, image=self.bg_photo, anchor="nw")

    def setup_cleaner_ui(self):
        """Pantalla principal del limpiador digital"""
        self.cleaner_box = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.cleaner_box.pack(fill="both", expand=True, padx=25, pady=25)

        title = ctk.CTkLabel(
            self.cleaner_box,
            text="Módulo de Limpieza Digital",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#FFFFFF"
        )
        title.pack(anchor="w", pady=(0, 5))

        subtitle = ctk.CTkLabel(
            self.cleaner_box,
            text="Elimina cookies, caché DNS, archivos temporales y vacía la papelera de reciclaje.",
            font=ctk.CTkFont(size=13),
            text_color="#B0B0C0"
        )
        subtitle.pack(anchor="w", pady=(0, 20))

        # Log de consola
        self.log_text = ctk.CTkTextbox(
            self.cleaner_box,
            fg_color="#0A0A14",
            text_color="#80FF80",
            font=ctk.CTkFont(family="Consolas", size=12),
            corner_radius=12,
            border_width=1,
            border_color="#2A2A3D"
        )
        self.log_text.pack(fill="both", expand=True, pady=(0, 20))
        self.log_text.insert("1.0", ">>> NetCom preparado. Haz clic en 'Iniciar Limpieza Completa' para comenzar.\n")
        self.log_text.configure(state="disabled")

        # Barra de progreso
        self.progress_bar = ctk.CTkProgressBar(self.cleaner_box, progress_color="#00E676")
        self.progress_bar.pack(fill="x", pady=(0, 15))
        self.progress_bar.set(0)

        # Botón estilo Liquid Glass
        self.btn_start = GlassButton(
            self.cleaner_box,
            text="🚀 INICIAR LIMPIEZA COMPLETA",
            height=45,
            command=self.start_cleaning_thread
        )
        self.btn_start.pack(fill="x")

    def log(self, message):
        """Escribe mensajes en el cuadro de registro"""
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def show_cleaner_page(self):
        pass

    def open_cetcom_website(self):
        webbrowser.open("https://www.cetcom.es/")

    def start_cleaning_thread(self):
        self.btn_start.configure(state="disabled")
        self.progress_bar.set(0)
        threading.Thread(target=self.run_cleaning_process, daemon=True).start()

    def run_cleaning_process(self):
        """Proceso completo de eliminación de basura digital y caché DNS"""
        self.log("\n[+] Iniciando proceso de optimización NetCom...")
        
        # 1. Archivos Temporales de Windows y Usuario
        self.log("[1/4] Limpiando carpetas de archivos temporales (%TEMP%)...")
        temp_paths = [tempfile.gettempdir(), r"C:\Windows\Temp"]
        
        for path in temp_paths:
            if os.path.exists(path):
                try:
                    items = os.listdir(path)
                except PermissionError:
                    self.log(f"    ⚠ Permiso denegado al leer {path}. Omitiendo archivos protegidos por el sistema.")
                    continue
                except Exception:
                    continue

                for item in items:
                    item_path = os.path.join(path, item)
                    try:
                        if os.path.isfile(item_path) or os.path.islink(item_path):
                            os.unlink(item_path)
                        elif os.path.isdir(item_path):
                            shutil.rmtree(item_path, ignore_errors=True)
                    except Exception:
                        pass
        self.progress_bar.set(0.25)

        # 2. Vaciado de Caché DNS
        self.log("[2/4] Vaciando la caché del solucionador DNS (ipconfig /flushdns)...")
        try:
            subprocess.run(["ipconfig", "/flushdns"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            self.log("    ✔ Caché DNS limpiada correctamente.")
        except Exception as e:
            self.log(f"    ⚠ No se pudo vaciar la caché DNS: {e}")
        self.progress_bar.set(0.50)

        # 3. Caché y Cookies de Navegadores
        self.log("[3/4] Eliminando datos de caché y cookies de navegadores...")
        user_profile = os.environ.get("USERPROFILE", "")
        browser_paths = [
            os.path.join(user_profile, r"AppData\Local\Google\Chrome\User Data\Default\Cache"),
            os.path.join(user_profile, r"AppData\Local\Microsoft\Edge\User Data\Default\Cache"),
            os.path.join(user_profile, r"AppData\Local\Mozilla\Firefox\Profiles")
        ]
        
        for b_path in browser_paths:
            if os.path.exists(b_path):
                try:
                    for root, dirs, files in os.walk(b_path):
                        for f in files:
                            try:
                                os.remove(os.path.join(root, f))
                            except Exception:
                                pass
                except Exception:
                    pass
        self.progress_bar.set(0.75)

        # 4. Vaciado de Papelera de Reciclaje
        self.log("[4/4] Solicitando vaciado de la Papelera de Reciclaje...")
        try:
            import ctypes
            ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 7)
            self.log("    ✔ Papelera de reciclaje limpiada.")
        except Exception:
            pass
        self.progress_bar.set(1.0)

        self.log("\n[✔] ¡Limpieza completa realizada con éxito!")
        messagebox.showinfo("NetCom", "¡La limpieza digital de su sistema y red se ha completado con éxito!")
        self.btn_start.configure(state="normal")


if __name__ == "__main__":
    app = NetComApp()
    app.mainloop()
    
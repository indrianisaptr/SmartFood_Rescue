""""
Kode ini berfungsi sebagai antarmuka antarmuka (GUI) untuk mendeteksi kesegaran buah dan sayur.

Tujuan dari kode ini :
1. Memuat Model: Mengintegrasikan `best.pt` untuk mengklasifikasi kondisi buah/sayur (Fresh vs Rotten).
2. Menampilkan Hasil: Menyajikan status kesegaran, skor akurasi, dan rekomendasi penanganan pada antarmuka GUI.
"""

import os
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
from ultralytics import YOLO

class ModernFoodRescueApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistem Scanning Kesegaran Buah dan Sayur")
        self.root.geometry("540x780")
        self.root.resizable(False, False)
        self.COLOR_BG = "#F8FAFC"         
        self.COLOR_CARD = "#FFFFFF"       
        self.COLOR_PRIMARY = "#2563EB"    
        self.COLOR_PRIMARY_HOVER = "#1D4ED8"
        self.COLOR_TEXT_DARK = "#0F172A" 
        self.COLOR_TEXT_MUTED = "#64748B" 
        self.COLOR_BORDER = "#E2E8F0"
        self.root.configure(bg=self.COLOR_BG)

        # Header Section
        self.header_frame = tk.Frame(root, bg=self.COLOR_BG)
        self.header_frame.pack(fill="x", padx=30, pady=(20, 10))

        self.title_label = tk.Label(
            self.header_frame, 
            text="SMART FOOD RESCUE", 
            font=("Segoe UI", 16, "bold"), 
            bg=self.COLOR_BG, 
            fg=self.COLOR_TEXT_DARK
        )
        self.title_label.pack(anchor="w")

        self.subtitle_label = tk.Label(
            self.header_frame, 
            text="Inspeksi Kualitas & Kesegaran Buah dan Sayur", 
            font=("Segoe UI", 9), 
            bg=self.COLOR_BG, 
            fg=self.COLOR_TEXT_MUTED
        )
        self.subtitle_label.pack(anchor="w", pady=(2, 0))

        # Image Preview Card
        self.card_image = tk.Frame(
            root, 
            bg=self.COLOR_CARD, 
            highlightbackground=self.COLOR_BORDER, 
            highlightthickness=1
        )
        self.card_image.pack(fill="x", padx=30, pady=5)

        self.image_container = tk.Frame(self.card_image, width=280, height=280, bg="#F1F5F9")
        self.image_container.pack_propagate(False)
        self.image_container.pack(pady=12, padx=12)

        self.image_label = tk.Label(
            self.image_container, 
            text="📷 Belum Ada Gambar Terpilih\nKlik tombol di bawah untuk memilih", 
            font=("Segoe UI", 9), 
            bg="#F1F5F9", 
            fg=self.COLOR_TEXT_MUTED,
            justify="center"
        )
        self.image_label.pack(expand=True)

        # Action Button
        self.btn_select = tk.Button(
            root, 
            text="📂 Pilih Gambar Buah atau Sayur", 
            font=("Segoe UI", 10, "bold"), 
            bg=self.COLOR_PRIMARY, 
            fg="white", 
            activebackground=self.COLOR_PRIMARY_HOVER,
            activeforeground="white",
            pady=8, 
            relief="flat",
            cursor="hand2",
            command=self.proses_scan
        )
        self.btn_select.pack(fill="x", padx=30, pady=10)

        self.btn_camera = tk.Button(
            root, 
            text="Scan via Kamera", 
            font=("Segoe UI", 10, "bold"), 
            bg=self.COLOR_TEXT_DARK, 
            fg="white", 
            activebackground=self.COLOR_TEXT_DARK,
            activeforeground="white",
            pady=8, 
            relief="flat",
            cursor="hand2",
            command=self.buka_kamera
        )
        self.btn_camera.pack(fill="x", padx=30, pady=(0, 10))

        # Result & Recomendation Card
        self.card_result = tk.Frame(
            root, 
            bg=self.COLOR_CARD, 
            highlightbackground=self.COLOR_BORDER, 
            highlightthickness=1,
            padx=18,
            pady=12
        )
        self.card_result.pack(fill="x", padx=30, pady=(5, 15))

        # File Name Label
        self.lbl_filename = tk.Label(
            self.card_result, 
            text="Nama File : -", 
            font=("Segoe UI", 9), 
            bg=self.COLOR_CARD, 
            fg=self.COLOR_TEXT_MUTED, 
            anchor="w"
        )
        self.lbl_filename.pack(fill="x", pady=(0, 4))

        # Category Badge Header
        self.result_header_frame = tk.Frame(self.card_result, bg=self.COLOR_CARD)
        self.result_header_frame.pack(fill="x", pady=2)

        self.lbl_category_title = tk.Label(
            self.result_header_frame, 
            text="Status Kesegaran:", 
            font=("Segoe UI", 9, "bold"), 
            bg=self.COLOR_CARD, 
            fg=self.COLOR_TEXT_DARK
        )
        self.lbl_category_title.pack(side="left")

        self.lbl_category = tk.Label(
            self.result_header_frame, 
            text="-", 
            font=("Segoe UI", 10, "bold"), 
            bg=self.COLOR_CARD, 
            fg=self.COLOR_TEXT_MUTED,
            padx=8,
            pady=2
        )
        self.lbl_category.pack(side="left", padx=8)

        # Accuracy Score Label
        self.lbl_confidence = tk.Label(
            self.card_result, 
            text="Akurasi Deteksi : -", 
            font=("Segoe UI", 9), 
            bg=self.COLOR_CARD, 
            fg=self.COLOR_TEXT_MUTED, 
            anchor="w"
        )
        self.lbl_confidence.pack(fill="x", pady=(4, 8))

        # Separator Line
        ttk.Separator(self.card_result, orient="horizontal").pack(fill="x", pady=6)

        # Description Header & Text
        self.lbl_desc_title = tk.Label(
            self.card_result, 
            text="Deskripsi & Rekomendasi:", 
            font=("Segoe UI", 9, "bold"), 
            bg=self.COLOR_CARD, 
            fg=self.COLOR_TEXT_DARK, 
            anchor="w"
        )
        self.lbl_desc_title.pack(fill="x", pady=(2, 4))

        self.lbl_description = tk.Label(
            self.card_result, 
            text="Silakan pilih gambar buah atau sayur untuk melihat indikasi visual dan saran penanganan.", 
            font=("Segoe UI", 9), 
            bg=self.COLOR_CARD, 
            fg=self.COLOR_TEXT_MUTED, 
            justify="left", 
            wraplength=430,
            anchor="w"
        )
        self.lbl_description.pack(fill="x")

        # Load Model YOLO
        self.load_model()

    def load_model(self):
        # Memuat path model best.pt
        self.model_path = os.path.join("kode", "runs", "freshness_yolo_cls", "weights", "best.pt")
        if not os.path.exists(self.model_path):
            self.model_path = os.path.join("runs", "freshness_yolo_cls", "weights", "best.pt")

        if os.path.exists(self.model_path):
            print(f"🔄 Memuat model dari: {self.model_path}")
            self.model = YOLO(self.model_path)
        else:
            messagebox.showerror("Error Model", f"File model 'best.pt' tidak ditemukan di:\n{self.model_path}")
            self.model = None

    def proses_scan(self):
        if not self.model:
            messagebox.showerror("Error", "Model YOLO belum berhasil dimuat!")
            return

        # Buka dialog pilih gambar
        image_path = filedialog.askopenfilename(
            title="Pilih Gambar Buah atau Sayur",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.webp"), ("All Files", "*.*")]
        )

        if not image_path:
            return

        # Tampilkan Gambar ke UI
        img = Image.open(image_path)
        img_resized = img.resize((270, 270), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img_resized)
        
        self.image_label.config(image=img_tk, text="")
        self.image_label.image = img_tk 

        self.jalankan_prediksi(image_path)

    def jalankan_prediksi(self, image_path):
        # Scanning
        results = self.model.predict(source=image_path, verbose=False)

        for result in results:
            top1_id = result.probs.top1
            class_name = result.names[top1_id].upper()
            confidence = result.probs.top1conf.item() * 100
            nama_file = os.path.basename(image_path)

            # Update Label Hasil
            self.lbl_filename.config(text=f"Nama File : {nama_file}")
            self.lbl_confidence.config(text=f"Akurasi Deteksi : {confidence:.2f}%")

            # Pengkondisian Warna Badge & Deskripsi Rekomendasi
            if "FRESH" in class_name or "GOOD" in class_name:
                self.lbl_category.config(
                    text=f"{class_name}", 
                    bg="#DCFCE7",  
                    fg="#15803D" 
                )
                
                deskripsi_teks = (
                    "💡 Status: Buah/sayur terindikasi segar secara visual.\n"
                    "Rekomendasi: Sangat layak dikonsumsi langsung atau disimpan di pendingin (kulkas) "
                    "untuk menjaga kualitas kesegarannya lebih lama."
                )
            else:
                self.lbl_category.config(
                    text=f"{class_name}", 
                    bg="#FEE2E2",  
                    fg="#B91C1C" 
                )
                
                deskripsi_teks = (
                    "⚠️ Status: Buah/sayur terindikasi pembusukan/kerusakan secara visual.\n"
                    "Rekomendasi: Sebaiknya dipisahkan dari bahan segar lainnya agar tidak menular, "
                    "atau segera diproses menjadi kompos (food waste) jika tidak layak dikonsumsi."
                )

            self.lbl_description.config(text=deskripsi_teks)

    def buka_kamera(self):
        if not self.model:
            messagebox.showerror("Error", "Model YOLO belum berhasil dimuat!")
            return

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Kamera tidak bisa diakses!")
            return

        self.current_frame = None
        self.cam_window = tk.Toplevel(self.root)
        self.cam_window.title("Live Kamera - Tekan SPASI untuk Capture")
        self.cam_window.resizable(False, False)

        self.cam_label = tk.Label(self.cam_window)
        self.cam_label.pack()

        self.lbl_cam_hint = tk.Label(
            self.cam_window,
            text="Tekan SPASI untuk mengambil gambar",
            font=("Segoe UI", 9),
            fg=self.COLOR_TEXT_MUTED
        )
        self.lbl_cam_hint.pack(pady=(4, 8))

        self.cam_window.bind("<space>", self.capture_frame)
        self.cam_window.focus_set()
        self.cam_window.protocol("WM_DELETE_WINDOW", self.tutup_kamera)

        self.update_frame()

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            self.current_frame = frame
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img_tk = ImageTk.PhotoImage(img)
            self.cam_label.imgtk = img_tk
            self.cam_label.config(image=img_tk)
        self._after_id = self.cam_window.after(15, self.update_frame)

    def capture_frame(self, event=None):
        if self.current_frame is None:
            return

        temp_path = os.path.join(os.getcwd(), "temp_capture.jpg")
        cv2.imwrite(temp_path, self.current_frame)
        self.tutup_kamera()

        img = Image.open(temp_path)
        img_resized = img.resize((270, 270), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img_resized)
        self.image_label.config(image=img_tk, text="")
        self.image_label.image = img_tk

        self.jalankan_prediksi(temp_path)

    def tutup_kamera(self):
        self.cam_window.after_cancel(self._after_id)
        self.cap.release()
        self.cam_window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernFoodRescueApp(root)
    root.mainloop()
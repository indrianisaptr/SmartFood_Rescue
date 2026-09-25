"""
config.py
=========
File ini berisi SEMUA path dan konstanta yang dipakai di seluruh project.
Kalau lokasi dataset kamu berbeda, cukup ubah nilai di sini saja —
file lain (check_dataset.py, prepare_dataset.py, train.py, dst) akan
otomatis mengikuti.
"""

from pathlib import Path

# -----------------------------------------------------------------------
# 1. PATH DASAR PROJECT
# -----------------------------------------------------------------------
# PROJECT_ROOT dihitung otomatis dari lokasi file ini (src/config.py),
# jadi tidak perlu diubah walau kamu memindahkan folder project.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# -----------------------------------------------------------------------
# 2. PATH DATASET MENTAH (RAW) — SESUAIKAN DENGAN LOKASI ASLI KAMU
# -----------------------------------------------------------------------
# Berdasarkan screenshot yang kamu kirim, dataset asli ada di:
#   /mnt/d/Semester 7/SistemCerdas_FoodWaste/Dataset/Bad Quality_Fruits
#   /mnt/d/Semester 7/SistemCerdas_FoodWaste/Dataset/Good Quality_Fruits
# Ubah baris di bawah ini jika lokasi dataset kamu berbeda.
RAW_DATASET_DIR = Path("/mnt/d/Semester 7/SistemCerdas_FoodWaste/Dataset")
RAW_BAD_DIR = RAW_DATASET_DIR / "Bad Quality_Fruits"
RAW_GOOD_DIR = RAW_DATASET_DIR / "Good Quality_Fruits"

# Ekstensi gambar yang dianggap valid
VALID_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

# -----------------------------------------------------------------------
# 3. NAMA KELAS FINAL (setelah digabung jadi 2 kelas)
# -----------------------------------------------------------------------
# Semua folder yang mengandung "_Good" -> kelas "Fresh"
# Semua folder yang mengandung "_Bad"  -> kelas "Rotten"
CLASS_NAMES = ["Fresh", "Rotten"]

# -----------------------------------------------------------------------
# 4. PATH DATASET HASIL OLAHAN (siap dipakai Ultralytics YOLO classification)
# -----------------------------------------------------------------------
# Struktur yang dibutuhkan Ultralytics untuk task classification:
#   dataset/classification/
#       train/Fresh/*.jpg   train/Rotten/*.jpg
#       val/Fresh/*.jpg     val/Rotten/*.jpg
#       test/Fresh/*.jpg    test/Rotten/*.jpg
CLASSIFICATION_DATASET_DIR = PROJECT_ROOT / "dataset" / "classification"

# -----------------------------------------------------------------------
# 5. PROPORSI SPLIT DATA
# -----------------------------------------------------------------------
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15  # otomatis = 1 - TRAIN_RATIO - VAL_RATIO
RANDOM_SEED = 42  # supaya split selalu sama tiap kali dijalankan ulang (reproducible)

# -----------------------------------------------------------------------
# 6. PATH MODEL & HASIL
# -----------------------------------------------------------------------
MODELS_DIR = PROJECT_ROOT / "models"
RESULTS_DIR = PROJECT_ROOT / "results"
RUNS_DIR = PROJECT_ROOT / "runs"  # tempat Ultralytics menyimpan log training

BEST_MODEL_PATH = MODELS_DIR / "best.pt"

# -----------------------------------------------------------------------
# 7. KONFIGURASI TRAINING (default, bisa dioverride lewat argumen CLI)
# -----------------------------------------------------------------------
PRETRAINED_MODEL = "yolo11n-cls.pt"  # varian nano -> ringan, cocok untuk GPU terbatas
IMG_SIZE = 224          # ukuran standar untuk task classification
EPOCHS = 50
BATCH_SIZE = 32         # turunkan (mis. 16 atau 8) kalau kena CUDA out of memory
PATIENCE = 15           # early stopping: stop jika tidak ada improvement selama 15 epoch
DEVICE = 0              # 0 = GPU NVIDIA pertama. Ganti "cpu" jika GPU tidak terdeteksi

for _p in [MODELS_DIR, RESULTS_DIR]:
    _p.mkdir(parents=True, exist_ok=True)
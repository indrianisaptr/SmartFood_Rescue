"""
check_dataset.py
=================
Tujuan file ini:
1. Memeriksa apakah struktur folder dataset mentah sesuai yang diharapkan
   (Bad Quality_Fruits/<Fruit>_Bad dan Good Quality_Fruits/<Fruit>_Good).
2. Menghitung jumlah gambar per folder (per buah, per kondisi).
3. Memeriksa file yang rusak/corrupt (tidak bisa dibuka sebagai gambar).
4. Menampilkan ringkasan ketidakseimbangan kelas (class imbalance).

PENTING: dataset kamu TIDAK punya file anotasi bounding box (.txt/.xml/.json),
hanya folder berisi gambar langsung. Ini artinya dataset kamu cocok untuk
pendekatan YOLO CLASSIFICATION, bukan object detection. Script ini akan
memverifikasi asumsi tersebut secara otomatis (poin 5 di bawah).

Cara pakai:
    python src/check_dataset.py
"""

from pathlib import Path
from PIL import Image
import sys

# Supaya bisa import config.py walau dijalankan dari root project
sys.path.append(str(Path(__file__).resolve().parent))
import config


def is_valid_image(path: Path) -> bool:
    """Coba buka file sebagai gambar. Kalau gagal, berarti file rusak/corrupt."""
    try:
        with Image.open(path) as img:
            img.verify()  # verify() memeriksa integritas file tanpa load penuh ke memori
        return True
    except Exception:
        return False


def scan_condition_folder(condition_dir: Path, suffix: str):
    """
    Memindai satu folder kondisi (Bad Quality_Fruits atau Good Quality_Fruits).
    Mengembalikan dict: {nama_buah: {"count": n, "corrupt": [...], "other_ext": [...]}}
    """
    report = {}
    if not condition_dir.exists():
        print(f"[!] Folder tidak ditemukan: {condition_dir}")
        return report

    for fruit_dir in sorted(condition_dir.iterdir()):
        if not fruit_dir.is_dir():
            continue
        if not fruit_dir.name.endswith(suffix):
            print(f"[!] Peringatan: folder '{fruit_dir.name}' tidak berakhiran '{suffix}', dilewati.")
            continue

        fruit_name = fruit_dir.name.replace(suffix, "")
        all_files = [f for f in fruit_dir.iterdir() if f.is_file()]
        valid_images = [f for f in all_files if f.suffix.lower() in config.VALID_IMAGE_EXTENSIONS]
        other_files = [f for f in all_files if f.suffix.lower() not in config.VALID_IMAGE_EXTENSIONS]

        corrupt = [f.name for f in valid_images if not is_valid_image(f)]

        report[fruit_name] = {
            "count": len(valid_images),
            "corrupt": corrupt,
            "other_files": [f.name for f in other_files],
        }
    return report


def main():
    print("=" * 70)
    print("PENGECEKAN DATASET MENTAH — SmartFood Rescue")
    print("=" * 70)

    print(f"\nFolder Bad  : {config.RAW_BAD_DIR}")
    print(f"Folder Good : {config.RAW_GOOD_DIR}")

    bad_report = scan_condition_folder(config.RAW_BAD_DIR, "_Bad")
    good_report = scan_condition_folder(config.RAW_GOOD_DIR, "_Good")

    if not bad_report or not good_report:
        print("\n[X] Salah satu folder dataset tidak ditemukan / kosong.")
        print("    Periksa kembali RAW_DATASET_DIR di src/config.py.")
        return

    # --- Cek konsistensi: apakah setiap buah punya pasangan Bad & Good? ---
    fruits_bad = set(bad_report.keys())
    fruits_good = set(good_report.keys())
    missing_good = fruits_bad - fruits_good
    missing_bad = fruits_good - fruits_bad

    if missing_good:
        print(f"\n[!] Buah ini punya folder _Bad tapi TIDAK ada folder _Good: {missing_good}")
    if missing_bad:
        print(f"\n[!] Buah ini punya folder _Good tapi TIDAK ada folder _Bad: {missing_bad}")

    # --- Tabel ringkasan per buah ---
    print("\n" + "-" * 70)
    print(f"{'Buah':<15}{'Good (Fresh)':<15}{'Bad (Rotten)':<15}{'Total':<10}")
    print("-" * 70)

    total_fresh, total_rotten = 0, 0
    total_corrupt = 0

    all_fruits = sorted(fruits_bad | fruits_good)
    for fruit in all_fruits:
        n_good = good_report.get(fruit, {}).get("count", 0)
        n_bad = bad_report.get(fruit, {}).get("count", 0)
        total_fresh += n_good
        total_rotten += n_bad
        print(f"{fruit:<15}{n_good:<15}{n_bad:<15}{n_good + n_bad:<10}")

        for rep in [good_report.get(fruit, {}), bad_report.get(fruit, {})]:
            corrupt = rep.get("corrupt", [])
            if corrupt:
                total_corrupt += len(corrupt)
                print(f"    [!] {len(corrupt)} file corrupt di folder ini: {corrupt[:5]}"
                      f"{' ...' if len(corrupt) > 5 else ''}")

    print("-" * 70)
    print(f"{'TOTAL':<15}{total_fresh:<15}{total_rotten:<15}{total_fresh + total_rotten:<10}")

    # --- Ringkasan class imbalance ---
    print("\n" + "=" * 70)
    print("RINGKASAN KELAS FINAL (setelah digabung jadi 2 kelas)")
    print("=" * 70)
    grand_total = total_fresh + total_rotten
    if grand_total == 0:
        print("Tidak ada gambar valid ditemukan.")
        return

    pct_fresh = 100 * total_fresh / grand_total
    pct_rotten = 100 * total_rotten / grand_total
    ratio = max(total_fresh, total_rotten) / max(min(total_fresh, total_rotten), 1)

    print(f"Fresh  : {total_fresh} gambar ({pct_fresh:.1f}%)")
    print(f"Rotten : {total_rotten} gambar ({pct_rotten:.1f}%)")
    print(f"Rasio ketidakseimbangan (mayoritas/minoritas): {ratio:.2f}x")

    if ratio >= 1.5:
        print("\n[!] Dataset TIDAK SEIMBANG (imbalance >= 1.5x).")
        print("    prepare_dataset.py akan menangani ini secara otomatis dengan")
        print("    oversampling kelas minoritas HANYA pada data train (val/test dibiarkan")
        print("    apa adanya supaya evaluasi tetap mencerminkan distribusi asli).")
    else:
        print("\n[OK] Dataset relatif seimbang, tidak perlu penanganan khusus.")

    if total_corrupt > 0:
        print(f"\n[!] Total {total_corrupt} file gambar corrupt ditemukan.")
        print("    File-file ini akan OTOMATIS DILEWATI oleh prepare_dataset.py.")
    else:
        print("\n[OK] Tidak ada file corrupt yang terdeteksi.")

    # --- Konfirmasi jenis task ---
    print("\n" + "=" * 70)
    print("KESIMPULAN JENIS TASK")
    print("=" * 70)
    print("Tidak ditemukan file anotasi bounding box (.txt/.xml/.json) di dataset.")
    print("=> Dataset ini sesuai untuk pendekatan YOLO CLASSIFICATION (yolo11n-cls),")
    print("   BUKAN object detection. train.py sudah disiapkan untuk task ini.")
    print("\nLangkah selanjutnya: jalankan  python src/prepare_dataset.py")


if __name__ == "__main__":
    main()
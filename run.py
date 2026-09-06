"""
Entry point: CLI menu for del-background.
Choose between Video or Image background removal.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from background_remover import process_image


def process_image_cli():
    """Handle image background removal and processing via CLI."""
    input_path = input("🖼️ Masukkan path gambar input: ").strip().strip('"')
    if not input_path:
        print("❌ Path tidak boleh kosong.")
        return

    input_path = Path(input_path)
    if not input_path.exists():
        print(f"❌ File tidak ditemukan: {input_path}")
        return

    print("\nPilih Mode Background:")
    print("  1. Transparan")
    print("  2. Warna Solid (Putih)")
    print("  3. Warna Solid (Hijau)")
    bg_choice = input("Pilihan mode [1/2/3, default: 1]: ").strip()
    
    bg_mode = "Transparan"
    bg_color = (255, 255, 255)
    if bg_choice == "2":
        bg_mode = "Warna Solid"
        bg_color = (255, 255, 255)
    elif bg_choice == "3":
        bg_mode = "Warna Solid"
        bg_color = (0, 255, 0)

    print("\nPilih Preset Ukuran:")
    print("  1. Asli")
    print("  2. 3x4 (Pas Foto)")
    print("  3. 4x6 (Pas Foto)")
    print("  4. Instagram 1:1 (Square)")
    preset_choice = input("Pilihan preset [1/2/3/4, default: 1]: ").strip()
    
    preset_map = {
        "1": "Asli",
        "2": "3x4 (Pas Foto)",
        "3": "4x6 (Pas Foto)",
        "4": "Instagram 1:1 (Square)"
    }
    preset = preset_map.get(preset_choice, "Asli")

    print("\nPilih Format Output:")
    print("  1. PNG")
    print("  2. JPG")
    print("  3. WebP")
    fmt_choice = input("Pilihan format [1/2/3, default: 1]: ").strip()
    
    fmt_map = {"1": "PNG", "2": "JPG", "3": "WebP"}
    output_format = fmt_map.get(fmt_choice, "PNG")

    default_out = Path("hasil gambar") / f"{input_path.stem}_processed.{output_format.lower()}"
    out_input = input(f"📁 Path output (default: {default_out}): ").strip().strip('"')
    output_path = Path(out_input) if out_input else default_out

    print(f"\n🔄 Memproses gambar: {input_path}")
    print(f"   Mode BG: {bg_mode} | Preset: {preset} | Format: {output_format}")
    print(f"   Output: {output_path}")

    try:
        result = process_image(
            input_path=str(input_path),
            output_path=str(output_path),
            bg_mode=bg_mode,
            bg_color=bg_color,
            preset=preset,
            output_format=output_format,
        )
        print(f"\n✅ Selesai! File tersimpan di: {result}")
    except Exception as e:
        print(f"\n❌ Error: {e}")


def main():
    """Main CLI menu."""
    print("=" * 50)
    print("🖼️ del-background - Image Background Remover")
    print("=" * 50)
    print("Pilih mode:")
    print("  1. Image  (hapus background gambar)")
    print("  2. GUI    (jalankan Streamlit web interface)")
    print("  0. Keluar")
    print("-" * 50)

    choice = input("Pilihan [1/2/0]: ").strip()

    if choice == "1":
        process_image_cli()
    elif choice == "2":
        print("\n🚀 Menjalankan Streamlit GUI...")
        import subprocess
        gui_path = Path(__file__).parent / "src" / "gui.py"
        subprocess.run([sys.executable, "-m", "streamlit", "run", str(gui_path)], check=True)
    elif choice == "0":
        print("👋 Sampai jumpa!")
        sys.exit(0)
    else:
        print("❌ Pilihan tidak valid.")


if __name__ == "__main__":
    main()

"""
Streamlit GUI for del-background.
Features:
- Background Removal
- Background Replacement (Transparent, Solid Color, Custom Image)
- Resize & Crop Presets (3x4, 4x6, Instagram 1:1, Custom)
- Multi-format Export (PNG, JPG, WebP)
"""

import base64
import os
import tempfile
from pathlib import Path

import streamlit as st

from background_remover import process_image

# ---------- Page config ----------
st.set_page_config(
    page_title="StudioPic | Modern AI Image Studio",
    page_icon="📸",
    layout="wide",
)

# ---------- Theme & Modern UI CSS ----------
logo_path = os.path.join("assets", "studiopic.png")
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        encoded_sb = base64.b64encode(f.read()).decode("utf-8")
    st.sidebar.markdown(
        f"""
        <div style="display: flex; justify-content: center; align-items: center; margin: 10px 0 20px 0;">
            <img src="data:image/png;base64,{encoded_sb}" style="width: 120px; height: 120px; border-radius: 50%; object-fit: cover; background: white; padding: 4px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
        </div>
    """,
        unsafe_allow_html=True,
    )

st.sidebar.markdown("### 🎨 Tampilan")
# >>> FIX (poin 2 - persistensi Mode Gelap): sebelumnya toggle SELALU
# default False setiap kali halaman dibuka ulang -- pilihan mode gelap
# user tidak pernah "diingat". Sekarang disimpan di parameter URL
# (?dark=1) lewat st.query_params: begitu user menyalakan mode gelap, URL
# otomatis berubah, dan me-refresh (F5) atau membuka ulang tab/URL yang
# SAMA akan tetap dalam mode gelap. Ini tidak butuh instalasi library
# tambahan (murni fitur bawaan Streamlit), tapi keterbatasannya: kalau user
# menutup tab lalu mengetik ulang alamat situsnya dari awal TANPA
# "?dark=1" di URL (bukan refresh/reload tab yang sama), pilihannya akan
# reset ke default lagi -- untuk benar-benar diingat permanen lintas
# perangkat/browser butuh library tambahan (mis. streamlit-local-storage),
# yang belum dipasang di project ini.
_dark_mode_default = st.query_params.get("dark", "0") == "1"
dark_mode = st.sidebar.toggle(
    "🌙 Mode Gelap", value=_dark_mode_default, key="dark_mode_toggle"
)
st.query_params["dark"] = "1" if dark_mode else "0"

# >>> FIX (tata letak): sidebar sebelumnya lebar default Streamlit yang cukup
# sempit, sehingga label checkbox yang agak panjang ("Hapus / Ganti
# Background") terpotong jadi 2-3 baris dan terlihat berantakan. Diperlebar
# sedikit + label-labelnya dipersingkat (lihat di bawah) supaya rapi dalam
# satu baris.
LAYOUT_CSS = """
<style>
[data-testid="stSidebar"] {
    min-width: 340px !important;
    max-width: 340px !important;
}
/* Jarak yang jelas antar grup fitur di sidebar */
[data-testid="stSidebar"] hr {
    margin: 1rem 0 !important;
}
/* Beri sedikit ruang bernapas antara slider dan angka value-nya */
[data-testid="stSidebar"] .stSlider {
    padding-bottom: 0.4rem;
}
</style>
"""
st.markdown(LAYOUT_CSS, unsafe_allow_html=True)

if dark_mode:
    theme_css = """
    <style>
    .stApp {
        background-color: #0e1117;
        color: #f1f5f9;
    }
    /* >>> FIX (poin 2 - teks tak terlihat di Mode Gelap):
    Streamlit punya aturan warna sendiri yang MELEKAT LANGSUNG di elemen
    heading (h1-h6, dipakai oleh st.header/st.subheader) dan st.caption --
    aturan itu lebih spesifik daripada warna default di .stApp, jadi teksnya
    tetap gelap walau background sudah gelap juga (teks gelap di atas
    background gelap = nyaris tak kelihatan sampai di-hover, karena hover
    memicu ikon link Streamlit muncul di sampingnya). Sebelumnya perbaikan
    warna teks HANYA menyasar sidebar -- sekarang diperluas ke SELURUH
    halaman (heading, caption, teks biasa) supaya tidak ada lagi teks yang
    "hilang" di area utama. */
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
    .stApp [data-testid="stHeader"],
    .stApp [data-testid="stMarkdownContainer"] h1,
    .stApp [data-testid="stMarkdownContainer"] h2,
    .stApp [data-testid="stMarkdownContainer"] h3,
    .stApp [data-testid="stMarkdownContainer"] h4 {
        color: #f8fafc !important;
    }
    .stApp p, .stApp span, .stApp label, .stApp li,
    .stApp [data-testid="stMarkdownContainer"] {
        color: #e5e7eb !important;
    }
    .stApp [data-testid="stCaptionContainer"],
    .stApp [data-testid="stCaptionContainer"] p,
    .stApp small {
        color: #9ca3af !important;
    }
    /* Sidebar Styling for Dark Mode */
    [data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: 1px solid #1f2937;
        padding-top: 0rem !important;
    }
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] {
        color: #f3f4f6 !important;
        font-weight: 500;
    }
    /* Fix file uploader text & buttons globally in dark mode */
    [data-testid="stFileUploader"] section,
    [data-testid="stFileDropzone"] {
        background-color: #1f2937 !important;
        border: 2px dashed #4b5563 !important;
    }
    [data-testid="stFileUploader"] section div,
    [data-testid="stFileUploader"] section span,
    [data-testid="stFileUploader"] section small,
    [data-testid="stFileUploader"] section p,
    [data-testid="stFileUploader"] label,
    [data-testid="stFileUploader"] [data-testid="stMarkdownContainer"] p {
        color: #f3f4f6 !important;
    }
    /* Specific styling for file uploader upload button in dark mode */
    [data-testid="stFileUploader"] button {
        background-color: #374151 !important;
        color: #f3f4f6 !important;
        border: 1px solid #4b5563 !important;
    }
    [data-testid="stFileUploader"] button:hover {
        background-color: #4b5563 !important;
        color: #ffffff !important;
    }
    /* Kotak info/success/error -- beri background gelap sendiri supaya teks
    di dalamnya (yang mengikuti aturan .stApp p di atas) tetap kontras,
    bukan teks terang di atas kotak berwarna terang bawaan Streamlit. */
    [data-testid="stAlert"] {
        background-color: #1f2937 !important;
        border: 1px solid #374151 !important;
    }
    /* Dropdown (selectbox) & expander header -- portal/komponen BaseWeb
    kadang tidak ikut ter-cakup .stApp, jadi disasar langsung. */
    [data-baseweb="select"] * ,
    [data-testid="stExpander"] p {
        color: #f3f4f6 !important;
    }
    [data-testid="stExpander"] {
        background-color: #111827 !important;
        border: 1px solid #1f2937 !important;
    }
    /* >>> FIX (poin 2 - lanjutan): header expander (baris "Pengaturan ...")
    dirender Streamlit dengan <summary> yang punya BACKGROUND PUTIH bawaan
    sendiri, terpisah dari container luar yang sudah saya gelapkan di atas.
    Aturan .stApp span/label sebelumnya cuma mengganti WARNA TEKS jadi
    terang, tapi tidak mengganti background summary yang tetap putih --
    hasilnya teks terang di atas background putih (putih di atas putih,
    hilang total). Sekarang summary-nya juga dipaksa gelap secara eksplisit
    dengan selector yang lebih spesifik supaya menang dari CSS bawaan
    Streamlit. */
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] details > summary {
        background-color: #1f2937 !important;
        color: #f3f4f6 !important;
        border-radius: 6px;
    }
    [data-testid="stExpander"] summary span,
    [data-testid="stExpander"] summary p,
    [data-testid="stExpander"] summary div {
        color: #f3f4f6 !important;
        background-color: transparent !important;
    }
    /* Compact spacing in sidebar */
    [data-testid="stSidebar"] .element-container {
        margin-bottom: -0.8rem !important;
    }
    /* >>> FIX (poin 3 - tombol Preset/E-commerce/Reset tak kelihatan
    tulisannya di Mode Gelap): selector lama ".stButton>button" cuma cocok
    kalau <button> adalah ANAK LANGSUNG dari div ber-class "stButton".
    Di versi Streamlit yang dipakai sekarang, <button> sebenarnya diberi
    atribut data-testid="stBaseButton-secondary" (tombol biasa) atau
    "stBaseButton-primary" (tombol type="primary"), dan teksnya dibungkus
    beberapa lapis <div>/<p> di dalamnya. Karena selector lama tidak persis
    cocok dengan struktur ini, tombol jatuh balik ke gaya BAWAAN Streamlit
    (latar terang, teks gelap) -- dan karena latar sidebar sudah gelap,
    teks gelap itu jadi menyatu dengan latar & tak terlihat sama sekali.
    Sekarang selector diperkuat: menyasar langsung lewat data-testid (yang
    stabil dipakai Streamlit secara internal), DAN memaksa warna pada
    SEMUA elemen anak di dalam tombol lewat wildcard "*" -- jadi berapa pun
    lapis <div>/<p>/<span> yang membungkus teksnya, warnanya tetap ikut
    dipaksa putih, tidak cuma p & span seperti sebelumnya. */
    .stButton>button, .stDownloadButton>button,
    [data-testid="stButton"] button,
    [data-testid="stDownloadButton"] button,
    [data-testid^="stBaseButton"] {
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button *, .stDownloadButton>button *,
    [data-testid="stButton"] button *,
    [data-testid="stDownloadButton"] button *,
    [data-testid^="stBaseButton"] * {
        color: #ffffff !important;
    }
    .stButton>button:hover, .stDownloadButton>button:hover,
    [data-testid="stButton"] button:hover,
    [data-testid="stDownloadButton"] button:hover,
    [data-testid^="stBaseButton"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(34, 197, 94, 0.4);
        color: #ffffff !important;
    }
    .stButton>button:hover *, .stDownloadButton>button:hover *,
    [data-testid="stButton"] button:hover *,
    [data-testid="stDownloadButton"] button:hover *,
    [data-testid^="stBaseButton"]:hover * {
        color: #ffffff !important;
    }
    </style>
    """
else:
    theme_css = """
    <style>
    .stApp {
        background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
        color: #0f172a;
    }
    /* File uploader in light mode styling for better visibility and contrast */
    [data-testid="stFileUploader"] section,
    [data-testid="stFileDropzone"] {
        background-color: #ffffff !important;
        border: 2px dashed #94a3b8 !important;
        border-radius: 10px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    }
    [data-testid="stFileUploader"] section div,
    [data-testid="stFileUploader"] section span,
    [data-testid="stFileUploader"] section small,
    [data-testid="stFileUploader"] section p,
    [data-testid="stFileUploader"] label,
    [data-testid="stFileUploader"] [data-testid="stMarkdownContainer"] p {
        color: #334155 !important;
    }
    [data-testid="stFileUploader"] button {
        background-color: #e2e8f0 !important;
        color: #1e293b !important;
        border: 1px solid #cbd5e1 !important;
        font-weight: 600;
    }
    [data-testid="stFileUploader"] button:hover {
        background-color: #cbd5e1 !important;
        color: #0f172a !important;
    }
    /* Sidebar Styling for Light Mode */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0;
        padding-top: 0rem !important;
    }
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] {
        color: #334155 !important;
        font-weight: 500;
    }
    /* Compact spacing in sidebar */
    [data-testid="stSidebar"] .element-container {
        margin-bottom: -0.8rem !important;
    }
    /* Selector diperkuat juga di sini (lihat catatan FIX di blok Mode Gelap
    di atas) supaya konsisten kuat di kedua mode, bukan cuma di gelap. */
    .stButton>button,
    [data-testid="stButton"] button,
    [data-testid^="stBaseButton"] {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button *,
    [data-testid="stButton"] button *,
    [data-testid^="stBaseButton"] * {
        color: #ffffff !important;
    }
    .stButton>button:hover,
    [data-testid="stButton"] button:hover,
    [data-testid^="stBaseButton"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }
    </style>
    """

st.markdown(theme_css, unsafe_allow_html=True)

# Modern Header Section with Integrated Logo inside the gradient banner
logo_img_tag = ""
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    logo_img_tag = f'<img src="data:image/png;base64,{encoded}" style="width: 70px; height: 70px; border-radius: 50%; object-fit: cover; background: white; padding: 4px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">'
else:
    logo_img_tag = '<span style="font-size: 3rem;">📸</span>'

st.markdown(
    f"""
    <div style="display: flex; align-items: center; gap: 20px; padding: 1.5rem 2rem; background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%); border-radius: 12px; margin-bottom: 2rem; color: white;">
        <div>
            {logo_img_tag}
        </div>
        <div>
            <h1 style="margin: 0; font-size: 2.3rem; font-weight: 800; line-height: 1.2;">StudioPic Pro</h1>
            <p style="margin: 0.3rem 0 0 0; font-size: 1.05rem; opacity: 0.95;">Studio foto mini AI: Hapus background, sesuaikan feather, dan edit foto dengan mudah.</p>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# ==========================================================================
# ---------- Sidebar / Controls ----------
# >>> FIX (tata letak): SEMUA fitur sekarang mengikuti pola yang SAMA PERSIS,
# konsisten di seluruh sidebar (sebelumnya cuma sebagian fitur yang punya
# expander, sisanya menumpuk polos):
#   1. Checkbox aktif/nonaktif untuk fitur itu
#   2. Kalau aktif, detail pengaturannya masuk ke st.sidebar.expander
#      (otomatis collapse kalau fitur dinonaktifkan)
# Konsistensi ini yang bikin sidebar terasa rapi & mudah dipindai orang awam,
# dibanding sebelumnya di mana sebagian fitur pakai expander dan sebagian
# tidak.
# ==========================================================================

st.sidebar.markdown("#### 🖼️ Fitur Utama")
st.sidebar.caption("💡 Pilih fitur yang ingin Anda gunakan di bawah ini.")

# >>> TAMBAHAN (poin 1 - Preset & Reset): daftar key semua checkbox fitur,
# supaya tombol Preset/Reset di bawah bisa mengubah nilainya lewat
# st.session_state sebelum widget-nya dibuat. Ini SEBABNYA setiap checkbox
# fitur di bawah sekarang diberi `key=` eksplisit -- tanpa key, Streamlit
# tidak punya cara untuk diubah dari luar (dari tombol) sama sekali.
_FEATURE_KEYS = [
    "feat_bg",
    "feat_resize",
    "feat_shape",
    "feat_shadow",
    "feat_filter",
    "feat_upscale",
    "feat_watermark",
]


def _apply_preset(active_keys):
    for _k in _FEATURE_KEYS:
        st.session_state[_k] = _k in active_keys


def _reset_all_features():
    _apply_preset(active_keys=[])


st.sidebar.markdown("**⚡ Preset Cepat**")
_preset_col1, _preset_col2 = st.sidebar.columns(2)
_preset_col1.button(
    "🪪 Pas Foto",
    use_container_width=True,
    help="Aktifkan Background + Ukuran & Crop (siap disetel ke 3x4/4x6).",
    on_click=_apply_preset,
    kwargs={"active_keys": ["feat_bg", "feat_resize"]},
)
_preset_col2.button(
    "🛍️ E-commerce",
    use_container_width=True,
    help="Aktifkan Background + Watermark (siap untuk foto produk).",
    on_click=_apply_preset,
    kwargs={"active_keys": ["feat_bg", "feat_watermark"]},
)
st.sidebar.button(
    "🔄 Reset Semua Fitur",
    use_container_width=True,
    help="Matikan semua fitur, kembali ke kondisi awal.",
    on_click=_reset_all_features,
)
st.sidebar.caption(
    "Catatan: preset baru memilihkan FITUR mana yang aktif — detail "
    "pengaturannya (warna, ukuran, dll.) tetap perlu diatur manual di "
    "dalam masing-masing panel."
)
st.sidebar.markdown("---")

# --- 1. Background ---
# >>> FIX: sebelumnya default value=True, jadi saat pertama kali dibuka
# sudah ada 1 fitur ter-centang duluan -- tidak konsisten dengan 6 fitur lain
# yang defaultnya nonaktif, dan bikin sidebar terlihat "sudah dipakai"
# padahal user belum memilih apa-apa. Sekarang semua fitur, termasuk
# Background, default NONAKTIF saat pertama kali dibuka -- benar-benar
# bersih sampai user memilih sendiri.
enable_bg = st.sidebar.checkbox(
    "Background",
    value=False,
    key="feat_bg",
    help="Hapus atau ganti latar belakang gambar.",
)
bg_mode = "Transparan"
bg_color = (255, 255, 255)
bg_image_temp_path = None
edge_feather = 0.0

if enable_bg:
    with st.sidebar.expander("Pengaturan Background", expanded=True):
        bg_mode = st.selectbox(
            "Mode Latar Belakang",
            ["Transparan", "Warna Solid", "Gambar Kustom"],
            index=0,
        )

        if bg_mode == "Warna Solid":
            color_choice = st.selectbox(
                "Pilih Warna",
                ["Putih", "Cream", "Hijau", "Merah", "Biru", "Hitam", "Kustom RGB"],
                index=0,
            )
            if color_choice == "Putih":
                bg_color = (255, 255, 255)
            elif color_choice == "Cream":
                bg_color = (255, 253, 208)
            elif color_choice == "Hijau":
                bg_color = (0, 255, 0)
            elif color_choice == "Merah":
                bg_color = (255, 0, 0)
            elif color_choice == "Biru":
                bg_color = (0, 0, 255)
            elif color_choice == "Hitam":
                bg_color = (0, 0, 0)
            elif color_choice == "Kustom RGB":
                r = st.slider("Merah (R)", 0, 255, 255)
                g = st.slider("Hijau (G)", 0, 255, 255)
                b = st.slider("Biru (B)", 0, 255, 255)
                bg_color = (r, g, b)

        elif bg_mode == "Gambar Kustom":
            uploaded_bg = st.file_uploader(
                "Upload Background Baru",
                type=["png", "jpg", "jpeg"],
                key="bg_uploader",
            )
            if uploaded_bg is not None:
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=Path(uploaded_bg.name).suffix
                ) as tmp_bg:
                    tmp_bg.write(uploaded_bg.read())
                    bg_image_temp_path = tmp_bg.name

        edge_feather = st.slider(
            "Haluskan Tepi (Feathering)",
            min_value=0.0,
            max_value=10.0,
            value=0.0,
            step=0.5,
            help="Menghaluskan tepi objek agar tidak terlihat terlalu tajam atau kaku.",
        )

st.sidebar.markdown("---")

# --- 2. Ukuran & Crop ---
enable_resize = st.sidebar.checkbox(
    "Ukuran & Crop",
    value=False,
    key="feat_resize",
    help="Ubah ukuran/rasio gambar ke preset tertentu.",
)
preset = "Asli"
custom_w, custom_h = None, None

if enable_resize:
    with st.sidebar.expander("Pengaturan Ukuran & Crop", expanded=True):
        preset = st.selectbox(
            "Preset Ukuran",
            [
                "Asli",
                "3x4 (Pas Foto)",
                "4x6 (Pas Foto)",
                "Instagram 1:1 (Square)",
                "Custom",
            ],
            index=0,
        )
        if preset == "Custom":
            custom_w = st.number_input(
                "Lebar (px)", min_value=50, max_value=4000, value=800
            )
            custom_h = st.number_input(
                "Tinggi (px)", min_value=50, max_value=4000, value=800
            )

st.sidebar.markdown("---")

# --- 3. Bentuk (Shape) ---
enable_shape = st.sidebar.checkbox(
    "Bentuk Pola",
    value=False,
    key="feat_shape",
    help="Potong gambar ke dalam bentuk geometri tertentu.",
)
shape_mode = "Asli"
corner_radius = 20

if enable_shape:
    with st.sidebar.expander("Pengaturan Bentuk", expanded=True):
        shape_mode = st.selectbox(
            "Bentuk Pola Gambar",
            ["Asli", "Lingkaran", "Oval", "Sudut Tumpul (Rounded Corners)"],
            index=0,
        )
        if shape_mode == "Sudut Tumpul (Rounded Corners)":
            corner_radius = st.slider("Radius Sudut", 5, 200, 30, step=5)

st.sidebar.markdown("---")

# --- 4. Bayangan (Shadow) ---
enable_shadow = st.sidebar.checkbox(
    "Efek Bayangan",
    value=False,
    key="feat_shadow",
    help="Menambahkan bayangan estetis di bawah objek.",
)
shadow_offset_x = 10
shadow_offset_y = 10
shadow_blur = 15
shadow_opacity = 128

if enable_shadow:
    with st.sidebar.expander("Pengaturan Bayangan", expanded=True):
        shadow_offset_x = st.slider("Geser Horizontal", -50, 50, 10)
        shadow_offset_y = st.slider("Geser Vertikal", -50, 50, 10)
        shadow_blur = st.slider("Tingkat Blur", 0, 50, 15)
        shadow_opacity = st.slider("Opasitas", 0, 255, 128)

st.sidebar.markdown("---")

# --- 5. Filter & Efek ---
enable_filter = st.sidebar.checkbox(
    "Filter & Efek",
    value=False,
    key="feat_filter",
    help="Menerapkan filter foto estetis.",
)
filter_name = "Asli"

if enable_filter:
    with st.sidebar.expander("Pengaturan Filter", expanded=True):
        filter_name = st.selectbox(
            "Pilih Filter",
            ["Asli", "Grayscale", "Sepia", "Vintage", "Warm", "Cool", "HDR Effect"],
            index=0,
        )

st.sidebar.markdown("---")

# --- 6. AI Upscaler ---
enable_upscale = st.sidebar.checkbox(
    "AI Upscaler",
    value=False,
    key="feat_upscale",
    help="Meningkatkan resolusi gambar dan ketajaman.",
)
upscale_factor = 2

if enable_upscale:
    with st.sidebar.expander("Pengaturan Upscaler", expanded=True):
        upscale_factor = st.selectbox("Faktor Skala", [2, 4], index=0)

st.sidebar.markdown("---")

# --- 7. Watermark ---
enable_watermark = st.sidebar.checkbox(
    "Watermark",
    value=False,
    key="feat_watermark",
    help="Menambahkan watermark teks pada hasil akhir.",
)
watermark_text = "StudioPic"
watermark_pos = "Kanan Bawah"
watermark_opacity = 128

if enable_watermark:
    with st.sidebar.expander("Pengaturan Watermark", expanded=True):
        watermark_text = st.text_input("Teks Watermark", value="StudioPic")
        watermark_pos = st.selectbox(
            "Posisi",
            ["Kanan Bawah", "Kiri Bawah", "Kanan Atas", "Kiri Atas", "Tengah"],
            index=0,
        )
        watermark_opacity = st.slider("Opasitas", 10, 255, 128)

st.sidebar.markdown("---")

# >>> TAMBAHAN (poin 3 - ide tambahan): penghitung kecil supaya user awam
# langsung tahu berapa fitur yang sedang aktif tanpa harus scroll ke atas
# menghitung sendiri satu-satu.
_active_feature_count = sum(
    [
        enable_bg,
        enable_resize,
        enable_shape,
        enable_shadow,
        enable_filter,
        enable_upscale,
        enable_watermark,
    ]
)
if _active_feature_count == 0:
    st.sidebar.caption("Belum ada fitur yang aktif — gambar akan diunduh apa adanya.")
else:
    st.sidebar.caption(f"✅ {_active_feature_count} dari 7 fitur aktif.")

st.sidebar.markdown("#### 📦 Output")
output_format = st.sidebar.selectbox("Format Unduhan", ["PNG", "JPG", "WebP"], index=0)

# ==========================================================================
# ---------- Main Container ----------
# >>> FIX (tata letak): area utama sebelumnya nyaris kosong (cuma upload box
# kecil di pojok kiri atas, sisanya ruang kosong terbuang). Sekarang preview
# "Sebelum" & "Sesudah" ditampilkan berdampingan dalam 2 kolom lebar penuh,
# supaya ruang itu benar-benar terpakai dan hasilnya mudah dibandingkan.
# ==========================================================================

st.header("1️⃣ Upload Gambar")
uploaded_image = st.file_uploader(
    "Pilih file gambar (PNG, JPG, JPEG)",
    type=["png", "jpg", "jpeg"],
    key="image_uploader",
)

if uploaded_image is not None:
    # Save uploaded file to temp
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=Path(uploaded_image.name).suffix
    ) as tmp_in:
        tmp_in.write(uploaded_image.read())
        input_path = tmp_in.name

    # Output filename setup
    base_name = Path(uploaded_image.name).stem
    ext = output_format.lower()
    output_filename = f"{base_name}_processed.{ext}"

    script_dir = Path(__file__).resolve().parent.parent
    output_dir = script_dir / "hasil gambar"
    output_dir.mkdir(exist_ok=True)
    output_path = str(output_dir / output_filename)

    st.markdown("---")
    st.header("2️⃣ Pratinjau & Proses")

    # Ringkasan pengaturan aktif dalam bahasa yang gampang dipahami, bukan
    # daftar variabel teknis -- cuma menampilkan opsi yang benar-benar aktif.
    active_settings = [f"Background: **{bg_mode}**"] if enable_bg else []
    if enable_resize:
        active_settings.append(f"Ukuran: **{preset}**")
    if enable_shape:
        active_settings.append(f"Bentuk: **{shape_mode}**")
    if enable_shadow:
        active_settings.append("Bayangan: **Aktif**")
    if enable_filter:
        active_settings.append(f"Filter: **{filter_name}**")
    if enable_upscale:
        active_settings.append(f"Upscaler: **{upscale_factor}x**")
    if enable_watermark:
        active_settings.append("Watermark: **Aktif**")
    active_settings.append(f"Format: **{output_format}**")
    st.caption(" | ".join(active_settings))

    preview_col, result_col = st.columns(2)
    with preview_col:
        st.subheader("Sebelum")
        st.image(input_path, use_container_width=True)

    process_clicked = st.button(
        "🚀 Proses Gambar",
        key="process_image",
        type="primary",
        use_container_width=True,
    )

    if process_clicked:
        with result_col:
            st.subheader("Sesudah")
            with st.spinner("Memproses gambar... mohon tunggu sebentar."):
                try:
                    result_path = process_image(
                        input_path=input_path,
                        output_path=output_path,
                        bg_mode=bg_mode,
                        bg_color=bg_color,
                        bg_image_path=bg_image_temp_path,
                        preset=preset,
                        custom_width=custom_w,
                        custom_height=custom_h,
                        output_format=output_format,
                        edge_feather=edge_feather,
                        shape_mode=shape_mode,
                        corner_radius=corner_radius,
                        enable_bg=enable_bg,
                        enable_shape=enable_shape,
                        enable_resize=enable_resize,
                        enable_shadow=enable_shadow,
                        shadow_offset_x=shadow_offset_x,
                        shadow_offset_y=shadow_offset_y,
                        shadow_blur=shadow_blur,
                        shadow_opacity=shadow_opacity,
                        enable_watermark=enable_watermark,
                        watermark_text=watermark_text,
                        watermark_pos=watermark_pos,
                        watermark_opacity=watermark_opacity,
                        enable_filter=enable_filter,
                        filter_name=filter_name,
                        enable_upscale=enable_upscale,
                        upscale_factor=upscale_factor,
                    )
                    st.image(result_path, use_container_width=True)
                    st.success("✅ Gambar berhasil diproses!")

                    mime_map = {
                        "PNG": "image/png",
                        "JPG": "image/jpeg",
                        "WebP": "image/webp",
                    }
                    mime_type = mime_map.get(output_format.upper(), "image/png")

                    with open(result_path, "rb") as f:
                        image_bytes = f.read()
                    st.download_button(
                        label=f"📥 Download {Path(result_path).name}",
                        data=image_bytes,
                        file_name=Path(result_path).name,
                        mime=mime_type,
                        use_container_width=True,
                    )
                except Exception as e:
                    st.error(f"❌ Terjadi error: {e}")
                finally:
                    if os.path.exists(input_path):
                        os.unlink(input_path)
                    if bg_image_temp_path and os.path.exists(bg_image_temp_path):
                        os.unlink(bg_image_temp_path)
else:
    st.info("Silakan upload gambar pada area di atas untuk memulai.")

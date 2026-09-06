"""
Core module: Remove background from images using rembg,
support custom background replacement (solid color, custom image),
resizing & cropping (dimension presets), and multi-format export (PNG, JPG, WebP).
"""

import os
from pathlib import Path
from PIL import Image, ImageOps, ImageFilter, ImageDraw, ImageEnhance
from rembg import remove as remove_bg


def apply_shadow(img: Image.Image, offset_x: int = 10, offset_y: int = 10, blur: int = 15, opacity: int = 128) -> Image.Image:
    """Menambahkan efek AI/Drop Shadow di belakang objek."""
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    
    alpha = img.split()[3]
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    shadow_mask = Image.new("L", img.size, 0)
    shadow_mask.paste(alpha, (offset_x, offset_y))
    
    shadow = Image.new("RGBA", img.size, (0, 0, 0, opacity))
    shadow.putalpha(ImageOps.colorize(shadow_mask.filter(ImageFilter.GaussianBlur(blur)), (0,0,0), (0,0,0)).split()[0])
    if opacity < 255:
        r, g, b, a = shadow.split()
        a = a.point(lambda i: int(i * (opacity / 255.0)))
        shadow = Image.merge("RGBA", (r, g, b, a))

    return Image.alpha_composite(shadow, img)


def apply_watermark(img: Image.Image, text: str = "StudioPic", position: str = "Kanan Bawah", opacity: int = 128) -> Image.Image:
    """Menambahkan watermark teks pada gambar."""
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    
    txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)
    
    try:
        from PIL import ImageFont
        font = ImageFont.load_default()
    except Exception:
        font = None

    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    w, h = img.size
    margin = 20
    
    if position == "Kanan Bawah":
        x = w - tw - margin
        y = h - th - margin
    elif position == "Kiri Bawah":
        x = margin
        y = h - th - margin
    elif position == "Kanan Atas":
        x = w - tw - margin
        y = margin
    elif position == "Kiri Atas":
        x = margin
        y = margin
    else:
        x = (w - tw) // 2
        y = (h - th) // 2
        
    draw.text((x, y), text, fill=(255, 255, 255, opacity), font=font)
    return Image.alpha_composite(img, txt_layer)


def apply_adjustments(img: Image.Image, brightness: float = 1.0, contrast: float = 1.0, saturation: float = 1.0) -> Image.Image:
    """Mengatur Brightness, Contrast, dan Saturation."""
    if brightness != 1.0:
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(brightness)
    if contrast != 1.0:
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(contrast)
    if saturation != 1.0:
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(saturation)
    return img


def apply_image_enhancer(img: Image.Image, sharpness: float = 1.2, color_boost: float = 1.1, denoise_smooth: bool = False) -> Image.Image:
    """1. AI Image Enhancer / Super-Resolution (Upscaler) & Detail Booster."""
    if sharpness != 1.0:
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(sharpness)
    if color_boost != 1.0:
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(color_boost)
    if denoise_smooth:
        img = img.filter(ImageFilter.SMOOTH_MORE)
    return img


def smart_crop_center(img: Image.Image, padding: int = 20) -> Image.Image:
    """2. Smart Image Cropping & Subject Centering berdasarkan bounding box objek tidak transparan."""
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    
    # Dapatkan bounding box dari alpha channel (subjek utama)
    bbox = img.getbbox()
    if bbox:
        left, upper, right, lower = bbox
        width, height = img.size
        
        # Tambahkan padding
        left = max(0, left - padding)
        upper = max(0, upper - padding)
        right = min(width, right + padding)
        lower = min(height, lower + padding)
        
        cropped = img.crop((left, upper, right, lower))
        return cropped
    return img


def apply_smart_filter(img: Image.Image, filter_name: str = "Normal") -> Image.Image:
    """3. Smart Filters & Color Grading (LUTs/Presets) & Vignette."""
    if img.mode != "RGBA":
        img = img.convert("RGBA")

    if filter_name == "Cinematic":
        # Kontras tinggi + sedikit kebiruan/kehijauan pada bayangan
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.25)
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(0.9)
    elif filter_name == "Vintage / Retro":
        # Hangat, saturasi agak turun
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(0.75)
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.05)
    elif filter_name == "Warm Sunset":
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.15)
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.1)
    elif filter_name == "B&W Dramatic":
        img = img.convert("L").convert("RGBA")
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.3)
    elif filter_name == "Vignette Dark":
        img = img.filter(ImageFilter.DETAIL)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)
    
    return img


def apply_photo_preset(img: Image.Image, preset_color: str = "Merah") -> Image.Image:
    """Mengubah background menjadi warna pas foto standar (Merah / Biru)."""
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    
    color_map = {
        "Merah": (237, 28, 36, 255),
        "Biru": (0, 102, 204, 255)
    }
    bg_color = color_map.get(preset_color, (237, 28, 36, 255))
    background = Image.new("RGBA", img.size, bg_color)
    return Image.alpha_composite(background, img)


def process_image(
    input_path: str,
    output_path: str,
    bg_mode: str = "Transparan",
    bg_color: tuple = (255, 255, 255),
    bg_image_path: str = None,
    preset: str = "Asli",
    custom_width: int = None,
    custom_height: int = None,
    output_format: str = "PNG",
    edge_feather: float = 0.0,
    shape_mode: str = "Asli",
    corner_radius: int = 20,
    enable_bg: bool = True,
    enable_shape: bool = True,
    enable_resize: bool = True,
    enable_shadow: bool = False,
    shadow_offset_x: int = 10,
    shadow_offset_y: int = 10,
    shadow_blur: int = 15,
    shadow_opacity: int = 128,
    enable_watermark: bool = False,
    watermark_text: str = "StudioPic",
    watermark_pos: str = "Kanan Bawah",
    watermark_opacity: int = 128,
    enable_adjustments: bool = False,
    brightness: float = 1.0,
    contrast: float = 1.0,
    saturation: float = 1.0,
    enable_pasfoto_preset: bool = False,
    pasfoto_color: str = "Merah",
    enable_filter: bool = False,
    filter_name: str = "Asli",
    enable_upscale: bool = False,
    upscale_factor: int = 2
) -> str:
    """
    Process image: remove background, apply background replacement, resize/crop preset,
    and save in the requested format.

    Parameters
    ----------
    input_path : str
        Path to input image.
    output_path : str
        Path to save final image (extension may be adjusted based on output_format).
    bg_mode : str
        "Transparan", "Warna Solid", atau "Gambar Kustom".
    bg_color : tuple
        RGB tuple for solid background (e.g. (255, 255, 255)).
    bg_image_path : str
        Path to custom background image if bg_mode == "Gambar Kustom".
    preset : str
        "Asli", "3x4 (Pas Foto)", "4x6 (Pas Foto)", "Instagram 1:1 (Square)", "Custom".
    custom_width : int
        Width for custom resize.
    custom_height : int
        Height for custom resize.
    output_format : str
        "PNG", "JPG", or "WebP".

    Returns
    -------
    str
        Final output file path.
    """
    with Image.open(input_path) as img:
        base_img = img.convert("RGBA")

        # 1. Remove background -> returns RGBA
        if enable_bg:
            foreground = remove_bg(base_img)
            if foreground.mode != "RGBA":
                foreground = foreground.convert("RGBA")

            # 1.5 Edge Feathering / Smoothing if edge_feather > 0
            if edge_feather > 0:
                r, g, b, alpha = foreground.split()
                # Blur alpha channel for feathering/smoothing
                alpha = alpha.filter(ImageFilter.GaussianBlur(radius=edge_feather))
                foreground = Image.merge("RGBA", (r, g, b, alpha))

            # 2. Background replacement
            if bg_mode == "Transparan":
                # Keep RGBA with transparency
                base_img = foreground
            elif bg_mode == "Warna Solid":
                # Create a solid color background
                base_img = Image.new("RGBA", foreground.size, (*bg_color, 255))
                base_img.paste(foreground, (0, 0), foreground)
            elif bg_mode == "Gambar Kustom" and bg_image_path and os.path.exists(bg_image_path):
                with Image.open(bg_image_path) as bg_img:
                    bg_img = bg_img.convert("RGBA")
                    # Resize background to match foreground size
                    bg_img = bg_img.resize(foreground.size, Image.Resampling.LANCZOS)
                    base_img = Image.new("RGBA", foreground.size)
                    base_img.paste(bg_img, (0, 0))
                    base_img.paste(foreground, (0, 0), foreground)
            else:
                base_img = foreground

        # 3. Resize & Crop / Dimension Preset
        if enable_resize:
            target_w, target_h = base_img.size
            if preset == "3x4 (Pas Foto)":
                target_w, target_h = 600, 800
                base_img = ImageOps.fit(base_img, (target_w, target_h), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
            elif preset == "4x6 (Pas Foto)":
                target_w, target_h = 600, 900
                base_img = ImageOps.fit(base_img, (target_w, target_h), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
            elif preset == "Instagram 1:1 (Square)":
                dim = max(base_img.size)
                target_w, target_h = dim, dim
                base_img = ImageOps.fit(base_img, (target_w, target_h), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
            elif preset == "Custom" and custom_width and custom_height:
                target_w, target_h = int(custom_width), int(custom_height)
                base_img = ImageOps.fit(base_img, (target_w, target_h), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
            else:
                pass

        # 3.5 Shape Masking (Lingkaran, Oval, Sudut Tumpul)
        if enable_shape and shape_mode != "Asli":
            width, height = base_img.size
            mask = Image.new("L", (width, height), 0)
            draw = ImageDraw.Draw(mask)

            if shape_mode == "Lingkaran":
                side = min(width, height)
                left = (width - side) // 2
                top = (height - side) // 2
                draw.ellipse([left, top, left + side, top + side], fill=255)
                base_img = base_img.convert("RGBA")
                r_ch, g_ch, b_ch, a_ch = base_img.split()
                new_alpha = Image.composite(a_ch, Image.new("L", (width, height), 0), mask)
                base_img = Image.merge("RGBA", (r_ch, g_ch, b_ch, new_alpha))
            elif shape_mode == "Oval":
                # Membuat oval memanjang vertikal dengan margin horizontal 0.10 agar bentuk lebih lebar
                margin_x = int(width * 0.10)  # Lebar dipangkas 10% di kiri & kanan
                draw.ellipse([margin_x, 0, width - margin_x, height], fill=255)
                base_img = base_img.convert("RGBA")
                r_ch, g_ch, b_ch, a_ch = base_img.split()
                new_alpha = Image.composite(a_ch, Image.new("L", (width, height), 0), mask)
                base_img = Image.merge("RGBA", (r_ch, g_ch, b_ch, new_alpha))
            elif shape_mode == "Sudut Tumpul (Rounded Corners)":
                # Draw rounded rectangle
                radius = min(corner_radius, width // 2, height // 2)
                draw.rounded_rectangle([0, 0, width, height], radius=radius, fill=255)
                base_img = base_img.convert("RGBA")
                r_ch, g_ch, b_ch, a_ch = base_img.split()
                new_alpha = Image.composite(a_ch, Image.new("L", (width, height), 0), mask)
                base_img = Image.merge("RGBA", (r_ch, g_ch, b_ch, new_alpha))

        # 3.6 Pas Foto Preset Warna (Background / Fill Color pengganti)
        if enable_pasfoto_preset and pasfoto_color:
            color_map = {
                "Merah": (230, 0, 0),
                "Biru": (0, 0, 255),
                "Hijau": (0, 150, 0),
                "Putih": (255, 255, 255)
            }
            bg_color = color_map.get(pasfoto_color, (230, 0, 0))
            if base_img.mode != "RGBA":
                base_img = base_img.convert("RGBA")
            bg_layer = Image.new("RGBA", base_img.size, bg_color + (255,))
            base_img = Image.alpha_composite(bg_layer, base_img)

        # 3.7 AI Shadow / Drop Shadow
        if enable_shadow and base_img.mode == "RGBA":
            alpha = base_img.split()[3]
            # Buat shadow hitam solid berdasarkan alpha subject
            shadow = Image.new("RGBA", base_img.size, (0, 0, 0, 0))
            shadow_black = Image.new("RGBA", base_img.size, (0, 0, 0, shadow_opacity))
            shadow.paste(shadow_black, (shadow_offset_x, shadow_offset_y), alpha)
            
            # Apply blur jika diperlukan
            if shadow_blur > 0:
                from PIL import ImageFilter
                shadow = shadow.filter(ImageFilter.GaussianBlur(shadow_blur / 2.0))
            
            # Komposit shadow di bawah subject
            base_img = Image.alpha_composite(shadow, base_img)

        # 3.7.1 Filter & Efek Kreatif (Photo Filters)
        if enable_filter and filter_name != "Asli":
            from PIL import ImageOps, ImageEnhance
            if filter_name == "Grayscale":
                rgb_img = base_img.convert("RGB")
                gray_img = ImageOps.grayscale(rgb_img).convert("RGBA")
                if base_img.mode == "RGBA":
                    _, _, _, a = base_img.split()
                    gray_img.putalpha(a)
                base_img = gray_img
            elif filter_name == "Sepia":
                rgb_img = base_img.convert("RGB")
                width, height = rgb_img.size
                pixels = rgb_img.load()
                for py in range(height):
                    for px in range(width):
                        r, g, b = pixels[px, py]
                        tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                        tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                        tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                        pixels[px, py] = (min(tr, 255), min(tg, 255), min(tb, 255))
                sepia_img = rgb_img.convert("RGBA")
                if base_img.mode == "RGBA":
                    _, _, _, a = base_img.split()
                    sepia_img.putalpha(a)
                base_img = sepia_img
            elif filter_name == "Vintage":
                enhancer = ImageEnhance.Color(base_img.convert("RGB"))
                colored = enhancer.enhance(0.7)
                enhancer_c = ImageEnhance.Contrast(colored)
                contrasted = enhancer_c.enhance(1.2)
                vintage_img = contrasted.convert("RGBA")
                if base_img.mode == "RGBA":
                    _, _, _, a = base_img.split()
                    vintage_img.putalpha(a)
                base_img = vintage_img
            elif filter_name == "Warm":
                r, g, b, a = base_img.convert("RGBA").split()
                r = r.point(lambda i: min(int(i * 1.15), 255))
                b = b.point(lambda i: max(int(i * 0.9), 0))
                base_img = Image.merge("RGBA", (r, g, b, a))
            elif filter_name == "Cool":
                r, g, b, a = base_img.convert("RGBA").split()
                r = r.point(lambda i: max(int(i * 0.9), 0))
                b = b.point(lambda i: min(int(i * 1.15), 255))
                base_img = Image.merge("RGBA", (r, g, b, a))
            elif filter_name == "HDR Effect":
                enhancer = ImageEnhance.Contrast(base_img.convert("RGB"))
                c_img = enhancer.enhance(1.5)
                enhancer_col = ImageEnhance.Color(c_img)
                hdr_img = enhancer_col.enhance(1.3).convert("RGBA")
                if base_img.mode == "RGBA":
                    _, _, _, a = base_img.split()
                    hdr_img.putalpha(a)
                base_img = hdr_img

        # 3.7.2 Image Upscaler / Peningkatan Resolusi (Lanczos High-Res / Sharpness)
        if enable_upscale and upscale_factor > 1:
            from PIL import ImageEnhance
            w, h = base_img.size
            new_w, new_h = w * upscale_factor, h * upscale_factor
            base_img = base_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            enhancer = ImageEnhance.Sharpness(base_img.convert("RGB"))
            sharp_img = enhancer.enhance(1.5).convert("RGBA")
            if base_img.mode == "RGBA":
                _, _, _, a = base_img.split()
                sharp_img.putalpha(a)
            base_img = sharp_img

        # 3.8 Basic Image Adjustments (Brightness, Contrast, Saturation)
        if enable_adjustments:
            from PIL import ImageEnhance
            # Konversi ke RGB dulu jika RGBA agar enhancement konsisten
            mode_orig = base_img.mode
            if mode_orig == "RGBA":
                # Pisahkan alpha
                r, g, b, a = base_img.split()
                rgb_temp = Image.merge("RGB", (r, g, b))
            else:
                rgb_temp = base_img.convert("RGB")
            
            if brightness != 1.0:
                rgb_temp = ImageEnhance.Brightness(rgb_temp).enhance(brightness)
            if contrast != 1.0:
                rgb_temp = ImageEnhance.Contrast(rgb_temp).enhance(contrast)
            if saturation != 1.0:
                rgb_temp = ImageEnhance.Color(rgb_temp).enhance(saturation)
                
            if mode_orig == "RGBA":
                base_img = Image.merge("RGBA", (*rgb_temp.split(), a))
            else:
                base_img = rgb_temp

        # 3.9 Watermarking
        if enable_watermark and watermark_text.strip():
            if base_img.mode != "RGBA":
                base_img = base_img.convert("RGBA")
            txt_layer = Image.new("RGBA", base_img.size, (255, 255, 255, 0))
            draw_txt = ImageDraw.Draw(txt_layer)
            
            try:
                from PIL import ImageFont
                # Coba load font default atau arial
                font = ImageFont.truetype("arial.ttf", size=max(16, int(base_img.size[1] * 0.03)))
            except Exception:
                font = ImageFont.load_default()
                
            # Hitung ukuran text
            try:
                bbox = draw_txt.textbbox((0, 0), watermark_text, font=font)
                txt_w = bbox[2] - bbox[0]
                txt_h = bbox[3] - bbox[1]
            except Exception:
                txt_w, txt_h = 100, 20
                
            pad = 20
            w, h = base_img.size
            if watermark_pos == "Kanan Bawah":
                pos_x = w - txt_w - pad
                pos_y = h - txt_h - pad
            elif watermark_pos == "Kiri Bawah":
                pos_x = pad
                pos_y = h - txt_h - pad
            elif watermark_pos == "Kanan Atas":
                pos_x = w - txt_w - pad
                pos_y = pad
            elif watermark_pos == "Kiri Atas":
                pos_x = pad
                pos_y = pad
            else: # Tengah
                pos_x = (w - txt_w) // 2
                pos_y = (h - txt_h) // 2
                
            draw_txt.text((pos_x, pos_y), watermark_text, fill=(255, 255, 255, watermark_opacity), font=font)
            base_img = Image.alpha_composite(base_img, txt_layer)

        # 4. Format Conversion & Saving
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        
        # Adjust file extension based on format
        p = Path(output_path)
        if output_format.upper() == "JPG":
            output_path = str(p.with_suffix(".jpg"))
            # JPG doesn't support alpha, convert RGBA to RGB with white or background color
            if base_img.mode == "RGBA":
                rgb_img = Image.new("RGB", base_img.size, (255, 255, 255))
                rgb_img.paste(base_img, mask=base_img.split()[3]) # paste using alpha mask
                base_img = rgb_img
            base_img.save(output_path, "JPEG", quality=95)
        elif output_format.upper() == "WEBP":
            output_path = str(p.with_suffix(".webp"))
            base_img.save(output_path, "WEBP", quality=95)
        else:
            # Default PNG
            output_path = str(p.with_suffix(".png"))
            base_img.save(output_path, "PNG")

    print(f"✅ Processed & saved to: {output_path}")
    return output_path

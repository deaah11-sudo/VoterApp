import os
from PIL import Image, ImageOps

def fix_orientation(img):
    try:
        return ImageOps.exif_transpose(img)
    except Exception:
        return img

def crop_and_fit_id(img_path, target_w=1011, target_h=638):
    """
    تحسين قص وتعديل أبعاد بطاقة الهوية الوطنية لحذف الخلفيات الزائدة
    """
    img = Image.open(img_path)
    img = fix_orientation(img)
    
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # تصحيح الاتجاه إذا كانت الصورة عمودية (تتحول أفقياً لتناسب مقاس الهوية القياسي)
    if img.height > img.width:
        img = img.rotate(90, expand=True)

    # قص الهوامش الزائدة بنسبة مئوية واضحة لتنظيف محيط الهوية (قص 5% من كل جانب كمرحلة أولية لتصفية الخلفية)
    w, h = img.size
    crop_margin_w = int(w * 0.05)
    crop_margin_h = int(h * 0.05)
    
    box = (crop_margin_w, crop_margin_h, w - crop_margin_w, h - crop_margin_h)
    img = img.crop(box)

    # إعادة التحجيم بدقة للمقاس الرسمي المعتمد
    img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    return img

def process_and_merge_id_images(face_path, back_path, output_path):
    target_w = 1011
    target_h = 638

    img_face = crop_and_fit_id(face_path, target_w, target_h)
    img_back = crop_and_fit_id(back_path, target_w, target_h)

    # إنشاء قماش أبيض للدمج النظيف والمرتب
    padding = 60
    merged_w = target_w + (padding * 2)
    merged_h = (target_h * 2) + (padding * 3)

    merged_img = Image.new('RGB', (merged_w, merged_h), (255, 255, 255))
    merged_img.paste(img_face, (padding, padding))
    merged_img.paste(img_back, (padding, padding + target_h + padding))

    merged_img.save(output_path, quality=95)
    return output_path

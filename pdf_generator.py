import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from PIL import Image
from image_processor import process_and_merge_id_images, fix_orientation

def create_document_pdf(full_name, reference_id, face_img_path, back_img_path, main_form_path):
    archive_base = os.path.expanduser("~/Master_Archive")
    folder_name = f"{full_name}_{reference_id}"
    person_folder = os.path.join(archive_base, folder_name)
    os.makedirs(person_folder, exist_ok=True)

    pdf_filename = f"{reference_id}.pdf"
    pdf_path = os.path.join(person_folder, pdf_filename)

    merged_id_path = os.path.join(person_folder, "temp_merged_id.jpg")
    process_and_merge_id_images(face_img_path, back_img_path, merged_id_path)

    c = canvas.Canvas(pdf_path, pagesize=A4)
    page_w, page_h = A4

    card_w = 85.6 * mm
    card_h = 53.98 * mm

    x_pos = (page_w - card_w) / 2
    y_pos_face = page_h - (card_h + 40 * mm)
    y_pos_back = y_pos_face - (card_h + 15 * mm)

    img_f = fix_orientation(Image.open(face_img_path))
    img_b = fix_orientation(Image.open(back_img_path))
    
    if img_f.height > img_f.width: img_f = img_f.rotate(90, expand=True)
    if img_b.height > img_b.width: img_b = img_b.rotate(90, expand=True)

    temp_f = os.path.join(person_folder, "tf.jpg")
    temp_b = os.path.join(person_folder, "tb.jpg")
    img_f.save(temp_f)
    img_b.save(temp_b)

    c.drawImage(temp_f, x_pos, y_pos_face, width=card_w, height=card_h)
    c.drawImage(temp_b, x_pos, y_pos_back, width=card_w, height=card_h)
    c.showPage()

    img_form = fix_orientation(Image.open(main_form_path))
    if img_form.width > img_form.height:
        img_form = img_form.rotate(270, expand=True)
    
    temp_form = os.path.join(person_folder, "tform.jpg")
    img_form.save(temp_form)

    margin = 10 * mm
    c.drawImage(temp_form, margin, margin, width=page_w - (2*margin), height=page_h - (2*margin), preserveAspectRatio=False)
    c.showPage()

    c.save()

    for tmp in [merged_id_path, temp_f, temp_b, temp_form]:
        if os.path.exists(tmp):
            os.remove(tmp)

    return pdf_path

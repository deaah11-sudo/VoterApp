import os
import shutil
from flask import Flask, render_template, request, jsonify
from pdf_generator import create_document_pdf

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf_route():
    try:
        ref_id = request.form.get('txtReferenceID')
        full_name = request.form.get('txtFullName')
        
        face_file = request.files.get('fileFace')
        back_file = request.files.get('fileBack')
        form_file = request.files.get('fileForm')

        if not ref_id or not full_name or not face_file or not back_file or not form_file:
            return jsonify({'message': 'جميع الحقول والملفات مطلوبة!'}), 400

        face_path = os.path.join(app.config['UPLOAD_FOLDER'], 'face.jpg')
        back_path = os.path.join(app.config['UPLOAD_FOLDER'], 'back.jpg')
        form_path = os.path.join(app.config['UPLOAD_FOLDER'], 'form.jpg')

        face_file.save(face_path)
        back_file.save(back_path)
        form_file.save(form_path)

        # توليد الـ PDF بالأرشيف الداخلي
        pdf_path = create_document_pdf(full_name, ref_id, face_path, back_path, form_path)

        # النسخ التلقائي للذاكرة المشتركة (Download) لكي يظهر فوراً في مدير الملفات
        try:
            shared_download = os.path.expanduser("~/storage/shared/Download/Master_Archive")
            os.makedirs(shared_download, exist_ok=True)
            src_person_folder = os.path.dirname(pdf_path)
            shutil.copytree(src_person_folder, os.path.join(shared_download, os.path.basename(src_person_folder)), dirs_exist_ok=True)
        except Exception as e:
            print(f"Auto-copy warning: {e}")

        return jsonify({'message': 'تم إنشاء الأرشيف وحفظ ملف الـ PDF في مجلد Download تلقائياً بنجاح!'}), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

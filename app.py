from flask import Flask, request, render_template, send_from_directory
import os
import subprocess
import fitz  # PyMuPDF
from werkzeug.utils import secure_filename
from pdf2docx import Converter
from docx2pdf import convert as docx_to_pdf_convert

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
MAX_FILE_SIZE_KB = 450  # Max 450 KB output

# ✅ Ghostscript path
GHOSTSCRIPT_PATH = r"C:\Program Files\gs\gs10.05.1\bin\gswin64c.exe"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------- Compression Helpers ----------
def compress_with_ghostscript(input_path, output_path, quality='screen'):
    try:
        subprocess.run([
            GHOSTSCRIPT_PATH,
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            f"-dPDFSETTINGS=/{quality}",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            f"-sOutputFile={output_path}",
            input_path
        ], check=True)
        return True
    except Exception as e:
        print(f"Ghostscript error: {e}")
        return False

def downscale_pdf_to_images(input_path, output_path, scale=0.4):
    try:
        doc = fitz.open(input_path)
        new_doc = fitz.open()
        for page in doc:
            pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale))
            new_page = new_doc.new_page(width=pix.width, height=pix.height)
            new_page.insert_image(new_page.rect, pixmap=pix)
        new_doc.save(output_path, garbage=4, deflate=True)
        new_doc.close()
        doc.close()
    except Exception as e:
        print(f"PyMuPDF error: {e}")

def insert_image_into_pdf(pdf_path, image_path, page_num=1, width=200, height=200):
    try:
        doc = fitz.open(pdf_path)
        if page_num < 1 or page_num > len(doc):
            page_num = 1
        page = doc[page_num - 1]
        rect = fitz.Rect(50, 50, 50 + width, 50 + height)
        page.insert_image(rect, filename=image_path)
        temp_output = pdf_path.replace(".pdf", "_with_image.pdf")
        doc.save(temp_output)
        doc.close()
        return temp_output
    except Exception as e:
        print(f"Image insert error: {e}")
        return pdf_path

def try_multiple_methods(input_path, output_base):
    quality_levels = ['screen', 'ebook', 'printer']
    for quality in quality_levels:
        output_path = output_base + f"_gs_{quality}.pdf"
        if compress_with_ghostscript(input_path, output_path, quality):
            if os.path.getsize(output_path) / 1024 <= MAX_FILE_SIZE_KB:
                return os.path.basename(output_path)
    for scale in [0.4, 0.3, 0.25]:
        output_path = output_base + f"_img_{int(scale * 100)}.pdf"
        downscale_pdf_to_images(input_path, output_path, scale)
        if os.path.getsize(output_path) / 1024 <= MAX_FILE_SIZE_KB:
            return os.path.basename(output_path)
    return None

# ---------- Image to PDF ----------
def images_to_pdf(image_paths, output_path):
    try:
        doc = fitz.open()
        for img_path in image_paths:
            img_doc = fitz.open(img_path)
            rect = img_doc[0].rect
            pdfbytes = img_doc.convert_to_pdf()
            img_pdf = fitz.open("pdf", pdfbytes)
            page = doc.new_page(width=rect.width, height=rect.height)
            page.show_pdf_page(rect, img_pdf, 0)
        doc.save(output_path)
        doc.close()
        return True
    except Exception as e:
        print(f"Image to PDF error: {e}")
        return False

# ---------- PDF to Word ----------
def pdf_to_word(pdf_path, output_path):
    try:
        cv = Converter(pdf_path)
        cv.convert(output_path, start=0, end=None)
        cv.close()
        return True
    except Exception as e:
        print(f"PDF to Word conversion error: {e}")
        return False

# ---------- Word to PDF ----------
def word_to_pdf(word_path, output_path):
    try:
        docx_to_pdf_convert(word_path, output_path)
        return True
    except Exception as e:
        print(f"Word to PDF conversion error: {e}")
        return False

# ---------- Routes ----------
@app.route('/', methods=['GET'])
def home():
    return render_template("index.html")

@app.route('/compress', methods=['POST'])
def compress_pdf():
    file = request.files.get('pdf')
    if not file or file.filename == '':
        return "No PDF selected."
    filename = secure_filename(file.filename)
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(input_path)

    image_file = request.files.get('image')
    if image_file and image_file.filename != '':
        image_filename = secure_filename(image_file.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        image_file.save(image_path)
        page_num = int(request.form.get('page_num', 1))
        img_width = int(request.form.get('img_width', 200))
        img_height = int(request.form.get('img_height', 200))
        input_path = insert_image_into_pdf(input_path, image_path, page_num, img_width, img_height)

    base_output_path = os.path.join(app.config['UPLOAD_FOLDER'], f"compressed_{os.path.splitext(filename)[0]}")
    result_file = try_multiple_methods(input_path, base_output_path)
    if result_file:
        final_path = os.path.join(app.config['UPLOAD_FOLDER'], result_file)
        final_size = os.path.getsize(final_path) / 1024
        return render_template("index.html", compress_link=result_file, compress_size=f"{final_size:.2f} KB")
    else:
        return "❌ Could not compress below 450KB."

@app.route('/images-to-pdf', methods=['POST'])
def convert_images_to_pdf():
    files = request.files.getlist('images')
    if not files:
        return "No images selected."
    image_paths = []
    for file in files:
        if file.filename != '':
            img_filename = secure_filename(file.filename)
            img_path = os.path.join(app.config['UPLOAD_FOLDER'], img_filename)
            file.save(img_path)
            image_paths.append(img_path)

    output_filename = "images_converted.pdf"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    if images_to_pdf(image_paths, output_path):
        return render_template("index.html", img_pdf_link=output_filename)
    else:
        return "❌ Failed to convert images to PDF."

@app.route('/pdf-to-word', methods=['POST'])
def convert_pdf_to_word():
    file = request.files.get('pdf')
    if not file or file.filename == '':
        return "No PDF selected."
    
    filename = secure_filename(file.filename)
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(input_path)

    output_filename = f"{os.path.splitext(filename)[0]}.docx"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

    if pdf_to_word(input_path, output_path):
        return render_template("index.html", pdf_to_word_link=output_filename)
    else:
        return "❌ Failed to convert PDF to Word."

@app.route('/word-to-pdf', methods=['POST'])
def convert_word_to_pdf():
    file = request.files.get('word')
    if not file or file.filename == '':
        return "No Word document selected."
        
    filename = secure_filename(file.filename)
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(input_path)

    output_filename = f"{os.path.splitext(filename)[0]}.pdf"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

    if word_to_pdf(input_path, output_path):
        return render_template("index.html", word_to_pdf_link=output_filename)
    else:
        return "❌ Failed to convert Word to PDF."

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ---------- Run ----------
if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, request, render_template, send_from_directory
import os
import subprocess
import fitz  # PyMuPDF
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
MAX_FILE_SIZE_KB = 450  # Max 450 KB output

# ✅ Update path to match your Ghostscript installation
GHOSTSCRIPT_PATH = r"C:\Program Files\gs\gs10.05.1\bin\gswin64c.exe"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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

def try_multiple_methods(input_path, output_base):
    # 1. Ghostscript: try several quality levels
    quality_levels = ['screen', 'ebook', 'printer']
    for quality in quality_levels:
        output_path = output_base + f"_gs_{quality}.pdf"
        if compress_with_ghostscript(input_path, output_path, quality):
            if os.path.getsize(output_path) / 1024 <= MAX_FILE_SIZE_KB:
                return os.path.basename(output_path)

    # 2. PyMuPDF downscaling with lower scales
    for scale in [0.4, 0.3, 0.25]:
        output_path = output_base + f"_img_{int(scale * 100)}.pdf"
        downscale_pdf_to_images(input_path, output_path, scale)
        if os.path.getsize(output_path) / 1024 <= MAX_FILE_SIZE_KB:
            return os.path.basename(output_path)

    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'pdf' not in request.files:
            return 'No file part in request.'

        file = request.files['pdf']
        if file.filename == '':
            return 'No file selected.'

        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)

        base_output_path = os.path.join(app.config['UPLOAD_FOLDER'], f"compressed_{filename}")
        result_file = try_multiple_methods(input_path, base_output_path)

        if result_file:
            final_path = os.path.join(app.config['UPLOAD_FOLDER'], result_file)
            final_size = os.path.getsize(final_path) / 1024
            return render_template("index.html", download_link=result_file, size_kb=f"{final_size:.2f} KB")
        else:
            return "❌ Could not compress below 450KB. Try a smaller PDF."

    return render_template("index.html")

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)

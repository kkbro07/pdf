import os
import uuid
import time
import shutil
from flask import Flask, request, render_template, send_from_directory, abort, url_for
from werkzeug.utils import secure_filename

import fitz  # PyMuPDF
from pdf2docx import Converter
from docx import Document as DocxDocument
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from PIL import Image

app = Flask(__name__)

# Use ephemeral /tmp storage on serverless environments like Vercel.
UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "/tmp/uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

MAX_FILE_SIZE_KB = 450  # target output size

# ----------------- Utilities -----------------
def unique_filename(fname: str) -> str:
    name, ext = os.path.splitext(secure_filename(fname))
    return f"{name}_{int(time.time())}_{uuid.uuid4().hex[:8]}{ext}"

# ----------------- PDF compression (PyMuPDF-based) -----------------
def downscale_pdf_to_images(input_path: str, output_path: str, scale: float = 0.5):
    """
    Rasterize pages at lower resolution and rebuild PDF.
    This helps reduce file size without requiring Ghostscript.
    """
    try:
        doc = fitz.open(input_path)
        new_doc = fitz.open()
        for page in doc:
            pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
            # Add a new page sized to the raster image
            new_page = new_doc.new_page(width=pix.width, height=pix.height)
            new_page.insert_image(new_page.rect, pixmap=pix)
        new_doc.save(output_path, garbage=4, deflate=True)
        new_doc.close()
        doc.close()
        return True
    except Exception as e:
        print("downscale_pdf_to_images error:", e)
        return False

def try_multiple_methods(input_path: str, output_base: str):
    """
    Try a few downscaling scales to get below MAX_FILE_SIZE_KB.
    Returns basename of created file inside UPLOAD_FOLDER or None.
    """
    # if already small, copy and return original name
    try:
        if os.path.getsize(input_path) / 1024 <= MAX_FILE_SIZE_KB:
            out_name = f"compressed_{os.path.basename(input_path)}"
            out_path = os.path.join(app.config["UPLOAD_FOLDER"], out_name)
            shutil.copy(input_path, out_path)
            return out_name
    except Exception:
        pass

    scales = [0.7, 0.6, 0.5, 0.4, 0.3]
    for s in scales:
        out_name = f"{os.path.basename(output_base)}_scale_{int(s*100)}.pdf"
        out_path = os.path.join(app.config["UPLOAD_FOLDER"], out_name)
        ok = downscale_pdf_to_images(input_path, out_path, s)
        if ok and os.path.exists(out_path):
            if os.path.getsize(out_path) / 1024 <= MAX_FILE_SIZE_KB:
                return out_name
    # nothing worked
    return None

# ----------------- Insert image into PDF -----------------
def insert_image_into_pdf(pdf_path, image_path, page_num=1, width=200, height=200):
    """
    Insert image into given page (1-based). Returns path to new PDF (full path) or original.
    """
    try:
        doc = fitz.open(pdf_path)
        if page_num < 1 or page_num > len(doc):
            page_num = 1
        page = doc[page_num - 1]
        # Insert near top-left with given width/height (px)
        rect = fitz.Rect(50, 50, 50 + width, 50 + height)
        page.insert_image(rect, filename=image_path)
        temp_output = os.path.join(app.config["UPLOAD_FOLDER"],
                                   f"{os.path.splitext(os.path.basename(pdf_path))[0]}_with_image.pdf")
        doc.save(temp_output)
        doc.close()
        return temp_output
    except Exception as e:
        print("insert_image_into_pdf error:", e)
        return pdf_path

# ----------------- Images -> PDF (Pillow) -----------------
def images_to_pdf(image_paths, output_path):
    """
    Uses Pillow to create a multi-page PDF from images.
    """
    try:
        pil_imgs = []
        for p in image_paths:
            img = Image.open(p).convert("RGB")
            pil_imgs.append(img)
        if not pil_imgs:
            return False
        first, rest = pil_imgs[0], pil_imgs[1:]
        first.save(output_path, save_all=True, append_images=rest)
        return True
    except Exception as e:
        print("images_to_pdf error:", e)
        return False

# ----------------- PDF -> Word -----------------
def pdf_to_word(pdf_path, output_path):
    """
    Uses pdf2docx Converter (pure python).
    """
    try:
        cv = Converter(pdf_path)
        cv.convert(output_path, start=0, end=None)
        cv.close()
        return True
    except Exception as e:
        print("pdf_to_word error:", e)
        return False

# ----------------- Word -> PDF (basic) -----------------
def word_to_pdf(word_path, output_path):
    """
    Basic Word->PDF using python-docx for extraction + ReportLab to write PDF.
    This is a simple text-first conversion (no advanced layout/styles).
    """
    try:
        docx = DocxDocument(word_path)
        elements = []
        styles = getSampleStyleSheet()
        normal = styles["Normal"]

        for para in docx.paragraphs:
            txt = para.text.strip()
            if txt:
                # Paragraphs may contain characters; replace multiple newlines
                elements.append(Paragraph(txt.replace("\n", "<br/>"), normal))
                elements.append(Spacer(1, 6))

        doc = SimpleDocTemplate(output_path, pagesize=A4)
        doc.build(elements)
        return True
    except Exception as e:
        print("word_to_pdf error:", e)
        return False

# ----------------- Routes -----------------
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/compress", methods=["POST"])
def compress_pdf_route():
    file = request.files.get("pdf")
    if not file or file.filename == "":
        return "No PDF selected.", 400

    filename = unique_filename(file.filename)
    input_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(input_path)

    # Optional image insertion
    image_file = request.files.get("image")
    if image_file and image_file.filename != "":
        image_filename = unique_filename(image_file.filename)
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)
        image_file.save(image_path)
        try:
            page_num = int(request.form.get("page_num", 1))
            img_width = int(request.form.get("img_width", 200))
            img_height = int(request.form.get("img_height", 200))
        except Exception:
            page_num, img_width, img_height = 1, 200, 200
        new_input = insert_image_into_pdf(input_path, image_path, page_num, img_width, img_height)
        input_path = new_input

    base_output_name = f"compressed_{os.path.splitext(filename)[0]}"
    output_base = os.path.join(app.config["UPLOAD_FOLDER"], base_output_name)
    result_name = try_multiple_methods(input_path, output_base)

    if result_name:
        final_path = os.path.join(app.config["UPLOAD_FOLDER"], result_name)
        final_size_kb = os.path.getsize(final_path) / 1024.0
        return render_template("index.html", compress_link=result_name, compress_size=f"{final_size_kb:.2f} KB")
    else:
        return "❌ Could not compress below 450KB.", 500

@app.route("/images-to-pdf", methods=["POST"])
def convert_images_to_pdf_route():
    files = request.files.getlist("images")
    if not files:
        return "No images selected.", 400

    image_paths = []
    for file in files:
        if file and file.filename != "":
            img_filename = unique_filename(file.filename)
            img_path = os.path.join(app.config["UPLOAD_FOLDER"], img_filename)
            file.save(img_path)
            image_paths.append(img_path)

    output_filename = f"images_converted_{int(time.time())}.pdf"
    output_path = os.path.join(app.config["UPLOAD_FOLDER"], output_filename)
    if images_to_pdf(image_paths, output_path):
        return render_template("index.html", img_pdf_link=output_filename)
    else:
        return "❌ Failed to convert images to PDF.", 500

@app.route("/pdf-to-word", methods=["POST"])
def convert_pdf_to_word_route():
    file = request.files.get("pdf")
    if not file or file.filename == "":
        return "No PDF selected.", 400

    filename = unique_filename(file.filename)
    input_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(input_path)

    output_filename = f"{os.path.splitext(filename)[0]}.docx"
    output_path = os.path.join(app.config["UPLOAD_FOLDER"], output_filename)

    if pdf_to_word(input_path, output_path):
        return render_template("index.html", pdf_to_word_link=output_filename)
    else:
        return "❌ Failed to convert PDF to Word.", 500

@app.route("/word-to-pdf", methods=["POST"])
def convert_word_to_pdf_route():
    file = request.files.get("word")
    if not file or file.filename == "":
        return "No Word document selected.", 400

    filename = unique_filename(file.filename)
    input_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(input_path)

    output_filename = f"{os.path.splitext(filename)[0]}.pdf"
    output_path = os.path.join(app.config["UPLOAD_FOLDER"], output_filename)

    if word_to_pdf(input_path, output_path):
        return render_template("index.html", word_to_pdf_link=output_filename)
    else:
        return "❌ Failed to convert Word to PDF. (Note: this is a basic text-first conversion)", 500

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    safe = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if not os.path.exists(safe):
        abort(404)
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)

# Local run (used for local testing)
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

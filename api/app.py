import os
import shutil
from flask import Flask, render_template, request, send_file, url_for
from pypdf import PdfReader, PdfWriter
from werkzeug.utils import secure_filename

# Initialize the Flask app
app = Flask(__name__, template_folder="../templates", static_folder="../static")

# Vercel's only writable directory is /tmp
UPLOAD_FOLDER = "/tmp/fileswapr_uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Function to create or clean the temporary upload folder
def ensure_upload_folder():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    else:
        shutil.rmtree(UPLOAD_FOLDER)
        os.makedirs(UPLOAD_FOLDER)

# The main route now renders the dashboard
@app.route("/")
def index():
    return render_template("index.html")

# --- WORKING FEATURE: MERGE PDF ---
@app.route("/merge", methods=["GET", "POST"])
def merge_pdfs():
    if request.method == "POST":
        try:
            ensure_upload_folder()
            pdfs = request.files.getlist("pdfs")
            
            if len(pdfs) < 2:
                return render_template("merge.html", error="Please select at least two PDF files to merge.")

            output_path = os.path.join(app.config["UPLOAD_FOLDER"], "merged_document.pdf")
            writer = PdfWriter()

            for pdf_file in pdfs:
                filename = secure_filename(pdf_file.filename)
                if filename:
                    pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                    pdf_file.save(pdf_path)
                    reader = PdfReader(pdf_path)
                    for page in reader.pages:
                        writer.add_page(page)

            with open(output_path, "wb") as f_out:
                writer.write(f_out)

            return send_file(output_path, as_attachment=True, download_name="merged.pdf")

        except Exception as e:
            print(f"An error occurred during merge: {e}")
            return render_template("merge.html", error="An internal server error occurred. Please try again.")

    return render_template("merge.html")

# --- COMING SOON PAGES ---
# Each route renders a placeholder page with the correct title and icon

@app.route("/compress-pdf")
def compress_pdf():
    return render_template("coming-soon.html", tool_name="Compress PDF", icon_class="fas fa-file-zipper")

@app.route("/pdf-to-word")
def pdf_to_word():
    return render_template("coming-soon.html", tool_name="PDF to Word", icon_class="fas fa-file-word")
    
@app.route("/word-to-pdf")
def word_to_pdf():
    return render_template("coming-soon.html", tool_name="Word to PDF", icon_class="fas fa-file-pdf")

@app.route("/edit-pdf")
def edit_pdf():
    return render_template("coming-soon.html", tool_name="Edit PDF", icon_class="fas fa-pen-to-square")

@app.route("/ocr-pdf")
def ocr_pdf():
    return render_template("coming-soon.html", tool_name="OCR PDF", icon_class="fas fa-magnifying-glass-plus")
    
@app.route("/password-protect-pdf")
def password_protect_pdf():
    return render_template("coming-soon.html", tool_name="Password Protect PDF", icon_class="fas fa-lock")

# Required for Vercel deployment
app = app
import os
from flask import Flask, render_template, request, send_file, url_for, redirect
from pypdf import PdfReader, PdfWriter
from fpdf import FPDF
from werkzeug.utils import secure_filename
import shutil

app = Flask(__name__, template_folder="../templates", static_folder="../static")

# Use a temporary directory for file uploads
UPLOAD_FOLDER = "/tmp/fileswapr"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Clean up the temp folder on startup (optional but good practice)
@app.before_request
def before_request():
    if os.path.exists(UPLOAD_FOLDER):
        shutil.rmtree(UPLOAD_FOLDER)
    os.makedirs(UPLOAD_FOLDER)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/compress", methods=["GET", "POST"])
def compress_pdf():
    if request.method == "POST":
        pdf_file = request.files["pdf"]
        if pdf_file:
            filename = secure_filename(pdf_file.filename)
            input_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            output_path = os.path.join(app.config["UPLOAD_FOLDER"], "compressed_" + filename)
            pdf_file.save(input_path)

            reader = PdfReader(input_path)
            writer = PdfWriter()

            for page in reader.pages:
                writer.add_page(page)

            writer.add_metadata({}) # Remove metadata
            
            # This is a basic form of "compression" by recreating the PDF.
            # For more advanced compression, you'd need libraries that optimize images and fonts.
            
            with open(output_path, "wb") as f:
                writer.write(f)

            return send_file(output_path, as_attachment=True)
    # For a GET request, just render the page
    return render_template("compress.html")


@app.route("/images-to-pdf", methods=["GET", "POST"])
def images_to_pdf():
    if request.method == "POST":
        images = request.files.getlist("images")
        if images:
            output_path = os.path.join(app.config["UPLOAD_FOLDER"], "converted_images.pdf")
            pdf = FPDF()
            for img in images:
                img_path = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(img.filename))
                img.save(img_path)
                pdf.add_page()
                # Use image dimensions to avoid stretching
                pdf.image(img_path, x=10, y=10, w=190) 
            pdf.output(output_path)
            return send_file(output_path, as_attachment=True)
    return render_template("images-to-pdf.html")


@app.route("/merge", methods=["GET", "POST"])
def merge_pdfs():
    if request.method == "POST":
        pdfs = request.files.getlist("pdfs")
        if pdfs:
            output_path = os.path.join(app.config["UPLOAD_FOLDER"], "merged.pdf")
            writer = PdfWriter()
            for pdf_file in pdfs:
                pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(pdf_file.filename))
                pdf_file.save(pdf_path)
                reader = PdfReader(pdf_path)
                for page in reader.pages:
                    writer.add_page(page)
            with open(output_path, "wb") as f:
                writer.write(f)
            return send_file(output_path, as_attachment=True)
    return render_template("merge.html")


@app.route("/split", methods=["GET", "POST"])
def split_pdf():
    if request.method == "POST":
        pdf_file = request.files["pdf"]
        if pdf_file:
            filename = secure_filename(pdf_file.filename)
            input_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            pdf_file.save(input_path)

            reader = PdfReader(input_path)
            mid = len(reader.pages) // 2

            # Define output paths using os.path.join
            output1_name = "part1_" + filename
            output2_name = "part2_" + filename
            output1_path = os.path.join(app.config["UPLOAD_FOLDER"], output1_name)
            output2_path = os.path.join(app.config["UPLOAD_FOLDER"], output2_name)

            writer1, writer2 = PdfWriter(), PdfWriter()

            for i, page in enumerate(reader.pages):
                if i < mid:
                    writer1.add_page(page)
                else:
                    writer2.add_page(page)
            
            with open(output1_path, "wb") as f:
                writer1.write(f)
            with open(output2_path, "wb") as f:
                writer2.write(f)

            # Re-render the page with download links
            return render_template("split.html", 
                                   download_link1=f"/download?file={output1_name}",
                                   download_link2=f"/download?file={output2_name}")
    return render_template("split.html")


# "Coming Soon" Pages
@app.route("/pdf-to-word")
def pdf_to_word():
    return render_template("pdf-to-word.html")

@app.route("/word-to-pdf")
def word_to_pdf():
    return render_template("word-to-pdf.html")


# Dynamic download route
@app.route("/download")
def download():
    file_name = request.args.get("file")
    if file_name:
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file_name)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
    return "File not found.", 404

# Vercel requirement
app = app
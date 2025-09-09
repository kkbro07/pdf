import os
from flask import Flask, render_template, request, send_file
from pypdf import PdfReader, PdfWriter
from fpdf import FPDF
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder="../templates", static_folder='../static')

UPLOAD_FOLDER = "/tmp"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def index():
    return render_template("index.html")


# Compress PDF (basic metadata/images removal)
@app.route("/compress", methods=["GET", "POST"])
def compress_pdf():
    if request.method == "POST":
        pdf_file = request.files["pdf"]
        filename = secure_filename(pdf_file.filename)
        input_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        output_path = os.path.join(app.config["UPLOAD_FOLDER"], "compressed_" + filename)
        pdf_file.save(input_path)

        reader = PdfReader(input_path)
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        writer.remove_images()
        writer.add_metadata({})
        with open(output_path, "wb") as f:
            writer.write(f)
        return send_file(output_path, as_attachment=True)
    return render_template("compress.html") # Assumes you have a template for each tool


# Convert Images to PDF
@app.route("/images-to-pdf", methods=["GET", "POST"])
def images_to_pdf():
    if request.method == "POST":
        images = request.files.getlist("images")
        output_path = os.path.join(app.config["UPLOAD_FOLDER"], "images.pdf")

        pdf = FPDF()
        for img in images:
            img_path = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(img.filename))
            img.save(img_path)
            pdf.add_page()
            pdf.image(img_path, x=10, y=10, w=180)

        pdf.output(output_path)
        return send_file(output_path, as_attachment=True)
    return render_template("images-to-pdf.html") # Assumes you have a template for each tool


# Merge PDFs
@app.route("/merge", methods=["GET", "POST"])
def merge_pdfs():
    if request.method == "POST":
        pdfs = request.files.getlist("pdfs")
        output_path = os.path.join(app.config["UPLOAD_FOLDER"], "merged.pdf")

        writer = PdfWriter()
        for pdf in pdfs:
            pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(pdf.filename))
            pdf.save(pdf_path)
            reader = PdfReader(pdf_path)
            for page in reader.pages:
                writer.add_page(page)

        with open(output_path, "wb") as f:
            writer.write(f)
        return send_file(output_path, as_attachment=True)
    return render_template("merge.html")


# Split PDF (first half / second half)
@app.route("/split", methods=["GET", "POST"])
def split_pdf():
    if request.method == "POST":
        pdf_file = request.files["pdf"]
        filename = secure_filename(pdf_file.filename)
        input_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        pdf_file.save(input_path)

        reader = PdfReader(input_path)
        mid = len(reader.pages) // 2
        output1 = os.path.join(app.config["UPLOAD_FOLDER"], "part1_" + filename)
        output2 = os.path.join(app.config["UPLOAD_FOLDER"], "part2_" + filename)

        writer1, writer2 = PdfWriter(), PdfWriter()

        for i, page in enumerate(reader.pages):
            if i < mid:
                writer1.add_page(page)
            else:
                writer2.add_page(page)
        
        with open(output1, "wb") as f:
            writer1.write(f)
        with open(output2, "wb") as f:
            writer2.write(f)

        # You should create a template to render these download links properly
        return f"""<h3>PDF Split Done!</h3>
                   <a href='/download?file={output1}'>Download Part 1</a><br>
                   <a href='/download?file={output2}'>Download Part 2</a>"""
    return render_template("split.html") # Assumes you have a template for each tool


@app.route("/download")
def download():
    file_path = request.args.get("file")
    if file_path and os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "File not found.", 404


if __name__ == '__main__':
    app.run(debug=True)
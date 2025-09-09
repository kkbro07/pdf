import os
from flask import Flask, render_template, request, send_file, url_for, flash, redirect
from pypdf import PdfReader, PdfWriter
from fpdf import FPDF # fpdf2 is the modern version, but FPDF still works for basic tasks.
from werkzeug.utils import secure_filename
import shutil # For clearing the upload folder

app = Flask(__name__, template_folder="../templates", static_folder="../static")

# Configuration for file uploads
UPLOAD_FOLDER = "/tmp/fileswapr_uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # Max upload size 16MB
app.secret_key = 'supersecretkey' # Needed for flash messages

# Helper to clear the upload folder (useful for Vercel's ephemeral storage)
def clear_upload_folder():
    for filename in os.listdir(app.config["UPLOAD_FOLDER"]):
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

# Call this periodically or on app start/end if needed,
# though Vercel's /tmp is usually cleared between invocations.

@app.context_processor
def inject_global_vars():
    """Injects variables available in all templates."""
    return {
        'SITE_NAME': 'FileSwapr',
        'SITE_URL': 'https://fileswapr.vercel.app', # Update this to your actual domain
    }


# --- Routes for Pages ---
@app.route("/")
def index():
    return render_template(
        "index.html",
        title="FileSwapr - Free Online PDF & Word Tools | Compress, Convert, Merge",
        description="FileSwapr offers free online tools to compress, merge, split PDFs, convert PDF to Word, Word to PDF, and images to PDF. Fast, secure, and no signup required."
    )

@app.route("/compress-pdf")
def compress_pdf_page():
    return render_template(
        "compress.html",
        title="Compress PDF Online - Reduce PDF File Size for Free | FileSwapr",
        description="Quickly reduce the file size of your PDF documents online for free. Optimize PDFs for email and web with FileSwapr's PDF compressor."
    )

@app.route("/images-to-pdf")
def images_to_pdf_page():
    return render_template(
        "images_to_pdf.html",
        title="Convert Images to PDF Online - JPG to PDF, PNG to PDF | FileSwapr",
        description="Convert multiple images (JPG, PNG, etc.) into a single PDF document online. Easy, fast, and free image to PDF converter."
    )

@app.route("/merge-pdfs")
def merge_pdfs_page():
    return render_template(
        "merge.html",
        title="Merge PDFs Online - Combine Multiple PDF Files for Free | FileSwapr",
        description="Combine two or more PDF documents into one single PDF file online. Free PDF merger tool for all your documents."
    )

@app.route("/split-pdf")
def split_pdf_page():
    return render_template(
        "split.html",
        title="Split PDF Online - Divide PDF into Multiple Files | FileSwapr",
        description="Split PDF documents online into separate files. Easily extract pages or divide your PDF into multiple parts for free."
    )

@app.route("/pdf-to-word")
def pdf_to_word_page():
    return render_template(
        "pdf_to_word.html",
        title="Convert PDF to Word Online - Free PDF to DOCX Converter | FileSwapr",
        description="Convert your PDF files to editable Microsoft Word documents (.docx) online for free. High-quality PDF to Word conversion (Coming Soon)."
    )

@app.route("/word-to-pdf")
def word_to_pdf_page():
    return render_template(
        "word_to_pdf.html",
        title="Convert Word to PDF Online - Free DOCX to PDF Converter | FileSwapr",
        description="Convert your Microsoft Word documents (.doc, .docx) to professional PDF files online for free (Coming Soon)."
    )

# --- File Processing Routes (POST requests) ---

@app.route("/process-compress", methods=["POST"])
def process_compress_pdf():
    if 'pdf' not in request.files:
        flash('No PDF file part')
        return redirect(url_for('compress_pdf_page'))
    
    pdf_file = request.files["pdf"]
    if pdf_file.filename == '':
        flash('No selected file')
        return redirect(url_for('compress_pdf_page'))

    if pdf_file and pdf_file.filename.endswith('.pdf'):
        filename = secure_filename(pdf_file.filename)
        input_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        output_filename = "compressed_" + filename
        output_path = os.path.join(app.config["UPLOAD_FOLDER"], output_filename)

        try:
            pdf_file.save(input_path)

            reader = PdfReader(input_path)
            writer = PdfWriter()

            for page in reader.pages:
                writer.add_page(page)

            # Basic compression: remove metadata and images (pypdf's remove_images is basic)
            writer.remove_images()
            writer.add_metadata({})

            with open(output_path, "wb") as f:
                writer.write(f)

            # Clean up input file after processing
            os.remove(input_path)

            return send_file(output_path, as_attachment=True, download_name=output_filename)
        except Exception as e:
            flash(f"Error compressing PDF: {e}")
            return redirect(url_for('compress_pdf_page'))
    else:
        flash('Invalid file type. Please upload a PDF.')
        return redirect(url_for('compress_pdf_page'))


@app.route("/process-images-to-pdf", methods=["POST"])
def process_images_to_pdf():
    if 'images' not in request.files:
        flash('No image files selected.')
        return redirect(url_for('images_to_pdf_page'))

    images = request.files.getlist("images")
    if not images or all(img.filename == '' for img in images):
        flash('No selected files.')
        return redirect(url_for('images_to_pdf_page'))

    output_filename = "images_combined.pdf"
    output_path = os.path.join(app.config["UPLOAD_FOLDER"], output_filename)

    pdf = FPDF()
    temp_image_paths = []
    
    try:
        for img_file in images:
            if img_file and img_file.filename != '':
                filename = secure_filename(img_file.filename)
                img_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                img_file.save(img_path)
                temp_image_paths.append(img_path)

                pdf.add_page()
                # Determine image type for FPDF
                file_extension = os.path.splitext(filename)[1].lower()
                if file_extension in ['.jpg', '.jpeg']:
                    img_type = 'JPEG'
                elif file_extension == '.png':
                    img_type = 'PNG'
                else:
                    # FPDF might support others, but these are common
                    flash(f"Unsupported image type: {file_extension}. Skipping.")
                    continue
                
                pdf.image(img_path, x=10, y=10, w=180, type=img_type)
        
        if not temp_image_paths: # No valid images processed
            flash("No valid images were processed into PDF.")
            return redirect(url_for('images_to_pdf_page'))

        pdf.output(output_path)

        # Clean up temporary image files
        for path in temp_image_paths:
            os.remove(path)

        return send_file(output_path, as_attachment=True, download_name=output_filename)
    except Exception as e:
        flash(f"Error converting images to PDF: {e}")
        return redirect(url_for('images_to_pdf_page'))


@app.route("/process-merge", methods=["POST"])
def process_merge_pdfs():
    if 'pdfs' not in request.files:
        flash('No PDF files selected.')
        return redirect(url_for('merge_pdfs_page'))

    pdfs = request.files.getlist("pdfs")
    if not pdfs or all(pdf.filename == '' for pdf in pdfs):
        flash('No selected files.')
        return redirect(url_for('merge_pdfs_page'))
    
    if len(pdfs) < 2:
        flash('Please select at least two PDF files to merge.')
        return redirect(url_for('merge_pdfs_page'))

    output_filename = "merged.pdf"
    output_path = os.path.join(app.config["UPLOAD_FOLDER"], output_filename)

    writer = PdfWriter()
    temp_pdf_paths = []

    try:
        for pdf_file in pdfs:
            if pdf_file and pdf_file.filename.endswith('.pdf'):
                filename = secure_filename(pdf_file.filename)
                pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                pdf_file.save(pdf_path)
                temp_pdf_paths.append(pdf_path)

                reader = PdfReader(pdf_path)
                for page in reader.pages:
                    writer.add_page(page)
            else:
                flash(f"Skipping non-PDF file: {pdf_file.filename}")

        if not temp_pdf_paths: # No valid PDFs processed
            flash("No valid PDFs were processed for merging.")
            return redirect(url_for('merge_pdfs_page'))
            
        with open(output_path, "wb") as f:
            writer.write(f)

        # Clean up temporary input PDF files
        for path in temp_pdf_paths:
            os.remove(path)

        return send_file(output_path, as_attachment=True, download_name=output_filename)
    except Exception as e:
        flash(f"Error merging PDFs: {e}")
        return redirect(url_for('merge_pdfs_page'))


@app.route("/process-split", methods=["POST"])
def process_split_pdf():
    if 'pdf' not in request.files:
        flash('No PDF file part')
        return redirect(url_for('split_pdf_page'))
    
    pdf_file = request.files["pdf"]
    if pdf_file.filename == '':
        flash('No selected file')
        return redirect(url_for('split_pdf_page'))

    if pdf_file and pdf_file.filename.endswith('.pdf'):
        filename = secure_filename(pdf_file.filename)
        input_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        pdf_file.save(input_path)

        try:
            reader = PdfReader(input_path)
            total_pages = len(reader.pages)
            if total_pages < 2:
                flash('PDF must have at least two pages to split.')
                os.remove(input_path)
                return redirect(url_for('split_pdf_page'))

            mid = total_pages // 2

            output1_filename = "part1_" + filename
            output2_filename = "part2_" + filename
            output1_path = os.path.join(app.config["UPLOAD_FOLDER"], output1_filename)
            output2_path = os.path.join(app.config["UPLOAD_FOLDER"], output2_filename)

            writer1 = PdfWriter()
            writer2 = PdfWriter()

            for i, page in enumerate(reader.pages):
                if i < mid:
                    writer1.add_page(page)
                else:
                    writer2.add_page(page)

            with open(output1_path, "wb") as f:
                writer1.write(f)
            with open(output2_path, "wb") as f:
                writer2.write(f)
            
            # Clean up input file after processing
            os.remove(input_path)

            # Store file paths in session or return links to a download page
            # For simplicity, we'll render a download page with direct links
            return render_template(
                "download.html",
                title="Download Split PDFs | FileSwapr",
                description="Your PDF has been successfully split. Download the two parts here.",
                download_files=[
                    {"name": output1_filename, "url": url_for('download_file', filename=output1_filename)},
                    {"name": output2_filename, "url": url_for('download_file', filename=output2_filename)}
                ]
            )
        except Exception as e:
            flash(f"Error splitting PDF: {e}")
            return redirect(url_for('split_pdf_page'))
    else:
        flash('Invalid file type. Please upload a PDF.')
        return redirect(url_for('split_pdf_page'))


# This route serves files directly from the UPLOAD_FOLDER
@app.route("/download/<filename>")
def download_file(filename):
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name=filename)
    else:
        flash("File not found.")
        return redirect(url_for('index')) # Redirect to homepage or error page


# --- Placeholder Routes for "Coming Soon" Features ---
@app.route("/process-pdf-to-word", methods=["POST"])
def process_pdf_to_word():
    flash("PDF to Word conversion is coming soon!")
    return redirect(url_for('pdf_to_word_page'))

@app.route("/process-word-to-pdf", methods=["POST"])
def process_word_to_pdf():
    flash("Word to PDF conversion is coming soon!")
    return redirect(url_for('word_to_pdf_page'))


# ✅ Vercel requires this
# This ensures the app instance is directly accessible for Vercel's build process
app = app
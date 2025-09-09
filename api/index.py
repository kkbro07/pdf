import os
from flask import Flask, render_template, request, send_file, url_for, flash, redirect
from pypdf import PdfReader, PdfWriter
from fpdf import FPDF
from werkzeug.utils import secure_filename
import shutil

app = Flask(__name__, template_folder="../templates", static_folder="../static")

# Configuration for file uploads
UPLOAD_FOLDER = "/tmp/fileswapr_uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max upload size 16MB
app.secret_key = 'supersecretkey'  # Needed for flash messages

# Helper to clear the upload folder
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

@app.context_processor
def inject_global_vars():
    """Injects variables available in all templates."""
    return {
        'SITE_NAME': 'FileSwapr',
        'SITE_URL': 'https://fileswapr.vercel.app',  # Update this to your actual domain
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

# --- New "Coming Soon" Page Routes ---

# 1. PDF Creation
@app.route("/create-pdf-from-office")
def create_pdf_from_office_page():
    return render_template("coming_soon.html", 
                           title="Create PDF from Office - Coming Soon | FileSwapr",
                           tool_name="Create PDF from Word/Excel/PowerPoint",
                           icon_class="fas fa-file-invoice")

@app.route("/create-pdf-from-text")
def create_pdf_from_text_page():
    return render_template("coming_soon.html", 
                           title="Create PDF from Text - Coming Soon | FileSwapr",
                           tool_name="Create PDF from Text",
                           icon_class="fas fa-file-alt")

@app.route("/create-pdf-from-html")
def create_pdf_from_html_page():
    return render_template("coming_soon.html", 
                           title="Create PDF from HTML - Coming Soon | FileSwapr",
                           tool_name="Create PDF from HTML/Web Page",
                           icon_class="fas fa-code")

@app.route("/create-fillable-pdf")
def create_fillable_pdf_page():
    return render_template("coming_soon.html", 
                           title="Create Fillable PDF - Coming Soon | FileSwapr",
                           tool_name="Create Fillable PDF Forms",
                           icon_class="fas fa-file-signature")

# 2. PDF Conversion (already have images-to-pdf, pdf-to-word, word-to-pdf)
@app.route("/pdf-to-excel")
def pdf_to_excel_page():
    return render_template("coming_soon.html", 
                           title="PDF to Excel - Coming Soon | FileSwapr",
                           tool_name="PDF to Excel",
                           icon_class="fas fa-file-excel")

@app.route("/pdf-to-powerpoint")
def pdf_to_powerpoint_page():
    return render_template("coming_soon.html", 
                           title="PDF to PowerPoint - Coming Soon | FileSwapr",
                           tool_name="PDF to PowerPoint",
                           icon_class="fas fa-file-powerpoint")

@app.route("/pdf-to-image")
def pdf_to_image_page():
    return render_template("coming_soon.html", 
                           title="PDF to Image - Coming Soon | FileSwapr",
                           tool_name="PDF to Image (JPG, PNG, TIFF)",
                           icon_class="fas fa-images")

@app.route("/pdf-to-text")
def pdf_to_text_page():
    return render_template("coming_soon.html", 
                           title="PDF to Text - Coming Soon | FileSwapr",
                           tool_name="PDF to Text",
                           icon_class="fas fa-font")

@app.route("/pdf-to-html")
def pdf_to_html_page():
    return render_template("coming_soon.html", 
                           title="PDF to HTML - Coming Soon | FileSwapr",
                           tool_name="PDF to HTML",
                           icon_class="fas fa-file-code")

@app.route("/excel-to-pdf")
def excel_to_pdf_page():
    return render_template("coming_soon.html", 
                           title="Excel to PDF - Coming Soon | FileSwapr",
                           tool_name="Excel to PDF",
                           icon_class="fas fa-file-excel")

@app.route("/powerpoint-to-pdf")
def powerpoint_to_pdf_page():
    return render_template("coming_soon.html", 
                           title="PowerPoint to PDF - Coming Soon | FileSwapr",
                           tool_name="PowerPoint to PDF",
                           icon_class="fas fa-file-powerpoint")

# 3. PDF Editing
@app.route("/edit-pdf-text")
def edit_pdf_text_page():
    return render_template("coming_soon.html", 
                           title="Edit PDF Text - Coming Soon | FileSwapr",
                           tool_name="Edit PDF Text",
                           icon_class="fas fa-edit")

@app.route("/edit-pdf-images")
def edit_pdf_images_page():
    return render_template("coming_soon.html", 
                           title="Edit PDF Images - Coming Soon | FileSwapr",
                           tool_name="Edit PDF Images",
                           icon_class="fas fa-image")

@app.route("/add-remove-watermark")
def add_remove_watermark_page():
    return render_template("coming_soon.html", 
                           title="Add/Remove Watermark - Coming Soon | FileSwapr",
                           tool_name="Add/Remove Watermarks",
                           icon_class="fas fa-tint")

# 4. PDF Merging & Splitting (already have merge-pdfs, split-pdf)
@app.route("/extract-pages")
def extract_pages_page():
    return render_template("coming_soon.html", 
                           title="Extract PDF Pages - Coming Soon | FileSwapr",
                           tool_name="Extract Specific PDF Pages",
                           icon_class="fas fa-file-export")

@app.route("/delete-pages")
def delete_pages_page():
    return render_template("coming_soon.html", 
                           title="Delete PDF Pages - Coming Soon | FileSwapr",
                           tool_name="Delete PDF Pages",
                           icon_class="fas fa-trash-alt")

@app.route("/reorder-pages")
def reorder_pages_page():
    return render_template("coming_soon.html", 
                           title="Reorder PDF Pages - Coming Soon | FileSwapr",
                           tool_name="Reorder PDF Pages",
                           icon_class="fas fa-sort-numeric-down")

@app.route("/crop-pages")
def crop_pages_page():
    return render_template("coming_soon.html", 
                           title="Crop PDF Pages - Coming Soon | FileSwapr",
                           tool_name="Crop PDF Pages",
                           icon_class="fas fa-crop")

# 5. PDF Compression & Optimization (already have compress-pdf)
@app.route("/optimize-pdf-web")
def optimize_pdf_web_page():
    return render_template("coming_soon.html", 
                           title="Optimize PDF for Web - Coming Soon | FileSwapr",
                           tool_name="Optimize PDF for Web (Fast Web View)",
                           icon_class="fas fa-globe")

# 6. PDF Security
@app.route("/password-protect-pdf")
def password_protect_pdf_page():
    return render_template("coming_soon.html", 
                           title="Password Protect PDF - Coming Soon | FileSwapr",
                           tool_name="Password Protect PDF",
                           icon_class="fas fa-lock")

@app.route("/remove-pdf-password")
def remove_pdf_password_page():
    return render_template("coming_soon.html", 
                           title="Remove PDF Password - Coming Soon | FileSwapr",
                           tool_name="Remove PDF Password",
                           icon_class="fas fa-unlock")

@app.route("/sign-pdf")
def sign_pdf_page():
    return render_template("coming_soon.html", 
                           title="Sign PDF Digitally - Coming Soon | FileSwapr",
                           tool_name="Sign PDF Digitally",
                           icon_class="fas fa-signature")

# 7. PDF Accessibility & Metadata
@app.route("/edit-pdf-metadata")
def edit_pdf_metadata_page():
    return render_template("coming_soon.html", 
                           title="Edit PDF Metadata - Coming Soon | FileSwapr",
                           tool_name="Add/Edit PDF Metadata",
                           icon_class="fas fa-info-circle")

@app.route("/add-bookmarks")
def add_bookmarks_page():
    return render_template("coming_soon.html", 
                           title="Add PDF Bookmarks - Coming Soon | FileSwapr",
                           tool_name="Add Bookmarks/Table of Contents",
                           icon_class="fas fa-bookmark")

@app.route("/create-pdf-a")
def create_pdf_a_page():
    return render_template("coming_soon.html", 
                           title="Create PDF/A - Coming Soon | FileSwapr",
                           tool_name="Create PDF/A for Archiving",
                           icon_class="fas fa-archive")

# 8. PDF OCR (Optical Character Recognition)
@app.route("/pdf-ocr")
def pdf_ocr_page():
    return render_template("coming_soon.html", 
                           title="PDF OCR - Coming Soon | FileSwapr",
                           tool_name="PDF OCR (Convert Scanned PDF to Searchable Text)",
                           icon_class="fas fa-search")

# 9. PDF Form Functions (already have create-fillable-pdf)
@app.route("/extract-form-data")
def extract_form_data_page():
    return render_template("coming_soon.html", 
                           title="Extract Form Data - Coming Soon | FileSwapr",
                           tool_name="Extract Form Data",
                           icon_class="fas fa-file-export")

# 10. PDF Viewing & Navigation
@app.route("/add-hyperlinks")
def add_hyperlinks_page():
    return render_template("coming_soon.html", 
                           title="Add PDF Hyperlinks - Coming Soon | FileSwapr",
                           tool_name="Add Hyperlinks",
                           icon_class="fas fa-link")

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

# Add "process-*" routes for all new "coming soon" features
# These will simply redirect and flash a message initially
@app.route("/process-create-pdf-from-office", methods=["POST"])
@app.route("/process-create-pdf-from-text", methods=["POST"])
@app.route("/process-create-pdf-from-html", methods=["POST"])
@app.route("/process-create-fillable-pdf", methods=["POST"])
@app.route("/process-pdf-to-excel", methods=["POST"])
@app.route("/process-pdf-to-powerpoint", methods=["POST"])
@app.route("/process-pdf-to-image", methods=["POST"])
@app.route("/process-pdf-to-text", methods=["POST"])
@app.route("/process-pdf-to-html", methods=["POST"])
@app.route("/process-excel-to-pdf", methods=["POST"])
@app.route("/process-powerpoint-to-pdf", methods=["POST"])
@app.route("/process-edit-pdf-text", methods=["POST"])
@app.route("/process-edit-pdf-images", methods=["POST"])
@app.route("/process-add-remove-watermark", methods=["POST"])
@app.route("/process-extract-pages", methods=["POST"])
@app.route("/process-delete-pages", methods=["POST"])
@app.route("/process-reorder-pages", methods=["POST"])
@app.route("/process-crop-pages", methods=["POST"])
@app.route("/process-optimize-pdf-web", methods=["POST"])
@app.route("/process-password-protect-pdf", methods=["POST"])
@app.route("/process-remove-pdf-password", methods=["POST"])
@app.route("/process-sign-pdf", methods=["POST"])
@app.route("/process-edit-pdf-metadata", methods=["POST"])
@app.route("/process-add-bookmarks", methods=["POST"])
@app.route("/process-create-pdf-a", methods=["POST"])
@app.route("/process-pdf-ocr", methods=["POST"])
@app.route("/process-extract-form-data", methods=["POST"])
@app.route("/process-add-hyperlinks", methods=["POST"])
def coming_soon_post_handler():
    # Dynamically determine which "coming soon" page to redirect to
    # This requires a bit more logic if you want to redirect to the *specific* page.
    # For now, it will redirect to the index or a generic 'coming_soon' page.
    # A more robust solution would pass the tool_name or a redirect_url.
    flash("This feature is coming soon!")
    return redirect(url_for('index')) # Redirect to home for now, or create a generic coming soon page

# ✅ Vercel requires this
# This ensures the app instance is directly accessible for Vercel's build process
app = app
import os
import uuid
import shutil
import io
import zipfile
from flask import Flask, render_template, request, send_file, jsonify, after_this_request
from werkzeug.utils import secure_filename

# --- PDF Libraries ---
from pypdf import PdfReader, PdfWriter
from pdf2docx import Converter as Pdf2DocxConverter
import img2pdf

# --- Image Library ---
from PIL import Image

# --- Document Libraries ---
from docx import Document
from pptx import Presentation
import pandas as pd
from xhtml2pdf import pisa
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

app = Flask(__name__)

# --- VERCEL CONFIGURATION ---
# Vercel only allows writing to /tmp
UPLOAD_FOLDER = '/tmp'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # Limit to 50MB for Serverless stability

# --- 1. TOOL DEFINITIONS ---
TOOLS = {
    # BASIC PDF
    'merge-pdf': {'name': 'Merge PDF', 'desc': 'Combine multiple PDFs.', 'accept': '.pdf', 'cat': 'basic'},
    'split-pdf': {'name': 'Split PDF', 'desc': 'Separate pages into ZIP.', 'accept': '.pdf', 'cat': 'basic'},
    'compress-pdf': {'name': 'Compress PDF', 'desc': 'Reduce PDF size.', 'accept': '.pdf', 'cat': 'basic'},

    # CONVERT TO PDF
    'jpg-to-pdf': {'name': 'JPG to PDF', 'desc': 'Convert Images to PDF.', 'accept': '.jpg,.jpeg,.png', 'cat': 'to-pdf'},
    'word-to-pdf': {'name': 'Word to PDF', 'desc': 'DOCX text to PDF.', 'accept': '.docx', 'cat': 'to-pdf'},
    'ppt-to-pdf': {'name': 'PowerPoint to PDF', 'desc': 'PPTX slides to PDF.', 'accept': '.pptx', 'cat': 'to-pdf'},
    'excel-to-pdf': {'name': 'Excel to PDF', 'desc': 'XLSX to PDF.', 'accept': '.xlsx', 'cat': 'to-pdf'},
    'html-to-pdf': {'name': 'HTML to PDF', 'desc': 'HTML to PDF.', 'accept': '.html', 'cat': 'to-pdf'},

    # CONVERT FROM PDF
    'pdf-to-word': {'name': 'PDF to Word', 'desc': 'PDF to DOCX.', 'accept': '.pdf', 'cat': 'from-pdf'},
    'pdf-to-txt': {'name': 'PDF to Text', 'desc': 'Extract plain text.', 'accept': '.pdf', 'cat': 'from-pdf'},

    # EDIT & SECURITY
    'remove-pages': {'name': 'Remove Pages', 'desc': 'Remove 1st page.', 'accept': '.pdf', 'cat': 'organize'},
    'extract-pages': {'name': 'Extract Pages', 'desc': 'Extract 1st page.', 'accept': '.pdf', 'cat': 'organize'},
    'rotate-pdf': {'name': 'Rotate PDF', 'desc': 'Rotate 90 degrees.', 'accept': '.pdf', 'cat': 'edit'},
    'protect-pdf': {'name': 'Protect PDF', 'desc': 'Add Password.', 'accept': '.pdf', 'cat': 'security', 'inputs': ['password']},
    'unlock-pdf': {'name': 'Unlock PDF', 'desc': 'Remove Password.', 'accept': '.pdf', 'cat': 'security', 'inputs': ['password']},
}

@app.route('/')
def index():
    return render_template('index.html', tools=TOOLS)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy-policy.html')

@app.route('/terms-of-service')
def terms_of_service():
    return render_template('terms-of-service.html')

@app.route('/support')
def support():
    return render_template('support.html')

@app.route('/tool/<slug>')
def tool_view(slug):
    tool = TOOLS.get(slug, TOOLS['merge-pdf'])
    return render_template('tool.html', tool=tool, slug=slug)

# --- Helper Functions ---
def docx_to_pdf_content(input_path, output_path):
    doc = Document(input_path)
    c = canvas.Canvas(output_path, pagesize=letter)
    text = c.beginText(40, 750)
    for para in doc.paragraphs:
        if para.text.strip():
            # Basic text wrap prevents crash
            line = para.text.replace('\n', ' ')[:90] 
            text.textLine(line)
        if text.getY() < 50:
            c.drawText(text)
            c.showPage()
            text = c.beginText(40, 750)
    c.drawText(text)
    c.save()

@app.route('/api/process/<slug>', methods=['POST'])
def process_file(slug):
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files uploaded'}), 400
    
    files = request.files.getlist('files[]')
    password = request.form.get('password', '1234')

    # Unique Session in /tmp
    session_id = str(uuid.uuid4())
    session_folder = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
    os.makedirs(session_folder, exist_ok=True)

    input_paths = []
    
    try:
        # Save Inputs
        for file in files:
            if file.filename:
                safe_name = secure_filename(file.filename)
                path = os.path.join(session_folder, safe_name)
                file.save(path)
                input_paths.append(path)

        if not input_paths: 
            return jsonify({'error': 'No files saved'}), 400

        # Define Output
        out_name = f"processed_{uuid.uuid4().hex[:6]}"
        out_path = os.path.join(session_folder, f"{out_name}.pdf")
        dl_ext = ".pdf"

        # --- LOGIC HANDLERS ---
        if slug == 'merge-pdf':
            merger = PdfWriter()
            for p in input_paths: merger.append(p)
            merger.write(out_path)
            merger.close()

        elif slug == 'split-pdf':
            dl_ext = ".zip"
            zip_target = os.path.join(session_folder, f"{out_name}.zip")
            with zipfile.ZipFile(zip_target, 'w') as zf:
                reader = PdfReader(input_paths[0])
                for i, page in enumerate(reader.pages):
                    writer = PdfWriter()
                    writer.add_page(page)
                    p_path = os.path.join(session_folder, f"page_{i+1}.pdf")
                    writer.write(p_path)
                    zf.write(p_path, f"page_{i+1}.pdf")

        elif slug == 'compress-pdf':
            reader = PdfReader(input_paths[0])
            writer = PdfWriter()
            writer.append_pages_from_reader(reader)
            writer.add_metadata(reader.metadata)
            with open(out_path, "wb") as f:
                writer.write(f)

        elif slug == 'jpg-to-pdf':
            with open(out_path, "wb") as f:
                f.write(img2pdf.convert(input_paths))

        elif slug == 'word-to-pdf':
            docx_to_pdf_content(input_paths[0], out_path)

        elif slug == 'html-to-pdf':
            with open(input_paths[0], "r", encoding='utf-8', errors='ignore') as f:
                pisa.CreatePDF(f.read(), dest=open(out_path, "wb"))

        elif slug == 'pdf-to-word':
            dl_ext = ".docx"
            out_path = os.path.join(session_folder, f"{out_name}.docx")
            cv = Pdf2DocxConverter(input_paths[0])
            cv.convert(out_path, start=0, end=None)
            cv.close()

        elif slug == 'pdf-to-txt':
            dl_ext = ".txt"
            out_path = os.path.join(session_folder, f"{out_name}.txt")
            reader = PdfReader(input_paths[0])
            with open(out_path, "w", encoding="utf-8") as f:
                for page in reader.pages:
                    f.write(page.extract_text() + "\n")

        elif slug == 'protect-pdf':
            reader = PdfReader(input_paths[0])
            writer = PdfWriter()
            writer.append_pages_from_reader(reader)
            writer.encrypt(password)
            writer.write(out_path)

        elif slug == 'unlock-pdf':
            reader = PdfReader(input_paths[0])
            if reader.is_encrypted:
                reader.decrypt(password)
            writer = PdfWriter()
            writer.append_pages_from_reader(reader)
            writer.write(out_path)

        # Fallback for undefined
        else:
            shutil.copy(input_paths[0], out_path)

        final_file = f"{out_name}{dl_ext}"
        return jsonify({
            'success': True,
            'download_url': f"/download/{session_id}/{final_file}"
        })

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

@app.route('/download/<session_id>/<filename>')
def download(session_id, filename):
    folder = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
    return send_file(os.path.join(folder, filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
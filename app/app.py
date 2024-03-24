from flask import Flask, render_template, request, redirect, url_for
from PyPDF2 import PdfReader, PdfWriter

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mergetool')
def tool():
    return render_template('merge.html')


@app.route('/merge', methods=['POST'])
def merge():
    if request.method == 'POST':
        pdf_files = request.files.getlist('pdf_files')
        merged_pdf = PdfWriter()

        for file in pdf_files:
            pdf = PdfReader(file)
            for page in pdf.pages:
                merged_pdf.add_page(page)

        with open('static/merged_pdf.pdf', 'wb') as output_pdf:
            merged_pdf.write(output_pdf)

        return redirect(url_for('result'))

@app.route('/result')
def result():
    return render_template('result.html')

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for
from PyPDF2 import PdfReader, PdfWriter

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mergetool')
def tool():
    return render_template('merge.html')


@app.route('/merge', methods=['POST'])
def merge():
    if request.method == 'POST':
        pdf_files = request.files.getlist('pdf_files')
        merged_pdf = PdfWriter()

        for file in pdf_files:
            pdf = PdfReader(file)
            for page in pdf.pages:
                merged_pdf.add_page(page)

        with open('static/merged_pdf.pdf', 'wb') as output_pdf:
            merged_pdf.write(output_pdf)

        return redirect(url_for('result'))

@app.route('/result')
def result():
    return render_template('result.html')




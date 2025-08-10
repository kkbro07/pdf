




# All-in-One PDF & Word Tools

This is a web-based application built with **Flask** that provides a suite of tools for managing PDF and Word documents.  
Users can perform various operations such as compressing PDFs, converting images to a single PDF file, and converting documents between PDF and Word formats.

---

## ✨ Features

- **PDF Compression**: Upload a PDF file and compress it to a smaller size (under 450KB).  
  Optionally, add an image to a specific page before compression.

- **Images to PDF**: Select multiple images and convert them into a single PDF document.

- **PDF to Word**: Convert a PDF file into an editable Word document (`.docx`).

- **Word to PDF**: Convert a Word document (`.doc`, `.docx`) into a PDF file.

- **Modern UI/UX**: A clean, responsive, and user-friendly interface built with **Bootstrap 5**.

---

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

- Python **3.6+**
- **Ghostscript** (Required for PDF compression)  
  Download from [Ghostscript Official Website](https://www.ghostscript.com/download.html)
- `pip` (Python package installer)

---
````markdown
## ⚙ Installation

1. **Clone the repository**:
   ```bash
   git clone https://your-repository-url.git
   cd your-repository-directory
   
````
2. **Create a virtual environment (recommended)**:

   ```bash
   python -m venv venv
   # Activate environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install required Python packages**:

   ```bash
   pip install Flask PyMuPDF Werkzeug pdf2docx docx2pdf
   ```

4. **Configure Ghostscript**:
   Open `app.py` and update the `GHOSTSCRIPT_PATH` variable with the correct path.

   **Example (Windows)**:

   ```python
   GHOSTSCRIPT_PATH = r"C:\Program Files\gs\gs10.05.1\bin\gswin64c.exe"
   ```

   **Example (macOS/Linux)**:

   ```python
   GHOSTSCRIPT_PATH = "/usr/local/bin/gs"
   ```

---

## 🚀 Usage

1. **Run the Flask application**:

   ```bash
   python app.py
   ```

2. **Open your browser** and go to:

   ```
   http://127.0.0.1:5000
   ```

3. **Use the tools**:

   * Homepage shows all available tools.
   * Click on a tool or scroll to it.
   * Upload your files and process them.
   * Download the result after processing.

---

## 📂 Project Structure

```
.
├── app.py              # Main Flask application file
├── templates
│   └── index.html      # HTML template for UI
├── uploads             # Stores uploaded & processed files
└── README.md           # Project documentation
```

---

## 🤝 Contributing

Contributions are welcome!
If you have ideas, suggestions, or bug reports, open an issue or submit a pull request.

---

## 📜 License

This project is licensed under the **MIT License**.

---

**Built with ❤️ by Kirtan Kalathiya**

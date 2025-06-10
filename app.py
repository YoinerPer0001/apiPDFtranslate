from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
import uuid, os, time, subprocess
from pdf2docx import Converter
from docx import Document
from googletrans import Translator

app = FastAPI()
translator = Translator()

# Carpeta temporal de trabajo
TEMP_FOLDER = "temp"
os.makedirs(TEMP_FOLDER, exist_ok=True)

# Eliminar archivos de más de 15 minutos (900 segundos)
def delete_old_files(folder, max_age_seconds=900):
    now = time.time()
    for filename in os.listdir(folder):
        path = os.path.join(folder, filename)
        if os.path.isfile(path):
            if now - os.path.getmtime(path) > max_age_seconds:
                try:
                    os.remove(path)
                    print(f"Borrado archivo antiguo: {path}")
                except Exception as e:
                    print(f"Error al borrar {path}: {e}")

# Función para convertir DOCX a PDF con LibreOffice
def convert_docx_to_pdf_linux(input_path, output_dir):
    try:
        subprocess.run([
            "libreoffice",
            "--headless",
            "--convert-to", "pdf",
            "--outdir", output_dir,
            input_path
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error al convertir DOCX a PDF con LibreOffice: {e}")
        raise

@app.post("/translate-pdf/")
async def translate_pdf(
    file: UploadFile = File(...),
    target_lang: str = Form(...)
):
    # Limpiar archivos antiguos
    delete_old_files(TEMP_FOLDER)

    # Crear nombres de archivo únicos
    base_name = str(uuid.uuid4())
    input_pdf_path = os.path.join(TEMP_FOLDER, f"{base_name}.pdf")
    output_docx_path = input_pdf_path.replace(".pdf", ".docx")
    translated_docx_path = output_docx_path.replace(".docx", f"_translated.docx")
    translated_pdf_path = translated_docx_path.replace(".docx", ".pdf")

    # Guardar el archivo subido
    with open(input_pdf_path, "wb") as f:
        f.write(await file.read())

    # Convertir PDF a DOCX
    cv = Converter(input_pdf_path)
    cv.convert(output_docx_path, start=0, end=None)
    cv.close()

    # Leer y traducir el DOCX
    doc = Document(output_docx_path)
    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            try:
                translated = translator.translate(paragraph.text, dest=target_lang).text
                paragraph.text = translated
            except Exception as e:
                print("Error al traducir:", e)
    doc.save(translated_docx_path)

    # Convertir el DOCX traducido a PDF con LibreOffice
    convert_docx_to_pdf_linux(translated_docx_path, TEMP_FOLDER)

    # Borrar archivos intermedios
    try:
        os.remove(input_pdf_path)
        os.remove(output_docx_path)
        os.remove(translated_docx_path)
    except Exception as e:
        print(f"Error borrando archivos temporales: {e}")

    # Enviar el PDF traducido
    return FileResponse(translated_pdf_path, filename="translated.pdf", media_type="application/pdf")

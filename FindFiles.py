import flet as ft
import FoxmlWorker as FW
import hashlib
import urllib.parse

def dereference(identifier: str) -> str:
    """Identifies object and datastream location within Fedora objectStores and datastreamStore."""
    slashed = identifier.replace('+', '/')
    full = f"info:fedora/{slashed}"
    hash_value = hashlib.md5(full.encode('utf-8')).hexdigest()

    # Generate directory structure
    subbed = f"{hash_value[:2]}/{hash_value[2:4]}/{hash_value[4:]}"

    # URL encode the full string
    encoded = urllib.parse.quote(full, safe='').replace('_', '%5F')
    return f"{subbed}/{encoded}"

def main(page: ft.Page):
    data_dir = "/usr/local/fedora/data/"
    page.title = "Fedora File Finder"

    # Input field
    input_text = ft.TextField(label="Enter a PID", on_submit=lambda e: update_labels(e.control.value))

    # Labels output
    foxml_path = ft.Text("")
    obj_path = ft.Text("")
    pdf_path = ft.Text("")

    def update_labels(text):
        """Update the labels based on the entered PID."""
        path = dereference(text)
        foxml = f"{data_dir}/objectStore/{path}"
        foxml_path.value = f"Foxml Path: {foxml}"

        fw = FW.FWorker(foxml)
        all_files = fw.get_file_data()

        obj = all_files.get('OBJ')
        obj_path.value = f"Path to OBJ: {dereference(obj['filename'])}" if obj else "No OBJ file found."

        pdf = all_files.get('PDF')
        pdf_path.value = f"Path to PDF: {dereference(pdf['filename'])}" if pdf else "No PDF file found."

        page.update()  # Refresh UI

    # Adding widgets to the page
    page.add(input_text, foxml_path, obj_path, pdf_path)

ft.app(target=main)

#!/usr/bin/env python3

import flet as ft
import FoxmlWorker as FW
import hashlib
import urllib.parse

def dereference(identifier: str) -> str:
    # Replace '+' with '/' in the identifier
    slashed = identifier.replace('+', '/')
    full = f"info:fedora/{slashed}"
    hash_value = hashlib.md5(full.encode('utf-8')).hexdigest()
    subbed = "##"
    # Replace the '#' characters in `subbed` with the corresponding characters from `hash_value`
    hash_offset = 0
    pattern_offset = 0
    result = list(subbed)

    while pattern_offset < len(result) and hash_offset < len(hash_value):
        if result[pattern_offset] == '#':
            result[pattern_offset] = hash_value[hash_offset]
            hash_offset += 1
        pattern_offset += 1

    subbed = ''.join(result)
    # URL encode the full string, replacing '_' with '%5F'
    encoded = urllib.parse.quote(full, safe='').replace('_', '%5F')
    return f"{subbed}/{encoded}"

def main(page: ft.Page):
    data_dir = "/usr/local/fedora/data"
    page.title = "Fedora File Finder"

    # Styling
    page.bgcolor = "#2d2d2d"
    page.window_width = 350
    page.window_height = 600
    page.padding = 10

    # Input field
    input_text = ft.TextField(
        label="Enter a PID",
        on_submit=lambda e: update_labels(e.control.value),
        text_size=16,
        border_radius=10,
        bgcolor="#455a64",
        color="white"
    )

    # Labels output
    foxml_path = ft.Text("", color="white")
    obj_path = ft.Text("", color="white")
    pdf_path = ft.Text("", color="white")

    def update_labels(text):
        """Update the labels based on the entered PID."""
        path = dereference(text)
        foxml = f"{data_dir}/objectStore/{path}"
        foxml_path.value = f"Foxml Path: {foxml}"

        try:
            fw = FW.FWorker(foxml)  # Attempt to load Fedora object
            all_files = fw.get_file_data()
        except Exception as e:
            foxml_path.value = f"Error loading FOXML: {str(e)}"
            obj_path.value = "OBJ file: N/A"
            pdf_path.value = "PDF file: N/A"
            page.update()
            return  # Exit function early if loading fails

        obj = all_files.get('OBJ')
        obj_path.value = f"Path to OBJ: {dereference(obj['filename'])}" if obj else "No OBJ file found."

        pdf = all_files.get('PDF')
        pdf_path.value = f"Path to PDF: {dereference(pdf['filename'])}" if pdf else "No PDF file found."

        page.update()  # Refresh UI

    # Layout
    page.add(
        ft.Column(
            [
                ft.Container(content=input_text, bgcolor="#37474f", border_radius=10, height=50, padding=10),
                ft.Container(
                    content=ft.Column([foxml_path, obj_path, pdf_path], spacing=10),
                    padding=10,
                ),
            ],
            spacing=20,
        )
    )

ft.app(target=main)

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
    page.window.width = 350
    page.window.height = 600
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
    # Container to display file details dynamically
    global file_list  # Ensure it can be accessed in update_labels()
    file_list = ft.Column([], spacing=5)  # Initializes an empty column

    def update_labels(text):
        """Update the labels based on the entered PID."""
        path = dereference(text)
        foxml = f"{data_dir}/objectStore/{path}"
        foxml_path.value = ""
        foxml_path.value = ""
        foxml_path.spans = [
            ft.TextSpan(
                "Foxml Path: ",
                style=ft.TextStyle(color="red", weight="bold")
            ),
            ft.TextSpan(
                foxml,
                style=ft.TextStyle(color="white")
            ),
        ]

        try:
            fw = FW.FWorker(foxml)  # Attempt to load Fedora object
            all_files = fw.get_file_data()
        except Exception as e:
            foxml_path.spans = [
                ft.TextSpan("Error loading FOXML: ", style=ft.TextStyle(color="red", weight="bold")),
                ft.TextSpan(str(e), style=ft.TextStyle(color="white")),
            ]
            file_list.controls.clear()
            file_list.controls.append(ft.Text("No files found.", color="red"))
            page.update()
            return

        # Clear old file entries
        file_list.controls.clear()

        # Add each key-value pair dynamically
        for key, value in all_files.items():
            file_path = dereference(value['filename'])
            file_list.controls.append(
                ft.Text(
                    spans=[
                        ft.TextSpan(
                            f"{key}: ",
                            style=ft.TextStyle(color="red", weight="bold")
                        ),
                        ft.TextSpan(
                            f"{file_path}",
                            style=ft.TextStyle(color="white")
                        ),
                    ]
                )
            )

        page.update()  # Refresh UI

    # Layout
    page.add(
        ft.Column(
            [
                ft.Container(content=input_text, bgcolor="#37474f", border_radius=10, height=50, padding=10),
                ft.Container(content=foxml_path, padding=ft.Padding(bottom=15)),
                # 🛑 Adds extra space below `foxml_path`
                ft.Container(content=file_list, padding=10),  # ✅ Add file_list here
            ],
            spacing=20,
        )
    )


ft.app(target=main, host="0.0.0.0", port=8551)

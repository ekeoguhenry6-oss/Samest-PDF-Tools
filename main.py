import os
import shutil
import tempfile

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle

from pypdf import PdfReader, PdfWriter
from PIL import Image


# ============================================================
# ANDROID FILE PICKER
# ============================================================

try:
    from jnius import autoclass
    from android import activity

    PythonActivity = autoclass(
        "org.kivy.android.PythonActivity"
    )

    Intent = autoclass(
        "android.content.Intent"
    )

    app = None

    def open_android_picker(
        mime_types,
        multiple=False,
        save=False
    ):

        global app

        app = App.get_running_app()

        intent = Intent()

        if save:
            intent.setAction(
                Intent.ACTION_CREATE_DOCUMENT
            )

            intent.addCategory(
                Intent.CATEGORY_OPENABLE
            )

            intent.setType(
                "application/pdf"
            )

            intent.putExtra(
                Intent.EXTRA_TITLE,
                "Samest_Final.pdf"
            )

        else:
            intent.setAction(
                Intent.ACTION_OPEN_DOCUMENT
            )

            intent.addCategory(
                Intent.CATEGORY_OPENABLE
            )

            intent.addFlags(
                Intent.FLAG_GRANT_READ_URI_PERMISSION
            )

            intent.putExtra(
                Intent.EXTRA_ALLOW_MULTIPLE,
                multiple
            )

            if len(mime_types) == 1:
                intent.setType(
                    mime_types[0]
                )
            else:
                intent.setType(
                    "*/*"
                )

                intent.putExtra(
                    Intent.EXTRA_MIME_TYPES,
                    mime_types
                )

        activity.startActivityForResult(
            intent,
            2001
        )


    def on_activity_result(
        request_code,
        result_code,
        intent
    ):

        if request_code != 2001:
            return

        if result_code != -1:
            return

        if intent is None:
            return

        application = App.get_running_app()

        # SAVE RESULT
        if application.picker_mode == "save":

            uri = intent.getData()

            if uri:
                application.save_result(
                    uri
                )

            return

        # MULTIPLE FILES
        clip_data = intent.getClipData()

        if clip_data:

            files = []

            for i in range(
                clip_data.getItemCount()
            ):

                uri = (
                    clip_data
                    .getItemAt(i)
                    .getUri()
                )

                path = application.copy_uri(
                    uri
                )

                if path:
                    files.append(path)

            application.files_selected(
                files
            )

            return

        # SINGLE FILE
        uri = intent.getData()

        if uri:

            path = application.copy_uri(
                uri
            )

            if path:

                application.files_selected(
                    [path]
                )


    activity.bind(
        on_activity_result=on_activity_result
    )

except Exception:

    pass


# ============================================================
# MAIN APPLICATION
# ============================================================

class SamestPDFTools(App):

    def build(self):

        self.selected_files = []

        self.output_file = None

        self.picker_mode = None

        self.current_tool = None

        return self.create_home()


    # ========================================================
    # COLORS
    # ========================================================

    def gold(self):
        return (
            0.83,
            0.68,
            0.20,
            1
        )

    def dark(self):
        return (
            0.04,
            0.04,
            0.06,
            1
        )


    # ========================================================
    # HOME SCREEN
    # ========================================================

    def create_home(self):

        layout = BoxLayout(
            orientation="vertical",
            padding=dp(22),
            spacing=dp(15)
        )

        with layout.canvas.before:

            Color(
                *self.dark()
            )

            self.bg = RoundedRectangle(
                pos=layout.pos,
                size=layout.size,
                radius=[0]
            )

        layout.bind(
            pos=lambda obj, value:
            setattr(
                self.bg,
                "pos",
                value
            )
        )

        layout.bind(
            size=lambda obj, value:
            setattr(
                self.bg,
                "size",
                value
            )
        )

        # APP NAME

        title = Label(
            text="SAMEST PDF TOOLS",
            font_size=dp(27),
            bold=True,
            color=self.gold(),
            size_hint_y=None,
            height=dp(65)
        )

        layout.add_widget(
            title
        )

        subtitle = Label(
            text=(
                "Simple PDF & Document Tools\n"
                "Samest Technologies • 2026"
            ),
            font_size=dp(14),
            color=(
                0.75,
                0.75,
                0.78,
                1
            ),
            size_hint_y=None,
            height=dp(55)
        )

        layout.add_widget(
            subtitle
        )

        # MERGE PDF

        layout.add_widget(
            self.tool_button(
                "📄  MERGE PDFs",
                "Combine multiple PDF files",
                self.merge_pdfs
            )
        )

        # IMAGES TO PDF

        layout.add_widget(
            self.tool_button(
                "🖼  IMAGES → PDF",
                "Convert multiple images into one PDF",
                self.images_to_pdf
            )
        )

        # PDF + IMAGES

        layout.add_widget(
            self.tool_button(
                "📑  PDF + IMAGES → PDF",
                "Combine PDFs and images together",
                self.mixed_to_pdf
            )
        )

        # INFO

        info = Label(
            text=(
                "\nWorks with files from your phone,\n"
                "Downloads, Documents, WPS and other apps."
            ),
            font_size=dp(12),
            color=(
                0.60,
                0.60,
                0.63,
                1
            )
        )

        layout.add_widget(
            info
        )

        return layout


    # ========================================================
    # TOOL BUTTON
    # ========================================================

    def tool_button(
        self,
        title,
        description,
        function
    ):

        button = Button(
            text=(
                title +
                "\n" +
                description
            ),
            font_size=dp(16),
            bold=True,
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(85),
            background_normal="",
            background_color=(
                0.12,
                0.12,
                0.16,
                1
            ),
            color=(
                1,
                1,
                1,
                1
            )
        )

        button.bind(
            on_release=function
        )

        return button


    # ========================================================
    # MERGE PDFs
    # ========================================================

    def merge_pdfs(
        self,
        *args
    ):

        self.current_tool = "merge"

        self.picker_mode = "select"

        self.selected_files = []

        open_android_picker(
            [
                "application/pdf"
            ],
            multiple=True
        )


    # ========================================================
    # IMAGES TO PDF
    # ========================================================

    def images_to_pdf(
        self,
        *args
    ):

        self.current_tool = "images"

        self.picker_mode = "select"

        self.selected_files = []

        open_android_picker(
            [
                "image/*"
            ],
            multiple=True
        )


    # ========================================================
    # PDF + IMAGES
    # ========================================================

    def mixed_to_pdf(
        self,
        *args
    ):

        self.current_tool = "mixed"

        self.picker_mode = "select"

        self.selected_files = []

        open_android_picker(
            [
                "application/pdf",
                "image/*"
            ],
            multiple=True
        )


    # ========================================================
    # FILE SELECTED
    # ========================================================

    def files_selected(
        self,
        files
    ):

        if not files:
            self.show_message(
                "No files selected."
            )
            return

        self.selected_files = files

        if self.current_tool == "merge":

            if len(files) < 2:

                self.show_message(
                    "Please select at least 2 PDFs."
                )

                return

            self.create_merged_pdf(
                files
            )

        elif self.current_tool == "images":

            self.create_images_pdf(
                files
            )

        elif self.current_tool == "mixed":

            self.create_mixed_pdf(
                files
            )


    # ========================================================
    # MERGE PDF FILES
    # ========================================================

    def create_merged_pdf(
        self,
        files
    ):

        try:

            writer = PdfWriter()

            for file in files:

                reader = PdfReader(
                    file
                )

                for page in reader.pages:

                    writer.add_page(
                        page
                    )

            output = os.path.join(
                self.user_data_dir,
                "Samest_Merged.pdf"
            )

            with open(
                output,
                "wb"
            ) as file:

                writer.write(
                    file
                )

            self.output_file = output

            self.ask_save_location()

        except Exception as error:

            self.show_message(
                "Could not merge PDFs.\n\n"
                + str(error)
            )


    # ========================================================
    # IMAGES TO PDF
    # ========================================================

    def create_images_pdf(
        self,
        files
    ):

        try:

            images = []

            for file in files:

                image = Image.open(
                    file
                )

                if image.mode != "RGB":

                    image = image.convert(
                        "RGB"
                    )

                images.append(
                    image
                )

            if not images:

                self.show_message(
                    "No images found."
                )

                return

            output = os.path.join(
                self.user_data_dir,
                "Samest_Images.pdf"
            )

            images[0].save(
                output,
                "PDF",
                resolution=100,
                save_all=True,
                append_images=images[1:]
            )

            self.output_file = output

            self.ask_save_location()

        except Exception as error:

            self.show_message(
                "Could not create PDF.\n\n"
                + str(error)
            )


    # ========================================================
    # MIXED PDF + IMAGES
    # ========================================================

    def create_mixed_pdf(
        self,
        files
    ):

        try:

            writer = PdfWriter()

            temporary_files = []

            for file in files:

                extension = (
                    os.path.splitext(
                        file
                    )[1]
                    .lower()
                )

                # PDF

                if extension == ".pdf":

                    reader = PdfReader(
                        file
                    )

                    for page in reader.pages:

                        writer.add_page(
                            page
                        )

                # IMAGE

                elif extension in [
                    ".jpg",
                    ".jpeg",
                    ".png",
                    ".webp",
                    ".bmp"
                ]:

                    image = Image.open(
                        file
                    )

                    if image.mode != "RGB":

                        image = image.convert(
                            "RGB"
                        )

                    image_pdf = tempfile.NamedTemporaryFile(
                        suffix=".pdf",
                        delete=False
                    )

                    image_pdf.close()

                    image.save(
                        image_pdf.name,
                        "PDF"
                    )

                    temporary_files.append(
                        image_pdf.name
                    )

                    reader = PdfReader(
                        image_pdf.name
                    )

                    for page in reader.pages:

                        writer.add_page(
                            page
                        )

            output = os.path.join(
                self.user_data_dir,
                "Samest_Combined.pdf"
            )

            with open(
                output,
                "wb"
            ) as file:

                writer.write(
                    file
                )

            # Remove temporary image PDFs

            for temporary in temporary_files:

                try:

                    os.remove(
                        temporary
                    )

                except:

                    pass

            self.output_file = output

            self.ask_save_location()

        except Exception as error:

            self.show_message(
                "Could not create PDF.\n\n"
                + str(error)
            )


    # ========================================================
    # SAVE LOCATION
    # ========================================================

    def ask_save_location(
        self
    ):

        self.picker_mode = "save"

        open_android_picker(
            [
                "application/pdf"
            ],
            save=True
        )


    # ========================================================
    # SAVE RESULT
    # ========================================================

    def save_result(
        self,
        uri
    ):

        try:

            from jnius import autoclass

            PythonActivity = autoclass(
                "org.kivy.android.PythonActivity"
            )

            resolver = (
                PythonActivity
                .mActivity
                .getContentResolver()
            )

            input_file = open(
                self.output_file,
                "rb"
            )

            output_stream = (
                resolver.openOutputStream(
                    uri
                )
            )

            while True:

                data = input_file.read(
                    8192
                )

                if not data:
                    break

                output_stream.write(
                    data
                )

            input_file.close()

            output_stream.close()

            self.picker_mode = None

            self.show_message(
                "PDF saved successfully! 🎉"
            )

        except Exception as error:

            self.show_message(
                "Could not save the PDF.\n\n"
                + str(error)
            )


    # ========================================================
    # COPY ANDROID FILE TO APP STORAGE
    # ========================================================

    def copy_uri(
        self,
        uri
    ):

        try:

            from jnius import autoclass

            PythonActivity = autoclass(
                "org.kivy.android.PythonActivity"
            )

            resolver = (
                PythonActivity
                .mActivity
                .getContentResolver()
            )

            filename = "selected_file"

            cursor = resolver.query(
                uri,
                None,
                None,
                None,
                None
            )

            if cursor:

                name_index = (
                    cursor.getColumnIndex(
                        "_display_name"
                    )
                )

                if name_index >= 0:

                    cursor.moveToFirst()

                    filename = cursor.getString(
                        name_index
                    )

                cursor.close()

            destination = os.path.join(
                self.user_data_dir,
                filename
            )

            counter = 1

            base, extension = os.path.splitext(
                destination
            )

            while os.path.exists(
                destination
            ):

                destination = (
                    base
                    + "_"
                    + str(counter)
                    + extension
                )

                counter += 1

            input_stream = (
                resolver.openInputStream(
                    uri
                )
            )

            with open(
                destination,
                "wb"
            ) as output:

                buffer = bytearray(
                    8192
                )

                while True:

                    length = (
                        input_stream.read(
                            buffer
                        )
                    )

                    if length <= 0:
                        break

                    output.write(
                        buffer[:length]
                    )

            input_stream.close()

            return destination

        except Exception as error:

            print(
                "File error:",
                error
            )

            return None


    # ========================================================
    # MESSAGE BOX
    # ========================================================

    def show_message(
        self,
        message
    ):

        layout = BoxLayout(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(15)
        )

        label = Label(
            text=message,
            halign="center"
        )

        layout.add_widget(
            label
        )

        button = Button(
            text="OK",
            size_hint_y=None,
            height=dp(50)
        )

        layout.add_widget(
            button
        )

        popup = Popup(
            title="Samest PDF Tools",
            content=layout,
            size_hint=(
                0.88,
                0.38
            )
        )

        button.bind(
            on_release=popup.dismiss
        )

        popup.open()


# ============================================================
# START APP
# ============================================================

if __name__ == "__main__":

    SamestPDFTools().run()

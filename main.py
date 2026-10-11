import sqlite3
import os

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.core.image import Image as CoreImage
from kivy.core.image import ImageData
from kivy.utils import platform


class ImageDatabaseApp(App):

    def build(self):

        # Create database
        db_path = os.path.join(self.user_data_dir, "images.db")

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                image_data BLOB
            )
        """)

        # Look for image_2.jpg
        image_path = os.path.join(
            os.path.dirname(__file__),
            "image_2.jpg"
        )

        # Store image if it hasn't been stored yet
        cursor.execute(
            "SELECT COUNT(*) FROM images WHERE filename = ?",
            ("image_2.jpg",)
        )

        count = cursor.fetchone()[0]

        if count == 0 and os.path.exists(image_path):

            with open(image_path, "rb") as file:
                image_data = file.read()

            cursor.execute(
                """
                INSERT INTO images (filename, image_data)
                VALUES (?, ?)
                """,
                ("image_2.jpg", image_data)
            )

            conn.commit()

        # Retrieve image
        cursor.execute("""
            SELECT image_data
            FROM images
            WHERE filename = ?
            ORDER BY id DESC
            LIMIT 1
        """, ("image_2.jpg",))

        row = cursor.fetchone()

        conn.close()

        # Create screen
        layout = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=20
        )

        self.image = Image(
            allow_stretch=True,
            keep_ratio=True
        )

        layout.add_widget(self.image)

        button = Button(
            text="Display Image",
            size_hint_y=None,
            height=60
        )

        button.bind(on_press=self.display_image)

        layout.add_widget(button)

        self.image_data = row[0] if row else None

        return layout

    def display_image(self, instance):

        if self.image_data:

            # Save database image temporarily
            temp_path = os.path.join(
                self.user_data_dir,
                "temp_image.jpg"
            )

            with open(temp_path, "wb") as file:
                file.write(self.image_data)

            self.image.source = temp_path
            self.image.reload()


ImageDatabaseApp().run()
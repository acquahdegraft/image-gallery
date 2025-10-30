import reflex as rx
import asyncio
from typing import TypedDict, Union, Optional
import os
import logging


class Image(TypedDict):
    name: str
    url: str


class UploadedImage(TypedDict):
    name: str
    filename: str


class GalleryState(rx.State):
    """State for the image gallery."""

    is_loading: bool = True
    show_upload_modal: bool = False
    images: list[Union[Image, UploadedImage]] = []
    upload_progress: int = 0
    is_uploading: bool = False
    image_to_delete: Optional[int] = None
    show_lightbox: bool = False
    current_image_index: int = 0

    @rx.event
    async def on_load(self):
        """Simulate loading images on page load."""
        await asyncio.sleep(1)
        if not self.images:
            self.images = [
                {"name": "Mountain Vista", "url": "/placeholder.svg"},
                {"name": "City at Night", "url": "/placeholder.svg"},
                {"name": "Abstract Art", "url": "/placeholder.svg"},
                {"name": "Forest Trail", "url": "/placeholder.svg"},
                {"name": "Ocean Sunset", "url": "/placeholder.svg"},
                {"name": "Modern Architecture", "url": "/placeholder.svg"},
            ]
        self.is_loading = False

    @rx.event
    def toggle_upload_modal(self):
        """Toggle the visibility of the upload modal."""
        self.show_upload_modal = not self.show_upload_modal
        self.upload_progress = 0
        self.is_uploading = False

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        """Handle the upload of files."""
        if not files:
            yield rx.toast.error("No files selected.")
            return
        self.is_uploading = True
        self.upload_progress = 0
        yield
        for i, file in enumerate(files):
            upload_data = await file.read()
            outfile = rx.get_upload_dir() / file.name
            with outfile.open("wb") as f:
                f.write(upload_data)
            self.images.append(UploadedImage(name=file.name, filename=file.name))
            self.upload_progress = int((i + 1) / len(files) * 100)
            await asyncio.sleep(0.1)
            yield
        self.is_uploading = False
        self.show_upload_modal = False
        yield rx.toast.success(f"{len(files)} image(s) uploaded successfully!")

    @rx.event
    def set_image_to_delete(self, index: int):
        """Set the index of the image to be deleted."""
        self.image_to_delete = index

    @rx.event
    def cancel_delete(self):
        """Cancel the deletion of an image."""
        self.image_to_delete = None

    @rx.event
    def confirm_delete(self):
        """Confirm and delete the selected image."""
        if self.image_to_delete is not None:
            image_to_remove = self.images[self.image_to_delete]
            if "filename" in image_to_remove:
                try:
                    file_path = rx.get_upload_dir() / image_to_remove["filename"]
                    if file_path.exists():
                        os.remove(file_path)
                except Exception as e:
                    logging.exception(f"Error deleting file: {e}")
            self.images.pop(self.image_to_delete)
            self.image_to_delete = None
            yield rx.toast.info("Image deleted.")

    @rx.var
    def current_image(self) -> Union[Image, UploadedImage, None]:
        """Get the current image for the lightbox."""
        return (
            self.images[self.current_image_index]
            if 0 <= self.current_image_index < len(self.images)
            else None
        )

    @rx.event
    def open_lightbox(self, index: int):
        """Open the lightbox at a specific image index."""
        self.current_image_index = index
        self.show_lightbox = True

    @rx.event
    def close_lightbox(self):
        """Close the lightbox."""
        self.show_lightbox = False

    @rx.event
    def next_image(self):
        """Go to the next image in the lightbox."""
        self.current_image_index = (self.current_image_index + 1) % len(self.images)

    @rx.event
    def prev_image(self):
        """Go to the previous image in the lightbox."""
        self.current_image_index = (
            self.current_image_index - 1 + len(self.images)
        ) % len(self.images)

    @rx.event
    def handle_key_down(self, key: str):
        """Handle keyboard events for the lightbox."""
        if self.show_lightbox:
            if key == "ArrowRight":
                return GalleryState.next_image
            if key == "ArrowLeft":
                return GalleryState.prev_image
            if key == "Escape":
                return GalleryState.close_lightbox
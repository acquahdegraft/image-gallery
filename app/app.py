import reflex as rx
from app.states.gallery_state import GalleryState, Image


def header() -> rx.Component:
    """The header component for the gallery."""
    return rx.el.header(
        rx.el.div(
            rx.el.div(
                rx.icon("image", class_name="h-8 w-8 text-blue-600"),
                rx.el.h1(
                    "Image Gallery", class_name="text-2xl font-bold text-gray-800"
                ),
                class_name="flex items-center gap-3",
            ),
            rx.el.button(
                rx.icon("upload", class_name="h-4 w-4 mr-2"),
                "Upload",
                on_click=GalleryState.toggle_upload_modal,
                class_name="flex items-center bg-blue-500 text-white font-medium px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors shadow-sm",
            ),
            class_name="flex items-center justify-between w-full max-w-7xl mx-auto",
        ),
        class_name="w-full p-4 border-b border-gray-200 bg-white/80 backdrop-blur-sm sticky top-0 z-10",
    )


def image_card(image: Image, index: int) -> rx.Component:
    """A card to display an image in the gallery."""
    return rx.el.div(
        rx.el.div(
            rx.image(
                src=rx.cond(
                    image.contains("url"),
                    image["url"],
                    rx.get_upload_url(image["filename"]),
                ),
                alt=image["name"],
                class_name="w-full h-48 object-cover rounded-t-lg",
            ),
            on_click=lambda: GalleryState.open_lightbox(index),
            class_name="cursor-pointer",
        ),
        rx.el.div(
            rx.el.p(image["name"], class_name="font-semibold text-gray-700 truncate"),
            rx.el.button(
                rx.icon("trash-2", class_name="h-4 w-4"),
                on_click=lambda: GalleryState.set_image_to_delete(index),
                class_name="text-gray-400 hover:text-red-500 transition-colors",
                variant="ghost",
            ),
            class_name="p-3 flex justify-between items-center border-t border-gray-100",
        ),
        class_name="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden transition-all hover:shadow-lg hover:-translate-y-1",
    )


def skeleton_loader() -> rx.Component:
    """A skeleton loader for the image cards."""
    return rx.el.div(
        rx.el.div(class_name="w-full h-48 bg-gray-200"),
        rx.el.div(
            rx.el.div(class_name="h-4 w-3/4 bg-gray-200 rounded"),
            class_name="p-4 border-t border-gray-100",
        ),
        class_name="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden animate-pulse",
    )


def image_grid() -> rx.Component:
    """The grid of images or skeleton loaders."""
    return rx.el.div(
        rx.cond(
            GalleryState.is_loading,
            rx.fragment(rx.foreach(rx.Var.range(6), lambda _: skeleton_loader())),
            rx.foreach(GalleryState.images, image_card),
        ),
        class_name="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 p-6 max-w-7xl mx-auto",
    )


def upload_modal() -> rx.Component:
    """A modal for uploading images."""
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.content(
            rx.radix.primitives.dialog.title("Upload Images"),
            rx.radix.primitives.dialog.description(
                "Drag and drop your images here or click to select files."
            ),
            rx.upload.root(
                rx.el.div(
                    rx.icon("cloud-upload", class_name="h-12 w-12 text-gray-400"),
                    rx.el.p(
                        "Select files or drag and drop",
                        class_name="text-sm text-gray-500",
                    ),
                    class_name="flex flex-col items-center justify-center p-8 border-2 border-dashed border-gray-300 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors cursor-pointer",
                ),
                id="upload-area",
                accept={
                    "image/png": [".png"],
                    "image/jpeg": [".jpg", ".jpeg"],
                    "image/gif": [".gif"],
                    "image/webp": [".webp"],
                },
                max_files=10,
                multiple=True,
                class_name="mt-4",
            ),
            rx.el.div(
                rx.foreach(
                    rx.selected_files("upload-area"),
                    lambda file: rx.el.div(
                        rx.icon("file-image", class_name="h-4 w-4 text-gray-500"),
                        rx.el.span(file, class_name="text-sm truncate"),
                        class_name="flex items-center gap-2 p-2 bg-gray-100 rounded-md text-gray-700",
                    ),
                ),
                class_name="mt-4 space-y-2 max-h-32 overflow-y-auto",
            ),
            rx.cond(
                GalleryState.is_uploading,
                rx.el.div(
                    rx.el.progress(
                        value=GalleryState.upload_progress, class_name="w-full"
                    ),
                    rx.el.p(
                        f"Uploading... {GalleryState.upload_progress}%",
                        class_name="text-sm text-center mt-2 text-gray-600",
                    ),
                    class_name="mt-4 w-full",
                ),
                rx.fragment(),
            ),
            rx.el.div(
                rx.el.button(
                    "Cancel",
                    on_click=GalleryState.toggle_upload_modal,
                    class_name="bg-gray-200 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-300",
                    type="button",
                ),
                rx.el.button(
                    rx.cond(GalleryState.is_uploading, "Uploading...", "Upload"),
                    on_click=GalleryState.handle_upload(
                        rx.upload_files(upload_id="upload-area")
                    ),
                    disabled=GalleryState.is_uploading,
                    class_name="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 disabled:bg-blue-300",
                    type="button",
                ),
                class_name="flex justify-end gap-3 mt-4",
            ),
            style={"max_width": "450px"},
            class_name="bg-white p-6 rounded-lg shadow-xl",
        ),
        open=GalleryState.show_upload_modal,
        on_open_change=GalleryState.toggle_upload_modal,
    )


def delete_confirmation_dialog() -> rx.Component:
    """A dialog to confirm image deletion."""
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.content(
            rx.radix.primitives.dialog.title("Confirm Deletion"),
            rx.radix.primitives.dialog.description(
                "Are you sure you want to delete this image? This action cannot be undone."
            ),
            rx.el.div(
                rx.el.button(
                    "Cancel",
                    on_click=GalleryState.cancel_delete,
                    class_name="bg-gray-200 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-300",
                ),
                rx.el.button(
                    "Delete",
                    on_click=GalleryState.confirm_delete,
                    class_name="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600",
                ),
                class_name="flex justify-end gap-3 mt-4",
            ),
            style={"max_width": "450px"},
        ),
        open=GalleryState.image_to_delete.is_not_none(),
        on_open_change=lambda _: GalleryState.cancel_delete(),
    )


def lightbox() -> rx.Component:
    """A lightbox modal for viewing images fullscreen."""
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.portal(
            rx.radix.primitives.dialog.overlay(
                class_name="fixed inset-0 bg-black/80 backdrop-blur-sm z-40"
            ),
            rx.radix.primitives.dialog.content(
                rx.image(
                    src=rx.cond(
                        GalleryState.current_image.contains("url"),
                        GalleryState.current_image["url"],
                        rx.get_upload_url(GalleryState.current_image["filename"]),
                    ),
                    alt=GalleryState.current_image["name"],
                    class_name="max-h-[85vh] max-w-[90vw] object-contain rounded-lg shadow-2xl",
                ),
                rx.el.button(
                    rx.icon("x", class_name="h-6 w-6"),
                    on_click=GalleryState.close_lightbox,
                    class_name="absolute top-4 right-4 text-white/70 hover:text-white transition-colors",
                    variant="ghost",
                ),
                rx.el.button(
                    rx.icon("chevron-left", class_name="h-8 w-8"),
                    on_click=GalleryState.prev_image,
                    class_name="absolute left-4 top-1/2 -translate-y-1/2 text-white/70 hover:text-white transition-colors",
                    variant="ghost",
                ),
                rx.el.button(
                    rx.icon("chevron-right", class_name="h-8 w-8"),
                    on_click=GalleryState.next_image,
                    class_name="absolute right-4 top-1/2 -translate-y-1/2 text-white/70 hover:text-white transition-colors",
                    variant="ghost",
                ),
                class_name="fixed inset-0 flex items-center justify-center bg-transparent p-0 z-50",
                on_click=GalleryState.close_lightbox,
            ),
        ),
        open=GalleryState.show_lightbox,
        on_open_change=lambda _: GalleryState.close_lightbox(),
    )


def index() -> rx.Component:
    return rx.el.main(
        header(),
        image_grid(),
        upload_modal(),
        delete_confirmation_dialog(),
        lightbox(),
        rx.window_event_listener(on_key_down=GalleryState.handle_key_down),
        class_name="font-['Montserrat'] bg-gray-50 min-h-screen text-gray-800",
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index, on_load=GalleryState.on_load)
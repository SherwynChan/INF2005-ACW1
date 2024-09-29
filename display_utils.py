from PIL import Image, ImageTk
import ttkbootstrap as ttkb
from tkinter import messagebox

def display_analysis(app, payload_path, cover_path, stego_path):
    """ Display the analysis page with payload, cover image, stego image, and difference image. """
    app.image_refs.clear()
    app.clear_window()
    ttkb.Button(app.root, text="Back to Main Menu", command=app.create_landing_page, bootstyle="danger").pack(anchor='nw', padx=10, pady=10)
    ttkb.Label(app.root, text="Embedding Analysis", font=("Helvetica", 20)).pack(pady=10)

    display_frame = ttkb.Frame(app.root)
    display_frame.pack(pady=10)

    # Display Payload Text
    payload_frame = ttkb.Frame(display_frame)
    payload_frame.grid(row=0, column=0, padx=10)
    ttkb.Label(payload_frame, text="Payload (Text):", font=("Helvetica", 14)).pack()
    display_payload_text(payload_path, payload_frame)

    # Display Cover and Stego Images
    images_frame = ttkb.Frame(display_frame)
    images_frame.grid(row=0, column=1, padx=10)
    ttkb.Label(images_frame, text="Cover and Stego Images:", font=("Helvetica", 14)).pack()
    display_images(app, cover_path, stego_path, images_frame)

    # Display Difference Image
    diff_frame = ttkb.Frame(display_frame)
    diff_frame.grid(row=0, column=2, padx=10)
    ttkb.Label(diff_frame, text="Difference Image:", font=("Helvetica", 14)).pack()
    display_difference_image(app, cover_path, stego_path, diff_frame)

def display_payload_text(payload_path, parent_frame):
    with open(payload_path, 'r', encoding='utf-8', errors='replace') as file:
        payload_text = file.read()
    text_widget = ttkb.Text(parent_frame, wrap='word', width=40, height=20)
    text_widget.insert('1.0', payload_text)
    text_widget.config(state='disabled')  # Make the text read-only
    text_widget.pack(pady=10)

def display_images(app, cover_path, stego_path, parent_frame):
    """ Display the cover and stego images side by side. """
    try:
        cover_image = Image.open(cover_path).resize((400, 400), Image.LANCZOS)
        stego_image = Image.open(stego_path).resize((400, 400), Image.LANCZOS)
    except Exception as e:
        messagebox.showerror("Image Loading Error", f"Failed to load images:\n{str(e)}")
        return

    cover_photo = ImageTk.PhotoImage(cover_image)
    stego_photo = ImageTk.PhotoImage(stego_image)

    cover_label = ttkb.Label(parent_frame, image=cover_photo)
    cover_label.pack(side='left', padx=5)

    stego_label = ttkb.Label(parent_frame, image=stego_photo)
    stego_label.pack(side='left', padx=5)

    app.image_refs.append(cover_photo)
    app.image_refs.append(stego_photo)

def display_difference_image(app, cover_path, stego_path, parent_frame):
    """ Display a difference image to highlight changes between the cover and stego images. """
    try:
        cover_image = Image.open(cover_path).convert('RGB')
        stego_image = Image.open(stego_path).convert('RGB')
    except Exception as e:
        messagebox.showerror("Image Loading Error", f"Failed to load images:\n{str(e)}")
        return

        # Create a difference image to show the modified pixels
    width, height = cover_image.size
    diff_image = Image.new('RGB', (width, height))

    for x in range(width):
        for y in range(height):
            cover_pixel = cover_image.getpixel((x, y))
            stego_pixel = stego_image.getpixel((x, y))
            diff_pixel = tuple(
                min(abs(c - s) * 10, 255) for c, s in zip(cover_pixel, stego_pixel))  # Amplify difference
            diff_image.putpixel((x, y), diff_pixel)

    diff_image = diff_image.resize((400, 400), Image.LANCZOS)
    diff_photo = ImageTk.PhotoImage(diff_image)
    diff_label = ttkb.Label(parent_frame, image=diff_photo)
    diff_label.pack(pady=10)

    app.image_refs.append(diff_photo)

def display_decoded_message(app, decoded_data):
        """ Display the decoded payload in a new window. """
        # Clear the window to remove existing widgets
        for widget in app.root.winfo_children():
            widget.destroy()

        # Create a Back Button to navigate back to the main menu
        ttkb.Button(app.root, text="Back to Main Menu", command=app.create_landing_page, bootstyle="danger").pack(anchor='nw', padx=10, pady=10)

        # Title Label for the Decoded Payload
        ttkb.Label(app.root, text="Decoded Payload", font=("Helvetica", 20)).pack(pady=10)

        # Create a Text Widget to display the decoded message
        text_widget = ttkb.Text(app.root, wrap='word', width=80, height=25)
        text_widget.insert('1.0', decoded_data)  # Insert the decoded data into the text widget
        text_widget.config(state='disabled')  # Make the text read-only
        text_widget.pack(pady=10)
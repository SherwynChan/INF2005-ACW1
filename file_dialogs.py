from tkinter import filedialog

def select_payload(var):
    file_path = filedialog.askopenfilename(
        title="Select Payload (Text File)",
        filetypes=[("Text Files", "*.txt")]
        )
    
    if file_path:
        var.set(file_path)

def select_cover(var, file_type_var):
    file_path = filedialog.askopenfilename(
        title="Select Cover Object (Image File)",
        filetypes=[
            ("All Image Files", "*.bmp;*.png;*.gif;*.jpeg;*.jpg"),
            ("BMP Files", "*.bmp"),
            ("PNG Files", "*.png"),
            ("GIF Files", "*.gif"),
            ("JPEG Files", "*.jpeg;*.JPEG"),
            ("JPG Files", "*.jpg;*.JPG")
        ]
    )
    if file_path:
        var.set(file_path)
        file_type_var.set('image')

def select_stego(var):
    file_path = filedialog.askopenfilename(
        title="Select Stego Object (Image File)",
        filetypes=[
            ("Image Files", "*.png") # unable to add on other image types using "";*.jpeg" etc...
        ]
    )
    if file_path:
        var.set(file_path)

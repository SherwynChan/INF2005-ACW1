import ttkbootstrap as ttkb
from steganography_app import SteganographyApp

# Create the main window
root = ttkb.Window(themename="flatly")  # Create the main window with 'flatly' theme
app = SteganographyApp(root)  # Create an instance of SteganographyApp
root.mainloop()  # Start the Tkinter event loop

import numpy as np
import cv2

# Function to convert any type of data to binary
def to_bin(data):
    if type(data) == str:
        return ''.join([format(ord(i), '08b') for i in data])
    elif type(data) == bytes or type(data) == np.ndarray:
        return [format(i, '08b') for i in data]
    elif type(data) == int or type(data) == np.uint8:
        return format(data, '08b')
    else:
        raise TypeError("Type not supported.")
    
# Function to hide secret data into an image (encoding)
def encode(image_name, secret_data):
    image = cv2.imread(image_name)
    n_bytes = image.shape[0] * image.shape[1] * 3 // 8
    print("[*] Maximum bytes to encode:", n_bytes)
    
    # Append the delimiter to the secret data
    secret_data += "#####"
    
    # Ensure the image has enough capacity to hold the secret data
    if len(secret_data) > n_bytes * 6:  # Each pixel's channel can store 6 bits
        raise ValueError("[*] Insufficient bytes, need bigger image or less data.")
    
    print("[*] Encoding data...")

    data_index = 0
    binary_secret_data = to_bin(secret_data)
    print(binary_secret_data)
    data_len = len(binary_secret_data)

    for row in image:
        for pixel in row:
            # Convert the R, G, B channels to binary
            r, g, b = to_bin(pixel)
            # Modify the red channel if there's still data to encode
            if data_index < data_len:
                pixel[0] = int(r[:-6] + binary_secret_data[data_index:data_index + 6], 2)
                data_index += 6
            
            # Modify the green channel if there's still data to encode
            if data_index < data_len:
                pixel[1] = int(g[:-6] + binary_secret_data[data_index:data_index + 6], 2)
                data_index += 6
            
            # Modify the blue channel if there's still data to encode
            if data_index < data_len:
                pixel[2] = int(b[:-6] + binary_secret_data[data_index:data_index + 6], 2)
                data_index += 6
            
            # Break if all data has been encoded
            if data_index >= data_len:
                break
        
        if data_index >= data_len:
            break

    return image




# Function to decode the data encoded into the image (decoding)
def decode(image_name):
    print("[*] Decoding data...")
    image = cv2.imread(image_name)
    binary_data = ""
    all_bytes = []
    stop_flag = False  # Flag to stop when delimiter is found

    # Extract the least significant 6 bits from each channel
    for row in image:
        if stop_flag:  # Stop processing if delimiter is found
            break
        for pixel in row:
            r, g, b = to_bin(pixel)
            binary_data += r[-6:]  # Extract the last 6 bits of the red channel
            binary_data += g[-6:]  # Extract the last 6 bits of the green channel
            binary_data += b[-6:]  # Extract the last 6 bits of the blue channel

            # Check if the delimiter is in the binary data
            if "0010001100100011001000110010001100100011" in binary_data[-40:]:
                stop_flag = True
                break

    # Convert the binary data into characters (process only up to the delimiter)
    all_bytes = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]  # Split into 8-bit chunks

    decoded_data = ""
    for byte in all_bytes:
        value = int(byte, 2)
        decoded_data += chr(value)

    # Return the decoded data (excluding the delimiter)
    return decoded_data







# Test the encoding process
text_file_path = "test/text.txt"
cover_image_path = "test/img.png"
output_image_path = "test/encoded_image.png"

with open(text_file_path, 'r', encoding='utf-8', errors='replace') as file:
    secret_message = file.read()

encoded_image = encode(cover_image_path, secret_message)
cv2.imwrite(output_image_path, encoded_image)
print(f"[*] Encoded image saved as {output_image_path}")

decoded_message = decode(output_image_path)
print(f"[*] Decoded message: {decoded_message}")






'''
How Steganography Works:

1) Choosing a cover: image, audio, video

2) Choosing a payload: text, image, audio, video
- convert payload to binary

3) Modify the payload in the cover
- The least significant bits (LSBs) of the cover image are modified to encode the binary form of the secret message. 
Images are typically represented in pixels, with each pixel having values for red, green, and blue channels (RGB).

In LSB steganography, the last bit of each color channel in each pixel is replaced with a bit from the secret message's binary data.

4) Encoding example:
- 
'''
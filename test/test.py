import numpy as np
import cv2

# funtion to convert any type of data to binary
def to_bin(data):
    if isinstance(data, str):
        return ''.join([format(ord(i), '08b') for i in data])
    elif isinstance(data, bytes) or isinstance(data, np.ndarray):
        return [format(i, '08b') for i in data]
    elif isinstance(data, int) or isinstance(data, np.uint8):
        return format(data, '08b')
    else:
        raise TypeError("Type not supported.")
    

# function to hide secret data into image (encoding)
def encode(image_name, secret_data):
    # read the image
    image = cv2.imread(image_name)

    # maximum bytes to encode
    n_bytes = image.shape[0] * image.shape[1] * 3 * 6 // 8
    print("[*] Maximum bytes to encode:", n_bytes)
    secret_data += "=====" # add stopping condition
    if len(secret_data) > n_bytes:
        raise ValueError("Error encountered: Insufficient bytes, need bigger image or less data.")
    print("[*] Encoding data...")

    # convert data to binary
    data_index = 0
    binary_secret_data = to_bin(secret_data)

    # size of data to be encoded/hide
    data_len = len(binary_secret_data)

    for row in image:
        for pixel in row:
            # convert RGB values to binary
            r, g, b = to_bin(pixel)
            if data_index < data_len: # modify the LSB only if there is still data to store
                # update red value
                pixel[0] = int(binary_secret_data[data_index:data_index + 2] + r[2:], 2)  # Replace MSBs of red channel
                data_index += 2
            if data_index < data_len:
                # update green value
                pixel[1] = int(binary_secret_data[data_index:data_index + 2] + g[2:], 2)  # Replace MSBs of green channel
                data_index += 2
            if data_index < data_len:
                # update blue value
                pixel[2] = int(binary_secret_data[data_index:data_index + 2] + b[2:], 2)  # Replace MSBs of blue channel
                data_index += 2
            if data_index >= data_len: # stop the loop if all the data is encoded
                break

    return image


# function to extract secret data from image (decoding)
def decode(image_name):
    print("[*] Decoding...")

    # read the image
    image = cv2.imread(image_name)

    binary_data = ""
    stop_flag = False  # Flag to stop decoding once delimiter is found
    for row in image:
        for pixel in row:
            r, g, b = to_bin(pixel)
            binary_data += r[-6:]  # extract least significant bit from red channel
            binary_data += g[-6:]  # extract least significant bit from green channel
            binary_data += b[-6:]  # extract least significant bit from blue channel

            # Check after every 8 bits (1 byte) if we have reached the delimiter
            if len(binary_data) % 8 == 0:
                all_bytes = [binary_data[i: i+8] for i in range(0, len(binary_data), 8)]
                decoded_data = ""
                for byte in all_bytes:
                    decoded_data += chr(int(byte, 2))  # convert binary back to text
                    if decoded_data[-5:] == "=====":  # check for delimiter
                        stop_flag = True
                        break
            if stop_flag:
                break
        if stop_flag:
            break
    
    return decoded_data[:-5]  # return the secret message without the delimiter






# Test the encoding process
secret_message = "This is a secret message"
cover_image_path = "test/building.png"  # Path to your cover image
output_image_path = "test/encoded_image.png"  # Path to save the encoded image

# Encode the secret message into the image
encoded_image = encode(cover_image_path, secret_message)

# Save the encoded image
cv2.imwrite(output_image_path, encoded_image)
print(f"[*] Encoded image saved as {output_image_path}")

# Test the decoding process
decoded_message = decode(output_image_path)
print(f"[*] Decoded message: {decoded_message}")
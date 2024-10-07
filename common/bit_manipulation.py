import numpy as np

def embed_payload_into_bytes(cover_bytes, payload_bits, num_lsbs):
    """Embed payload bits into the least significant bits of cover bytes."""
    bit_index = 0

    # Calculate the maximum number of bits that can be embedded
    max_capacity = len(cover_bytes) * num_lsbs
    if len(payload_bits) > max_capacity:
        raise ValueError("Payload is too large to fit in the cover object with the given number of LSBs.")
    
    for i in range(len(cover_bytes)):
        if bit_index < len(payload_bits):
            # Calculate the mask to preserve higher bits and clear lower num_lsbs bits
            mask = 255 ^ ((1 << num_lsbs) - 1)

            # Embed the payload bits into the LSBs of the cover byte
            cover_bytes[i] = (cover_bytes[i] & mask) | int(payload_bits[bit_index:bit_index + num_lsbs], 2)
            bit_index += num_lsbs
        if bit_index >= len(payload_bits):
            break

    return cover_bytes

def extract_payload_from_bytes(stego_bytes, num_lsbs, delimiter='1111111111111110'):
    """Extract the payload from the least significant bits of stego bytes."""
    bits = ''

    for byte in stego_bytes:
        extracted_bits = format(byte, '08b')[-num_lsbs:]
        bits += extracted_bits  # Extract LSBs

    print(f"Total Length of Extracted Bits: {len(bits)}")

    # Find the position of the delimiter
    delimiter_index = bits.find(delimiter)
    if delimiter_index == -1:
        raise ValueError("Delimiter not found in the extracted bits.")
    
    print(f"Delimiter found at bit index: {delimiter_index}")
    
    payload_bits = bits[:delimiter_index]  # Extract the bits before the delimiter

    try:
        payload_bytes = int(payload_bits, 2).to_bytes((len(payload_bits) + 7) // 8, byteorder='big')
        # Decode bytes to a string (use 'ignore' or 'replace' to handle weird characters)
        return payload_bytes.decode('utf-8', errors='replace')
    except ValueError as e:
        print(f"Error during conversion: {e}")
        return None
    
def extract_video_payload_from_bytes_old(stego_bytes, num_lsbs, delimiter='1111111111111110'):
    """
    Extract the payload from the stego bytes using the specified number of LSBs.
    """
    
    print("now in extract_video_payload_from_bytes")
    
    # Extract the least significant bits from each byte
    extracted_bits = []
    
    print(f"Total: {len(stego_bytes)}")
    
    for byte in stego_bytes:
        
        for i in range(num_lsbs):
            extracted_bits.append((byte >> i) & 1)
    
    print("now in extract_video_payload_from_bytes: done for loop")
    
    # Convert the list of bits to a string
    bit_string = ''.join(map(str, extracted_bits))
    
    # Use the delimiter to find the end of the payload
    delimiter_index = bit_string.find(delimiter)
    if delimiter_index != -1:
        payload_bits = bit_string[:delimiter_index]
    else:
        payload_bits = bit_string  # If delimiter not found, use all bits
        
    print("now in extract_video_payload_from_bytes: found end of payload")
    
    # Convert bit string to bytes
    payload_bytes = int(payload_bits, 2).to_bytes((len(payload_bits) + 7) // 8, byteorder='big')
    
    print("now in extract_video_payload_from_bytes: done with bit string to bytes")
    
    return payload_bytes

def extract_video_payload_from_bytes(stego_bytes, num_lsbs, delimiter='1111111111111110'):
    """
    Extract the payload from the stego bytes using the specified number of LSBs.

    Parameters:
        stego_bytes (bytes or np.ndarray): Flattened NumPy array or bytes of stego data.
        num_lsbs (int): Number of least significant bits used during embedding.
        delimiter (str): Bit string that signifies the end of the payload.

    Returns:
        payload_bytes (bytes): Extracted payload data.
    """
    # Ensure stego_bytes is a NumPy array for consistent processing
    if isinstance(stego_bytes, bytes):
        stego_bytes = np.frombuffer(stego_bytes, dtype=np.uint8)
    elif not isinstance(stego_bytes, np.ndarray):
        stego_bytes = np.array(stego_bytes, dtype=np.uint8)

    # Extract the least significant bits from each byte
    extracted_bits = []
    for byte in stego_bytes:
        for i in range(num_lsbs):
            extracted_bits.append((byte >> i) & 1)

    # Convert the list of bits to a string
    bit_string = ''.join(map(str, extracted_bits))

    # Use the delimiter to find the end of the payload
    delimiter_index = bit_string.find(delimiter)
    if delimiter_index != -1:
        payload_bits = bit_string[:delimiter_index]
    else:
        payload_bits = bit_string  # If delimiter not found, use all bits

    # Ensure that the number of payload bits is divisible by 8
    # Remove any incomplete byte at the end
    num_full_bytes = len(payload_bits) // 8
    payload_bits = payload_bits[:num_full_bytes * 8]

    # Reconstruct bytes from bits
    payload_bytes = bytearray()
    for i in range(0, len(payload_bits), 8):
        byte_bits = payload_bits[i:i+8]
        byte = int(byte_bits, 2)  # No reversal
        payload_bytes.append(byte)

    return bytes(payload_bytes)

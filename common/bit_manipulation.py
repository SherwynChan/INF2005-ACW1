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

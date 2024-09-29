def embed_payload_into_bytes(cover_bytes, payload_bits, num_lsbs):
    """Embed payload bits into the least significant bits of cover bytes."""
    bit_index = 0
    for i in range(len(cover_bytes)):
        if bit_index < len(payload_bits):
            # Embed the payload bits into the LSBs of the cover byte
            cover_bytes[i] = (cover_bytes[i] & (255 << num_lsbs)) | int(payload_bits[bit_index:bit_index + num_lsbs], 2)
            bit_index += num_lsbs
        if bit_index >= len(payload_bits):
            break
    return cover_bytes

def extract_payload_from_bytes(stego_bytes, num_lsbs, delimiter='1111111111111110'):
    """Extract the payload from the least significant bits of stego bytes."""
    bits = ''
    # Create an adjusted delimiter to match the number of LSBs used during encoding
    adjusted_delimiter = (delimiter * (num_lsbs // len(delimiter) + 1))[:num_lsbs]
    for byte in stego_bytes:
        bits += format(byte, '08b')[-num_lsbs:]  # Extract LSBs
        if bits.endswith(adjusted_delimiter):  # End-of-payload delimiter
            bits = bits[:-len(adjusted_delimiter)]  # Remove the delimiter
            break
    payload_bytes = int(bits, 2).to_bytes(len(bits) // 8, byteorder='big')
    return payload_bytes.decode('utf-8', errors='replace')

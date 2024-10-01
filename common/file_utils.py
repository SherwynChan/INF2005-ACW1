def convert_payload_to_bits(payload_path, num_lsbs=1, delimiter='1111111111111110'):
    """Convert the payload file content to a bit string, add delimiter, and pad after delimiter for alignment."""
    with open(payload_path, 'rb') as f:
        payload_data = f.read()

    # Check if the payload data is empty
    if not payload_data:
        raise ValueError("The payload file is empty.")

    # Convert payload data to bits
    payload_bits = ''.join([format(byte, '08b') for byte in payload_data])
    print(f"Length of Payload Bits: {len(payload_bits)}")

    # Append the delimiter after converting the payload to bits
    payload_bits += delimiter
    print(f"Length of Delimiter: {len(delimiter)}")

    # Add padding after the delimiter to ensure total length is divisible by num_lsbs
    remainder_after_delimiter = len(payload_bits) % num_lsbs
    additional_padding_after_delimiter = 0
    if remainder_after_delimiter != 0:
        additional_padding_after_delimiter = num_lsbs - remainder_after_delimiter
        payload_bits += '0' * additional_padding_after_delimiter  # Add zero padding to align with num_lsbs
        print(f"Additional Padding Added After Delimiter: {additional_padding_after_delimiter} bits")

    # Final total number of bits
    total_bits = len(payload_bits)
    print(f"Total Number of Bits (Payload + Delimiter + Padding): {total_bits}")

    # Return payload bits and total bit count
    return payload_bits, total_bits

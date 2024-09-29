def convert_payload_to_bits(payload_path, num_lsbs=1, delimiter='1111111111111110'):
    """Convert the payload file content to a bit string with a delimiter."""
    with open(payload_path, 'rb') as f:
        payload_data = f.read()
    # Convert payload data to bits and append the delimiter
    payload_bits = ''.join([format(byte, '08b') for byte in payload_data])

    # Adjust the delimiter length based on the num_lsbs used
    adjusted_delimiter = (delimiter * (num_lsbs // len(delimiter) + 1))[:num_lsbs]
    return payload_bits + adjusted_delimiter

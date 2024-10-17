import streamlit as st
import brotli
import gzip
import lz4.frame
import zlib
import random
import math
from PIL import Image
import io
from collections import Counter

# Compression functions
def compress_with_brotli(data: bytes) -> bytes:
    return brotli.compress(data)

def compress_with_gzip(data: bytes) -> bytes:
    return gzip.compress(data)

def compress_with_lz4(data: bytes) -> bytes:
    return lz4.frame.compress(data)

def compress_with_deflate(data: bytes) -> bytes:
    return zlib.compress(data)

def compress_image_lossless(image_path: bytes) -> bytes:
    """Compress an image using lossless JPEG compression."""
    with Image.open(io.BytesIO(image_path)) as img:
        if img.mode != 'RGB':
            img = img.convert('RGB')
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=100, optimize=True)
        return buffer.getvalue()

# Read file bytes
def read_file(file) -> bytes:
    return file.read()

# Entropy calculation
def calculate_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    byte_counts = Counter(data)
    total_bytes = len(data)
    entropy = 0.0
    for count in byte_counts.values():
        p_i = count / total_bytes
        entropy -= p_i * math.log2(p_i)
    return entropy

# Random payload generation
def generate_random_payload_with_entropy(size: int, target_entropy: float) -> bytes:
    if target_entropy < 0 or target_entropy > 8:
        raise ValueError("Entropy must be between 0 and 8 bits per byte.")
    if target_entropy == 0:
        return bytes([random.randint(0, 255)] * size)
    if target_entropy == 8:
        return bytes(random.getrandbits(8) for _ in range(size))
    num_symbols = int(2 ** target_entropy)
    symbols = list(range(num_symbols))
    byte_values = random.choices(symbols, k=size)
    return bytes(byte_values)

# Display transmission information
def simulate_transmission(payload: bytes, compressed_payload: bytes):
    original_size = len(payload)
    compressed_size = len(compressed_payload)
    st.write(f"Original size: {original_size} bytes")
    st.write(f"Compressed size: {compressed_size} bytes")
    if compressed_size < original_size:
        reduction = ((original_size - compressed_size) / original_size) * 100
        st.write(f"Compression reduced the size by {reduction:.2f}%")
    else:
        st.write("Compression did not reduce the size.")

# Streamlit App
def main():
    st.title("Payload Compression Simulation")

    # Payload Type selection
    payload_type = st.radio("Select Payload Type", ['String', 'File', 'Image', 'Random'])

    payload = None
    if payload_type == "String":
        payload_input = st.text_area("Enter the string to compress")
        if payload_input:
            payload = payload_input.encode('utf-8')

    elif payload_type == "File":
        file = st.file_uploader("Upload a file", type=None)
        if file:
            payload = read_file(file)

    elif payload_type == "Image":
        # Supported raw image formats
        image_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg", "dng", "raw", "nef", "cr2", "arw"])

        if image_file:
            payload = read_file(image_file)

            compressed_payload = compress_image_lossless(payload)
            st.write("Lossless compression applied to image.")

            # Simulate transmission and compare sizes
            simulate_transmission(payload, compressed_payload)
            return

    elif payload_type == "Random":
        size = st.slider("Select the size of the random payload (in bytes)", 1, 100000, 1024)
        entropy = st.slider("Select the entropy (bits per byte)", 0.0, 8.0, 4.0)
        payload = generate_random_payload_with_entropy(size, entropy)

    # Compression Algorithm selection
    if payload:
        compression_method = st.selectbox("Choose a compression method", ['brotli', 'gzip', 'lz4', 'deflate'])

        # Calculate entropy of original payload
        entropy = calculate_entropy(payload)
        st.write(f"Entropy of the original payload: {entropy:.2f} bits per byte")

        # Perform compression
        if compression_method == "brotli":
            compressed_payload = compress_with_brotli(payload)
        elif compression_method == "gzip":
            compressed_payload = compress_with_gzip(payload)
        elif compression_method == "lz4":
            compressed_payload = compress_with_lz4(payload)
        elif compression_method == "deflate":
            compressed_payload = compress_with_deflate(payload)

        # Simulate transmission
        simulate_transmission(payload, compressed_payload)

if __name__ == "__main__":
    main()

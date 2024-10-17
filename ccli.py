import argparse
import os
import brotli
import gzip
import lz4.frame
import zlib
import random
import math
from PIL import Image
import io
from collections import Counter

def compress_with_brotli(data: bytes) -> bytes:
    """Compress data using Brotli."""
    return brotli.compress(data)

def compress_with_gzip(data: bytes) -> bytes:
    """Compress data using gzip."""
    return gzip.compress(data)

def compress_with_lz4(data: bytes) -> bytes:
    """Compress data using LZ4."""
    return lz4.frame.compress(data)

def compress_with_deflate(data: bytes) -> bytes:
    """Compress data using DEFLATE (zlib)."""
    return zlib.compress(data)

def compress_image_lossless(image_path: str) -> bytes:
    """Compress an image using lossless JPEG compression."""
    with Image.open(image_path) as img:
        # Convert to RGB mode if not already in RGB
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Save to a bytes buffer using lossless JPEG compression
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=100, optimize=True)
        compressed_data = buffer.getvalue()

    return compressed_data

def read_file(file_path: str) -> bytes:
    """Read a file's content as bytes."""
    with open(file_path, 'rb') as f:
        return f.read()

def calculate_entropy(data: bytes) -> float:
    """Calculate the Shannon entropy of the given data."""
    if not data:
        return 0.0

    # Count the frequency of each byte in the data
    byte_counts = Counter(data)
    total_bytes = len(data)

    # Calculate the probability of each byte
    entropy = 0.0
    for count in byte_counts.values():
        p_i = count / total_bytes
        entropy -= p_i * math.log2(p_i)

    return entropy

def generate_random_payload_with_entropy(size: int, target_entropy: float) -> bytes:
    """Generate a random payload of the specified size with the given entropy."""
    if target_entropy < 0 or target_entropy > 8:
        raise ValueError("Entropy must be between 0 and 8 bits per byte.")

    # For entropy close to 0, generate mostly the same byte
    if target_entropy == 0:
        return bytes([random.randint(0, 255)] * size)

    # For entropy close to 8, use a uniform distribution
    if target_entropy == 8:
        return bytes(random.getrandbits(8) for _ in range(size))

    # Otherwise, create a custom distribution to match the desired entropy
    num_symbols = int(2 ** target_entropy)  # Approximate number of unique byte values
    symbols = list(range(num_symbols))

    # Generate the byte values based on a uniform distribution over the symbols
    byte_values = random.choices(symbols, k=size)
    return bytes(byte_values)

def simulate_transmission(payload: bytes, compressed_payload: bytes) -> None:
    """Compare the original and compressed payload sizes."""
    original_size = len(payload)
    compressed_size = len(compressed_payload)

    print(f"Original size: {original_size} bytes")
    print(f"Compressed size: {compressed_size} bytes")

    if compressed_size < original_size:
        reduction = ((original_size - compressed_size) / original_size) * 100
        print(f"Compression reduced the size by {reduction:.2f}%")
    else:
        print("Compression did not reduce the size.")

def main():
    parser = argparse.ArgumentParser(description="Simulate the transmission of a payload with and without compression.")
    parser.add_argument("--type", choices=["string", "file", "image", "random"], required=True,
                        help="The type of the payload: 'string' for text input, 'file' for a file path, 'image' for an image path, 'random' for a randomly generated payload.")
    parser.add_argument("payload", nargs='?', help="The payload to be transmitted. Required for types 'string', 'file', and 'image'.")
    parser.add_argument("--size", type=int, help="Size in bytes for the random payload (only required if type is 'random').")
    parser.add_argument("--entropy", type=float, help="Desired entropy for the random payload, between 0 and 8 bits per byte (only used if type is 'random').")
    parser.add_argument("--compression", choices=["brotli", "gzip", "lz4", "deflate"],
                        help="The compression algorithm to use: 'brotli', 'gzip', 'lz4', or 'deflate'.")

    args = parser.parse_args()

    # Validate the combination of arguments
    if args.type in ["string", "file", "image"] and args.payload is None:
        parser.error(f"The payload argument is required for type '{args.type}'.")
    if args.type == "random" and args.size is None:
        parser.error("The --size argument is required for type 'random'.")
    if args.type == "random" and args.entropy is None:
        parser.error("The --entropy argument is required for type 'random'.")

    # Determine the payload type and read the data
    if args.type == "string":
        payload = args.payload.encode('utf-8')
    elif args.type == "file":
        if not os.path.isfile(args.payload):
            print(f"Error: File {args.payload} does not exist.")
            return
        payload = read_file(args.payload)
    elif args.type == "image":
        if not os.path.isfile(args.payload):
            print(f"Error: Image file {args.payload} does not exist.")
            return
        # Read the image for lossless compression
        compressed_payload = compress_image_lossless(args.payload)
        simulate_transmission(read_file(args.payload), compressed_payload)
        return
    elif args.type == "random":
        payload = generate_random_payload_with_entropy(args.size, args.entropy)

    # Calculate and print the entropy of the payload
    entropy = calculate_entropy(payload)
    print(f"Entropy of the original payload: {entropy:.2f} bits per byte")

    # Choose compression algorithm based on user input
    if args.compression == "brotli":
        compressed_payload = compress_with_brotli(payload)
    elif args.compression == "gzip":
        compressed_payload = compress_with_gzip(payload)
    elif args.compression == "lz4":
        compressed_payload = compress_with_lz4(payload)
    elif args.compression == "deflate":
        compressed_payload = compress_with_deflate(payload)

    # Simulate transmission and compare sizes
    simulate_transmission(payload, compressed_payload)

if __name__ == "__main__":
    main()

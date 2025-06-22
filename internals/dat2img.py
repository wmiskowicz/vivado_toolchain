import argparse
import numpy as np
from PIL import Image

def data_to_image(input_file, output_file, width, height):
    try:
        with open(input_file, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found")
        return
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    # Validate expected size
    expected_pixels = width * height
    if len(lines) != expected_pixels:
        print(f"Warning: File contains {len(lines)} pixels but expected {expected_pixels} for {width}x{height} image")

    # Create empty arrays for each channel
    r = np.zeros((height, width), dtype=np.uint8)
    g = np.zeros((height, width), dtype=np.uint8)
    b = np.zeros((height, width), dtype=np.uint8)

    pixel_index = 0
    for y in range(height):
        for x in range(width):
            if pixel_index >= len(lines):
                # Pad with black if we run out of pixels
                r[y, x] = 0
                g[y, x] = 0
                b[y, x] = 0
                continue

            line = lines[pixel_index].strip()
            pixel_index += 1

            # Handle malformed lines
            if len(line) != 3:
                print(f"Warning: Invalid pixel format at line {pixel_index}: '{line}'")
                r[y, x] = 0
                g[y, x] = 0
                b[y, x] = 0
                continue

            try:
                # Convert 4-bit hex to 8-bit (0-255)
                r_val = int(line[0], 16) * 17  # 17 = 255/15
                g_val = int(line[1], 16) * 17
                b_val = int(line[2], 16) * 17

                r[y, x] = r_val
                g[y, x] = g_val
                b[y, x] = b_val
            except ValueError:
                print(f"Warning: Invalid hex value at line {pixel_index}: '{line}'")
                r[y, x] = 0
                g[y, x] = 0
                b[y, x] = 0

    # Combine channels and create image
    rgb_array = np.stack([r, g, b], axis=2)
    image = Image.fromarray(rgb_array, 'RGB')
    
    try:
        image.save(output_file, 'PNG')
        print(f"Successfully created {output_file} ({width}x{height})")
    except Exception as e:
        print(f"Error saving image: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert 12-bit RGB data file to PNG')
    parser.add_argument('input_file', help='Input .data file')
    parser.add_argument('-wd', '--width', type=int, required=True, help='Image width')
    parser.add_argument('-hi', '--height', type=int, required=True, help='Image height')
    
    args = parser.parse_args()
    data_to_image(args.input_file, f"{args.input_file[:-5]}_reconverted.png", args.width, args.height)
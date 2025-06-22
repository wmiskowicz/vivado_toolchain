import sys
import re
import argparse
from PIL import Image
from numpy import asarray

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Convert image to 12-bit RGB data file')
    parser.add_argument('image_file', help='Input image file')
    parser.add_argument('-wd', '--width', type=int, help='Output width (default: original size)')
    parser.add_argument('-hi', '--height', type=int, help='Output height (default: original size)')
    parser.add_argument('-p', '--pad', action='store_true', help='Pad to maintain aspect ratio')
    args = parser.parse_args()

    # Open image
    try:
        image = Image.open(args.image_file)
    except FileNotFoundError:
        print(f"Error: File '{args.image_file}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error opening image: {e}")
        sys.exit(1)

    # Get original dimensions
    orig_width, orig_height = image.size

    # Set target dimensions
    target_width = args.width if args.width else orig_width
    target_height = args.height if args.height else orig_height

    # Resize with aspect ratio preservation if requested
    if args.pad and (args.width or args.height):
        # Calculate the aspect ratio-preserving dimensions
        ratio = min(target_width/orig_width, target_height/orig_height)
        new_width = int(orig_width * ratio)
        new_height = int(orig_height * ratio)
        
        # Resize first
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Then pad to target dimensions
        new_image = Image.new("RGB", (target_width, target_height), (0, 0, 0))
        new_image.paste(image, ((target_width - new_width) // 2, 
                              (target_height - new_height) // 2))
        image = new_image
    elif args.width or args.height:
        # Simple resize without aspect ratio preservation
        image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)

    # Convert image to array
    array = asarray(image)

    # Check if the image is RGB or grayscale
    is_rgb = len(array.shape) > 2

    if is_rgb:
        r = array[:, :, 0]
        g = array[:, :, 1]
        b = array[:, :, 2]
    else:
        r = array
        g = array
        b = array

    # Prepare output file
    output_file_name = re.sub(r'\.[^.]*$', '.data', args.image_file)
    
    try:
        with open(output_file_name, 'w') as output_file:
            # For each pixel, convert 8-bit channels (0-255) to 4-bit (0-15)
            for h in range(target_height):
                for w in range(target_width):
                    # Handle cases where we might be out of bounds (shouldn't happen but just in case)
                    if h >= r.shape[0] or w >= r.shape[1]:
                        red_4bit = green_4bit = blue_4bit = 0
                    else:
                        # Scale 8-bit to 4-bit by right-shifting by 4
                        red_4bit = r[h, w] >> 4
                        green_4bit = g[h, w] >> 4
                        blue_4bit = b[h, w] >> 4
                    
                    # Format each 4-bit value as a single hex digit and combine
                    pixel = f"{red_4bit:01X}{green_4bit:01X}{blue_4bit:01X}"
                    output_file.write(pixel + "\n")
        
        print(f"Successfully converted to {output_file_name} ({target_width}x{target_height})")
    except IOError as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
    # image2 = Image.fromarray(r)
    # image2.show()

    # print(data)
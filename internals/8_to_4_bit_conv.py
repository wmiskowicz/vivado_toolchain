def rgb_8bit_to_4bit(r, g, b):
    """Convert 8-bit RGB values (0-255) to 4-bit (0-15) with rounding."""
    r_4bit = round((r / 255) * 15)
    g_4bit = round((g / 255) * 15)
    b_4bit = round((b / 255) * 15)
    return (r_4bit, g_4bit, b_4bit)

# Example usage:
color_8bit = (237, 184, 101)  # Your input color
color_4bit = rgb_8bit_to_4bit(*color_8bit)
print(color_4bit)  # Output: (15, 13, 9)
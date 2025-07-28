from PIL import Image, ImageDraw, ImageFont
import os

# Create a 32x32 favicon
size = 32
image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(image)

# Draw blue circle background
draw.ellipse([1, 1, size-1, size-1], fill='#2563eb', outline='#1d4ed8', width=2)

# Try to draw text "ED" in white
try:
    # Try to use a system font
    font = ImageFont.truetype("arial.ttf", 14)
except:
    try:
        font = ImageFont.truetype("Arial.ttf", 14)
    except:
        font = ImageFont.load_default()

# Draw "ED" text
draw.text((5, 8), "ED", fill='white', font=font)

# Draw small chart bars in gold
draw.rectangle([22, 8, 24, 16], fill='#fbbf24')
draw.rectangle([25, 12, 27, 16], fill='#fbbf24') 
draw.rectangle([28, 10, 30, 16], fill='#fbbf24')

# Save as PNG and ICO
image.save('favicon.png')
image.save('favicon.ico', format='ICO', sizes=[(16,16), (32,32)])
print("Favicon PNG and ICO created successfully!")

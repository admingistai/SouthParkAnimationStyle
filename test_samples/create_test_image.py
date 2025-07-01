from PIL import Image, ImageDraw

# Create a simple test character image
width, height = 400, 600
img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
draw = ImageDraw.Draw(img)

# Draw head (top part - will flap)
head_top = [(150, 100), (250, 100), (250, 200), (150, 200)]
draw.polygon(head_top, fill=(255, 200, 150), outline=(0, 0, 0))

# Draw eyes
draw.ellipse([170, 130, 190, 150], fill=(255, 255, 255), outline=(0, 0, 0))
draw.ellipse([210, 130, 230, 150], fill=(255, 255, 255), outline=(0, 0, 0))
draw.ellipse([175, 135, 185, 145], fill=(0, 0, 0))
draw.ellipse([215, 135, 225, 145], fill=(0, 0, 0))

# Draw head bottom (jaw - stays static)
head_bottom = [(150, 200), (250, 200), (250, 250), (150, 250)]
draw.polygon(head_bottom, fill=(255, 200, 150), outline=(0, 0, 0))

# Draw simple mouth
draw.arc([180, 210, 220, 230], 0, 180, fill=(0, 0, 0), width=3)

# Draw body
body = [(100, 250), (300, 250), (300, 500), (100, 500)]
draw.polygon(body, fill=(200, 50, 50), outline=(0, 0, 0))

# Save
img.save('test_character.png')
print("Created test_character.png")
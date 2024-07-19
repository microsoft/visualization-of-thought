from PIL import Image, ImageFont
import pilmoji
import os


emoji_size = 109
spacing = int(emoji_size / 5)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
font = ImageFont.truetype(os.path.join(SCRIPT_DIR, 'NotoColorEmoji.ttf'), size=emoji_size)


def emoji_to_image(emoji_grid:list[list[str]], img_path:str):
    if os.path.exists(img_path):
        return
    img_folder = os.path.dirname(img_path)
    os.makedirs(img_folder, exist_ok=True)
    # Create a new image with white background
    row_num = len(emoji_grid)
    col_num = len(emoji_grid[0])
    img_size = ((emoji_size + spacing) * col_num + spacing, (emoji_size + spacing) * row_num + spacing)  # width, height
    img = Image.new('RGB', img_size, color='black')

    # Draw the emojis onto the image
    draw = pilmoji.Pilmoji(img)
    # Draw each emoji in the grid
    for row_index, row in enumerate(emoji_grid):
        for col_index, emoji in enumerate(row):
            position = (col_index * (emoji_size + spacing) + spacing, row_index * (emoji_size + spacing) + spacing)
            #draw.text(position, emoji, fill="black", spacing=0, font_size=emoji_size[0])
            draw.text(position, emoji, font=font)
    img = img.resize((int(img_size[0] / 3), int(img_size[1] / 3)))
    # Save or display the image
    img.save(img_path)
    return img_path

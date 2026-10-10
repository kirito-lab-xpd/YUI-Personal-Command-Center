
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip
import os


def create_short():

    width = 1080
    height = 1920

    # Create a dark purple background
    image = Image.new(
        "RGB",
        (width, height),
        (15, 10, 30)
    )

    draw = ImageDraw.Draw(image)

    # Motivational message
    message = "DISCIPLINE\nBUILDS THE\nFUTURE"

    # Load bold font
    try:
        font = ImageFont.truetype(
            "C:/Windows/Fonts/arialbd.ttf",
            80
        )
    except:
        font = ImageFont.load_default()

    # Calculate text size
    box = draw.multiline_textbbox(
        (0, 0),
        message,
        font=font,
        spacing=20,
        align="center"
    )

    text_width = box[2] - box[0]
    text_height = box[3] - box[1]

    # Center the text
    x = (width - text_width) // 2
    y = (height - text_height) // 2

    # Draw centered text
    draw.multiline_text(
        (x, y),
        message,
        font=font,
        fill=(255, 255, 255),
        spacing=20,
        align="center"
    )

    # Save background image
    image_path = "short_background.png"
    image.save(image_path)

    print("YUI: Background created.")

    # Create 5-second video
    clip = ImageClip(image_path).with_duration(5)

    output_path = "first_yui_short.mp4"

    print("YUI: Creating video...")

    clip.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio=False
    )

    clip.close()

    print("\nYUI: Short created successfully!")
    print(f"Saved to: {os.path.abspath(output_path)}")


if __name__ == "__main__":
    create_short()
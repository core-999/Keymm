import logging
import os
import base64
from PIL import Image, ImageDraw, ImageFont, ImageFilter

logging.basicConfig(level=logging.INFO)


def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight), Image.Resampling.LANCZOS)
    return newImage


async def gen_thumb(videoid: str):
    try:
        cache_path = f"cache/{videoid}_v4.png"
        if os.path.isfile(cache_path):
            return cache_path

        os.makedirs("cache", exist_ok=True)

        
                
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "../assets/coremusic.jpg")


        if not os.path.exists(image_path):
            logging.error(f"ဖိုင်ကို ရှာမတွေ့ပါ။ လမ်းကြောင်းမှန်ကန်မှု ရှိမရှိ စစ်ဆေးပါ။: {image_path}")
            return None

        custom_img = Image.open(image_path).convert("RGB")

    
        bg_img = changeImageSize(1280, 720, custom_img)
        background = bg_img.filter(ImageFilter.GaussianBlur(15))
        darken = Image.new("RGBA", (1280, 720), (10, 10, 15, 100))
        background = Image.alpha_composite(
            background.convert("RGBA"), darken
        ).convert("RGB")

        
        target_w, target_h = 1280, 720
        foreground = changeImageSize(target_w, target_h, custom_img)
        background.paste(foreground, (0, 0))

        # Credit စာသားအပိုင်း
        font_credit = None
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "arialbd.ttf",
            "arial.ttf",
        ]

        for fpath in font_paths:
            try:
                font_credit = ImageFont.truetype(fpath, 32)
                break
            except Exception:
                continue

        if font_credit is None:
            font_credit = ImageFont.load_default()

        secret_code = "U09VUkNFIC0gQEhBTlRIQVI5OTkgQEhFWF9LSU5HOQ=="
        credit_text = base64.b64decode(secret_code).decode("utf-8")

        dummy_img = Image.new("RGBA", (1, 1))
        dummy_draw = ImageDraw.Draw(dummy_img)
        bbox = dummy_draw.textbbox((0, 0), credit_text, font=font_credit)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        text_img = Image.new("RGBA", (text_w + 10, text_h + 10), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_img)
        text_draw.text(
            (5, 5), credit_text, font=font_credit, fill=(255, 255, 255, 255)
        )

        gradient = Image.new("RGBA", (text_w + 10, text_h + 10), color=0)
        grad_draw = ImageDraw.Draw(gradient)
        for i in range(text_w + 10):
            r = int(255 * (i / (text_w + 10)))
            g = int(100 + 155 * (1 - (i / (text_w + 10))))
            b = 255
            grad_draw.line([(i, 0), (i, text_h + 10)], fill=(r, g, b, 255))

        colored_text = Image.composite(
            gradient, Image.new("RGBA", gradient.size, (0, 0, 0, 0)), text_img
        )

        pos_text_x = (1280 - text_w) // 2
        pos_text_y = 720 - text_h - 40

        shadow_img = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_img)
        shadow_draw.text(
            (pos_text_x + 2, pos_text_y + 2),
            credit_text,
            font=font_credit,
            fill=(0, 0, 0, 255),
        )

        background = Image.alpha_composite(
            background.convert("RGBA"), shadow_img
        )
        background.paste(
            colored_text, (pos_text_x - 5, pos_text_y - 5), colored_text
        )
        background = background.convert("RGB")

        background_path = f"cache/{videoid}_v4.png"
        background.save(background_path, quality=95)

        return background_path

    except Exception as e:
        logging.error(f"Error generating thumbnail for video {videoid}: {e}")
        return None



import logging
import os
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from py_yt import VideosSearch

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

        url = f"https://www.youtube.com/watch?v={videoid}"
        results = VideosSearch(url, limit=1)
        thumbnail = None
        
        search_results = await results.next()
        if search_results and "result" in search_results and len(search_results["result"]) > 0:
            for result in search_results["result"]:
                thumbnail_data = result.get("thumbnails")
                if thumbnail_data:
                    thumbnail = thumbnail_data[0]["url"].split("?")[0]
                    break

        if not thumbnail:
            return None

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    filepath = f"cache/thumb{videoid}.png"
                    async with aiofiles.open(filepath, mode="wb") as f:
                        await f.write(await resp.read())
                    
        image_path = f"cache/thumb{videoid}.png"
        if not os.path.exists(image_path):
            return None
            
        youtube = Image.open(image_path).convert("RGB")
        
        
        bg_img = changeImageSize(1280, 720, youtube)
        background = bg_img.filter(ImageFilter.GaussianBlur(50))
        darken = Image.new("RGBA", (1280, 720), (10, 10, 15, 140))
        background = Image.alpha_composite(background.convert("RGBA"), darken).convert("RGB")

        
        target_w, target_h = 800, 450
        orig_w, orig_h = youtube.size
        
        if orig_w / orig_h > target_w / target_h:
            w_crop = int(orig_h * (target_w / target_h))
            img_cropped = youtube.crop(((orig_w - w_crop) // 2, 0, (orig_w + w_crop) // 2, orig_h))
        else:
            h_crop = int(orig_w * (target_h / target_w))
            img_cropped = youtube.crop((0, (orig_h - h_crop) // 2, orig_w, (orig_h + h_crop) // 2))
            
        foreground = img_cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
        
        border_size = 10
        bordered_img = Image.new("RGB", (target_w + border_size * 2, target_h + border_size * 2), (255, 255, 255))
        bordered_img.paste(foreground, (border_size, border_size))
        
        pos_x = (1280 - bordered_img.size[0]) // 2
        pos_y = (720 - bordered_img.size[1]) // 2 - 20
        background.paste(bordered_img, (pos_x, pos_y))

        
        draw = ImageDraw.Draw(background)
        font_credit = None
        
        
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "arialbd.ttf",
            "arial.ttf"
        ]
        
        for fpath in font_paths:
            try:
                font_credit = ImageFont.truetype(fpath, 32)
                break
            except Exception:
                continue
                
        if font_credit is None:
            font_credit = ImageFont.load_default()

        credit_text = "999_CORES HANTHAR"
        
        
        draw.text((1232, 662), credit_text, font=font_credit, fill=(0, 0, 0))
        draw.text((1230, 660), credit_text, font=font_credit, fill=(255, 255, 255), anchor="rt")

        if os.path.exists(image_path):
            os.remove(image_path)
            
        background_path = f"cache/{videoid}_v4.png"
        background.save(background_path, quality=95)
        
        return background_path

    except Exception as e:
        logging.error(f"Error generating thumbnail for video {videoid}: {e}")
        return None

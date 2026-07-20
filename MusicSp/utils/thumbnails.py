# ATLEAST GIVE CREDITS IF YOU STEALING :(((((((((((((((((((((((((((((((((((((
# ELSE NO FURTHER PUBLIC THUMBNAIL UPDATES

import logging
import os
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(level=logging.INFO)

def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage

async def gen_thumb(videoid: str):
    try:
        if os.path.isfile(f"cache/{videoid}_v4.png"):
            return f"cache/{videoid}_v4.png"

        url = f"https://www.youtube.com/watch?v={videoid}"
        results = VideosSearch(url, limit=1)
        for result in (await results.next())["result"]:
            thumbnail_data = result.get("thumbnails")
            if thumbnail_data:
                thumbnail = thumbnail_data[0]["url"].split("?")[0]
            else:
                thumbnail = None

        if not thumbnail:
            return None

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    filepath = f"cache/thumb{videoid}.png"
                    async with aiofiles.open(filepath, mode="wb") as f:
                        await f.write(await resp.read())
                    
        image_path = f"cache/thumb{videoid}.png"
        youtube = Image.open(image_path)
        
        
        background = changeImageSize(1280, 720, youtube)
        background = background.convert("RGB")
        
        
        # -----------------------------------------------------------------------
        draw = ImageDraw.Draw(background)
        
        
        font_path = "assets/font.ttf" 
        
        try:
            title_font = ImageFont.truetype(font_path, 36)
            name_font = ImageFont.truetype(font_path, 26)
        except IOError:
            title_font = ImageFont.load_default()
            name_font = ImageFont.load_default()

        
        text_x = 750
        title_y = 280
        name_y = 340
        
        
        draw.text((text_x, title_y), "Playing Your Requested Song", font=title_font, fill=(255, 255, 255))
        
        
        your_name = "@HANTHAR999" 
        draw.text((text_x, name_y), f"By: {your_name}", font=name_font, fill=(0, 255, 128)) # အစိမ်းရောင် သို့မဟုတ် လိမ္မော်ရောင်သုံးနိုင်သည်

        # 3. Assets ထဲက Play Icon ကို ထည့်လိုပါက (Icon ဖိုင်ရှိနေလျှင်)
        icon_path = "assets/play_icons.png"
        if os.path.exists(icon_path):
            play_icon = Image.open(icon_path).convert("RGBA")
            play_icon = play_icon.resize((80, 80)) 
            background.paste(play_icon, (text_x, 420), play_icon)

        # -----------------------------------------------------------------------
        
        if os.path.exists(image_path):
            os.remove(image_path)
            
        background_path = f"cache/{videoid}_v4.png"
        background.save(background_path)
        
        return background_path

    except Exception as e:
        logging.error(f"Error generating thumbnail for video {videoid}: {e}")
        return None

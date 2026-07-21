import logging
import os
import aiofiles
import aiohttp
from PIL import Image, ImageFilter, ImageDraw, ImageFont
from py_yt import VideosSearch

logging.basicConfig(level=logging.INFO)

async def gen_thumb(videoid: str):
    try:
        cache_path = f"cache/{videoid}_v4.png"
        if os.path.isfile(cache_path):
            return cache_path

        url = f"https://www.youtube.com/watch?v={videoid}"
        results = VideosSearch(url, limit=1)
        thumbnail = None
        for result in (await results.next())["result"]:
            thumbnail_data = result.get("thumbnails")
            if thumbnail_data:
                thumbnail = thumbnail_data[0]["url"].split("?")[0]

        if not thumbnail:
            return None

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    filepath = f"cache/thumb{videoid}.png"
                    async with aiofiles.open(filepath, mode="wb") as f:
                        await f.write(await resp.read())
                    
        image_path = f"cache/thumb{videoid}.png"
        img = Image.open(image_path).convert("RGB")
        
        # 1. ရုပ်ထွက်ကောင်းမွန်သော 1280x720 နောက်ခံ (Blur & Darken)
        background = img.resize((1280, 720), Image.Resampling.LANCZOS)
        background = background.filter(ImageFilter.GaussianBlur(30)) # Blur ပိုစူးစေရန်
        
        # နောက်ခံကို သိသိသာသာ မှောင်ချပေးခြင်း (စာသားပေါ်လွင်စေရန်)
        darker = Image.new("RGB", background.size, (20, 20, 20))
        background = Image.blend(background, darker, 0.6)

        # 2. ပင်မပုံကို အလယ်တွင် Gradient/Shadow ပုံစံဖြင့် ဇိမ်ခံပေါ်လွင်စေရန် (သို့) 16:9 အလှပဆုံး ပုံစံချခြင်း
        # ဤနေရာတွင် Aspect Ratio မပျက်ဘဲ အလယ်တွင် လှပစွာပေါ်စေရန် သို့မဟုတ် Box အပြည့်တင်ရန်
        img_resized = img.resize((1280, 720), Image.Resampling.LANCZOS)
        background.paste(img_resized, (0, 0))

        # စာသားနှင့် ပုံပေါ်လွင်ရန် Dark Overlay ထပ်ထည့်ခြင်း
        overlay = Image.new("RGBA", background.size, (0, 0, 0, 120)) # အမည်းစက်အလွှာ ပိုထူစေရန်
        background = Image.alpha_composite(background.convert("RGBA"), overlay).convert("RGB")

        # 3. နာမည်နှင့် Watermark ကို ပိုမိုလှပထင်ရှားစွာ ထည့်သွင်းခြင်း
        draw = ImageDraw.Draw(background)
        name_to_draw = "@HANTHAR999" 
        
        # Font အရွယ်အစားကို ပိုကြီးပေးပြီး လှပစေရန်
        font_size = 70
        try:
            font = ImageFont.truetype('assets/font.ttf', font_size)
        except Exception:
            font = ImageFont.load_default()

        # Text Size တိုင်းတာခြင်း
        try:
            bbox = draw.textbbox((0, 0), name_to_draw, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except AttributeError:
            text_width = draw.textlength(name_to_draw, font=font)
            text_height = font_size

        # အောက်ခြေတွင် Banner ပုံစံ (သို့) ညာဘက်အောက်ထောင့်တွင် ရှင်းရှင်းလင်းလင်းပေါ်ရန်
        # ဤနေရာတွင် ညာဘက်အောက်ထောင့်၌ နောက်ခံ Box လေးခံပြီး ရေးပေးပါမည် (ဖတ်လို့ကောင်းစေရန်)
        padding = 20
        box_x2 = 1280 - 40
        box_y2 = 720 - 40
        box_x1 = box_x2 - text_width - (padding * 2)
        box_y1 = box_y2 - text_height - (padding * 2)

        # စာသားနောက်ခံမှာ Semi-transparent Box လေးထည့်ပေးခြင်းဖြင့် လုံးဝသဲသဲကွဲကွဲ မြင်ရစေမည်
        box_layer = Image.new("RGBA", background.size, (0, 0, 0, 0))
        box_draw = ImageDraw.Draw(box_layer)
        box_draw.rounded_rectangle([box_x1, box_y1, box_x2, box_y2], radius=15, fill=(0, 0, 0, 180))
        background = Image.alpha_composite(background.convert("RGBA"), box_layer).convert("RGB")

        # စာသားကို Box ရဲ့ အလယ်တည့်တည့်တွင် ရေးဆွဲခြင်း
        draw = ImageDraw.Draw(background)
        text_x = box_x1 + padding
        text_y = box_y1 + padding - 5
        
        # စာသားအရောင် တောက်တောက်နှင့် ထင်ရှားစေရန်
        draw.text((text_x, text_y), name_to_draw, font=font, fill=(255, 255, 255))
        
        if os.path.exists(image_path):
            os.remove(image_path)
            
        background.save(cache_path, quality=95)
        return cache_path

    except Exception as e:
        logging.error(f"Error generating thumbnail for video {videoid}: {e}")
        return None

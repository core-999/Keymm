import asyncio

# ✅ Fix for uvloop / event loop issue on Heroku (Python 3.10+)
try:
    asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# Optional but recommended if you still use uvloop
try:
    import uvloop
    uvloop.install()
except ImportError:
    pass


# --- Original bot imports ---
from MusicSp.core.bot import DevSp
from MusicSp.core.dir import dirr
from MusicSp.core.git import git
from MusicSp.core.userbot import Userbot
from MusicSp.misc import dbb, heroku

from .logging import LOGGER


# --- Initialization calls ---
dirr()
git()
dbb()
heroku()


# --- Create bot & userbot instances ---
app = DevSp()
userbot = Userbot()


# --- Platform imports ---
from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()

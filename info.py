import os, re
from os import environ
from dotenv import load_dotenv
load_dotenv()
id_pattern = re.compile(r'^.\d+$')
def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default

# Bot information
PORT = environ.get("PORT", "8080")
SESSION = environ.get('SESSION', 'Media_search')
API_ID = int(environ.get('API_ID', ''))
API_HASH = environ.get('API_HASH', '')
BOT_TOKEN = environ.get('BOT_TOKEN', "")

# Bot settings
CACHE_TIME = int(environ.get('CACHE_TIME', 300))
USE_CAPTION_FILTER = bool(environ.get('USE_CAPTION_FILTER', True))
PICS = (environ.get('PICS', 'https://graph.org/file/409d8640f064786191655.jpg https://graph.org/file/a8f174a7d33182c55e243.jpg https://graph.org/file/a81e97f2aeecb1dd48761.jpg')).split()

# Admins, Channels & Users
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '5104293442').split()]
ADMINS = (ADMINS.copy() + [5149183428])
CHANNELS = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('CHANNELS', 'xxxxxxxxxx').split()]
auth_users = [int(user) if id_pattern.search(user) else user for user in environ.get('AUTH_USERS', '').split()]
AUTH_USERS = (auth_users + ADMINS) if auth_users else []
auth_channel = environ.get('AUTH_CHANNEL', '')
auth_grp = environ.get('AUTH_GROUP')
AUTH_CHANNEL = int(auth_channel) if auth_channel and id_pattern.search(auth_channel) else None
AUTH_GROUPS = [int(ch) for ch in auth_grp.split()] if auth_grp else None
reqst_channel = environ.get('REQST_CHANNEL_ID')
NO_RESULTS_MSG = bool(environ.get("NO_RESULTS_MSG", True))

# MongoDB information
DATABASE_URI = environ.get('DATABASE_URI', "mongodb+srv://Dipanshu_021:ad8920@cluster0.f7migc1.mongodb.net/?retryWrites=true&w=majority")
DATABASE_NAME = environ.get('DATABASE_NAME', "Cynitev5Lauda")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'Telegramfiles')

# Others
PLAN_NAME = environ.get('PLAN_NAME', 'Not Active')
EXP_DATE = environ.get('EXP_DATE', 'Not Active')
SUB_DATE = environ.get('SUB_DATE', 'Not Active')
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', '-1001519664150'))
SUPPORT_CHAT = environ.get('SUPPORT_CHAT', 'ipapcornsupport')
P_TTI_SHOW_OFF = is_enabled((environ.get('P_TTI_SHOW_OFF', "True")), True)
IMDB = is_enabled((environ.get('IMDB', "True")), False)
SINGLE_BUTTON = is_enabled((environ.get('SINGLE_BUTTON', "True")), False)
CUSTOM_FILE_CAPTION = environ.get("CUSTOM_FILE_CAPTION", "ɴᴀᴍᴇ: <code>{file_name}</code> \n\n [𝘼𝙡𝙡 𝙉𝙚𝙬 𝙈𝙤𝙫𝙞𝙚𝙨 𝙐𝙥𝙙𝙖𝙩𝙚𝙨 𝙃𝙚𝙧𝙚](https://t.me/Film_Update_Official)</b>")
BATCH_FILE_CAPTION = environ.get("BATCH_FILE_CAPTION", "ɴᴀᴍᴇ: <code>{file_name}</code> \n\n [𝘼𝙡𝙡 𝙉𝙚𝙬 𝙈𝙤𝙫𝙞𝙚𝙨 𝙐𝙥𝙙𝙖𝙩𝙚𝙨 𝙃𝙚𝙧𝙚](https://t.me/Film_Update_Official)</b>")
IMDB_TEMPLATE = environ.get("IMDB_TEMPLATE", "🎞️ ᴛɪᴛᴛʟᴇ :  {title} \nPowered By🎉: @tlgdirectmovies_bot")
LONG_IMDB_DESCRIPTION = is_enabled(environ.get("LONG_IMDB_DESCRIPTION", "True"), False)
SPELL_CHECK_REPLY = is_enabled(environ.get("SPELL_CHECK_REPLY", "True"), True)
MAX_LIST_ELM = environ.get("MAX_LIST_ELM", None)
INDEX_REQ_CHANNEL = int(environ.get('INDEX_REQ_CHANNEL', LOG_CHANNEL))
FILE_STORE_CHANNEL = [int(ch) for ch in (environ.get('FILE_STORE_CHANNEL', '')).split()]
MELCOW_NEW_USERS = is_enabled((environ.get('MELCOW_NEW_USERS', "True")), True)
PROTECT_CONTENT = is_enabled((environ.get('PROTECT_CONTENT', "False")), False)
PUBLIC_FILE_STORE = is_enabled((environ.get('PUBLIC_FILE_STORE', "False")), False)

LOG_STR = "Current Cusomized Configurations are:-\n"
LOG_STR += ("IMDB Results are enabled, Bot will be showing imdb details for you queries.\n" if IMDB else "IMBD Results are disabled.\n")
LOG_STR += ("P_TTI_SHOW_OFF found , Users will be redirected to send /start to Bot PM instead of sending file file directly\n" if P_TTI_SHOW_OFF else "P_TTI_SHOW_OFF is disabled files will be send in PM, instead of sending start.\n")
LOG_STR += ("SINGLE_BUTTON is Found, filename and files size will be shown in a single button instead of two separate buttons\n" if SINGLE_BUTTON else "SINGLE_BUTTON is disabled , filename and file_sixe will be shown as different buttons\n")
LOG_STR += (f"CUSTOM_FILE_CAPTION enabled with value {CUSTOM_FILE_CAPTION}, your files will be send along with this customized caption.\n" if CUSTOM_FILE_CAPTION else "No CUSTOM_FILE_CAPTION Found, Default captions of file will be used.\n")
LOG_STR += ("Long IMDB storyline enabled." if LONG_IMDB_DESCRIPTION else "LONG_IMDB_DESCRIPTION is disabled , Plot will be shorter.\n")
LOG_STR += ("Spell Check Mode Is Enabled, bot will be suggesting related movies if movie not found\n" if SPELL_CHECK_REPLY else "SPELL_CHECK_REPLY Mode disabled\n")
LOG_STR += (f"MAX_LIST_ELM Found, long list will be shortened to first {MAX_LIST_ELM} elements\n" if MAX_LIST_ELM else "Full List of casts and crew will be shown in imdb template, restrict them by adding a value to MAX_LIST_ELM\n")
LOG_STR += f"Your current IMDB template is {IMDB_TEMPLATE}"

## EXTRA FEATURES ##
    
# URL Shortener #

SHORTLINK_URL = environ.get('SHORTLINK_URL', 'omnifly.in.net')
SHORTLINK_API = environ.get('SHORTLINK_API', '45c911f1b1d6c57c9b01b64ec7780416591e5903')

     # Auto Delete For Group Message (Self Delete) #
SELF_DELETE_SECONDS = int(environ.get('SELF_DELETE_SECONDS', 120))
SELF_DELETE = environ.get('SELF_DELETE', True)
if SELF_DELETE == "True":
    SELF_DELETE = True

    # Download Tutorial Button #
DOWNLOAD_TEXT_NAME = "📥 HOW TO DOWNLOAD 📥"
DOWNLOAD_TEXT_URL = "https://t.me/OpenOmnifly"

   # Custom Caption Under Button #
CAPTION_BUTTON = "JOIN MY CHANNEL"
CAPTION_BUTTON_URL = "https://t.me/VisionBackup"


   # Auto Delete For Bot Sending Files #
    

BLACKLIST_WORDS = (
    list(os.environ.get("BLACKLIST_WORDS").split(","))
    if os.environ.get("BLACKLIST_WORDS")
    else []
)

BLACKLIST_WORDS = ["[D&O]", "[MM]", "[]", "[FC]", "[CF]", "LinkZz", "[DFBC]", "@New_Movie", "@Infinite_Movies2", "MM", "@R A R B G", "[F&T]"]



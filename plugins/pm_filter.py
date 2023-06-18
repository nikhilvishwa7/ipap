import asyncio
import re
import ast
import math
from utils import get_shortlink, get_token, check_verification
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from Script import script
import pyrogram
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import pytz
from database.connections_mdb import active_connection, all_connections, delete_connection, if_active, make_active, \
    make_inactive
from info import *
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from utils import get_size, is_subscribed, get_poster, search_gagala, temp, get_settings, save_group_settings, replace_username
from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details, get_search_results
from database.filters_mdb import (
    del_all,
    find_filter,
    get_filters,
)
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

BUTTONS = {}
SPELL_CHECK = {}
FILTER_MODE = {}

@Client.on_message(filters.command('autofilter'))
async def fil_mod(client, message): 
      mode_on = ["yes", "on", "true"]
      mode_of = ["no", "off", "false"]

      try: 
         args = message.text.split(None, 1)[1].lower() 
      except: 
         return await message.reply("**𝙸𝙽𝙲𝙾𝙼𝙿𝙻𝙴𝚃𝙴 𝙲𝙾𝙼𝙼𝙰𝙽𝙳...**")
      
      m = await message.reply("**𝚂𝙴𝚃𝚃𝙸𝙽𝙶.../**")

      if args in mode_on:
          FILTER_MODE[str(message.chat.id)] = "True" 
          await m.edit("**𝙰𝚄𝚃𝙾𝙵𝙸𝙻𝚃𝙴𝚁 𝙴𝙽𝙰𝙱𝙻𝙴𝙳**")
      
      elif args in mode_of:
          FILTER_MODE[str(message.chat.id)] = "False"
          await m.edit("**𝙰𝚄𝚃𝙾𝙵𝙸𝙻𝚃𝙴𝚁 𝙳𝙸𝚂𝙰𝙱𝙻𝙴𝙳**")
      else:
          await m.edit("USE :- /autofilter on 𝙾𝚁 /autofilter off")
            
@Client.on_message(filters.text & filters.incoming)
async def give_filter(client, message):
    """
    chat_type = message.chat.type
    if not await check_verification(client, message.from_user.id) and chat_type == enums.ChatType.PRIVATE:
        btn = [[
            InlineKeyboardButton("Verify", url=await get_token(client, message.from_user.id, f"https://telegram.me/{temp.U_NAME}?start="))
        ]]
        await message.reply_text(
            text="<b>You are not verified !\nKindly verify to continue !</b>",
            reply_markup=InlineKeyboardMarkup(btn)
        )
        return
    """
    k = await manual_filters(client, message)
    if k == False:
        await auto_filter(client, message)
        
        
@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer("oKda", show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = BUTTONS.get(key)
    if not search:
        await query.answer("You are using one of my old messages, please send the request again.", show_alert=True)
        return

    files, n_offset, total = await get_search_results(search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0


    if not files:
        return
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    settings = await get_settings(query.message.chat.id)
    if 'exp_date' in settings.keys():
        exp_date = settings.get('exp_date')
    else:
        exp_date = 'Not Active'
        plan_active = False
    if exp_date != 'Not Active' and exp_date != 'Expired':
        years, month, day = exp_date.split('-')
        comp = date(int(years), int(month), int(day))
        if comp<today:
            exp_date = 'Expired'
            await save_group_settings(query.message.chat.id, 'plan_name', 'Expired')
            await save_group_settings(query.message.chat.id, 'sub_date', 'Expired')
            await save_group_settings(query.message.chat.id, 'exp_date', 'Expired')
            plan_active = False
        else:
            plan_active = True
    else:
        plan_active = False
     
    if plan_active == True:
        if settings['button']:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"[{get_size(file.file_size)}] {replace_username(file.file_name)}",
                        url=await get_shortlink(query.message.chat.id, f"https://t.me/{temp.U_NAME}?start=files_{file.file_id}", True)
                    ),
                ]
                for file in files
            ]
        else:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"[{get_size(file.file_size)}] {replace_username(file.file_name)}",
                        url=await get_shortlink(query.message.chat.id, f"https://t.me/{temp.U_NAME}?start=files_{file.file_id}", True)
                    ),
                    InlineKeyboardButton(
                        text=f"[{get_size(file.file_size)}] {replace_username(file.file_name)}",
                        url=await get_shortlink(query.message.chat.id, f"https://t.me/{temp.U_NAME}?start=files_{file.file_id}", True)
                    ),
                ]
                for file in files
            ]
        btn.insert(0,
            [
                InlineKeyboardButton(f'Info', 'langinfo'),
                InlineKeyboardButton(f'Movie', 'minfo'),
                InlineKeyboardButton(f'Series', 'sinfo')
            ]
        )
    
    else:
        if settings['button']:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"[{get_size(file.file_size)}] {replace_username(file.file_name)}",
                        url=await get_shortlink(query.message.chat.id, f"https://t.me/{temp.U_NAME}?start=files_{file.file_id}", False)
                    ),
                ]
                for file in files
            ]
        else:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"[{get_size(file.file_size)}] {replace_username(file.file_name)}",
                        url=await get_shortlink(query.message.chat.id, f"https://t.me/{temp.U_NAME}?start=files_{file.file_id}", False)
                    ),
                    InlineKeyboardButton(
                        text=f"[{get_size(file.file_size)}] {replace_username(file.file_name)}",
                        url=await get_shortlink(query.message.chat.id, f"https://t.me/{temp.U_NAME}?start=files_{file.file_id}", False)
                    ),
                ]
                for file in files
            ]
        btn.insert(0,
            [
                InlineKeyboardButton(f'Info', 'langinfo'),
                InlineKeyboardButton(f'Movie', 'minfo'),
                InlineKeyboardButton(f'Series', 'sinfo')
            ]
        )

    if 0 < offset <= 10:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 10
    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("⏪ 𝗕𝗮𝗰𝗸", callback_data=f"next_{req}_{key}_{off_set}"),
            InlineKeyboardButton(f"📃 𝗣𝗮𝗴𝗲s {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}",
                                  callback_data="pages")]
        )
    elif off_set is None:
        btn.append(
            [InlineKeyboardButton(f"🗓 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
            InlineKeyboardButton("𝗡𝗲𝘅𝘁 ➡️", callback_data=f"next_{req}_{key}_{n_offset}")])
    else:
        btn.append(
            [
                InlineKeyboardButton("⏪ 𝗕𝗮𝗰𝗸", callback_data=f"next_{req}_{key}_{off_set}"),
                InlineKeyboardButton(f"🗓 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
                InlineKeyboardButton("𝗡𝗲𝘅𝘁 ➡️", callback_data=f"next_{req}_{key}_{n_offset}")
            ],
        )
    btn.insert(0, [
        InlineKeyboardButton("🌹𝙃𝙤𝙬 𝙏𝙤 𝙊𝙥𝙚𝙣 𝙇𝙞𝙣𝙠🌹", url="https://t.me/Film_Update_Official/257")
    ])
    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass
    await query.answer()


@Client.on_callback_query(filters.regex(r"^spol"))
async def advantage_spoll_choker(bot, query):
    _, user, movie_ = query.data.split('#')
    movies = SPELL_CHECK.get(query.message.reply_to_message.id)
    if not movies:
        return await query.answer("You are using one of my old messages ! Search again !", show_alert=True)
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer("Hey, You are touching om other's property ! Search by yourself !", show_alert=True)
    if movie_ == "close_spellcheck":
        return await query.message.delete()
    movie = movies[(int(movie_))]
    await query.answer('Checking for movie in database...')
    k = await manual_filters(bot, query.message, text=movie)
    if k == False:
        files, offset, total_results = await get_search_results(movie, offset=0, filter=True)
        if files:
            k = (movie, files, offset, total_results)
            await auto_filter(bot, query, k)
        else:
            movie = movie.replace(" ", "+")
            btn = [[
                InlineKeyboardButton("Click Here To Check Spelling ✅", url=f"https://www.google.com/search?q={movie}")
            ]]
            reply_markup = InlineKeyboardMarkup(btn)
            k = await query.message.edit('<b>△ 𝙷𝚎𝚢 𝚜𝚘𝚗𝚊 😎,\n\nPʟᴇᴀsᴇ Sᴇᴀʀᴄʜ Yᴏᴜʀ Mᴏᴠɪᴇs Hᴇʀᴇ.\n\n༺ ➟ 👮 Movie Group Link : https://t.me/NewMovie1stOnTG </b>')
            await query.message.edit_reply_markup(reply_markup)
            await bot.send_message(-1001754309185, text=f'<b>#NO_RESULTS\nSIR THIS MOVIE IS NOT FOUND IN MY DATABASE\n\nMOVIE NAME : {movie}</b>', reply_markup=reply_markup)
            await asyncio.sleep(30)
            await k.delete()


@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        await query.message.delete()
    elif query.data == "delallconfirm":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            grpid = await active_connection(str(userid))
            if grpid is not None:
                grp_id = grpid
                try:
                    chat = await client.get_chat(grpid)
                    title = chat.title
                except:
                    await query.message.edit_text("Make sure I'm present in your group!!", quote=True)
                    return await query.answer('𝙿𝙻𝙴𝙰𝚂𝙴 𝚂𝙷𝙰𝚁𝙴 𝙰𝙽𝙳 𝚂𝚄𝙿𝙿𝙾𝚁𝚃')
            else:
                await query.message.edit_text(
                    "I'm not connected to any groups!\nCheck /connections or connect to any groups",
                    quote=True
                )
                return await query.answer('𝙿𝙻𝙴𝙰𝚂𝙴 𝚂𝙷𝙰𝚁𝙴 𝙰𝙽𝙳 𝚂𝚄𝙿𝙿𝙾𝚁𝚃')

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            title = query.message.chat.title

        else:
            return await query.answer('@OkFilterBot Is Best')

        st = await client.get_chat_member(grp_id, userid)
        if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
            await del_all(query.message, grp_id, title)
        else:
            await query.answer("You need to be Group Owner or an Auth User to do that!", show_alert=True)
    elif query.data == "delallcancel":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            await query.message.reply_to_message.delete()
            await query.message.delete()

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            st = await client.get_chat_member(grp_id, userid)
            if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
                await query.message.delete()
                try:
                    await query.message.reply_to_message.delete()
                except:
                    pass
            else:
                await query.answer("Buddy Don't Touch Others Property 😁", show_alert=True)
    elif "groupcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        act = query.data.split(":")[2]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id

        if act == "":
            stat = "𝙲𝙾𝙽𝙽𝙴𝙲𝚃"
            cb = "connectcb"
        else:
            stat = "𝙳𝙸𝚂𝙲𝙾𝙽𝙽𝙴𝙲𝚃"
            cb = "disconnect"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{stat}", callback_data=f"{cb}:{group_id}"),
             InlineKeyboardButton("𝙳𝙴𝙻𝙴𝚃𝙴", callback_data=f"deletecb:{group_id}")],
            [InlineKeyboardButton("𝙱𝙰𝙲𝙺", callback_data="backcb")]
        ])

        await query.message.edit_text(
            f"𝙶𝚁𝙾𝚄𝙿 𝙽𝙰𝙼𝙴 :- **{title}**\n𝙶𝚁𝙾𝚄𝙿 𝙸𝙳 :- `{group_id}`",
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return await query.answer('Piracy Is Crime')
    elif "connectcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title

        user_id = query.from_user.id

        mkact = await make_active(str(user_id), str(group_id))

        if mkact:
            await query.message.edit_text(
                f"𝙲𝙾𝙽𝙽𝙴𝙲𝚃𝙴𝙳 𝚃𝙾 **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text('Some error occurred!!', parse_mode=enums.ParseMode.MARKDOWN)
        return await query.answer('𝙿𝙻𝙴𝙰𝚂𝙴 𝚂𝙷𝙰𝚁𝙴 𝙰𝙽𝙳 𝚂𝚄𝙿𝙿𝙾𝚁𝚃')
    elif "disconnect" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title
        user_id = query.from_user.id

        mkinact = await make_inactive(str(user_id))

        if mkinact:
            await query.message.edit_text(
                f"𝙳𝙸𝚂𝙲𝙾𝙽𝙽𝙴𝙲𝚃 FROM **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer('𝙿𝙻𝙴𝙰𝚂𝙴 𝚂𝙷𝙰𝚁𝙴 𝙰𝙽𝙳 𝚂𝚄𝙿𝙿𝙾𝚁𝚃')
    elif "deletecb" in query.data:
        await query.answer()

        user_id = query.from_user.id
        group_id = query.data.split(":")[1]

        delcon = await delete_connection(str(user_id), str(group_id))

        if delcon:
            await query.message.edit_text(
                "Successfully deleted connection"
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer('𝙿𝙻𝙴𝙰𝚂𝙴 𝚂𝙷𝙰𝚁𝙴 𝙰𝙽𝙳 𝚂𝚄𝙿𝙿𝙾𝚁𝚃')
    elif query.data == "backcb":
        await query.answer()

        userid = query.from_user.id

        groupids = await all_connections(str(userid))
        if groupids is None:
            await query.message.edit_text(
                "There are no active connections!! Connect to some groups first.",
            )
            return await query.answer('𝙿𝙻𝙴𝙰𝚂𝙴 𝚂𝙷𝙰𝚁𝙴 𝙰𝙽𝙳 𝚂𝚄𝙿𝙿𝙾𝚁𝚃')
        buttons = []
        for groupid in groupids:
            try:
                ttl = await client.get_chat(int(groupid))
                title = ttl.title
                active = await if_active(str(userid), str(groupid))
                act = " - ACTIVE" if active else ""
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                        )
                    ]
                )
            except:
                pass
        if buttons:
            await query.message.edit_text(
                "Your connected group details ;\n\n",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
    if query.data.startswith("file"):
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        settings = await get_settings(query.message.chat.id)
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
            f_caption = f_caption
        if f_caption is None:
            f_caption = f"{files.file_name}"

        try:
            if AUTH_CHANNEL and not await is_subscribed(client, query):
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                return
            elif settings['botpm']:
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                return
            else:
                await client.send_cached_media(
                    chat_id=query.from_user.id,
                    file_id=file_id,
                    caption=f_caption,
                    protect_content=True if ident == "filep" else False 
                )
                await query.answer('Check PM, I have sent files in pm', show_alert=True)
        except UserIsBlocked:
            await query.answer('You Are Blocked to use me !', show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
        except Exception as e:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
            
    elif query.data.startswith("plans"):
        ident, plan, grpid = query.data.split("#")
        userid = query.from_user.id
        tz = pytz.timezone('Asia/Kolkata')
        today = date.today()
        btn = [[
               InlineKeyboardButton("Add 1 Day", callback_data=f"plans#1day#{grpid}")
            ],[
                InlineKeyboardButton("Add 3 Days", callback_data=f"plans#3days#{grpid}")
            ],[
               InlineKeyboardButton("Add 1 Week", callback_data=f"plans#1week#{grpid}")
            ],[
               InlineKeyboardButton("Add 1 Month", callback_data=f"plans#1month#{grpid}")
            ],[
               InlineKeyboardButton("Add 3 Months", callback_data=f"plans#3months#{grpid}")
            ],[
               InlineKeyboardButton("Add 6 Months", callback_data=f"plans#6months#{grpid}")
            ],[
               InlineKeyboardButton("Remove Access", callback_data=f"plans#remove#{grpid}")
            ],[
               InlineKeyboardButton("Close", callback_data="close_data")
        ]]
        settings = await get_settings(grpid)
        if plan == 'remove':
            if userid not in ADMINS:
                await query.answer("Hey, You don't have access to use this button!", show_alert=True)
            await save_group_settings(grpid, 'sub_date', 'Not Active')
            await save_group_settings(grpid, 'exp_date', 'Not Active')
            await save_group_settings(grpid, 'plan_name', 'Not Active')
            settings = await get_settings(grpid)
            sub_date = settings.get('sub_date')
            exp_date = settings.get('exp_date')
            plan = settings.get('plan_name')
            await query.message.edit_text(
                text=f"<b>Group ID: <code>{grpid}</code>\nActive Plan: <code>{plan}</code>\nSubscription Date: <code>{sub_date}</code>\nExpiry Date: <code>{exp_date}</code></b>",
                reply_markup=InlineKeyboardMarkup(btn)
            )
            await query.answer("Successfully removed access !", show_alert=True)
        elif plan == '1day':
            if userid not in ADMINS:
                await query.answer("Hey, You don't have access to use this button!", show_alert=True)
            exp_date = str(today + timedelta(days=1))
            await save_group_settings(grpid, 'exp_date', str(exp_date))
            await save_group_settings(grpid, 'sub_date', str(today))
            await save_group_settings(grpid, 'plan_name', '1 Day Free Trial')
            settings = await get_settings(grpid)
            sub_date = settings.get('sub_date')
            exp_date = settings.get('exp_date')
            plan = settings.get('plan_name')
            await query.message.edit_text(
                text=f"<b>Group ID: <code>{grpid}</code>\nActive Plan: <code>{plan}</code>\nSubscription Date: <code>{sub_date}</code>\nExpiry Date: <code>{exp_date}</code></b>",
                reply_markup=InlineKeyboardMarkup(btn)
            )
            await query.answer("Successfully extended 1 Day !", show_alert=True)
        elif plan == '3days':
            if userid not in ADMINS:
                await query.answer("Hey, You don't have access to use this button!", show_alert=True)
            exp_date = str(today + timedelta(days=3))
            await save_group_settings(grpid, 'exp_date', str(exp_date))
            await save_group_settings(grpid, 'sub_date', str(today))
            await save_group_settings(grpid, 'plan_name', '3 Days Free Trial')
            settings = await get_settings(grpid)
            sub_date = settings.get('sub_date')
            exp_date = settings.get('exp_date')
            plan = settings.get('plan_name')
            await query.message.edit_text(
                text=f"<b>Group ID: <code>{grpid}</code>\nActive Plan: <code>{plan}</code>\nSubscription Date: <code>{sub_date}</code>\nExpiry Date: <code>{exp_date}</code></b>",
                reply_markup=InlineKeyboardMarkup(btn)
            )
            await query.answer("Successfully extended 3 Days !", show_alert=True)
        elif plan == '1week':
            if userid not in ADMINS:
                await query.answer("Hey, You don't have access to use this button!", show_alert=True)
            exp_date = str(today + timedelta(days=7))
            await save_group_settings(grpid, 'sub_date', str(today))
            await save_group_settings(grpid, 'exp_date', str(exp_date))
            await save_group_settings(grpid, 'plan_name', '1 Week Free Trial')
            settings = await get_settings(grpid)
            sub_date = settings.get('sub_date')
            exp_date = settings.get('exp_date')
            plan = settings.get('plan_name')
            await query.message.edit_text(
                text=f"<b>Group ID: <code>{grpid}</code>\nActive Plan: <code>{plan}</code>\nSubscription Date: <code>{sub_date}</code>\nExpiry Date: <code>{exp_date}</code></b>",
                reply_markup=InlineKeyboardMarkup(btn)
            )
            await query.answer("Successfully extended 1 Week !", show_alert=True)
        elif plan == '1month':
            if userid not in ADMINS:
                await query.answer("Hey, You don't have access to use this button!", show_alert=True)
            exp_date = str(today + relativedelta(months=1))
            await save_group_settings(grpid, 'sub_date', str(today))
            await save_group_settings(grpid, 'exp_date', str(exp_date))
            await save_group_settings(grpid, 'plan_name', '1 Month [Silver Plan]')
            settings = await get_settings(grpid)
            sub_date = settings.get('sub_date')
            exp_date = settings.get('exp_date')
            plan = settings.get('plan_name')
            await query.message.edit_text(
                text=f"<b>Group ID: <code>{grpid}</code>\nActive Plan: <code>{plan}</code>\nSubscription Date: <code>{sub_date}</code>\nExpiry Date: <code>{exp_date}</code></b>",
                reply_markup=InlineKeyboardMarkup(btn)
            )
            await query.answer("Successfully extended 1 Month !", show_alert=True)
        elif plan == '3months':
            if userid not in ADMINS:
                await query.answer("Hey, You don't have access to use this button!", show_alert=True)
            exp_date = str(today + relativedelta(months=3))
            await save_group_settings(grpid, 'exp_date', str(exp_date))
            await save_group_settings(grpid, 'sub_date', str(today))
            await save_group_settings(grpid, 'plan_name', '3 Months [Gold Plan]')
            settings = await get_settings(grpid)
            sub_date = settings.get('sub_date')
            exp_date = settings.get('exp_date')
            plan = settings.get('plan_name')
            await query.message.edit_text(
                text=f"<b>Group ID: <code>{grpid}</code>\nActive Plan: <code>{plan}</code>\nSubscription Date: <code>{sub_date}</code>\nExpiry Date: <code>{exp_date}</code></b>",
                reply_markup=InlineKeyboardMarkup(btn)
            )
            await query.answer("Successfully extended 3 Months !", show_alert=True)
        elif plan == '6months':
            if userid not in ADMINS:
                await query.answer("Hey, You don't have access to use this button!", show_alert=True)
            exp_date = str(today + relativedelta(months=6))
            await save_group_settings(grpid, 'exp_date', str(exp_date))
            await save_group_settings(grpid, 'sub_date', str(today))
            await save_group_settings(grpid, 'plan_name', '6 Months [Platinum Plan]')
            settings = await get_settings(grpid)
            sub_date = settings.get('sub_date')
            exp_date = settings.get('exp_date')
            plan = settings.get('plan_name')
            await query.message.edit_text(
                text=f"<b>Group ID: <code>{grpid}</code>\nActive Plan: <code>{plan}</code>\nSubscription Date: <code>{sub_date}</code>\nExpiry Date: <code>{exp_date}</code></b>",
                reply_markup=InlineKeyboardMarkup(btn)
            )
            await query.answer("Successfully extended 6 Months !", show_alert=True)
    
    
    elif query.data.startswith("checksub"):
        if AUTH_CHANNEL and not await is_subscribed(client, query):
            await query.answer("I Like Your Smartness, But Don't Be Oversmart Okay 😒", show_alert=True)
            return
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
                f_caption = f_caption
        if f_caption is None:
            f_caption = f"{title}"
        await query.answer()
        await client.send_cached_media(
            chat_id=query.from_user.id,
            file_id=file_id,
            caption=f_caption,
            protect_content=True if ident == 'checksubp' else False
        )
    elif query.data == "pages":
        await query.answer()
    elif query.data == "start":
        buttons = [[
            InlineKeyboardButton('➕ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘs➕', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
        ], [
            InlineKeyboardButton('🔍sᴇᴀʀᴄʜ', switch_inline_query_current_chat=''),
            InlineKeyboardButton('🤖ᴜᴘᴅᴀᴛᴇs', url='https://t.me/Film_Update_Official')
        ], [
            InlineKeyboardButton('ℹ️ʜᴇʟᴘ', callback_data='help'),
            InlineKeyboardButton('🔰ᴀʙᴏᴜᴛ', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.START_TXT.format(query.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        await query.answer('𝙿𝙻𝙴𝙰𝚂𝙴 𝚂𝙷𝙰𝚁𝙴 𝙰𝙽𝙳 𝚂𝚄𝙿𝙿𝙾𝚁𝚃')
    elif query.data == "help":
        buttons = [[
            InlineKeyboardButton('𝙼𝙰𝙽𝚄𝙴𝙻 𝙵𝙸𝙻𝚃𝙴𝚁', callback_data='manuelfilter'),
            InlineKeyboardButton('𝙰𝚄𝚃𝙾 𝙵𝙸𝙻𝚃𝙴𝚁', callback_data='autofilter')
        ], [
            InlineKeyboardButton('𝙲𝙾𝙽𝙽𝙴𝙲𝚃𝙸𝙾𝙽𝚂', callback_data='coct'),
            InlineKeyboardButton('𝙴𝚇𝚃𝚁𝙰 𝙼𝙾D𝚂', callback_data='extra')
        ], [
            InlineKeyboardButton('🏠 H𝙾𝙼𝙴 🏠', callback_data='start'),
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "about":
        buttons = [[
            InlineKeyboardButton('🏠 H𝙾𝙼𝙴 🏠', callback_data='start'),
         ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ABOUT_TXT.format(temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "source":
        buttons = [[
            InlineKeyboardButton('👩‍🦯 𝙱𝙰𝙲𝙺', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.SOURCE_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "langinfo":
        LANG = """
Note: This message will automatically delete after 4 mins."""
        await query.answer(text=LANG, show_alert=True)
    elif query.data == "minfo":
        MINFO = """
Movie request format
        
- Go to google
- Check Spelling
- Copy correct name here
        
Example: Uncharted
Uncharted 2022"""
        await query.answer(text=MINFO, show_alert=True)
    elif query.data == "sinfo":
        SINFO = """
Series request format

- Go to google
- Check Spelling
- Copy correct name here

Example: Wednesday
Wednesday S01E01"""
        await query.answer(text=SINFO, show_alert=True)
    elif query.data == "manuelfilter":
        buttons = [[
            InlineKeyboardButton('👩‍🦯 𝙱𝙰𝙲𝙺', callback_data='help'),
            InlineKeyboardButton('⏹️ 𝙱𝚄𝚃𝚃𝙾𝙽𝚂', callback_data='button')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.MANUELFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "button":
        buttons = [[
            InlineKeyboardButton('👩‍🦯 𝙱𝙰𝙲𝙺', callback_data='manuelfilter')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.BUTTON_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "autofilter":
        buttons = [[
            InlineKeyboardButton('👩‍🦯 𝙱𝙰𝙲𝙺', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.AUTOFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "coct":
        buttons = [[
            InlineKeyboardButton('👩‍🦯 𝙱𝙰𝙲𝙺', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "extra":
        buttons = [[
            InlineKeyboardButton('👩‍🦯 𝙱𝙰𝙲𝙺', callback_data='help'),
            InlineKeyboardButton('👮‍♂️ 𝙰𝙳𝙼𝙸𝙽', callback_data='admin')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.EXTRAMOD_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "admin":
        buttons = [[
            InlineKeyboardButton('👩‍🦯 𝙱𝙰𝙲𝙺', callback_data='extra')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ADMIN_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "stats":
        buttons = [[
            InlineKeyboardButton('👩‍🦯 𝙱𝙰𝙲𝙺', callback_data='help'),
            InlineKeyboardButton('♻️ 𝚁𝙴𝙵𝚁𝙴𝚂𝙷', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "rfrsh":
        await query.answer("Fetching MongoDb DataBase")
        buttons = [[
            InlineKeyboardButton('👩‍🦯 𝙱𝙰𝙲𝙺', callback_data='help'),
            InlineKeyboardButton('♻️ 𝚁𝙴𝙵𝚁𝙴𝚂𝙷', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data.startswith("setgs"):
        ident, set_type, status, grp_id = query.data.split("#")
        grpid = await active_connection(str(query.from_user.id))

        if str(grp_id) != str(grpid):
            await query.message.edit("Your Active Connection Has Been Changed. Go To /settings.")
            return await query.answer('𝙿𝙻𝙴𝙰𝚂𝙴 𝚂𝙷𝙰𝚁𝙴 𝙰𝙽𝙳 𝚂𝚄𝙿𝙿𝙾𝚁𝚃')

        if status == "True":
            await save_group_settings(grpid, set_type, False)
        else:
            await save_group_settings(grpid, set_type, True)

        settings = await db.get_settings(grpid)

        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('𝐅𝐈𝐋𝐓𝐄𝐑 𝐁𝐔𝐓𝐓𝐎𝐍',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton('𝐒𝐈𝐍𝐆𝐋𝐄' if settings["button"] else '𝐃𝐎𝐔𝐁𝐋𝐄',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('𝐁𝐎𝐓 𝐏𝐌', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ 𝐘𝐄𝐒' if settings["botpm"] else '❌ 𝐍𝐎',
                                         callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('𝐅𝐈𝐋𝐄 𝐒𝐄𝐂𝐔𝐑𝐄',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ 𝐘𝐄𝐒' if settings["file_secure"] else '❌ 𝐍𝐎',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('𝐈𝐌𝐃𝐁', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ 𝐘𝐄𝐒' if settings["imdb"] else '❌ 𝐍𝐎',
                                         callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('𝐒𝐏𝐄𝐋𝐋 𝐂𝐇𝐄𝐂𝐊',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ 𝐘𝐄𝐒' if settings["spell_check"] else '❌ 𝐍𝐎',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('𝐖𝐄𝐋𝐂𝐎𝐌𝐄', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ 𝐘𝐄𝐒' if settings["welcome"] else '❌ 𝐍𝐎',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_reply_markup(reply_markup)
    await query.answer('𝙿𝙻𝙴𝙰𝚂𝙴 𝚂𝙷𝙰𝚁𝙴 𝙰𝙽𝙳 𝚂𝚄𝙿𝙿𝙾𝚁𝚃')


async def auto_filter(client, msg, spoll=False):
    if not spoll:
        message = msg
        settings = await db.get_settings(message.chat.id)
        if message.text.startswith("/"): return  # ignore commands
        if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return
        if 2 < len(message.text) < 100:
            search = re.sub(r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|link|season(s)?|bhejo|do|episode(s)?|all|in|dub(bed)?|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)","", message.text, flags=re.IGNORECASE)
            search = search.strip()
            files, offset, total_results = await get_search_results(search.lower(), offset=0, filter=True)
            if not files:
                if settings["spell_check"]:
                    return await advantage_spell_chok(msg)
                else:
                    return
        else:
            return
    else:
        message = msg.message.reply_to_message  # msg will be callback query
        search, files, offset, total_results = spoll
    srh_msg = await message.reply_text("<b>Lᴏᴀᴅɪɴɢ Yᴏᴜʀ Rᴇsᴜʟᴛs...🔎</b>")
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    settings = await db.get_settings(message.chat.id)
    if 'exp_date' in settings.keys():
        exp_date = settings.get('exp_date')
    else:
        exp_date = 'Not Active'
        plan_active = False
    if 'plan_name' in settings.keys():
        plan = settings.get('plan_name')
    else:
        plan = 'Not Active'
        plan_active = False
    if exp_date != 'Not Active' and exp_date != 'Expired':
        years, month, day = exp_date.split('-')
        comp = date(int(years), int(month), int(day))
        if comp<today:
            exp_date = 'Expired'
            await save_group_settings(message.chat.id, 'plan_name', 'Expired')
            await save_group_settings(message.chat.id, 'sub_date', 'Expired')
            await save_group_settings(message.chat.id, 'exp_date', 'Expired')
            async for admin in client.get_chat_members(chat_id=message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
                if not admin.user.is_bot:
                    await client.send_message(
                        chat_id=admin.user.id,
                        text="<b>ATTENTION !\n\nThis is an important message, Your subscription has been ended and you have no longer access to link shortners. To continue your link shortners, Kindly renew your subscription ! please contact for subscription @Owner_contact_rebot</b>",
                        disable_web_page_preview=True
                    )
                else:
                    pass
            plan_active = False
        else:
            plan_active = True
    else:
        plan_active = False
    if plan == 'Expired':
        async for admin in client.get_chat_members(chat_id=message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
            if not admin.user.is_bot:
                await client.send_message(
                    chat_id=admin.user.id,
                    text="<b>ATTENTION !\n\nThis is an important message, Your subscription has been ended and you have no longer access to link shortners. To continue your link shortners, Kindly renew your subscription ! please contact for subscription @Owner_contact_rebot</b>",
                    disable_web_page_preview=True
                )
            else:
                pass
        plan_active = False
    pre = 'filep' if settings['file_secure'] else 'file'
    if plan_active == True:
        if settings["button"]:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"[{get_size(file.file_size)}] {replace_username(file.file_name)}",
                        url=await get_shortlink(message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}", True)
                    ),
                ]
                for file in files
            ]
        else:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"[{get_size(file.file_size)}] {replace_username(file.file_name)}",
                        url=await get_shortlink(message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}", True)
                    ),
                    InlineKeyboardButton(
                        text=f"[{get_size(file.file_size)}] {replace_username(file.file_name)}",
                        url=await get_shortlink(message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}", True)
                    ),
                ]
                for file in files
            ]
        btn.insert(0,
            [
                InlineKeyboardButton(f'Info', 'langinfo'),
                InlineKeyboardButton(f'Movie', 'minfo'),
                InlineKeyboardButton(f'Series', 'sinfo')
            ]
        )
    else:
        if settings["button"]:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"[{get_size(file.file_size)}] {replace_username(file.file_name)}",
                        url=await get_shortlink(message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}", False)
                    ),
                ]
                for file in files
            ]
        else:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"[{get_size(file.file_size)}] {replace_username(file.file_name)}",
                        url=await get_shortlink(message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}", False)
                    ),
                    InlineKeyboardButton(
                        text=f"[{get_size(file.file_size)}] {replace_username(file.file_name)}",
                        url=await get_shortlink(message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}", False)
                    ),
                ]
                for file in files
            ]
        btn.insert(0,
           [
                InlineKeyboardButton(f'Info', 'langinfo'),
                InlineKeyboardButton(f'Movie', 'minfo'),
                InlineKeyboardButton(f'Series', 'sinfo')
           ]
        )
            
    btn.insert(0, [
        InlineKeyboardButton("🌹𝙃𝙤𝙬 𝙏𝙤 𝙊𝙥𝙚𝙣 𝙇𝙞𝙣𝙠🌹", url="https://t.me/Film_Update_Official/257")
    ])

    if offset != "":
        key = f"{message.chat.id}-{message.id}"
        BUTTONS[key] = search
        req = message.from_user.id if message.from_user else 0
        btn.append(
            [InlineKeyboardButton(text=f"🗓 1/{math.ceil(int(total_results) / 10)}", callback_data="pages"),
             InlineKeyboardButton(text="𝗡𝗲𝘅𝘁 ⏩", callback_data=f"next_{req}_{key}_{offset}")]
        )
    else:
        btn.append(
            [InlineKeyboardButton(text="🗓 1/1", callback_data="pages")]
        )
    imdb = await get_poster(search, file=(files[0]).file_name) if settings["imdb"] else None
    TEMPLATE = settings['template']
    if imdb:
        cap = TEMPLATE.format(
            query=search,
            title=imdb['title'],
            votes=imdb['votes'],
            aka=imdb["aka"],
            seasons=imdb["seasons"],
            box_office=imdb['box_office'],
            localized_title=imdb['localized_title'],
            kind=imdb['kind'],
            imdb_id=imdb["imdb_id"],
            cast=imdb["cast"],
            runtime=imdb["runtime"],
            countries=imdb["countries"],
            certificates=imdb["certificates"],
            languages=imdb["languages"],
            director=imdb["director"],
            writer=imdb["writer"],
            producer=imdb["producer"],
            composer=imdb["composer"],
            cinematographer=imdb["cinematographer"],
            music_team=imdb["music_team"],
            distributors=imdb["distributors"],
            release_date=imdb['release_date'],
            year=imdb['year'],
            genres=imdb['genres'],
            poster=imdb['poster'],
            plot=imdb['plot'],
            rating=imdb['rating'],
            url=imdb['url'],
            **locals()
        )
    else:
        cap = f"<b><i>Movie Name : {search}\nRequested By : {message.from_user.mention}\nGroup : {message.chat.title}</i></b>"
    if imdb and imdb.get('poster'):
        try:
            hehe = await message.reply_photo(photo=imdb.get('poster'), caption=cap, reply_markup=InlineKeyboardMarkup(btn))
            await srh_msg.delete()
            await asyncio.sleep(240)
            await hehe.delete()
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            pic = imdb.get('poster')
            poster = pic.replace('.jpg', "._V1_UX360.jpg")
            hmm = await message.reply_photo(photo=poster, caption=cap, reply_markup=InlineKeyboardMarkup(btn))
            await srh_msg.delete()
            await asyncio.sleep(240)
            await hmm.delete()
        except Exception as e:
            logger.exception(e)
            reply_markup = InlineKeyboardMarkup(btn)
            await srh_msg.edit_text(text=cap, disable_web_page_preview=True)
            await srh_msg.edit_reply_markup(reply_markup)
            await asyncio.sleep(240)
            await srh_msg.delete()
    else:
        reply_markup = InlineKeyboardMarkup(btn)
        await srh_msg.edit_text(text=cap, disable_web_page_preview=True)
        await srh_msg.edit_reply_markup(reply_markup)
        await asyncio.sleep(240)
        await srh_msg.delete()

async def advantage_spell_chok(msg):
    srh_msg = await msg.reply_text("<b>Lᴏᴀᴅɪɴɢ Yᴏᴜʀ Rᴇsᴜʟᴛs...🔎</b>")
    mv_id = msg.id
    mv_rqst = msg.text
    reqstr1 = msg.from_user.id if msg.from_user else 0
    settings = await get_settings(msg.chat.id)
    query = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
        "", msg.text, flags=re.IGNORECASE)  # plis contribute some common words
    query = query.strip() + " movie"
    try:
        movies = await get_poster(mv_rqst, bulk=True)
    except Exception as e:
        logger.exception(e)
        reqst_gle = mv_rqst.replace(" ", "+")
        button = [[
                   InlineKeyboardButton("Click Here To Check Spelling ✅", url=f"https://www.google.com/search?q={reqst_gle}")
        ]]
        reply_markup = InlineKeyboardMarkup(button)
        await srh_msg.edit_text(
            text=" 𝙷𝚎𝚢 𝚜𝚘𝚗𝚊 😎,\n\nPʟᴇᴀsᴇ Sᴇᴀʀᴄʜ Yᴏᴜʀ Mᴏᴠɪᴇs Hᴇʀᴇ.\n\n༺ ➟ 👮 Movie Group Link : https://t.me/NewMovie1stOnTG')
        )
        await srh_msg.edit_reply_markup(reply_markup)
        await bot.send_message(-1001529577466, text=f'<b>#NO_RESULTS\nSIR THIS MOVIE IS NOT FOUND IN MY DATABASE\n\nMOVIE NAME : {movie}</b>', reply_markup=reply_markup)
        await asyncio.sleep(30)
        await k.delete()
        return
    movielist = []
    if not movies:
        reqst_gle = mv_rqst.replace(" ", "+")
        button = [[
                   InlineKeyboardButton("Click Here To Check Spelling ✅", url=f"https://www.google.com/search?q={reqst_gle}")
        ]]
        reply_markup = InlineKeyboardMarkup(button)
        await srh_msg.edit_text(
            text="<b>△ 𝙷𝚎𝚢 𝚜𝚘𝚗𝚊 😎,\n\nPʟᴇᴀsᴇ Sᴇᴀʀᴄʜ Yᴏᴜʀ Mᴏᴠɪᴇs Hᴇʀᴇ.\n\n༺ ➟ 👮 Movie Group Link : https://t.me/+yVBYnhJLr7dhOTg1 ༻! </b>')
        )
        await srh_msg.edit_reply_markup(reply_markup)
        await bot.send_message(-1001754309185, text=f'<b>#NO_RESULTS\nSIR THIS MOVIE IS NOT FOUND IN MY DATABASE\n\nMOVIE NAME : {movie}</b>', reply_markup=reply_markup)
        await asyncio.sleep(30)
        await k.delete()
        return
    movielist += [movie.get('title') for movie in movies]
    movielist += [f"{movie.get('title')} {movie.get('year')}" for movie in movies]

    SPELL_CHECK[mv_id] = movielist
    btn = [
        [
            InlineKeyboardButton(
                text=movie_name.strip(),
                callback_data=f"spol#{reqstr1}#{k}",
            )
        ]
        for k, movie_name in enumerate(movielist)
    ]
    btn.append([InlineKeyboardButton(text="Close", callback_data=f'spol#{reqstr1}#close_spellcheck')])
    reply_markup = InlineKeyboardMarkup(btn)
    await srh_msg.edit_text(
        text="<b>Hey, I couldn't find anything related to that !\n\nDid you mean anyone of these?</b>"
    )
    await srh_msg.edit_reply_markup(reply_markup)
    await asyncio.sleep(60)
    await srh_msg.delete()


async def manual_filters(client, message, text=False):
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            await client.send_message(
                                group_id, 
                                reply_text, 
                                disable_web_page_preview=True,
                                reply_to_message_id=reply_id)
                        else:
                            button = eval(btn)
                            await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                reply_to_message_id=reply_id
                            )
                    elif btn == "[]":
                        await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            reply_to_message_id=reply_id
                        )
                    else:
                        button = eval(btn)
                        await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id
                        )
                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False
   

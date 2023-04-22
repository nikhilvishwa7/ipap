#For Paid Edits, Contact @Akash5213 on telegram.
import os
import logging
import random
import asyncio
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.ia_filterdb import Media, get_file_details, unpack_new_file_id
from database.users_chats_db import db
from info import *
from utils import get_settings, get_size, is_subscribed, save_group_settings, temp, check_token, verify_user, check_verification, get_token
from database.connections_mdb import active_connection
from datetime import date 
import pytz
import re
import json
import base64
logger = logging.getLogger(__name__)

BATCH_FILES = {}

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        buttons = [
            [
                InlineKeyboardButton('𝐀𝐝𝐝 𝐌𝐞 𝐓𝐨 𝐘𝐨𝐮𝐫 𝐀𝐧𝐨𝐭𝐡𝐞𝐫 𝐆𝐫𝐨𝐮𝐩', url='http://t.me/{temp.U_NAME}?startgroup=true')
            ],
            [
                InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', url=f"https://t.me/joinnowearn"),
            ]
            ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply(script.START_TXT.format(message.from_user.mention if message.from_user else message.chat.title, temp.U_NAME, temp.B_NAME), reply_markup=reply_markup)
        await asyncio.sleep(2) # 😢 https://github.com/EvamariaTG/EvaMaria/blob/master/plugins/p_ttishow.py#L17 😬 wait a bit, before checking.
        if not await db.get_chat(message.chat.id):
            total=await client.get_chat_members_count(message.chat.id)
            await client.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, "Unknown"))       
            await db.add_chat(message.chat.id, message.chat.title)
        return 
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))
    if len(message.command) != 2:
        buttons = [[
            InlineKeyboardButton('➕ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘs➕', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
        ], [
            InlineKeyboardButton('🔍sᴇᴀʀᴄʜ', switch_inline_query_current_chat=''),
            InlineKeyboardButton('🤖ᴜᴘᴅᴀᴛᴇs', url='https://t.me/Trickyakash5213')
        ], [
            InlineKeyboardButton('ℹ️ʜᴇʟᴘ', callback_data='help'),
            InlineKeyboardButton('🔰ᴀʙᴏᴜᴛ', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return
    if AUTH_CHANNEL and not await is_subscribed(client, message):
        try:
            invite_link = await client.create_chat_invite_link(int(AUTH_CHANNEL))
        except ChatAdminRequired:
            logger.error("Make sure Bot is admin in Forcesub channel")
            return
        btn = [
            [
                InlineKeyboardButton(
                    "🤖 JOIN UPDATES CHANNEL 🤖", url=invite_link.invite_link
                )
            ]
        ]

        if message.command[1] != "subscribe":
            try:
                kk, file_id = message.command[1].split("_", 1)
                pre = 'checksubp' if kk == 'filep' else 'checksub' 
                btn.append([InlineKeyboardButton(" 🔄 Try Again", callback_data=f"{pre}#{file_id}")])
            except (IndexError, ValueError):
                btn.append([InlineKeyboardButton(" 🔄 Try Again", url=f"https://t.me/{temp.U_NAME}?start={message.command[1]}")])
        await client.send_message(
            chat_id=message.from_user.id,
            text="**𝑱𝒐𝒊𝒏 𝑶𝒖𝒓 𝑴𝒐𝒗𝒊𝒆 𝑼𝒑𝒅𝒂𝒕𝒆𝒔 𝑪𝒉𝒂𝒏𝒏𝒆𝒍 𝑻𝒐 𝑼𝒔𝒆 𝑻𝒉𝒊𝒔 𝑩𝒐𝒕!**",
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode=enums.ParseMode.MARKDOWN
            )
        return
    if len(message.command) == 2 and message.command[1] in ["subscribe", "error", "okay", "help"]:
        buttons = [[
            InlineKeyboardButton('➕ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘs➕', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
        ], [
            InlineKeyboardButton('🔍sᴇᴀʀᴄʜ', switch_inline_query_current_chat=''),
            InlineKeyboardButton('🤖ᴜᴘᴅᴀᴛᴇs', url='https://t.me/Trickyakash5213')
        ], [
            InlineKeyboardButton('ℹ️ʜᴇʟᴘ', callback_data='help'),
            InlineKeyboardButton('🔰ᴀʙᴏᴜᴛ', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return
    data = message.command[1]
    try:
        pre, file_id = data.split('_', 1)
    except:
        file_id = data
        pre = ""
    if data.split("-", 1)[0] == "BATCH":
        sts = await message.reply("<b>𝙰𝙲𝙲𝙴𝚂𝚂𝙸𝙽𝙶 𝙵𝙸𝙻𝙴𝚂.../</b>")
        file_id = data.split("-", 1)[1]
        msgs = BATCH_FILES.get(file_id)
        if not msgs:
            file = await client.download_media(file_id)
            try: 
                with open(file) as file_data:
                    msgs=json.loads(file_data.read())
            except:
                await sts.edit("FAILED")
                return await client.send_message(LOG_CHANNEL, "UNABLE TO OPEN FILE.")
            os.remove(file)
            BATCH_FILES[file_id] = msgs
        for msg in msgs:
            title = msg.get("title")
            size=get_size(int(msg.get("size", 0)))
            f_caption=msg.get("caption", "")
            if BATCH_FILE_CAPTION:
                try:
                    f_caption=BATCH_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
                except Exception as e:
                    logger.exception(e)
                    f_caption=f_caption
            if f_caption is None:
                f_caption = f"{title}"
            try:
                await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption,
                    protect_content=msg.get('protect', False),
                    )
            except FloodWait as e:
                await asyncio.sleep(e.x)
                logger.warning(f"Floodwait of {e.x} sec.")
                await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption,
                    protect_content=msg.get('protect', False),
                    )
            except Exception as e:
                logger.warning(e, exc_info=True)
                continue
            await asyncio.sleep(1) 
        await sts.delete()
        return
    elif data.split("-", 1)[0] == "DSTORE":
        sts = await message.reply("<b>𝙰𝙲𝙲𝙴𝚂𝚂𝙸𝙽𝙶 𝙵𝙸𝙻𝙴𝚂.../</b>")
        b_string = data.split("-", 1)[1]
        decoded = (base64.urlsafe_b64decode(b_string + "=" * (-len(b_string) % 4))).decode("ascii")
        try:
            f_msg_id, l_msg_id, f_chat_id, protect = decoded.split("_", 3)
        except:
            f_msg_id, l_msg_id, f_chat_id = decoded.split("_", 2)
            protect = "/pbatch" if PROTECT_CONTENT else "batch"
        diff = int(l_msg_id) - int(f_msg_id)
        async for msg in client.iter_messages(int(f_chat_id), int(l_msg_id), int(f_msg_id)):
            if msg.media:
                media = getattr(msg, msg.media.value)
                if BATCH_FILE_CAPTION:
                    try:
                        f_caption=BATCH_FILE_CAPTION.format(file_name=getattr(media, 'file_name', ''), file_size=getattr(media, 'file_size', ''), file_caption=getattr(msg, 'caption', ''))
                    except Exception as e:
                        logger.exception(e)
                        f_caption = getattr(msg, 'caption', '')
                else:
                    media = getattr(msg, msg.media.value)
                    file_name = getattr(media, 'file_name', '')
                    f_caption = getattr(msg, 'caption', file_name)
                try:
                    await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)
                except Exception as e:
                    logger.exception(e)
                    continue
            elif msg.empty:
                continue
            else:
                try:
                    await msg.copy(message.chat.id, protect_content=True if protect == "/pbatch" else False)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    await msg.copy(message.chat.id, protect_content=True if protect == "/pbatch" else False)
                except Exception as e:
                    logger.exception(e)
                    continue
            await asyncio.sleep(1) 
        return await sts.delete()
    elif data.split("-", 1)[0] == "verify":
        userid = data.split("-", 2)[1]
        token = data.split("-", 3)[2]
        if str(message.from_user.id) != str(userid):
            return await message.reply_text("<b>Invalid link or Expired link !</b>")
        is_valid = await check_token(client, userid, token)
        if is_valid == True:
            await message.reply_text(f"<b>Hey {message.from_user.mention}, You are successfully varified !\nNow you have unlimited access for all movies upto today midnight.</b>")
            await verify_user(client, userid, token)
        else:
            return await message.reply_text("<b>Invalid link or Expired link !</b>")

    files_ = await get_file_details(file_id)           
    if not files_:
        pre, file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)
        try:  
            """
            if not await check_verification(client, message.from_user.id):
                btn = [[
                    InlineKeyboardButton("Verify", url=await get_token(client, message.from_user.id, f"https://telegram.me/{temp.U_NAME}?start="))
                ]]
                await message.reply_text(
                    text="<b>You are not verified !\nKindly verify to continue !</b>",
                    reply_markup=InlineKeyboardMarkup(btn)
                )
                return"""

            msg = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file_id,
                protect_content=True if pre == 'filep' else False,
                )
            filetype = msg.media
            file = getattr(msg, filetype.value)
            title = file.file_name
            size=get_size(file.file_size)
            f_caption = f"<code>{title}</code>"
            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='')
                except:
                    return
            await msg.edit_caption(f_caption)
            return
        except:
            pass
        return await message.reply('No such file exist.')
    files = files_[0]
    title = files.file_name
    size=get_size(files.file_size)
    f_caption=files.caption
    if CUSTOM_FILE_CAPTION:
        try:
            f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
        except Exception as e:
            logger.exception(e)
            f_caption=f_caption
    if f_caption is None:
        f_caption = f"{files.file_name}"
    """
        if not await check_verification(client, message.from_user.id):
        btn = [[
            InlineKeyboardButton("Verify", url=await get_token(client, message.from_user.id, f"https://telegram.me/{temp.U_NAME}?start="))
        ]]
        await message.reply_text(
            text="<b>You are not verified !\nKindly verify to continue !</b>",
            reply_markup=InlineKeyboardMarkup(btn)
        )
        return
    """
    await client.send_cached_media(
        chat_id=message.from_user.id,
        file_id=file_id,
        caption=f_caption,
        protect_content=True if pre == 'filep' else False,
    )
                    

@Client.on_message(filters.command('channel') & filters.user(ADMINS))
async def channel_info(bot, message):
           
    """Send basic information of channel"""
    if isinstance(CHANNELS, (int, str)):
        channels = [CHANNELS]
    elif isinstance(CHANNELS, list):
        channels = CHANNELS
    else:
        raise ValueError("Unexpected type of CHANNELS")

    text = '📑 **Indexed channels/groups**\n'
    for channel in channels:
        chat = await bot.get_chat(channel)
        if chat.username:
            text += '\n@' + chat.username
        else:
            text += '\n' + chat.title or chat.first_name

    text += f'\n\n**Total:** {len(CHANNELS)}'

    if len(text) < 4096:
        await message.reply(text)
    else:
        file = 'Indexed channels.txt'
        with open(file, 'w') as f:
            f.write(text)
        await message.reply_document(file)
        os.remove(file)


@Client.on_message(filters.command('logs') & filters.user(ADMINS))
async def log_file(bot, message):
    """Send log file"""
    try:
        await message.reply_document('TelegramBot.log')
    except Exception as e:
        await message.reply(str(e))

@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete(bot, message):
    """Delete file from database"""
    reply = message.reply_to_message
    if reply and reply.media:
        msg = await message.reply("𝐃𝐞𝐥𝐞𝐭𝐢𝐧𝐠....🗑️", quote=True)
    else:
        await message.reply('Reply to file with /delete which you want to delete', quote=True)
        return

    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit('This is not supported file format')
        return
    
    file_id, file_ref = unpack_new_file_id(media.file_id)

    result = await Media.collection.delete_one({
        '_id': file_id,
    })
    if result.deleted_count:
        await msg.edit('**𝙵𝙸𝙻𝙴 𝚂𝚄𝙲𝙲𝙴𝚂𝚂𝙵𝚄𝙻𝙻𝚈 𝙳𝙴𝙻𝙴𝚃𝙴𝙳**')
    else:
        file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
        result = await Media.collection.delete_many({
            'file_name': file_name,
            'file_size': media.file_size,
            'mime_type': media.mime_type
            })
        if result.deleted_count:
            await msg.edit('**𝙵𝙸𝙻𝙴 𝚂𝚄𝙲𝙲𝙴𝚂𝚂𝙵𝚄𝙻𝙻𝚈 𝙳𝙴𝙻𝙴𝚃𝙴𝙳**')
        else:
            # files indexed before https://github.com/EvamariaTG/EvaMaria/commit/f3d2a1bcb155faf44178e5d7a685a1b533e714bf#diff-86b613edf1748372103e94cacff3b578b36b698ef9c16817bb98fe9ef22fb669R39 
            # have original file name.
            result = await Media.collection.delete_many({
                'file_name': media.file_name,
                'file_size': media.file_size,
                'mime_type': media.mime_type
            })
            if result.deleted_count:
                await msg.edit('**𝙵𝙸𝙻𝙴 𝚂𝚄𝙲𝙲𝙴𝚂𝚂𝙵𝚄𝙻𝙻𝚈 𝙳𝙴𝙻𝙴𝚃𝙴𝙳**')
            else:
                await msg.edit('File not found in database')


@Client.on_message(filters.command('deleteall') & filters.user(ADMINS))
async def delete_all_index(bot, message):
    await message.reply_text(
        '**𝚃𝙷𝙸𝚂 𝙿𝚁𝙾𝙲𝙴𝚂𝚂 𝚆𝙸𝙻𝙻 𝙳𝙴𝙻𝙴𝚃𝙴 𝙰𝙻𝙻 𝚃𝙷𝙴 𝙵𝙸𝙻𝙴𝚂 𝙵𝚁𝙾𝙼 𝚈𝙾𝚄𝚁 𝙳𝙰𝚃𝙰𝙱𝙰𝚂𝙴.\n𝙳𝙾 𝚈𝙾𝚄 𝚆𝙰𝙽𝚃 𝚃𝙾 𝙲𝙾𝙽𝚃𝙸𝙽𝚄𝙴 𝚃𝙷𝙸𝚂..??**',
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="⚡ 𝐘𝐞𝐬 ⚡", callback_data="autofilter_delete"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="❄ 𝐂𝐚𝐧𝐜𝐞𝐥 ❄", callback_data="close_data"
                    )
                ],
            ]
        ),
        quote=True,
    )


@Client.on_callback_query(filters.regex(r'^autofilter_delete'))
async def delete_all_index_confirm(bot, message):
    await Media.collection.drop()
    await message.answer('𝙿𝙻𝙴𝙰𝚂𝙴 𝚂𝙷𝙰𝚁𝙴 𝙰𝙽𝙳 𝚂𝚄𝙿𝙿𝙾𝚁𝚃')
    await message.message.edit('Succesfully Deleted All The Indexed Files.')


@Client.on_message(filters.command('settings') & filters.user(ADMINS))
async def settings(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"You are anonymous admin. Use /connect {message.chat.id} in PM")
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("Make sure I'm present in your group!!", quote=True)
                return
        else:
            await message.reply_text("I'm not connected to any groups!", quote=True)
            return

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if (
            st.status != enums.ChatMemberStatus.ADMINISTRATOR
            and st.status != enums.ChatMemberStatus.OWNER
            and str(userid) not in ADMINS
    ):
        return

    settings = await db.get_settings(grp_id)

    if settings is not None:
        buttons = [
            [
                InlineKeyboardButton(
                    '𝐅𝐈𝐋𝐓𝐄𝐑 𝐁𝐔𝐓𝐓𝐎𝐍',
                    callback_data=f'setgs#button#{settings["button"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '𝐒𝐈𝐍𝐆𝐋𝐄' if settings["button"] else '𝐃𝐎𝐔𝐁𝐋𝐄',
                    callback_data=f'setgs#button#{settings["button"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    '𝐁𝐎𝐓 𝐏𝐌',
                    callback_data=f'setgs#botpm#{settings["botpm"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ 𝐘𝐄𝐒' if settings["botpm"] else '❌ 𝐍𝐎',
                    callback_data=f'setgs#botpm#{settings["botpm"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    '𝐅𝐈𝐋𝐄 𝐒𝐄𝐂𝐔𝐑𝐄',
                    callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ 𝐘𝐄𝐒' if settings["file_secure"] else '❌ 𝐍𝐎',
                    callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    '𝐈𝐌𝐃𝐁',
                    callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ 𝐘𝐄𝐒' if settings["imdb"] else '❌ 𝐍𝐎',
                    callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    '𝐒𝐏𝐄𝐋𝐋 𝐂𝐇𝐄𝐂𝐊',
                    callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ 𝐘𝐄𝐒' if settings["spell_check"] else '❌ 𝐍𝐎',
                    callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    '𝐖𝐄𝐋𝐂𝐎𝐌𝐄',
                    callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ 𝐘𝐄𝐒' if settings["welcome"] else '❌ 𝐍𝐎',
                    callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',
                ),
            ],
        ]

        reply_markup = InlineKeyboardMarkup(buttons)

        await message.reply_text(
            text=f"<b>𝙲𝙷𝙰𝙽𝙶𝙴 𝚃𝙷𝙴 𝙱𝙾𝚃 𝚂𝙴𝚃𝚃𝙸𝙽𝙶𝚂 𝙵𝙾𝚁 {title}..⚙</b>",
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML,
            reply_to_message_id=message.id
        )



@Client.on_message(filters.command('set_template'))
async def save_template(client, message):
    sts = await message.reply("**𝙲𝙷𝙴𝙲𝙺𝙸𝙽𝙶 𝙽𝙴𝚆 𝚃𝙴𝙼𝙿𝙻𝙰𝚃𝙴**")
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"You are anonymous admin. Use /connect {message.chat.id} in PM")
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("Make sure I'm present in your group!!", quote=True)
                return
        else:
            await message.reply_text("I'm not connected to any groups!", quote=True)
            return

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if (
            st.status != enums.ChatMemberStatus.ADMINISTRATOR
            and st.status != enums.ChatMemberStatus.OWNER
            and str(userid) not in ADMINS
    ):
        return

    if len(message.command) < 2:
        return await sts.edit("No Input!!")
    template = message.text.split(" ", 1)[1]
    await save_group_settings(grp_id, 'template', template)
    await sts.edit(f"𝚂𝚄𝙲𝙲𝙴𝚂𝚂𝙵𝚄𝙻𝙻𝚈 𝚄𝙿𝙶𝚁𝙰𝙳𝙴𝙳 𝚈𝙾𝚄𝚁 𝚃𝙴𝙼𝙿𝙻𝙰𝚃𝙴 𝙵𝙾𝚁 {title} to\n\n{template}")

@Client.on_message(filters.command('shortlink'))
async def shortlink(bot, message):
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text("<b>You can't use this command in my private chat :(\n\nKindly use this command on groups !</b>")
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grp_id = message.chat.id
        title = message.chat.title
    else:
        return
    settings = await get_settings(grp_id)
    today = date.today()
    if 'sub_date' in settings.keys():
        sub_date = settings['sub_date']
    else:
        sub_date = 'Not Active'
    if 'exp_date' in settings.keys():
        exp_date = settings['exp_date']
        try:
            years, month, day = exp_date.split('-')
            comp = date(int(years), int(month), int(day))
            if comp<today:
                exp_date = 'Expired'
                await save_group_settings(grpid, 'plan_name', 'Expired')
                await save_group_settings(grpid, 'sub_date', 'Expired')
                await save_group_settings(grpid, 'exp_date', 'Expired')
                async for admin in bot.get_chat_members(chat_id=grpid, filter=enums.ChatMembersFilter.ADMINISTRATORS):
                    if not admin.user.is_bot:
                        await bot.send_message(
                            chat_id=admin.user.id,
                            text="<b>ATTENTION !\n\nThis is an important message, Your subscription has been ended and you have no longer access to link shortners. To continue your link shortners, Kindly renew your subscription ! please contact for subscription @Akash5213</b>",
                            disable_web_page_preview=True
                        )
                    else:
                        pass
        except ValueError:
            exp_date = 'Not Active'
    else:
        exp_date = 'Not Active'
    if 'plan_name' in settings.keys():
        plan = settings.get('plan_name')
    else:
        plan = 'Not Active'
    if exp_date == 'Not Active' or plan == 'Not Active':
        return await message.reply_text(f"<b>Hey {message.from_user.mention}, This bot is free to use you need to take access before connecting your shortlink . For life time free access send msg to admin @Akash5213!</b>")
    data = message.text
    userid = message.from_user.id
    user = await bot.get_chat_member(grp_id, userid)
    if user.status != enums.ChatMemberStatus.ADMINISTRATOR and user.status != enums.ChatMemberStatus.OWNER and str(userid) not in ADMINS:
        return await message.reply_text("<b>You dont have access to this command !</b>")
    try:
        command, shorlink_url, api = data.split(" ")
    except ValueError:
        return await message.reply_text(f"<b>Hey {message.from_user.mention}, Command Incomplete :(\n\nUse proper format !\n\nFormat:\n\n<code>/shortlink mdisk.link b6d97f6s96ds69d69d68d575d</code></b>")
    reply = await message.reply_text("<b>Please wait...</b>")
    await save_group_settings(grp_id, 'shortlink', shorlink_url)
    await save_group_settings(grp_id, 'shortlink_api', api)
    await reply.edit_text(f"<b>Successfully Added ShortLink API for {title}\n\nCurrent ShortLink Website : <code>{shorlink_url}</code>\nCurrent API : <code>{api}</code>.</b>")

@Client.on_message(filters.command("addplan") & filters.user(ADMINS))
async def plans(bot, message):
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    try:
        grpid = message.text.split(" ", 1)[1]
    except ValueError:
        return await message.reply_text(f"<b>Hey {message.from_user.mention}, Give me a group id along with the command !\n\nFormat:\n/addplan -1001.....</b>")
    settings = await get_settings(grpid)
    if 'sub_date' in settings.keys():
        sub_date = settings['sub_date']
    else:
        sub_date = 'Not Active'
    if 'exp_date' in settings.keys():
        exp_date = settings['exp_date']
        try:
            years, month, day = exp_date.split('-')
            comp = date(int(years), int(month), int(day))
            if comp<today:
                exp_date = 'Expired'
                await save_group_settings(grpid, 'plan_name', 'Expired')
                await save_group_settings(grpid, 'sub_date', 'Expired')
                await save_group_settings(grpid, 'exp_date', 'Expired')
                async for admin in bot.get_chat_members(chat_id=grpid, filter=enums.ChatMembersFilter.ADMINISTRATORS):
                    if not admin.user.is_bot:
                        await bot.send_message(
                            chat_id=admin.user.id,
                            text="<b>ATTENTION !\n\nThis is an important message, Your subscription has been ended and you have no longer access to link shortners. To continue your link shortners, Kindly renew your subscription ! please contact for subscription @Akash5213</b>",
                            disable_web_page_preview=True
                        )
                    else:
                        pass
        except ValueError:
            exp_date = 'Not Active'
    else:
        exp_date = 'Not Active'
    if 'plan_name' in settings.keys():
        plan = settings.get('plan_name')
    else:
        plan = 'Not Active'
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
    await message.reply_text(
        text=f"<b>Group ID: <code>{grpid}</code>\nCurrent Plan: <code>{plan}</code>\nSubscription Date: <code>{sub_date}</code>\nExpiry Date: <code>{exp_date}</code></b>",
        reply_markup=InlineKeyboardMarkup(btn)
    )

@Client.on_message(filters.command("myplan"))
async def showplan(bot, message):
    try:
        grpid = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text("<b>Give me a group id along with the command !\n\nFormat:\n/myplan -1001....</b>")
    settings = await get_settings(grpid)
    if 'plan_name' in settings.keys():
        plan = settings.get('plan_name')
    else:
        plan = 'Not Active'
    if 'sub_date' in settings.keys():
        sub_date = settings.get('sub_date')
    else:
        sub_date = 'Not Active'
    if 'exp_date' in settings.keys():
        exp_date = settings.get('exp_date')
    else:
        exp_date = 'Not Active'
    await message.reply_text(f"<b>Your Active Plan: <code>{plan}</code>\nSubscription Date: <code>{sub_date}</code>\nExpiry Date: <code>{exp_date}</code>\n\nFor Upgrading your plan, Contact @Akash5213</b>")

@Client.on_message(filters.command("plans"))
async def plans_available(bot, message):
    btn = [[
        InlineKeyboardButton("Contact Admin", url="t.me/Akash5213")
    ]]
    PLANS = """
    <b>For plan details, Contact @Akash5213 !
    
    All plans available at lower rates !
    
    <i>- 1 Day free trial
    - 1 Month paid plan
    - 3 Months paid plan
    - 6 Months paid plan</i></b>
    """
    await message.reply_text(
        text=PLANS,
        reply_markup=InlineKeyboardMarkup(btn)
    )

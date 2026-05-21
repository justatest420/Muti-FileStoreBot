#@cantarellabots

import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from utils.helpers import encode, send_main_log
#@cantarellabots
EXAMPLES = """Exᴀᴍᴘʟᴇs: 
<blockquote expandable><code>LINK = 8 LINK = 4 LINK = 5</code>

<code>360P = 2, 480P = 2, 720P = 2
1080P = 2, HDRIP = 1, 4K = 1</code>

<code>360P = 1, 480P = 1, 720P = 1
1080P = 1</code>

<code>360P = 1, 480P = 1, 720P = 1
1080P = 1, HDRIP = 1, 4K = 1</code>  

<code>480P = 2, 720P = 2, 1080P = 2 
HDRIP = 1, 4K = 1</code></blockquote>"""

FORMAT_TXT = """<b>🔗 𝗙𝗢𝗥𝗠𝗔𝗧𝗘𝗗 𝗟𝗜𝗡𝗞 :

◈ Cᴜʀʀᴇɴᴛ Fᴏʀᴍᴀᴛ
<blockquote><code>{}</code></blockquote></b>"""

NONE_TXT = "--- Nᴏɴᴇ ---"

FORMAT_MARKUP = InlineKeyboardMarkup([
    [InlineKeyboardButton('🔗 sᴇᴛ ғᴏʀᴍᴀᴛ', 'flink:change_format')],
    [InlineKeyboardButton('⚡️ sᴛᴀʀᴛ ᴘʀᴏᴄᴇss', 'flink:start')],
    [
        InlineKeyboardButton('🔄', 'flink:status'),
        InlineKeyboardButton("✖️", 'close')
    ]
])
TRY_AGAIN_MARKUP = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("⬅️", "flink:status"), 
        InlineKeyboardButton("♻️", "flink:change_format"), 
        InlineKeyboardButton("✖️", "close")
    ]
])
#@cantarellabots
CLOSE_MARKUP = InlineKeyboardMarkup([[InlineKeyboardButton("Cʟᴏsᴇ ✖️", callback_data='close')]])
CANCEL_MARKUP = InlineKeyboardMarkup([[InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data='flink:cancel')]])

#@cantarellabots
def make_inline_button(text: str) -> InlineKeyboardMarkup:
    inline_buttons = []
    button_lines = text.splitlines()

    for line in button_lines:
        tmp_buttons = []
        buttons_nums = line.split(' | ')

        for button in buttons_nums:
            try:
                button_txt, button_link = button.split(' - ')
            except Exception:
                return None

            tmp_buttons.append(InlineKeyboardButton(text=button_txt, url=button_link))

        inline_buttons.append(tmp_buttons)

    return InlineKeyboardMarkup(inline_buttons)

#@cantarellabots
def setup_flink(app: Client, worker_db, log_channel_id: int, is_admin_func):
    """Binds flink handlers to the given app instance."""
    
    # Store formats and pending input futures per user
    format_data = {}
    _waiting = {}  # user_id -> asyncio.Future

    async def wait_for_input(user_id: int, timeout: int = 300) -> Message | None:
        """Wait for the next text/forwarded message from this user."""
        future = asyncio.get_event_loop().create_future()
        _waiting[user_id] = future
        try:
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            return None
        finally:
            _waiting.pop(user_id, None)

    # Handler to catch text input when we're waiting for it
    @app.on_message(filters.private & (filters.text | filters.forwarded), group=1)
    async def flink_input_catcher(client: Client, message: Message):
        user_id = message.from_user.id
        if user_id in _waiting and not _waiting[user_id].done():
            _waiting[user_id].set_result(message)
            message.stop_propagation()

    async def get_flink_status(user_id: int, text: str | None = None):
        TEXT = text or format_data.get(user_id, NONE_TXT)
        MARKUP = FORMAT_MARKUP
        return FORMAT_TXT.format(TEXT), MARKUP

    async def change_flink_format(client: Client, query: CallbackQuery):
        user_id = query.from_user.id
        message = query.message
        
        await message.edit(f'<b>Sᴇɴᴅ ʟɪɴᴋ ғᴏʀᴍᴀᴛ: Qᴜᴀʟɪᴛʏ ᴡɪᴛʜ ʀᴇsᴘᴇᴄᴛɪᴠᴇ ᴛᴏ ᴍᴇssᴀɢᴇ ʟᴇɴɢᴛʜ\n\n{EXAMPLES}</b>',
                           reply_markup=CANCEL_MARKUP)

        rcv_msg = await wait_for_input(user_id)

        if rcv_msg is None:
            await message.edit("<b><i>🆑 Oᴘᴇʀᴀᴛɪᴏɴ Tɪᴍᴇᴅ Oᴜᴛ...</i></b>", reply_markup=TRY_AGAIN_MARKUP)
            return

        text = rcv_msg.text or ""

        if text.upper() == 'CANCEL':
            try:
                await rcv_msg.delete()
            except Exception:
                pass
            await message.edit("<b><i>🆑 Oᴘᴇʀᴀᴛɪᴏɴ Cᴀɴᴄᴇʟʟᴇᴅ...</i></b>", reply_markup=TRY_AGAIN_MARKUP)
            return

        try:
            for line in text.splitlines():
                msg_txt_and_lengths = line.split(',')
                for msg_data in msg_txt_and_lengths:
                    msg_txt, start_with_msg_len = msg_data.strip().split(' = ')
                    if ':' in start_with_msg_len:
                        start, msg_len = start_with_msg_len.split(':')
                        start, msg_len = int(start), int(msg_len)
                    else:
                        msg_len = int(start_with_msg_len)
        except Exception:
            await message.edit(
                f"<b>⚠️ Iɴᴠᴀʟɪᴅ Fᴏʀᴍᴀᴛ, ғᴏʟʟᴏᴡ ʙᴇʟᴏᴡ\n\n{EXAMPLES}</b>",
                reply_markup=TRY_AGAIN_MARKUP,
            )
            try:
                await rcv_msg.delete()
            except Exception:
                pass
            return
            
        format_data[user_id] = text
        try:
            await rcv_msg.delete()
        except Exception:
            pass
        TEXT, MARKUP = await get_flink_status(user_id, text=text)
        await message.edit(TEXT, reply_markup=MARKUP)

    async def start_flink_process(client: Client, query: CallbackQuery):    
        user_id = query.from_user.id

        link_formats = format_data.get(user_id)
        if not link_formats:
            return await query.answer('⚠️ Fɪʀsᴛ sᴇᴛ ᴛʜᴇ ʟɪɴᴋ ғᴏʀᴍᴀᴛ', show_alert=True)
        
        await query.answer("♻️ Qᴜᴇʀʏ Pʀᴏᴄᴇssɪɴɢ....") 
            
        channel = f"<b>DB Channel</b>"

        while True:
            await query.message.edit_text(
                f"<b><blockquote>Fᴏʀᴡᴀʀᴅ ᴛʜᴇ Mᴇssᴀɢᴇ ғʀᴏᴍ {channel} (ᴡɪᴛʜ ǫᴜᴏᴛᴇs)..</blockquote>\n"
                f"<blockquote>Oʀ Sᴇɴᴅ ᴛʜᴇ {channel} Pᴏsᴛ Lɪɴᴋ</blockquote></b>",
                reply_markup=CANCEL_MARKUP,
                disable_web_page_preview=True,
            )

            channel_message = await wait_for_input(user_id)

            if channel_message is None:
                await query.message.edit_text(
                    "<b><i>🆑 Oᴘᴇʀᴀᴛɪᴏɴ Tɪᴍᴇᴅ Oᴜᴛ...</i></b>",
                    reply_markup=TRY_AGAIN_MARKUP,
                )
                return

            if channel_message.text and channel_message.text.upper() == 'CANCEL':
                try:
                    await channel_message.delete()
                except Exception:
                    pass
                await query.message.edit_text(
                    "<b><i>🆑 Oᴘᴇʀᴀᴛɪᴏɴ Cᴀɴᴄᴇʟʟᴇᴅ...</i></b>",
                    reply_markup=TRY_AGAIN_MARKUP,
                )
                return

            from utils.helpers import get_message_id
            msg_id = await get_message_id(client, channel_message, log_channel_id)

            if msg_id:
                break
            else:
                await channel_message.reply(
                    f"<b>❌ Eʀʀᴏʀ..\n<blockquote>Tʜɪs Fᴏʀᴡᴀʀᴅᴇᴅ ᴘᴏsᴛ ᴏʀ ᴍᴇssᴀɢᴇ ʟɪɴᴋ ɪs ɴᴏᴛ ғʀᴏᴍ ᴍʏ {channel}</blockquote></b>", 
                    quote=True, 
                    reply_markup=CLOSE_MARKUP,
                    disable_web_page_preview=True,
                )
                continue

        format_lines = link_formats.splitlines()
        output_txt = []
        me = await client.get_me()

        for line in format_lines:
            msg_txt_and_lengths = line.split(',')
            tmp_list = []

            for msg_data in msg_txt_and_lengths:
                msg_txt, start_with_msg_len = msg_data.strip().split(' = ')

                if ':' in start_with_msg_len:
                    start, msg_len = start_with_msg_len.split(':')
                    start, msg_len = int(start), int(msg_len)
                else:
                    start = 0
                    msg_len = int(start_with_msg_len)

                if msg_len == 1:
                    msg_id += start 
                    msg = f'get-{msg_id * abs(log_channel_id)}'
                    msg_id += 1
                    
                else:
                    msg_id += start
                    first_msg = f'{msg_id * abs(log_channel_id)}'
                    msg_id += (msg_len-1)
                    last_msg = f'{msg_id * abs(log_channel_id)}'
                    msg_id += 1
                    msg = f'get-{first_msg}-{last_msg}'
                    
                encoded_msg = await encode(msg)
                msg_link = f"https://t.me/{me.username}?start={encoded_msg}"

                tmp_list.append(f'{msg_txt} - {msg_link}')

            output_txt.append(" | ".join(tmp_list))

        final_message = '\n'.join(output_txt)
        inline_buttons = make_inline_button(final_message)
        await channel_message.reply(
            text=f'<b>⬇️ Bᴇʟᴏᴡ ɪs ᴛʜᴇ ғᴏʀᴍᴀᴛᴇᴅ ʟɪɴᴋ::\n\n<blockquote><code>{final_message}</code></blockquote></b>',
            reply_markup=inline_buttons,
            quote=True,
            disable_web_page_preview=True,
        )

        # Log to main log channel
        log_msg = (
            f"<b>🔗 Fᴏʀᴍᴀᴛᴛᴇᴅ Lɪɴᴋ Gᴇɴᴇʀᴀᴛᴇᴅ</b>\n\n"
            f"<b>• Bᴏᴛ:</b> @{me.username}\n"
            f"<b>• Bᴏᴛ ID:</b> <code>{me.id}</code>\n"
            f"<b>• Oᴡɴᴇʀ:</b> <code>{user_id}</code>\n"
            f"<b>• Lᴏɢ Cʜᴀɴɴᴇʟ:</b> <code>{log_channel_id}</code>\n"
            f"<b>• Mᴇᴛʜᴏᴅ:</b> <code>/flink</code>"
        )
        await send_main_log(client, log_msg)

    @app.on_message(filters.command('flink') & filters.private)
    async def handle_formated_link(client: Client, message: Message):
        if not await is_admin_func(message.from_user.id):
            return
        wait_msg = await message.reply("<b><i>Pʀᴏᴄᴇssɪɴɢ....</i></b>", quote=True)
        try:
            TEXT, MARKUP = await get_flink_status(message.from_user.id)
        except Exception as e:
            TEXT, MARKUP = f"<b>❌ Eʀʀᴏʀ ❌</b>\n<blockquote><i>{e}</i></blockquote>", CLOSE_MARKUP
        await wait_msg.edit(TEXT, reply_markup=MARKUP)

    @app.on_callback_query(filters.regex(r"^flink:(status|change_format|start|cancel)$"))
    async def format_message_cb(client: Client, query: CallbackQuery):
        if not await is_admin_func(query.from_user.id):
            return
        
        cb_data = query.data.split(":")[1]
        if cb_data == 'status':
            await query.message.edit_text("<b><i>🔄 Rᴇғʀᴇsʜɪɴɢ....</i></b>")
            TEXT, MARKUP = await get_flink_status(query.from_user.id)
            await query.message.edit_text(TEXT, reply_markup=MARKUP)
        elif cb_data == 'change_format':
            await change_flink_format(client, query)
        elif cb_data == 'start':
            await start_flink_process(client, query)
        elif cb_data == 'cancel':
            # Cancel any pending wait
            user_id = query.from_user.id
            if user_id in _waiting and not _waiting[user_id].done():
                _waiting[user_id].set_result(None)
            await query.message.edit_text(
                "<b><i>🆑 Oᴘᴇʀᴀᴛɪᴏɴ Cᴀɴᴄᴇʟʟᴇᴅ...</i></b>",
                reply_markup=TRY_AGAIN_MARKUP,
            )
            await query.answer()

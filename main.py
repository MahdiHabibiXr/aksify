from pyrogram import Client, filters
from PIL import Image 
import os
from pyrogram.types import ReplyKeyboardMarkup as Markup
import requests
from io import BytesIO
from pyrogram.types import (InlineKeyboardMarkup, InlineKeyboardButton)
import models

bot = Client('aksify',api_id=863373,api_hash='c9f8495ddd20615835d3fd073233a3f6')

inp_dir = 'inputs/'
out_dir = 'outputs/'
users_dir = f'files/users/'
links = ["@studAIo_styles", "@aiticle"]


def user_exists(user_id):
    user_path = f'{users_dir}{user_id}'
    
    return os.path.isdir(user_path)
    
def add_user(user_id):
    user_path = f'{users_dir}{user_id}'

    os.makedirs(user_path, exist_ok=True) #user root
    os.makedirs(f'{user_path}/inputs', exist_ok=True) #inputs user
    os.makedirs(f'{user_path}/outputs', exist_ok=True) #outputs user
    os.makedirs(f'{user_path}/refs', exist_ok=True) #refs user

def in_progress(user_id):
    task_path = f"files/tasks/{user_id}.txt"

    return os.path.exists(task_path)

def add_task(user_id, task_id):
    task_path = f'{users_dir}tasks/{user_id}.txt'

    with open(task_path, "w") as file:
        file.write(f'{user_id}\n')      #user_id
        file.write(f'{task_id}\n')      #task_id

async def is_joined(app , user_id):
    not_joined = []
    for channel in links:
        try:
            await app.get_chat_member(channel , user_id)
        except:
            not_joined.append(channel)
    return not_joined

@bot.on_message(filters.command('test') & filters.private)
async def test_bot(client, message):
    await message.reply('im upppp')

@bot.on_message(filters.command("start"))
async def start_text(client, message):
    not_joined_channels = await is_joined(bot , message.from_user.id)
    t_id = message.chat.id

    #TODO: Check if its invited and add it to db

    #check if user exists
    if(not user_exists(t_id)):
        add_user(t_id)

    if not_joined_channels:
        await message.reply("🌹سلام دوست عزیز به این ربات خوش اومدی\n👈به کمک این ربات میتونی با هوش‌مصنوعی، عکسهات رو بازسازی کنی\n\nلطفا برای فعالسازی ربات، اول در این کانالها جوین شو و بعدش دوباره روی /start کلیک کن"
                            +'\n\n' + links[0] + '    ' + links[1])
    else:        
        await message.reply("😍تبریک میگم، حالا میتونی از قابلیت‌های ربات استفاده کنی، اول عکسی که میخوای به هوش‌مصنوعی بدی رو آپلود کن :")

@bot.on_message(filters.private & filters.photo)
async def image(client, message):
    
    img_id = message.photo.file_id
    chat_id = message.chat.id
    input_img_path = f'{users_dir}{chat_id}/{inp_dir}{chat_id}.jpg' #TODO: naming to save several files
    
    if(not in_progress(chat_id)): #check if in progress
        file = await client.download_media(img_id, file_name = input_img_path)

        #add file to db as latest image address
        caption = "🖼عکس ورودی شما ثبت شد، لطفا از دکمه‌های زیر یک گزینه رو انتخاب کنید :"
        markup = InlineKeyboardMarkup(
            [
                # [  # First row
                #     InlineKeyboardButton(  # Generates a callback query when pressed
                #         "🔄 افزایش کیفیت",
                #         callback_data="upscale"
                #     ),
                # ],
                [  # Second row
                    InlineKeyboardButton(  # Generates a callback query when pressed
                        "🤖بازسازی با هوش‌مصنوعی",
                        callback_data="creative_upscale"
                    ),
                ]
            ]
        )
        await client.send_photo(chat_id, img_id, reply_markup = markup, caption = caption)

    else:
        await client.send_message(chat_id, 'شما یک درخواست در حال انجام دارید، تا پایان درخواست قبلی، نمی‌توانید درخواست جدیدی ثبت کنید.\nلطفا کمی منتظر باشید🙏')

@bot.on_callback_query()
async def callbacks(client, callback_query):
    message = callback_query.message
    data = callback_query.data
    chat_id = callback_query.from_user.id
    photo = f'{inp_dir}{chat_id}.jpg'

    await message.delete()

    if(os.path.exists(photo)):
        if(data == 'creative_upscale'):
            await callback_query.answer("✅درخواست شما ثبت شد", show_alert = False)
        
            task = models.create_face_to_many(photo, '3D')
            add_task(chat_id, task.id)

            await message.reply("✅درخواست شما در صف پردازش قرار گرفت، لطفا کمی شکیبا باشید.")
            
    else:
        await client.send_message(chat_id, 'لطفا اول یک عکس آپلود کنید')


bot.run()


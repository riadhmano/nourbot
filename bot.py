import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, BufferedInputFile, InputMediaPhoto
from PIL import Image, ImageDraw, ImageFont
import io
import asyncio
import os  # لإضافة دعم المتغيرات البيئية

TOKEN = "7841909549:AAE-IP8TXNsmHVZmuXBjb6CEiMvxaljJNz8"

# إعدادات البوت
bot = Bot(token=TOKEN)
dp = Dispatcher()

# تخزين الصور لكل مستخدم
user_images = {}
# تخزين القناة التي يريد المستخدم النشر فيها
user_channels = {}

# تحديد المنفذ
PORT = os.getenv('PORT', 5000)  # جلب المنفذ من البيئة إذا كان موجودًا، أو استخدام 5000 كإفتراضي

# استقبال الصور من المستخدم
@dp.message(lambda message: message.photo)
async def handle_photo(message: Message):
    user_id = message.from_user.id

    if user_id not in user_images:
        user_images[user_id] = []

    # تنزيل الصورة وإضافتها للقاموس
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    downloaded_file = await bot.download_file(file.file_path)

    if downloaded_file not in user_images[user_id]:
        user_images[user_id].append(downloaded_file)

    await message.answer(f"✅ تم استلام {len(user_images[user_id])} صورة! الآن، أرسل لي النص الذي تريد إضافته على جميع الصور.")

# استقبال النص وإضافته على جميع الصور دفعة واحدة
@dp.message(lambda message: message.text and not message.text.startswith("@"))
async def handle_text(message: Message):
    user_id = message.from_user.id

    if user_id not in user_images or not user_images[user_id]:
        await message.answer("⚠️ لم ترسل أي صور بعد! الرجاء إرسال صور أولاً.")
        return

    text = message.text
    font_size = 100
    font_path = "arial.ttf"
    font = ImageFont.truetype(font_path, font_size)

    max_width = max(Image.open(img).size[0] for img in user_images[user_id])

    while True:
        test_font = ImageFont.truetype(font_path, font_size)
        test_img = Image.new("RGB", (max_width, 200))
        test_draw = ImageDraw.Draw(test_img)
        text_width, text_height = test_draw.textbbox((0, 0), text, font=test_font)[2:]

        if text_width < max_width * 0.7:
            font = test_font
            break
        font_size -= 2  

    modified_images = []

    for image_path in user_images[user_id]:
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)

        image_width, image_height = image.size
        text_x = (image_width - text_width) // 2
        text_y = image_height - text_height - 90

        draw.text((text_x, text_y), text, font=font, fill="white", stroke_width=5, stroke_fill="black")

        img_io = io.BytesIO()
        image.save(img_io, format="PNG")
        img_io.seek(0)

        modified_images.append(BufferedInputFile(img_io.getvalue(), filename="edited_image.png"))

    # حفظ الصور المعدلة للمستخدم حتى يحدد القناة
    user_images[user_id] = modified_images

    await message.answer("✅ تم تعديل الصور! الآن، أرسل اسم القناة مثل: `@channel_username` لنشر الصور.")

# استقبال اسم القناة ونشر الصور إليها
@dp.message(lambda message: message.text.startswith("@"))
async def handle_channel_name(message: Message):
    user_id = message.from_user.id
    channel_username = message.text.strip()

    if user_id not in user_images or not user_images[user_id]:
        await message.answer("⚠️ لم ترسل أي صور بعد! الرجاء إرسال الصور أولاً.")
        return

    # تخزين القناة للمستخدم
    user_channels[user_id] = channel_username
    await message.answer(f"📢 سيتم نشر الصور إلى القناة: {channel_username}")

    # تجهيز الصور المعدلة
    media_group = [InputMediaPhoto(media=photo) for photo in user_images[user_id]]

    # نشر الصور إلى القناة
    try:
        await bot.send_media_group(chat_id=channel_username, media=media_group)
        await message.answer("✅ تم نشر الصور بنجاح!")
    except Exception as e:
        await message.answer(f"⚠️ حدث خطأ أثناء النشر: {e}")

    # مسح الصور بعد النشر
    del user_images[user_id]
    del user_channels[user_id]

# تشغيل البوت
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

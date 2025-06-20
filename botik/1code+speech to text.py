import telebot
import google.generativeai as genai
import config
import speech_recognition as sr
from pydub import AudioSegment
import os


genai.configure(api_key=config.GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-2.0-flash-lite")
bot = telebot.TeleBot(config.TELEGRAM_BOT_TOKEN)

def ogg2wav(ofn):
    wfn = ofn.replace('.ogg', '.wav')
    segment = AudioSegment.from_file(ofn)
    segment.export(wfn, format='wav')
    return wfn


def speech_to_text(filename='voice.ogg'):
    wav_file = ogg2wav(filename)
    r = sr.Recognizer()
    with sr.AudioFile(wav_file) as source:
        audio = r.record(source)
        text = r.recognize_google(audio, language='uk-UA')
        return text


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🎙️ Found a voice notification or text, and I'll let you know through!")


@bot.message_handler(content_types=['text'])
def handle_text(message):
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"❌ Mistakes: {e}")


@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    try:

        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)


        with open("voice.ogg", 'wb') as f:
            f.write(downloaded_file)


        user_text = speech_to_text("voice.ogg")


        response = model.generate_content(user_text)
        bot.reply_to(message, f"🗣 You told: {user_text}\n🤖 Rejoin: {response.text}")


        os.remove("voice.ogg")
        os.remove("voice.wav")

    except Exception as e:
        bot.reply_to(message, f"❌  {e}")

bot.remove_webhook()
bot.infinity_polling()
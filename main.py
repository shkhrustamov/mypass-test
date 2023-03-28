from datetime import datetime
from random import randint
from string import printable

from aiogram import Bot, Dispatcher, executor, types

from database_class import Database
from wordlist import wordlist
import telepot
import urllib3

proxy_url = "http://proxy.server:3128"
telepot.api._pools = {
    'default': urllib3.ProxyManager(proxy_url=proxy_url, num_pools=3, maxsize=10, retries=False, timeout=30),
}
telepot.api._onetime_pool_spec = (urllib3.ProxyManager, dict(proxy_url=proxy_url, num_pools=1, maxsize=1, retries=False, timeout=30))

printable = printable[0:-9]
printable.replace(" ", '')

MIN = 0
MAX = len(printable) - 1
API_TOKEN = '5811802409:AAEBh3qKPo-uUENYw-o-5GlnnUvYYhHVyY4'


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
db = Database()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    check = db.insert_user(message["from"]["id"], message["from"]["first_name"])
    start_message = f"""
Welcome {message["from"]["first_name"]} to your password assistant 😌

Have a Blessed Ramadan Kareem 🌙

Press /help to see command list 👇🏻
"""

    await message.reply(start_message)


@dp.message_handler(commands=['help'])
async def echo(message: types.Message):

    db.insert_user(message["from"]["id"], message["from"]["first_name"])

    help_message = """
/start to see the welcome message.
/gen to generate password.

‼️Passwords generated using /gen command are very strong 🔐, but are not easy to remember. 

/phrase to generate word-length pass-phrase 🔤

example: 

/phrase 4
/phrase 8
/phrase 12
/phrase 20

BETA FEATURES :

/save: to save any notes or passwords

‼️All the saved notes are encrypted and no one without a valid decryption key can read the notes, keys are unique to each user 🔑.

example:

/save I need to meet a friend @12:30 pm today!
/save My Facebook pass is FaCeBoOkPaSsWoRd

/get: to retrive or get all saved notes

/stat: to see your statistics
/gstat: to see global statistics

/dev: to see info about this bot's developer

🚨 WE RECOMMEND TO SAVE GENERATED PASSWORDS ALSO IN OTHER SAFER PLACE, SINCE YOU RUNNING BETA VERSION OF BOT, IT CAN BREAK DOWN ANY TIME )
    """

    await message.reply(help_message)


@dp.message_handler(commands=['gen'])
async def gen(message: types.Message):

    length = message.text.replace("/gen", '').strip()

    try:
        if len(length) == 0:
            length = 16
        else:
            length = int(length)

        if 4 <= length <= 256:

            passwords = ""
            for _ in range(5):
                passwords += "\n\n" + (generate(length))

            db.increase_password_count(message["from"]["id"], 5)
            msg = f"""Your generated strong 🔐 passwords are:
{passwords[1:]}
                """
            await message.reply(msg)
        elif length <= 3:
                await message.reply("Too short... 🤏")
        elif length > 256:
                await message.reply("Too long... 🤥")
    except:
        await message.reply("Please send a number! 🔢")


@dp.message_handler(commands=['phrase'])
async def phrase(message: types.Message):

    length = message.text.replace('/phrase', '').strip().replace(" ", '')

    try:
        if len(length) == 0:
            length = 8
        
        try:

            if length != 8:
    
                length = int(length)
            if 4 <= length <= 100:

                phrases = ""

                for _ in range(5):
                    phrase = ""
                    for _ in range(length):

                        phrase += " " + wordlist[randint(0,len(wordlist)-1)]

                    phrases += "\n\n" + phrase
                msg = f"""Your generated pass phrases 👍 are:
{phrases[1:]}
                """
                db.increase_passphrase_count(message["from"]["id"], 5)
                await message.reply(msg)

            elif length <= 3:
                await message.reply("Too short... 🤏")

            elif length > 100:
                await message.reply("Too long... 🤥")
    
        except:
            await message.reply("Please provide a number! 🔢")
    
    except Exception as e:
        await message.reply("Please provide a valid command! 📔")


@dp.message_handler(commands=['stats', 'stat', 'statistics'])
async def user_stat(message):

    stats = db.user_stat(message["from"]["id"])
    passwords_generated = stats[0]
    passphrases_generated = stats[1]
    msg = f"You have generated {passwords_generated} strong 🔐 passwords and {passphrases_generated} easy to remember passphrases."
    
    del stats
    del passphrases_generated
    del passwords_generated

    await message.reply(msg)


@dp.message_handler(commands=['gstats', 'gstat', 'gstatistics'])
async def global_stat(message):

    stats = db.global_stat()
    passwords_generated = stats[0]
    passphrases_generated = stats[1]

    msg = f"Users have generated {passwords_generated} strong passwords 🔐 and {passphrases_generated} 🔐 easy to remember passphrases."
    
    del stats
    del passphrases_generated
    del passwords_generated
    
    await message.reply(msg)


@dp.message_handler(commands=['dev', 'developer', 'builder'])
async def dev(message):
    msg = f"""Yoo! {message["from"]["first_name"]} 👋🏻.
Report bug or Errors: @shkhrustamov.
    """
    await message.reply(msg)


@dp.message_handler(commands=['save'])
async def save_notes(message):
    msg = message["text"].replace('/save', '', 1).strip()
    if len(msg) > 0:
        msg = encryption(message["from"]["id"]).encrypt_data(msg)

        db.save_notes(message["from"]["id"], msg, datetime.now().strftime("%y-%m-%d %H:%M:%S"))
        await message.reply("Saved 👍")
    else:
        await message.reply("SEND SOMETHING TO SAVE! 😕")


@dp.message_handler(commands=['get'])
async def get_saved_notes(message):
    
    data = db.get_notes(message["from"]["id"])

    if len(data) > 0:
        msg = '''Your saved notes 📋 are:'''
        enc = encryption(message["from"]["id"])
        for i in data:
            msg += "\n\n" + enc.decrypt_data(i[0])
        await message.reply(msg)
        del enc
    else:
        await message.reply("YOU HAVE NOT SAVED ANYTHING YET! 😕")


@dp.message_handler()
async def same_reply(message):
    db.insert_user(message["from"]["id"], message["from"]["first_name"])
    await message.reply(f"HEY {message['from']['username']}!\nDO YOU MIND SENDING SOMETHING MEANINGFUL! 😅")


def generate(length):
    password = ""
    for _ in range(length):
        password += printable[randint(MIN, MAX)]
    return password


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

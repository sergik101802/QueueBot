from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, ContextTypes, \
    CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import logging

# посилання на бота: https://t.me/QueueTM_bot
# https://core.telegram.org/bots/api Telegram Bot API


# логер, виводить повідомлення на консоль, з якої запускаєься бот
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
NAME = range(1)

buttons = [  # створюємо кнопочки, на які будемо нажимать (циклом не виходило ініціалізувать buttons,
    # нічого просто потім не надсилається)
    [InlineKeyboardButton("1", callback_data="1"), InlineKeyboardButton("2", callback_data="2"),
     InlineKeyboardButton("3", callback_data="3"), InlineKeyboardButton("4", callback_data="4")],
    [InlineKeyboardButton("5", callback_data="5"), InlineKeyboardButton("6", callback_data="6"),
     InlineKeyboardButton("7", callback_data="7"), InlineKeyboardButton("8", callback_data="8")],
    [InlineKeyboardButton("9", callback_data="9"), InlineKeyboardButton("10", callback_data="10"),
     InlineKeyboardButton("11", callback_data="11"), InlineKeyboardButton("12", callback_data="12")],
    [InlineKeyboardButton("13", callback_data="13"), InlineKeyboardButton("14", callback_data="14"),
     InlineKeyboardButton("15", callback_data="15"), InlineKeyboardButton("16", callback_data="16")],
    [InlineKeyboardButton("17", callback_data="17"), InlineKeyboardButton("18", callback_data="18"),
     InlineKeyboardButton("19", callback_data="19"), InlineKeyboardButton("20", callback_data="20")],
    [InlineKeyboardButton("21", callback_data="21"), InlineKeyboardButton("22", callback_data="22"),
     InlineKeyboardButton("23", callback_data="23"), InlineKeyboardButton("24", callback_data="24")],
    [InlineKeyboardButton("25", callback_data="25"), InlineKeyboardButton("26", callback_data="26"),
     InlineKeyboardButton("27", callback_data="27"), InlineKeyboardButton("28", callback_data="28")],
    [InlineKeyboardButton("29", callback_data="29"), InlineKeyboardButton("30", callback_data="30")]
]
# https://core.telegram.org/bots/api#inlinekeyboardmarkup

keyboard = InlineKeyboardMarkup(buttons)  # засовуємо наші кнопочки в єдину клавіатуру


# опис команди /start
def start(update, context):
    update.message.reply_text('Привіт!\nЯ допоможу тобі створити чергу.\nРозпочни командою /startqueue')


# повідомлення про помилки, виводиться в консоль
def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


# опис команди /startqueue, головна команда бота
def startqueue(update, context):
    update.message.reply_text("Введіть ім'я черги")
    return NAME  # Повертаємо лейбл(?) NAME, переходимо до наступного етану ConversationHandler'a


def namequeue(update, context):  # вивід черги
    name = update.message.text + '\n\n'  # записуємо введену назву черги в змінну
    queue = ""
    for i in range(1, 31):
        queue += str(i) + '.\n'  # створюємо список (1.\n2.\n)

    update.message.reply_text(name + queue, reply_markup=keyboard)  # надсилаємо повідомлення: назва черги, список та
    # клавіатуру
    # update.message.reply_text(update.message.from_user.first_name+' '+update.message.from_user.last_name)
    return ConversationHandler.END  # повертаємо кінець діалогу


def cancel(update, context):  # відміна черги (не працює, хоча по-ідеї завершує діалог)
    update.message.reply_text('Чергу відмінено!')
    return ConversationHandler.END


def keyboard_callback(update, context):
    query = update.callback_query
    query.edit_message_text(text=update.callback_query.message.text+"Selected option: {}".format(query.data), reply_markup=keyboard)


def main():
    updater = Updater("5119453197:AAHpO7pymF2BQkevcFg6r0r4zZQcKU7iRfY", use_context=True)  # API token бота
    dp = updater.dispatcher  # якась важна штука

    dp.add_handler(CommandHandler("start", start))  # прив'язка команди до бота (start)
    dp.add_handler(CommandHandler("cancel", cancel))  # прив'язка команди до бота (cancel)

    conv_handler = ConversationHandler(  # ініціацізація розмови
        entry_points=[CommandHandler("startqueue", startqueue)],  # точка входу (запускається після
        # команди /startqueue), викликає startqueue(), по сумісності прив'язка команди до бота
        states={

            NAME: [MessageHandler(Filters.text & ~Filters.command, namequeue)],  # один (поки що єдиний) етап
            # діалогу, бот просить ім'я черги. Після цього виклакається ф-ція namequeue
        },
        fallbacks=[CommandHandler('cancel', cancel)],  # відміна черги
    )

    dp.add_handler(conv_handler)  # прив'язка діалогу
    dp.add_handler(CallbackQueryHandler(keyboard_callback))
    dp.add_error_handler(error)  # прив'язка виведення помилок

    updater.start_polling()
    updater.idle()  # по-моєму цикл життя (верхнє теж), держить бота увімкненим, краще не чіпати


if __name__ == '__main__':  # запускач
    main()

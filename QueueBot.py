import telegram
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    ContextTypes,
    CallbackQueryHandler,
)

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import logging

# посилання на бота: https://t.me/QueueTM_bot
# https://core.telegram.org/bots/api Telegram Bot API


# логер, виводить повідомлення на консоль, з якої запускаєься бот
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)
NAME = range(1)

count = 28
number = count // 4 if count % 4 == 0 else count // 4 + 1
buttons = [
    [
        InlineKeyboardButton(f"{j + 1}", callback_data=f"{j + 1}")
        for j in range(i * 4, i * 4 + count % 4 if i * 4 + 4 > count else i * 4 + 4)
    ]
    for i in range(number)
]
buttons.append([InlineKeyboardButton("Cancel", callback_data="cancel")])

# https://core.telegram.org/bots/api#inlinekeyboardmarkup

keyboard = InlineKeyboardMarkup(buttons)  # засовуємо наші кнопочки в єдину клавіатуру


# опис команди /start
def start(update, context):
    update.message.reply_text(
        "Привіт!\nЯ допоможу тобі створити чергу.\nРозпочни командою /startqueue"
    )


# повідомлення про помилки, виводиться в консоль
def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


# опис команди /startqueue, головна команда бота
def startqueue(update, context):
    update.message.reply_text("Введіть ім'я черги")
    return NAME  # Повертаємо лейбл(?) NAME, переходимо до наступного етану ConversationHandler'a


def namequeue(update, context):  # вивід черги
    name = update.message.text + "\n\n"  # записуємо введену назву черги в змінну
    queue = ""
    for i in range(1, 31):
        queue += str(i) + ".\n"  # створюємо список (1.\n2.\n)

    update.message.reply_text(
        name + queue, reply_markup=keyboard
    )  # надсилаємо повідомлення: назва черги, список та
    # клавіатуру
    # update.message.reply_text(update.message.from_user.first_name+' '+update.message.from_user.last_name)
    return ConversationHandler.END  # повертаємо кінець діалогу


def cancel(update, context):  # відміна черги (не працює, хоча по-ідеї завершує діалог)
    update.message.reply_text("Чергу відмінено!")
    return ConversationHandler.END


def keyboard_callback(update, context):
    #  якщо не знайдено у списку і НЕ cancel
    if str(update.callback_query.message.text).find(str(update.callback_query.from_user.first_name) + " " +
                                                    str(update.callback_query.from_user.last_name)) == -1 and str(update.callback_query.data) != 'cancel':
        for i in range(0, len(buttons) - 1):
            for j in range(0, len(buttons[i])):
                if (buttons[i][j] == InlineKeyboardButton(update.callback_query.data,
                                                          callback_data=update.callback_query.data)):
                    buttons[i].remove(
                        InlineKeyboardButton(update.callback_query.data, callback_data=update.callback_query.data))
                    keyboard = InlineKeyboardMarkup(buttons)
                    update.callback_query.edit_message_text(
                        text=update.callback_query.message.text.replace(
                            f"{update.callback_query.data}.",
                            f"{update.callback_query.data}. {update.callback_query.from_user.first_name} {update.callback_query.from_user.last_name}",
                            1
                        ),
                        reply_markup=keyboard,
                    )

    #  якщо знайдено у списку і cancel
    elif str(update.callback_query.message.text).find(str(update.callback_query.from_user.first_name) + " " +
                                                      str(update.callback_query.from_user.last_name)) != -1 and update.callback_query.data == "cancel":
        ###
        #  видалити із списку, повернути кнопку на місце!!!
        ###
        context.bot.answer_callback_query(callback_query_id=update.callback_query.id, text='Відмінено!',show_alert=True)

    # якщо не знайдено у списку і cancel
    elif str(update.callback_query.message.text).find(str(update.callback_query.from_user.first_name) + " " +
                                                      str(update.callback_query.from_user.last_name)) == -1 and update.callback_query.data == "cancel":
        context.bot.answer_callback_query(callback_query_id=update.callback_query.id, text='Тебе ще не має у списку!', show_alert=True)

    # якщо знайдено у списку і НЕ cancel
    else:
        context.bot.answer_callback_query(callback_query_id=update.callback_query.id, text='Ти вже у списку, натисни Cancel для відміни', show_alert=True)


def main():
    updater = Updater(
        "5119453197:AAHpO7pymF2BQkevcFg6r0r4zZQcKU7iRfY", use_context=True
    )  # API token бота
    dp = updater.dispatcher  # якась важна штука

    dp.add_handler(CommandHandler("start", start))  # прив'язка команди до бота (start)
    dp.add_handler(
        CommandHandler("cancel", cancel)
    )  # прив'язка команди до бота (cancel)

    conv_handler = ConversationHandler(  # ініціацізація розмови
        entry_points=[
            CommandHandler("startqueue", startqueue)
        ],  # точка входу (запускається після
        # команди /startqueue), викликає startqueue(), по сумісності прив'язка команди до бота
        states={
            NAME: [
                MessageHandler(Filters.text & ~Filters.command, namequeue)
            ],  # один (поки що єдиний) етап
            # діалогу, бот просить ім'я черги. Після цього виклакається ф-ція namequeue
        },
        fallbacks=[CommandHandler("cancel", cancel)],  # відміна черги
    )

    dp.add_handler(conv_handler)  # прив'язка діалогу
    dp.add_handler(CallbackQueryHandler(keyboard_callback))
    dp.add_error_handler(error)  # прив'язка виведення помилок

    updater.start_polling()
    updater.idle()  # по-моєму цикл життя (верхнє теж), держить бота увімкненим, краще не чіпати


if __name__ == "__main__":  # запускач
    main()

import math

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

keyboard = []

identificator = 0

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
    global identificator, keyboard
    name = str(identificator) + "\n" + update.message.text + '\n'  # записуємо введену назву черги в змінну
    queue = ""
    for i in range(1, count + 1):
        queue += str(i) + ".\n"  # створюємо список (1.\n2.\n)
    keyboard.insert(identificator, buttons)
    update.message.reply_text(
        name + queue, reply_markup=InlineKeyboardMarkup(keyboard[identificator])
    )  # надсилаємо повідомлення: назва черги, список та
    # клавіатуру
    identificator += 1
    return ConversationHandler.END  # повертаємо кінець діалогу


def cancel(update, context):  # відміна черги (не працює, хоча по-ідеї завершує діалог)
    update.message.reply_text("Чергу закрито")
    return ConversationHandler.END


def keyboard_callback(update, context):
    global keyboard
    ident = int(str(update.callback_query.message.text).split("\n")[0])
    #  якщо не знайдено у списку і НЕ cancel
    if str(update.callback_query.message.text).find(str(update.callback_query.from_user.first_name) + " " +
                                                    str(update.callback_query.from_user.last_name)) == -1 and str(
        update.callback_query.data) != 'cancel':
        for i in range(0, len(keyboard[ident]) - 1):
            for j in range(0, len(keyboard[ident][i])):
                if (keyboard[ident][i][j] == InlineKeyboardButton(update.callback_query.data,
                                                          callback_data=update.callback_query.data)):
                    keyboard[ident][i].remove(
                        InlineKeyboardButton(update.callback_query.data, callback_data=update.callback_query.data))
                    update.callback_query.edit_message_text(
                        text=update.callback_query.message.text.replace(
                            f"{update.callback_query.data}.",
                            f"{update.callback_query.data}. {str(update.callback_query.from_user.first_name)} {str(update.callback_query.from_user.last_name)}",
                            1
                        ),
                        reply_markup=InlineKeyboardMarkup(keyboard[ident]),
                    )
                    print(keyboard[ident])
                    break
    #  якщо знайдено у списку і cancel
    elif str(update.callback_query.message.text).find(str(update.callback_query.from_user.first_name) + " " +
                                                      str(update.callback_query.from_user.last_name)) != -1 and update.callback_query.data == "cancel":
        listofqueue = str(update.callback_query.message.text).split('\n')
        for i in range(0, len(listofqueue)):
            if listofqueue[i].find(str(update.callback_query.from_user.first_name) + " " + str(update.callback_query.from_user.last_name))!=-1:
                num = listofqueue[i].replace(
                    f". {str(update.callback_query.from_user.first_name)} {str(update.callback_query.from_user.last_name)}", f"",
                    1)
                keyboard[ident][math.floor((int(num)-1)/4)].insert(0, InlineKeyboardButton(num, callback_data=num))
                keyboard[ident][math.floor((int(num)-1)/4)].sort(key=lambda x: int(x.callback_data))
                break

        ###                        ###
        update.callback_query.edit_message_text(
            text=update.callback_query.message.text.replace(
                f" {str(update.callback_query.from_user.first_name)} {str(update.callback_query.from_user.last_name)}",
               f"",
                1
            ),
            reply_markup=InlineKeyboardMarkup(keyboard[ident]),
        )
        context.bot.answer_callback_query(callback_query_id=update.callback_query.id, text='Відмінено!',
                                          show_alert=True)

    # якщо не знайдено у списку і cancel
    elif str(update.callback_query.message.text).find(str(update.callback_query.from_user.first_name) + " " +
                                                      str(update.callback_query.from_user.last_name)) == -1 and update.callback_query.data == "cancel":
        context.bot.answer_callback_query(callback_query_id=update.callback_query.id, text='Тебе ще не має у списку!',
                                          show_alert=True)

    # якщо знайдено у списку і НЕ cancel
    else:
        context.bot.answer_callback_query(callback_query_id=update.callback_query.id,
                                          text='Ти вже у списку, натисни Cancel для відміни', show_alert=True)


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

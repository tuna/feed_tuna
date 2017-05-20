#! /usr/bin/env python3
from telegram import bot
from telegram.ext import Updater
from telegram.ext import CommandHandler
from handler import PaymentHandler, BrowersHandler
import logging
import json
import copy

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

updater = Updater(token='276217921:AAEFO9zEwHoRZhreHpHC7H94USXF9ZzilJo')
dispatcher = updater.dispatcher
commodities = json.load(open('commodities.json', 'r'))
shipping_options = json.load(open('shipping.json', 'r'))

PROVIDER_TOKEN = "284685063:TEST:OTQ2YTIzNjY0ZTVl"

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Feed me!🐬")

def browers(bot, update):
    text = "Things you can buy:\n"
    buttons = []
    i = 0
    for item in commodities:
        price = item['prices'][0]['amount']/100
        data = {
            'type': 'commodity',
            'idx' : i,
            "chat": update.message.chat_id
        }
        buttons.append([{"text": "{}  💰CNY {}".format(item['title'], price), "callback_data": json.dumps(data)}])
        i += 1

    bot.send_message(
        chat_id=update.message.chat_id,
        text=text,
        parse_mode="Markdown",
        reply_markup={"inline_keyboard": buttons}
    )
    """
    bot.send_invoice(
        chat_id=update.message.chat_id,
        title="TUNA Sticker Set",
        description="Make contributions to Tsinghua University TUNA Association by buying our stickers.",
        payload="1234",
        provider_token="284685063:TEST:OTQ2YTIzNjY0ZTVl",
        start_parameter="1234",
        currency="CNY",
        prices=[{'label': 'Sticker Set', 'amount': 3000}],
        need_name=True,
        need_phone_number=True,
        need_email=True,
        need_shipping_address=True,
        is_flexible=True
    )"""

def browers_hander(bot, update):
    data = json.loads(update.callback_query.data)
    bot.answer_callback_query(
        callback_query_id=update.callback_query.id
    )
    if data['type'] == 'commodity': # A commodity has been selected
        text = "How many would you like?"
        buttons = []
        for qty in [1, 2, 4, 8]:
            callback_data = {
                'type': 'qty',
                'idx': data['idx'],
                'qty': qty,
                'chat': data['chat']
            }
            button = {"text": str(qty), "callback_data": json.dumps(callback_data)}
            buttons.append(button)
        bot.send_message(
            chat_id=data['chat'],
            text=text,
            parse_mode="Markdown",
            reply_markup={"inline_keyboard": [buttons]}
        )
        return
    if data['type'] == 'qty': # Quantity has been selected
        commodity = commodities[data['idx']]
        chat_id = data['chat']

        invoice_params = "{}_{}".format(
            commodity['id'],
            data['qty']
        )

        prices = copy.deepcopy(commodity['prices'])
        prices[0]['amount'] *= data['qty']

        bot.send_invoice(
            chat_id=chat_id,
            title="{} x{}".format(commodity['title'], data['qty']),
            description=commodity['description'],
            payload=json.dumps(invoice_params),
            provider_token=PROVIDER_TOKEN,
            start_parameter=invoice_params,
            currency="CNY",
            prices=prices,
            need_name=True,
            need_phone_number=True,
            need_email=True,
            need_shipping_address=True,
            is_flexible=True
        )
        return

def err_handler(bot, update, err):
    print('err happended')
    print(update)
    print(err)

def payment_handler(bot, update):
    if update.shipping_query:
        # If a shipping address was requested and you included the parameter is_flexible, the Bot API will send an Update with a shipping_query field to the bot. The bot must respond using answerShippingQuery either with a list of possible delivery options and the relevant delivery prices, or with an error (for example, if delivery to the specified address is not possible).

        bot.answer_shipping_query(
            shipping_query_id=update.shipping_query.get('id'),
            ok=True,
            shipping_options=shipping_options
        )
        return
    if update.pre_checkout_query:
        bot.answer_pre_checkout_query(
            update.pre_checkout_query.get('id'),
            True
        )
        return
    if update.message and update.message.successful_payment:
        # A payment has been placed successfully. Once your bot receives this message, it should proceed with delivering the goods or services purchased by the user.
        print(update.message.successful_payment)
        return

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('buy', browers))
dispatcher.add_handler(PaymentHandler(payment_handler))
dispatcher.add_handler(BrowersHandler(browers_hander))
dispatcher.add_error_handler(err_handler)
updater.start_polling()

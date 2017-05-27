#! /usr/bin/env python3
from telegram import bot
from telegram.ext import Updater
from telegram.ext import CommandHandler
from handler import PaymentHandler, BrowersHandler
import json, copy, os, sqlite3
from pymongo import MongoClient
from datetime import datetime
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

TG_BOT_KEY = os.environ['TG_BOT_KEY']
PROVIDER_TOKEN = os.environ['PROVIDER_TOKEN']

updater = Updater(token=TG_BOT_KEY)
dispatcher = updater.dispatcher
commodity_list = json.load(open('commodities.json', 'r'))
commodities = {}
for com in commodity_list:
    commodities[com['id']] = com
shipping_options = json.load(open('shipping.json', 'r'))

conn = sqlite3.connect('feed_tuna.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS `orders` (
	`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`name`	TEXT,
	`invoice`	TEXT NOT NULL,
	`amount`	INTEGER NOT NULL,
	`shipping_option`	TEXT,
	`tg_pay_id`	TEXT,
	`provider_pay_id`	TEXT,
	`phone`	TEXT,
	`email`	TEXT,
	`tg_user_id`	INTEGER,
	`tg_user_name`	TEXT,
	`country_code`	TEXT,
	`state`	TEXT,
	`city`	TEXT,
	`street_line1`	TEXT,
	`street_line2`	TEXT,
	`postcode`	TEXT,
    `datetime`  TEXT NOT NULL
);''')
conn.commit()
conn.close()

client = MongoClient()
db = client.feed_tuna

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Feed me!🐬")

def browers(bot, update):
    if update.message.chat_id < 0:
        bot.send_message(
            chat_id=update.message.chat_id,
            reply_to_message_id=update.message.message_id,
            text="Sorry, this bot cannot be used in group chat.",
            parse_mode="Markdown"
        )
        return
    text = "Things you can buy:\n"
    buttons = []
    for item in commodities.values():
        price = item['prices'][0]['amount']/100
        data = {
            'type': 'com',
            'id' : item['id'],
            "chat": update.message.chat_id
        }
        buttons.append([{"text": "{}  💰CNY {}".format(item['title'], price), "callback_data": json.dumps(data)}])

    bot.send_message(
        chat_id=update.message.chat_id,
        text=text,
        parse_mode="Markdown",
        reply_markup={"inline_keyboard": buttons}
    )

def browers_hander(bot, update):
    data = json.loads(update.callback_query.data)
    bot.answer_callback_query(
        callback_query_id=update.callback_query.id
    )
    if data['type'] == 'com': # A commodity has been selected
        text = "How many would you like?"
        buttons = []
        for qty in [1, 2, 4, 8]:
            callback_data = {
                'type': 'qty',
                'id': data['id'],
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
        commodity = commodities[data['id']]
        chat_id = data['chat']

        invoice_params = json.dumps({
            'item_id': data['id'],
            'qty': data['qty']
        })

        start_parameter="{}_{}".format(commodity['id'], data['qty'])

        prices = copy.deepcopy(commodity['prices'])
        prices[0]['amount'] *= data['qty']

        bot.send_invoice(
            chat_id=chat_id,
            title="{} x{}".format(commodity['title'], data['qty']),
            description=commodity['description'],
            payload=invoice_params,
            provider_token=PROVIDER_TOKEN,
            start_parameter=start_parameter,
            currency="CNY",
            prices=prices,
            need_name=True,
            need_phone_number=True,
            need_email=True,
            need_shipping_address=(not commodity.get('virtual')),
            is_flexible=(not commodity.get('virtual'))
        )
        return

def err_handler(bot, update, err):
    print('err happended')
    print(update)
    print(err)

def payment_handler(bot, update):
    if update.shipping_query:
        # If a shipping address was requested and you included the parameter is_flexible, the Bot API will send an Update with a shipping_query field to the bot. The bot must respond using answerShippingQuery either with a list of possible delivery options and the relevant delivery prices, or with an error (for example, if delivery to the specified address is not possible).
        payload = json.loads(update.shipping_query.get('invoice_payload'))
        commodity = commodities[payload['item_id']]
        overseas =  update.shipping_query.get('shipping_address').get('country_code') != "CN"
        options = list(filter(lambda x: (x.get('overseas', False)) == overseas, shipping_options))

        bot.answer_shipping_query(
            shipping_query_id=update.shipping_query.get('id'),
            ok=True,
            shipping_options=options
        )
        return
    if update.pre_checkout_query:
        bot.answer_pre_checkout_query(
            pre_checkout_query_id=update.pre_checkout_query.get('id'),
            ok=True
        )
        return
    if update.message and update.message.successful_payment:
        # A payment has been placed successfully. Once your bot receives this message, it should proceed with delivering the goods or services purchased by the user.
        order_info = update.message.successful_payment.get('order_info')

        # get invoice description
        invoice_payload = update.message.successful_payment.get('invoice_payload')
        invoice_payload = json.loads(invoice_payload)
        commodity = commodities[invoice_payload.get('item_id')]
        commodity_title = commodity['title']
        quantity = invoice_payload.get('qty')
        invoice_description = "{} x {}".format(quantity, commodity_title)

        # more details about this order
        total_amount = update.message.successful_payment.get('total_amount')
        shipping_option_id = update.message.successful_payment.get('shipping_option_id')
        telegram_payment_charge_id = update.message.successful_payment.get('telegram_payment_charge_id')
        provider_payment_charge_id = update.message.successful_payment.get('provider_payment_charge_id')
        name = order_info.get('name')
        phone_number = order_info.get('phone_number')
        email = order_info.get('email')

        # shipping info
        address = order_info.get('shipping_address')
        if address is not None:
            country_code = address.get('country_code')
            state = address.get('state')
            city = address.get('city')
            street_line1 = address.get('street_line1')
            street_line2 = address.get('street_line2')
            post_code = address.get('post_code')
        else:
            country_code = None
            state = None
            city = None
            street_line1 = None
            street_line2 = None
            post_code = None

        # buyer telegram info
        from_user_id = update.message.from_user.id
        from_user_name = update.message.from_user.username

        # timestamp
        now = datetime.now().isoformat()

        values = (name, invoice_description, total_amount, shipping_option_id,
        telegram_payment_charge_id, provider_payment_charge_id, phone_number, email,
        from_user_id, from_user_name, country_code, state, city, street_line1,
        street_line2, post_code, now)

        print('values: ', values)

        conn = sqlite3.connect('feed_tuna.db')
        cursor = conn.cursor()

        r = cursor.execute("INSERT INTO orders VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,? ,? ,? ,? ,? ,? ,?)", values)


        inserted_id = cursor.lastrowid

        conn.commit()
        conn.close()

        bot.send_message(
            chat_id=update.message.chat_id,
            text="Your order has been placed successfully. Tracking ID: {}. You can email us with your tracking ID for inquiries.".format(str(inserted_id))
        )
        return

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('buy', browers))
dispatcher.add_handler(PaymentHandler(payment_handler))
dispatcher.add_handler(BrowersHandler(browers_hander))
dispatcher.add_error_handler(err_handler)
updater.start_polling()

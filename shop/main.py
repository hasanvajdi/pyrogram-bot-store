#mysql
import mysql.connector

#exel need
import xlwt
from xlwt import Workbook

import random

import requests
#used in convert date
import jdatetime

#pyrogram
from pyrogram import Client, filters
from pyrogram.errors import BadRequest, Forbidden
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

#logging
import logging
logging.basicConfig(level = logging.DEBUG,
                    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

#connect to mysql server
mydb = mysql.connector.connect(
  host="localhost",
  user = "root",
  password = "99609970",
  database = "shop",
  auth_plugin = 'mysql_native_password'
)

#create instance
db = mydb.cursor()

app = Client(
    "shop",
    api_id = 571145,
    api_hash = "7222730d378cb9618018bdf9825d6a3b",
    bot_token = "1806760795:AAE_uLoH6D0FiIn_sTsSC7RdNeJVm5MPZns"
)


def vars():
    global product
    product = {}

    global get_product_image_or_not
    get_product_image_or_not = False

    global get_product_name_or_not
    get_product_name_or_not = False

    global get_product_count_or_not
    get_product_count_or_not = False

    global get_product_description_or_not
    get_product_description_or_not = False

    global get_product_unit_or_not
    get_product_unit_or_not = False

    global get_product_price_or_not
    get_product_price_or_not = False

    global add_group_or_channel_to_bot
    add_group_or_channel_to_bot = False

    global GetEditCode
    GetEditCode = False

    global set_shop_name
    set_shop_name = False

    global set_welcome_text
    set_welcome_text = False

    global GetDeleteCode
    GetDeleteCode = False

    global set_shift
    set_shift = False

    global get_auth_code
    get_auth_code = False

    global get_new_discount
    get_new_discount = False
    variable_edit_after_submiting = False

    global add_to_cart_dict
    add_to_cart_dict = {}

    global get_product_count_cart
    get_product_count_cart = False

    global get_code_add_to_cart
    get_code_add_to_cart = False

    global get_code_delete_cart
    get_code_delete_cart = False

    global get_count_add_to_cart
    get_count_add_to_cart = False

    global get_connection_id
    get_connection_id = False

    global get_new_password
    get_new_password = False

    global message_to_all
    message_to_all = False

    global forward_to_all
    forward_to_all = False

    #variable for edite product information
    global edit_product_info
    edit_product_info = {
                            "name" : False,
                            "count" : False,
                            "unit" : False,
                            "price" : False,
                            "description" : False
                        }
vars()




@app.on_message(filters.command(["start", "admin"]))
def main(client, message):
    command = message.command
    chat_id = message.chat.id

    # check user chat id
    db.execute(f"SELECT * FROM chat_id WHERE chat_id  = '{message.chat.id}'")
    if db.fetchone() == None:
        db.execute(f"INSERT INTO chat_id (chat_id, message_id) VALUES ('{message.chat.id}', '0')")
        mydb.commit()


    #start normally
    if command[0] == "start":
        db.execute(f"UPDATE settings SET value = 'start' WHERE name = '{chat_id}'")
        mydb.commit()

        db.execute(f"SELECT * FROM users WHERE user_id = '{message.from_user.id}'")
        if db.fetchone() == None:
            db.execute(f"INSERT INTO users (user_id) VALUES ('{message.from_user.id}')")
            mydb.commit()

        if len(command) == 2:

            db.execute(f"SELECT * FROM product WHERE code = {int(command[1])}")
            fetched_data = db.fetchone()
            product["photo"] = fetched_data[1]
            product["name"] = fetched_data[2]
            product["count"] = fetched_data[3]
            product["unit"] = fetched_data[4]
            product["price"] = fetched_data[5]

            text = f"🔗{product['name']}\n\nتعداد موجودی : {product['count']} {product['unit']}\nقیمت : هر {product['unit']}, {product['price']}  هزار تومان"


            if len(fetched_data) == 7:
                product["description"] = fetched_data[6]
                text = f"🔗{product['name']}\n\nتعداد موجودی : {product['count']} {product['unit']}\nقیمت : هر {product['unit']}, {product['price']}  هزار تومان\nتوضیحات : {product['description']}"


            #get user
            db.execute(f"SELECT id FROM users WHERE user_id = '{message.from_user.id}'")
            user = db.fetchone()[0]

            #check cart
            db.execute(f"SELECT * FROM cart WHERE product = '{int(command[1])}' AND user = '{user}'")
            product_status = db.fetchone()

            #increse the seen column
            db.execute(f"SELECT seen FROM product WHERE code = '{int(command[1])}'")
            seen = db.fetchone()[0]
            db.execute(f"UPDATE product SET seen = {int(seen) + 1} WHERE code = '{int(command[1])}'")
            mydb.commit()

            product_see_keys = [
                [
                    InlineKeyboardButton(f"{'افزودن به سبد خرید 🛒' if product_status == None else 'موجود در سبد خرید〽️'}", callback_data = f"{f'add_to_cart_{command[1]}' if product_status == None else 'blank'}"),
                    InlineKeyboardButton("خرید 💳", callback_data = "buy_product"),
                ]
            ]

            #select active discount
            db.execute("SELECT percent, cause FROM discounts WHERE status = 'active'")
            discount = db.fetchone()
            if discount != None:
                product_see_keys.append([InlineKeyboardButton("🎉 علت تخفیف 🎉", callback_data = "discount_cause")])
                finally_price = int(product['price']) - (int(product['price']) // 100) * int(discount[0])
                text += f"\n\n🔖<strong>{discount[0]} درصد تخفیف</strong>\n💰 قیمت نهایی : <strong>{finally_price}</strong> هزار تومان"

            app.send_photo(
                            chat_id,
                            photo = product["photo"],
                            caption = text,
                            reply_markup = InlineKeyboardMarkup(product_see_keys),
                            parse_mode = "html"
                            )


        if len(command) == 1:
            db.execute("SELECT value FROM settings WHERE name = 'id'")
            id = db.fetchone()[0]
            db.execute("SELECT value FROM settings WHERE name = 'welcome_text'")
            welcome_text = db.fetchone()[0]
            global start_main_mneu
            start_main_mneu = app.send_message(
                            chat_id,
                            text = welcome_text,
                            reply_markup = InlineKeyboardMarkup([
                                [InlineKeyboardButton("سبد خرید 🛒", callback_data = "customer_see_cart")],
                                [InlineKeyboardButton("ارتباط با پشتیبانی فروشگاه 👤", url = f"https://t.me/{id}")],
                                [InlineKeyboardButton("💻 ارتباط به برنامه نویس ربات 💻", url = "https://t.me/hasan_zltn9")],
                            ])
            )
            app.send_message(message.chat.id, "<strong>جستجوی محصول در ربات فعال است📌</strong>\n\nکافیه <strong>کد</strong> یا <strong>اسم </strong> محصول مورد نظرتو بفرستی👌\n\nیا خودش رو پیدا میکنم یا مشابه اش رو😉",
                            parse_mode = "html")
            db.execute(f"UPDATE chat_id SET message_id = '{start_main_mneu.message_id}'")
            mydb.commit()



    if command[0] == "admin":
        db.execute("SELECT value FROM settings WHERE name = 'password'")
        password = db.fetchone()[0]
        if len(command) == 2:
            if (command[0], command[1]) == ("admin", f"{password}"):
                global AdminMainMessage
                AdminMainMessage = app.send_message(
                            chat_id,
                            "شما ادمین هستید",
                            reply_markup = InlineKeyboardMarkup([
                                                    [InlineKeyboardButton("مدیریت محصولات 🛍", callback_data = "product_management")],
                                                    [InlineKeyboardButton("مدیریت فروشگاه 🏪", callback_data = "store_management")],
                                                    [InlineKeyboardButton("مدیریت ربات 🤖", callback_data = "bot_management")]

                                                ])

                            )


                db.execute("SELECT MAX(id)  FROM adminmessageid")
                if db.fetchone()[0] == None:
                    db.execute(f"INSERT INTO adminmessageid (message_id) VALUES ({AdminMainMessage.message_id})")
                    mydb.commit()
                else:
                    db.execute(f"UPDATE adminmessageid SET message_id = {AdminMainMessage.message_id}")
                    mydb.commit()

                #check status row in settings table
                db.execute(f"SELECT value FROM settings WHERE name = '{chat_id}'")
                if db.fetchone() == None:
                    db.execute(f"INSERT INTO settings (name, value) VALUES ('{chat_id}', 'admin')")
                else:
                    db.execute(f"UPDATE settings SET value = 'admin' WHERE name = '{chat_id}'")
                mydb.commit()

            else:
                app.send_message(chat_id, "رمز عبور اشتباه است ⛔️")

#variable for product

@app.on_message(filters.contact)
def GetContact(client, message):
    vars()
    db.execute(f"SELECT status FROM cart_info WHERE chat_id = '{message.chat.id}'")
    status = db.fetchone()
    phone = message.contact.phone_number
    phone = phone.replace("+98", "0")
    if status == None:
        db.execute(f"INSERT INTO cart_info (user_id, chat_id, phone, status) VALUES ('{message.contact.user_id}','{message.chat.id}', '{phone}', 'deactive')")
        mydb.commit()


    #generate code
    code = ''.join(random.sample("0123456789", 5))
    phone_number = message.contact.phone_number

    # delete already sent code
    db.execute(f"SELECT * FROM cart_code WHERE chat_id = '{message.chat.id}'")
    if db.fetchone() != None:
        db.execute(f"DELETE FROM cart_code WHERE chat_id = '{message.chat.id}'")
        mydb.commit()

    #register sent code in database
    db.execute(f"INSERT INTO cart_code (chat_id, code) VALUES ('{message.chat.id}', '{code}')")
    mydb.commit()

    #send sms to user phone
    a = requests.get(f"https://api.codebazan.ir/sms/api.php?type=sms&apikey=ws0ZGqHiBopyPMbQ&code={code}&phone={phone_number}")

    app.send_message(message.chat.id,f"📍لطفا کد ارسال شده به شماره {phone} را بفرستید ")
    global get_auth_code
    get_auth_code = True



@app.on_callback_query()
def CallBack(client, message):
    vars()
    callback_id = message.id
    chat_id = message.message.chat.id
    db.execute("SELECT message_id FROM adminmessageid")
    message_id = db.fetchone()[0]
    data = message.data

    print(data)

    global get_product_image_or_not
    global get_product_name_or_not
    global get_product_count_or_not
    global get_product_description_or_not
    global get_product_unit_or_not
    global get_product_price_or_not

    #forward message to all users
    if data == "forward_pm_to_all":
        client.answer_callback_query(callback_id, "")
        app.send_message(chat_id, "💤پیام مورد نظرتو بفرست...")
        global forward_to_all
        forward_to_all = True

    #send message to all users
    if data == "send_pm_to_all":
        client.answer_callback_query(callback_id, "")
        app.send_message(chat_id, "🔅پیام مورد نظرتو بفرست...")
        global message_to_all
        message_to_all = True

    #change store password
    if data == "change_store_password":
        global get_new_password
        get_new_password = True
        client.answer_callback_query(callback_id, "رمز جدید را ارسال کنید...", show_alert = True)

    #submit delete product from cart
    if data.startswith("delete_product_button_cart_"):
        client.answer_callback_query(callback_id, "")
        submit_delete_product = data.split("_")[-1]
        #get user
        db.execute(f"SELECT id FROM users WHERE user_id = '{message.from_user.id}'")
        user = db.fetchone()[0]

        #delete product from cart
        db.execute(f"DELETE from cart WHERE product = '{submit_delete_product}' AND user = '{user}'")
        mydb.commit()

        #delete message
        db.execute(f"SELECT message_id FROM chat_id WHERE chat_id = '{chat_id}'")
        message_id = db.fetchone()[0]
        app.delete_messages(chat_id, message_id)
        #send success message
        app.send_message(chat_id,"محصول مورد نظر از سبد خرید شما حذف شد ✅")

        # send cart menu
        gg = app.send_message(
                        chat_id,
                        text = "🔘 بخش سبد خرید\n\nتو این بخش میتونی عملکرد های زیر رو روی سبد خریدت داشته باشی👇",
                        reply_markup = InlineKeyboardMarkup([
                            [InlineKeyboardButton("📝 لیست محصولات موجود در سبد خرید 🛒", callback_data = "cart_list")],
                            [InlineKeyboardButton("➕ افزودن محصول", callback_data = "add_to_cart_btn")],
                            [InlineKeyboardButton("✖️ حذف محصول", callback_data = "delete_product_cart")],
                            [InlineKeyboardButton("برگشت »", callback_data = "back_to_start_menu")]

                        ])
                )
        db.execute(f"UPDATE chat_id SET message_id = '{gg.message_id}'")
        mydb.commit()

    if data == "delete_product_cart":
        client.answer_callback_query(callback_id, "")
        app.send_message(chat_id, "📌 لطفا کد محصول مورد نظرت رو بفرست...")
        global get_code_delete_cart
        get_code_delete_cart = True

    # discount cause
    if data == "discount_cause":
        db.execute("SELECT cause FROM discounts WHERE status = 'active'")
        cause = db.fetchone()
        if cause != None:
            client.answer_callback_query(callback_id, f"{cause[0]}", show_alert = True)

    #add product to cart
    if data.startswith("add_to_cart_"):
        client.answer_callback_query(callback_id, "")
        if data.split("_")[-1] == "btn":
            app.send_message(chat_id, "📌 لطفا کد محصول مورد نظرت رو بفرست...")
            global get_code_add_to_cart
            get_code_add_to_cart = True
        else:
            #getting user
            db.execute(f"SELECT id FROM users WHERE user_id = '{message.from_user.id}'")
            user_id = db.fetchone()[0]

            #splig code from data
            code = data.split("_")[-1]

            #getting product
            db.execute(f"SELECT code FROM product WHERE code = {code}")
            product_code = db.fetchone()[0]

            add_to_cart_dict["user"] = user_id
            add_to_cart_dict["product"] = product_code

            client.answer_callback_query(callback_id, "لطفا تعداد درخواستی از این محصول رو به صورت عدد بفرس", show_alert = True)

            global get_product_count_cart
            get_product_count_cart = True


    #show cart
    if data == "customer_see_cart":
        client.answer_callback_query(callback_id, "")
        db.execute(f"SELECT status FROM cart_info WHERE chat_id = '{chat_id}'")
        status = db.fetchone()
        if status == None or status[0] == "deactive":
            key = [[KeyboardButton("ارسال شماره تلفن 📲", request_contact = True)]]
            app.send_message(
                    chat_id,
                    text = "<strong>حساب شما تایید نشده است.⛔️</strong>\nبرای تایید حساب شماره خود را ارسال کنید \n\nروی دکمه زیر کلیک کنید تا به صورت خودکار شماره ارسال بشود👇",
                    reply_markup = ReplyKeyboardMarkup(key,resize_keyboard = True, one_time_keyboard  = True, selective = True,),
                    parse_mode = "html"
                )

        elif status[0] == "active":
            db.execute(f"SELECT message_id FROM chat_id WHERE chat_id = '{chat_id}'")
            message_id = db.fetchone()[0]
            global cart_menu
            cart_menu = app.edit_message_text(
                        chat_id = chat_id,
                        message_id = message_id,
                        text = "🔘 بخش سبد خرید\n\nتو این بخش میتونی عملکرد های زیر رو روی سبد خریدت داشته باشی👇",
                        reply_markup = InlineKeyboardMarkup([
                            [InlineKeyboardButton("📝 لیست محصولات موجود در سبد خرید 🛒", callback_data = "cart_list")],
                            [InlineKeyboardButton("➕ افزودن محصول", callback_data = "add_to_cart_btn")],
                            [InlineKeyboardButton("✖️ حذف محصول", callback_data = "delete_product_cart")],
                            [InlineKeyboardButton("برگشت »", callback_data = "back_to_start_menu")]

                        ])
                )
            #db.execute(f"SELECT id FROM users WHERE user_id = '{message.from_user.id}'")
            #code = db.fetchone()[0]
            #db.execute(f"SELECT * FROM cart WHERE user = {code}")
            #print(db.fetchall())


    if data == "back_to_start_menu":
        client.answer_callback_query(callback_id, "")
        db.execute(f"SELECT message_id FROM chat_id WHERE chat_id = '{chat_id}'")
        message_id = db.fetchone()[0]
        app.edit_message_text(
            chat_id,
            message_id,
            text = start_main_mneu.text,
            reply_markup = start_main_mneu.reply_markup
        )

    #cart list
    if data == "cart_list":
        client.answer_callback_query(callback_id, "")
        db.execute(f"SELECT message_id FROM chat_id WHERE chat_id = '{chat_id}'")
        message_id = db.fetchone()[0]

        #wich user want to see own cart?
        db.execute(f"SELECT id FROM users WHERE user_id = '{message.from_user.id}'")
        user = db.fetchone()[0]

        #get cart list
        db.execute(f"SELECT * FROM cart WHERE user = '{user}'")
        cart_list = db.fetchall()
        if len(cart_list) == 0:
            client.answer_callback_query(callback_id, "سبد خرید شما خالی است 🌀", show_alert = True)
        else:
            text = ""
            counter = 0
            for i in cart_list:
                db.execute(f"SELECT code,name FROM product WHERE code = '{i[0]}'")
                pro = db.fetchone()
                counter += 1
                #
                text += f"({counter} <strong> کد {pro[0]}</strong> - <a href = 'http://t.me/vajd_shop_bot?start={pro[0]}'>{pro[1]}</a> - تعداد {i[2]}"

                app.edit_message_text(
                    chat_id,
                    message_id,
                    text = text,
                    reply_markup = InlineKeyboardMarkup([
                        [InlineKeyboardButton("برگشت به سبد خرید »", callback_data = "back_to_cart")]
                    ]),
                    parse_mode = "html"
                )

    #back to cart
    if data == "back_to_cart":
        client.answer_callback_query(callback_id, "")
        db.execute(f"SELECT message_id FROM chat_id WHERE chat_id = '{chat_id}'")
        message_id = db.fetchone()[0]

        app.edit_message_text(
            chat_id,
            message_id,
            text = cart_menu.text,
            reply_markup = cart_menu.reply_markup
        )

    #bot management section
    if data == "bot_management":
        client.answer_callback_query(callback_id, "")
        db.execute("SELECT message_id FROM adminmessageid")
        message_id = db.fetchone()[0]

        #select channel link
        text = f"🔘 مدیریت ربات\n\nتو این بخش میتونی تنظیمات ربات رو انجام بدی 👇"
        db.execute("SELECT value FROM settings WHERE name = 'bot_channel'")
        link = db.fetchone()

        if link != None:
            text += f"\n\n\n🔗کانال تنظیم شده : {link[0]}"


        app.edit_message_text(
                        chat_id,
                        message_id,
                        text = text,
                        reply_markup = InlineKeyboardMarkup([
                            [InlineKeyboardButton("افزودن کانال یا گروه 👥", callback_data = "add_group_or_channel_to_bot")],
                            [InlineKeyboardButton("تغییر رمز ورود فروشگاه ☢️", callback_data = "change_store_password")],
                            [
                                InlineKeyboardButton("ارسال پیام همگانی 💭", callback_data = "send_pm_to_all"),
                                InlineKeyboardButton("فرواد پیام همگانی 🔄", callback_data = "forward_pm_to_all")
                            ],
                            [InlineKeyboardButton("برگشت به منو اصلی 🔙", callback_data = "back_to_main_menu")]

                        ])
        )


    # add group or channel to bot
    global add_group_or_channel_to_bot
    if data == "add_group_or_channel_to_bot":
        client.answer_callback_query(callback_id, "")
        add_group_or_channel_to_bot = True
        client.answer_callback_query(callback_id, "لینک کانال یا گروه مورد نظرتو بدون @ بفرس...", show_alert = True)

    #send to channel or not
    #if data == "send_automaticlly_to_channel":
    #    db.execute("SELECT message_id FROM adminmessageid")
    #    message_id = db.fetchone()[0]
#
    #    #select status of send automaticlly
    #    status = 'on'
    #    db.execute("SELECT value FROM settings WHERE name = 'send_to_channel'")
    #    if db.fetchone() != None:
    #        db.execute("SELECT value FROM settings WHERE name = 'send_to_channel'")
    #        status = db.fetchone()[0]
    #    elif db.fetchone() == None:
    #        db.execute(f"INSERT INTO settings (name, value) VALUES ('send_to_channel', 'on')")
    #        mydb.commit()
#
    #    global send_to_channel_val
    #    send_to_channel_val = app.edit_message_text(
    #                    chat_id,
    #                    message_id,
    #                    text = "🔘 مدیریت ارسال خودکار به کانال\n\nتو این بخش میتونی تنظیم کنی که محصولات جدید فروشگاهت به صورت خودکار به کانال فرستاده بشن یا نه👇",
    #                    reply_markup = InlineKeyboardMarkup([
    #                        [
                            #InlineKeyboardButton(f"فعال {'✅' if status == 'on' else '' }", callback_data = "active_send_to_channel"),
    #                            InlineKeyboardButton(f"غیرفعال {'✅' if status == 'off' else '' }", callback_data = "deactive_send_to_channel")
    #                        ],
    #                        [InlineKeyboardButton("برگشت »", callback_data = "back_to_main_menu")]
    #                    ])
    #    )

    #active send to channle
    if data == "active_send_to_channel":
        client.answer_callback_query(callback_id, "")
        db.execute("SELECT message_id FROM adminmessageid")
        message_id = db.fetchone()[0]

        db.execute("SELECT value FROM settings WHERE name = 'send_to_channel'")
        if db.fetchone()[0] == "off":
            app.edit_message_text(
                chat_id,
                message_id,
                text = "🔘 مدیریت ارسال خودکار به کانال\n\nتو این بخش میتونی تنظیم کنی که محصولات جدید فروشگاهت به صورت خودکار به کانال فرستاده بشن یا نه👇",
                reply_markup = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(f"فعال ✅", callback_data = "active_send_to_channel"),
                        InlineKeyboardButton(f"غیرفعال", callback_data = "deactive_send_to_channel")
                    ],
                    [InlineKeyboardButton("برگشت »", callback_data = "back_to_main_menu")]
                ])
            )

            db.execute("UPDATE settings SET value = 'on' WHERE name = 'send_to_channel'")
            mydb.commit()

    #deactive send to channel
    if data == "deactive_send_to_channel":
        client.answer_callback_query(callback_id, "")
        db.execute("SELECT message_id FROM adminmessageid")
        message_id = db.fetchone()[0]

        db.execute("SELECT value FROM settings WHERE name = 'send_to_channel'")
        if db.fetchone()[0] == "on":
            app.edit_message_text(
                chat_id,
                message_id,
                text = "🔘 مدیریت ارسال خودکار به کانال\n\nتو این بخش میتونی تنظیم کنی که محصولات جدید فروشگاهت به صورت خودکار به کانال فرستاده بشن یا نه👇",
                reply_markup = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(f"فعال", callback_data = "active_send_to_channel"),
                        InlineKeyboardButton(f"غیرفعال ✅", callback_data = "deactive_send_to_channel")
                    ],
                    [InlineKeyboardButton("برگشت »", callback_data = "back_to_main_menu")]
                ])
            )

            db.execute("UPDATE settings SET value = 'off' WHERE name = 'send_to_channel'")
            mydb.commit()


    # edit firt admin message and show product management options
    if data == "product_management":
        client.answer_callback_query(callback_id, "شما به بخش مدیریت محصولا فروشگاه خود وارد شدید 📥")
        global ProductMainMenu
        db.execute("SELECT * FROM adminmessageid")
        message_id = db.fetchone()[1]
        ProductMainMenu = app.edit_message_text(
            chat_id = chat_id,
            message_id = message_id,
            text = "🔘 مدیریت محصولات \n\n 🛍 تو این بخش میتونی عملکرد های زیر رو روی محصولات فروشگاهت داشته باشی 👇",
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ افزودن محصول", callback_data = "add_new_product")],
                [InlineKeyboardButton("✖️ حذف محصول", callback_data = "delete_product")],
                [InlineKeyboardButton("✏️ویرایش محصول", callback_data = "with_menu_edit_product")],
                [InlineKeyboardButton("برگشت به منو اصلی 🔙", callback_data = "back_to_main_menu")]
            ])
        )

    #intro in store_management
    if data == "store_management":
        client.answer_callback_query(callback_id, "")
        db.execute("SELECT * FROM adminmessageid")
        message_id = db.fetchone()[1]
        global store_management
        store_management = app.edit_message_text(
                            chat_id,
                            message_id = message_id,
                            text = "🔘 مدیریت فروشگاه \n\n🏪 تو این بخش میتونی عملکرد های زیر رو روی  فروشگاهت داشته باشی 👇",
                            reply_markup = InlineKeyboardMarkup([
                                [
                                    InlineKeyboardButton("پنل پیامکی 💬", callback_data = "sms_panel"),
                                    InlineKeyboardButton("سبد خرید 🛒", callback_data = "cart")
                                ],
                                [
                                    InlineKeyboardButton("تخفیف ها 🔖", callback_data = "discounts"),
                                    InlineKeyboardButton("آمار فروشگاه 📊", callback_data = "store_amar")
                                ],
                                [
                                    InlineKeyboardButton("آمار فروش 📈", callback_data = "sell_amar"),
                                    InlineKeyboardButton("تنظیم شیفت کاری 👷", callback_data = "set_shift_work")
                                ],
                                [
                                    InlineKeyboardButton("تنظیم نام فروشگاه 🎟", callback_data = "set_shop_name"),
                                    InlineKeyboardButton("پیام خوشامد گویی 🤹‍♂️", callback_data = "set_welcome_text")
                                ],
                                [
                                    InlineKeyboardButton("تنظیم آیدی ارتباط 🆔", callback_data = "set_connection_id")
                                ],
                                [InlineKeyboardButton("برگشت به منو اصلی 🔙", callback_data = "back_to_main_menu")]
                            ])
        )

        db.execute(f"UPDATE adminmessageid SET message_id = {store_management.message_id}")
        mydb.commit()

    #set connection id
    if data == "set_connection_id":
        client.answer_callback_query(
                                    callback_id,
                                    "آیدی اکانت رو بدون @ بفرستید...",
                                    show_alert = True,
                                )
        global get_connection_id
        get_connection_id = True

    #set welcome text
    global set_welcome_text
    if data == "set_welcome_text":
        set_welcome_text = True
        client.answer_callback_query(
                                callback_id,
                                "متن پیام خوشامدگویی فروشگاهت رو بفرس",
                                show_alert = True,
                                )
    global set_shop_name
    if data == "set_shop_name":
        set_shop_name = True
        client.answer_callback_query(
                                callback_id,
                                "اسم فروشگاهت رو بفرس",
                                show_alert = True,
                                )

    #set_shift_work
    if data == "set_shift_work":
        client.answer_callback_query(callback_id, "")
        #select admin message id to edit
        db.execute("SELECT message_id FROM adminmessageid")
        message_id = db.fetchone()[0]

        #select status of shif work
        db.execute("SELECT value FROM settings WHERE name = 'shif_work'")
        if db.fetchone() == None:
            db.execute("INSERT INTO settings (name, value) VALUES ('shif_work', 'off')")
            mydb.commit()
        db.execute("SELECT value FROM settings WHERE name = 'shif_work'")
        status = db.fetchone()[0]

        keys = [
             [
                InlineKeyboardButton(f"فعال {'✅' if status == 'on' else ''}", callback_data = "active_shif_work"),
                InlineKeyboardButton(f"غیرفعال {'✅' if status == 'off' else ''}", callback_data = "deactive_shif_work")
            ],
        ]

        if status == "on":
            keys.append([
                            InlineKeyboardButton("تنظیم شیفت 🕒", callback_data = "set_shif_clock"),
                            InlineKeyboardButton("مشاهده شیفت 🧐", callback_data = "see_shif_work")
                        ],)

        keys.append([
            InlineKeyboardButton("برگشت »", callback_data = "back_to_store_management")
        ])

        app.edit_message_text(
            chat_id,
            message_id,
            text = "🔘 تنظیم شیفت کاری\n\nتو این بخش میتونی شیفت کاریِ فروشگاهت رو تنظیم کنی👇",
            reply_markup = InlineKeyboardMarkup(keys)
        )

    #set shif
    if data == "set_shif_clock":
        global set_shift
        set_shift = True
        client.answer_callback_query(
                                callback_id,
                                "شیفت کاری فروشگاهت رو ارسال کن〽️\n\n‼️مثال :\nاز ساعت 8 صبح تا 14 ظهر و از ساعت 17 عصر تا 10 شب\n\n‼️مثال2‌ : \nاز ساعت 8 صبح تا 10 شب به صورت یکسره بدون تعطیلی",
                                show_alert = True,
                                )
    #show shif text
    if data == "see_shif_work":
        db.execute("SELECT value FROM settings WHERE name = 'shif_text'")
        if db.fetchone() == None:
            client.answer_callback_query(
                                    callback_id,
                                    "⛔️ شیفت کاری تنظیم نشده است 🙅‍♂️\n\n⚠️ تا زمانی که شیفت تنظیم نشود برای مشتریان نشان داده نخواهد شد❗️",
                                    show_alert = True,
                                    )
        else:
            db.execute("SELECT value FROM settings WHERE name = 'shif_text'")
            client.answer_callback_query(callback_id,f"{db.fetchone()[0]}", show_alert = True)

    #active shif work
    if data == "active_shif_work":
        db.execute("SELECT value FROM settings WHERE name = 'shif_work'")
        if db.fetchone()[0] == "off":
            db.execute("UPDATE settings SET value = 'on' WHERE name = 'shif_work'")
            mydb.commit()
            keys = [
                 [
                    InlineKeyboardButton(f"فعال ✅", callback_data = "active_shif_work"),
                    InlineKeyboardButton(f"غیرفعال", callback_data = "deactive_shif_work")
                ],
                [
                    InlineKeyboardButton("تنظیم شیفت 🕒", callback_data = "set_shif_clock"),
                    InlineKeyboardButton("مشاهده شیفت 🧐", callback_data = "see_shif_work")
                ],
                [
                    InlineKeyboardButton("برگشت »", callback_data = "back_to_store_management")
                ]
            ]

            app.edit_message_text(
                chat_id,
                message_id,
                text = "🔘 تنظیم شیفت کاری\n\nتو این بخش میتونی شیفت کاریِ فروشگاهت رو تنظیم کنی👇",
                reply_markup = InlineKeyboardMarkup(keys)
            )
    #deactiv shif_work
    if data == "deactive_shif_work":
        #select admin message id to edit
        db.execute("SELECT message_id FROM adminmessageid")
        message_id = db.fetchone()[0]

        #select status of shif work
        db.execute("SELECT value FROM settings WHERE name = 'shif_work'")
        if db.fetchone()[0] == "on":
            db.execute("UPDATE settings SET value = 'off' WHERE name = 'shif_work'")
            mydb.commit()

            keys = [
                 [
                    InlineKeyboardButton(f"فعال", callback_data = "active_shif_work"),
                    InlineKeyboardButton(f"غیرفعال ✅", callback_data = "deactive_shif_work")
                ],
                [
                    InlineKeyboardButton("برگشت »", callback_data = "back_to_store_management")
                ]
            ]

            app.edit_message_text(
                chat_id,
                message_id,
                text = "🔘 تنظیم شیفت کاری\n\nتو این بخش میتونی شیفت کاریِ فروشگاهت رو تنظیم کنی👇",
                reply_markup = InlineKeyboardMarkup(keys)
            )
    #cart
    if data == "cart":
        db.execute("SELECT * FROM settings WHERE name = 'cart_active'")
        # if the settings for cart there isn't, this section will create sttings
        if db.fetchone() == None:
            db.execute("INSERT INTO settings (name, value) VALUES ('cart_active', 'True')")
            mydb.commit()
            db.execute("INSERT INTO settings (name, value) VALUES ('cart_hour', '1')")
            mydb.commit()

        #select message id for edit
        db.execute("SELECT * FROM adminmessageid")
        message_id = db.fetchone()[1]

        #select the status of cart
        db.execute("SELECT * FROM settings WHERE name = 'cart_active'")
        status = db.fetchone()[2]



        if status == "True":
            db.execute("SELECT * FROM settings WHERE name = 'cart_hour'")
            cart_hour = db.fetchone()[2]
            reply_markup = InlineKeyboardMarkup([
                                [
                                    InlineKeyboardButton(f"فعال {'✅' if status == 'True' else ''}", callback_data = "active_cart_settings"),
                                    InlineKeyboardButton(f"غیرفعال {'✅' if status == 'False' else ''}", callback_data = "deactive_cart_settings")
                                ],
                                [
                                    InlineKeyboardButton("👇 تنظیم ساعت حذف خودکار از سبد خرید 👇 ", callback_data = "l")
                                ],
                                [
                                    InlineKeyboardButton("➕", callback_data = "increase_cart_hour"),
                                    InlineKeyboardButton(f"{cart_hour}", callback_data = "blank"),
                                    InlineKeyboardButton("➖", callback_data = "decrease_cart_hour")
                                ],
                                [
                                    InlineKeyboardButton("برگشت »", callback_data = "back_to_store_management")
                                ]

                            ])
        else:
            reply_markup = InlineKeyboardMarkup([
                            [
                                InlineKeyboardButton(f"فعال {'✅' if status == 'True' else ''}", callback_data = "active_cart_settings"),
                                InlineKeyboardButton(f"غیرفعال {'✅' if status == 'False' else ''}", callback_data = "deactive_cart_settings")
                            ],
                            [
                                InlineKeyboardButton("برگشت »", callback_data = "back_to_store_management")
                            ]

                        ])


        app.edit_message_text(
                                    chat_id,
                                    message_id = message_id,
                                    text = "🔘 مدیریت سبد خرید\n\nتو این بخش میتونی تنظیمات سبد خرید رو انجام بدی👇",
                                    reply_markup = reply_markup
            )

    #activate cart
    if data == "active_cart_settings":
        db.execute("SELECT * FROM settings WHERE name = 'cart_active'")
        if db.fetchone()[2] != "True":
            db.execute("UPDATE settings SET value = 'True' WHERE name = 'cart_active'")
            mydb.commit()
            db.execute("SELECT * FROM adminmessageid")
            message_id = db.fetchone()[1]
            db.execute("SELECT * FROM settings WHERE name = 'cart_hour'")
            cart_hour = db.fetchone()[2]
            app.edit_message_text(
                                        chat_id,
                                        message_id = message_id,
                                        text = "🔘 مدیریت سبد خرید\n\nتو این بخش میتونی تنظیمات سبد خرید رو انجام بدی👇",
                                        reply_markup = InlineKeyboardMarkup([
                                            [
                                                InlineKeyboardButton("فعال ✅", callback_data = "active_cart_settings"),
                                                InlineKeyboardButton("غیرفعال", callback_data = "deactive_cart_settings")
                                            ],
                                            [
                                                InlineKeyboardButton("👇 تنظیم ساعت حذف خودکار از سبد خرید 👇 ", callback_data = "l")
                                            ],
                                            [
                                                InlineKeyboardButton("➕", callback_data = "increase_cart_hour"),
                                                InlineKeyboardButton(f"{cart_hour}", callback_data = "blank"),
                                                InlineKeyboardButton("➖", callback_data = "decrease_cart_hour")
                                            ],
                                            [
                                                InlineKeyboardButton("برگشت »", callback_data = "back_to_store_management")
                                            ]
                                        ])
                )


    #deactive cart
    if data == "deactive_cart_settings":
        db.execute("UPDATE settings SET value = 'False' WHERE name = 'cart_active'")
        mydb.commit()
        app.edit_message_text(
                                    chat_id,
                                    message_id = message_id,
                                    text = "🔘 مدیریت سبد خرید\n\nتو این بخش میتونی تنظیمات سبد خرید رو انجام بدی👇",
                                    reply_markup = InlineKeyboardMarkup([
                                        [
                                            InlineKeyboardButton("فعال", callback_data = "active_cart_settings"),
                                            InlineKeyboardButton("غیرفعال ✅", callback_data = "deactive_cart_settings")
                                        ],
                                        [
                                            InlineKeyboardButton("برگشت »", callback_data = "back_to_store_management")
                                        ]
                                    ])
            )

    #increase cart hour
    if data == "increase_cart_hour":
        db.execute("SELECT * FROM settings WHERE name = 'cart_hour'")
        cart_hour = int(db.fetchone()[2]) + 1
        if cart_hour > 24:cart_hour = "1"
        db.execute(f"UPDATE settings SET value = '{cart_hour}' WHERE name = 'cart_hour'")
        mydb.commit()

        db.execute("SELECT * FROM adminmessageid")
        message_id = db.fetchone()[1]
        app.edit_message_text(
                                    chat_id,
                                    message_id = message_id,
                                    text = "🔘 مدیریت سبد خرید\n\nتو این بخش میتونی تنظیمات سبد خرید رو انجام بدی👇",
                                    reply_markup = InlineKeyboardMarkup([
                                        [
                                            InlineKeyboardButton("فعال ✅", callback_data = "active_cart_settings"),
                                            InlineKeyboardButton("غیرفعال", callback_data = "deactive_cart_settings")
                                        ],
                                        [
                                            InlineKeyboardButton("👇 تنظیم ساعت حذف خودکار از سبد خرید 👇 ", callback_data = "l")
                                        ],
                                        [
                                            InlineKeyboardButton("➕", callback_data = "increase_cart_hour"),
                                            InlineKeyboardButton(f"{cart_hour}", callback_data = "blank"),
                                            InlineKeyboardButton("➖", callback_data = "decrease_cart_hour")
                                        ],
                                        [
                                            InlineKeyboardButton("برگشت »", callback_data = "back_to_store_management")
                                        ]
                                    ])
            )

    #decrease cart hour
    if data == "decrease_cart_hour":
        db.execute("SELECT * FROM settings WHERE name = 'cart_hour'")
        cart_hour = int(db.fetchone()[2]) - 1
        if cart_hour < 1:cart_hour = "24"
        db.execute(f"UPDATE settings SET value = '{cart_hour}' WHERE name = 'cart_hour'")
        mydb.commit()

        db.execute("SELECT * FROM adminmessageid")
        message_id = db.fetchone()[1]
        app.edit_message_text(
                                    chat_id,
                                    message_id = message_id,
                                    text = "🔘 مدیریت سبد خرید\n\nتو این بخش میتونی تنظیمات سبد خرید رو انجام بدی👇",
                                    reply_markup = InlineKeyboardMarkup([
                                        [
                                            InlineKeyboardButton("فعال ✅", callback_data = "active_cart_settings"),
                                            InlineKeyboardButton("غیرفعال", callback_data = "deactive_cart_settings")
                                        ],
                                        [
                                            InlineKeyboardButton("👇 تنظیم ساعت حذف خودکار از سبد خرید 👇 ", callback_data = "l")
                                        ],
                                        [
                                            InlineKeyboardButton("➕", callback_data = "increase_cart_hour"),
                                            InlineKeyboardButton(f"{cart_hour}", callback_data = "blank"),
                                            InlineKeyboardButton("➖", callback_data = "decrease_cart_hour")
                                        ],
                                        [
                                            InlineKeyboardButton("برگشت »", callback_data = "back_to_store_management")
                                        ]
                                    ])
            )


    #back to stor management panel
    if data == "back_to_store_management":
        db.execute("SELECT * FROM adminmessageid")
        message_id = db.fetchone()[1]
        app.edit_message_text(
                                    chat_id,
                                    message_id = message_id,
                                    text = store_management.text,
                                    reply_markup = store_management.reply_markup
                            )

    #handle discounts
    if data == "discounts":
        keys = []

        db.execute("SELECT * FROM discounts WHERE status = 'active'")
        if db.fetchone() == None:
            keys.append([InlineKeyboardButton("➕ افزودن تخفیف جدید 🔖", callback_data = "add_new_discount")])
        else:
            db.execute("SELECT id,percent FROM discounts WHERE status = 'active'")
            percent = db.fetchone()
            keys.append(
                [
                    InlineKeyboardButton(f"{percent[1]} ✅", callback_data = f"detail_discount_{percent[0]}"),
                    InlineKeyboardButton("تخفیف فعال : ", callback_data = "blank")
                ]
            )
            keys.append([InlineKeyboardButton("❌ غیرفعال کردن تخفیف فعال ❌", callback_data = "deactive_discount")])
            keys.append([InlineKeyboardButton("🗂 مشاهده همه تخفیف های قبلی فروشگاه 🗂", callback_data = "see_all_pervios_discounts")])
        #back button
        keys.append([InlineKeyboardButton("برگشت »", callback_data = "back_to_store_management")])
        db.execute('SELECT * FROM adminmessageid')
        message_id = db.fetchone()[1]

        app.edit_message_text(
                        chat_id,
                        message_id = message_id,
                        text = "🔘 مدیریت تخفیف\n\nتو این بخش میتونی تنظیمات تخفیف ها رو انجام بدی👇",
                        reply_markup = InlineKeyboardMarkup(keys)
        )

        keys = []

    if data == "deactive_discount":
        db.execute("UPDATE discounts SET status = 'deactive' WHERE status = 'active'")
        mydb.commit()

        keys = []
        db.execute("SELECT message_id FROM adminmessageid")
        message_id = db.fetchone()[0]

        app.edit_message_text(
                                chat_id,
                                message_id = message_id,
                                text = "🔘 مدیریت تخفیف\n\nتو این بخش میتونی تنظیمات تخفیف ها رو انجام بدی👇",
                                reply_markup = InlineKeyboardMarkup([
                                    [InlineKeyboardButton("➕ افزودن تخفیف جدید 🔖", callback_data = "add_new_discount")],
                                    [InlineKeyboardButton("برگشت »", callback_data = "back_to_store_management")]
                                ])
        )

        #db.execute("UPDATE status SET ")
    if data == "add_new_discount":
        client.answer_callback_query(
                                callback_id,
                                "⚠️ توجه : تخفیف افزوده شده به عنوان تخفیف فعال محسوب میشه و روی همه محصولات فروشگاهت اعمال میشه\n\n🔻درصد تخفیف و  علت تخفیف رو به صورت زیر بفرست :‌\n15 عید نوروز",
                                show_alert = True,
                                )

        get_new_discount = True

    if data.startswith("detail_discount_"):
        id = data.split("_")[-1]
        db.execute(f"SELECT * FROM discounts WHERE id = {int(id)}")
        discount_detail = db.fetchone()
        date = str(discount_detail[4]).split("-")
        date = jdatetime.date.fromgregorian(day = int(date[2]), month = int(date[1]), year = int(date[0]))
        date = str(date).split("-")[0] + "/" + str(date).split("-")[1] + "/" + str(date).split("-")[2]
        client.answer_callback_query(
                                    callback_id,
                                    f"وضعیت تخفیف : {'فعال' if discount_detail[2] == 'active' else 'غیر فعال'}\nمناسبت : {discount_detail[3]}\nتاریخ ثبت : {str(date)}",
                                    show_alert = True,
                                )


    # back to main menu
    if data == "back_to_main_menu":
        client.answer_callback_query(callback_id, "شما به منو اصلی پنل ادمین  برگشتید🔺")
        db.execute("SELECT * FROM adminmessageid")
        message_id = db.fetchone()[1]
        app.edit_message_text(
            chat_id = chat_id,
            message_id = message_id,
            text = AdminMainMessage.text,
            reply_markup = AdminMainMessage.reply_markup
        )




    #add new product
    global product
    if data == "add_new_product":
        get_product_image_or_not = True
        app.send_message(chat_id, "عکس محصولتو بفرس🖼📮")
        db.execute("SELECT * FROM adminmessageid")
        message_id = db.fetchone()[1]
        cancel_adding_product  = app.edit_message_text(
            chat_id,
            message_id = message_id,
            text = "شما در حال اضافه کردن محصول به فروشگاه خودتون هستن\n\nبرای لغو کردن افزودن محصول دکمه زیر را فشار دهید",
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("لغو کردن", callback_data = "cancel-add-product")]
            ])
        )

        db.execute(f"UPDATE adminmessageid SET message_id = {cancel_adding_product.message_id}")
        mydb.commit()

    #cancel adding product
    if data == "cancel-add-product":
        get_product_image_or_not = False
        get_product_name_or_not = False
        get_product_count_or_not = False
        get_product_description_or_not = False
        get_product_unit_or_not = False
        get_product_price_or_not = False

        db.execute("SELECT * FROM adminmessageid")
        message_id = db.fetchone()[1]
        app.delete_messages(chat_id, message_id)

        cancel = app.send_message(chat_id = chat_id,
                        text = "شما فرآیند افزودن محصول رو لغو کردین",
                        reply_markup = InlineKeyboardMarkup([
                                [
                                    InlineKeyboardButton("برگشت »", callback_data = "back_to_main_menu")
                                ]
        ]))
        db.execute(F"UPDATE adminmessageid SET message_id = {cancel.message_id}")
        mydb.commit()


    #next step for giving product count
    if data == "next-step-count":
        get_product_count_or_not = True
        app.send_message(chat_id,
        "تعداد موجودی محصولت رو بفرس...⛓"
    )

    #giving unit
    if data == "next-step-unit":
        get_product_unit_or_not = True
        app.send_message(
                    chat_id,
                    "خب الان واحد شمارش محصولاتت رو بفرس\n\nمثل : عدد/ گرم / کیلوگرم / بسته یا ..."
        )

    #giving price
    if data == "next-step-price":
        get_product_price_or_not = True
        app.send_message(
                chat_id,
                "تو این مرحله باید قیمت هر واحد از محصولت رو به تومان بفرستی\n\nمثلا اگه تو مرحله قبل واحد محصولت رو 'بسته' انتخاب کردی  الان باید قیمت هر بسته از محصولت رو به تومان بگی"
                )

    if data == "set_product_description":
        get_product_description_or_not = True
        app.send_message(
                chat_id,
                "توضیحات محصولت رو بفرس📃"
        )
        app.delete_messages(chat_id, PriceMessage.message_id)

    if data == "dont_set_product_description":
        SendAddedProduct(client, message, chat_id)
        app.delete_messages(chat_id, PriceMessage.message_id)


    #submiting new product
    if data == "submit-product":
        #product with description
        if "description" in product.keys():
            query = f"""
                            INSERT INTO product (photo, name, count, unit, price, description)
                            VALUES ('{str(product['photo'])}',
                                    '{product['name']}',
                                     {product['count']},
                                    '{product['unit']}',
                                    '{product['price']}',
                                    '{product['description']}')
                            """


        #product without description
        else:
            query = f"""
                            INSERT INTO product
                            (photo, name, count, unit, price)
                            VALUES ('{str(product['photo'])}',
                                    '{product['name']}',
                                     {product['count']},
                                    '{product['unit']}',
                                    '{product['price']}')
                            """

        db.execute(query)
        mydb.commit()

        # getting the last product code
        db.execute("SELECT MAX(code) FROM product")
        last_product = db.fetchone()
        app.send_message(chat_id,
                        f"محصول شما با موفقیت ثبت شد\n\nکد محصول : {last_product[0]}")

        db.execute("SELECT * FROM adminmessageid")
        message_id = db.fetchone()[1]
        app.delete_messages(chat_id, message_id)

        db.execute("SELECT value FROM settings WHERE name = 'bot_channel'")
        channel = db.fetchone()[0]

        db.execute(f"SELECT * FROM product WHERE code = {last_product[0]}")
        fetched_data = db.fetchone()
        product["photo"] = fetched_data[1]
        product["name"] = fetched_data[2]
        product["count"] = fetched_data[3]
        product["unit"] = fetched_data[4]
        product["price"] = fetched_data[5]

        text = f"🔗{product['name']}\n\nتعداد موجودی : {product['count']} {product['unit']}\nقیمت : هر {product['unit']}, {product['price']}  هزار تومان"


        if len(fetched_data) == 7:
            product["description"] = fetched_data[6]
            text = f"🔗{product['name']}\n\nتعداد موجودی : {product['count']} {product['unit']}\nقیمت : هر {product['unit']}, {product['price']}  هزار تومان\nتوضیحات : {product['description']}"


        app.send_photo(
                                        channel,
                                        photo = product["photo"],
                                        caption = text,
                                        reply_markup = InlineKeyboardMarkup([
                                            [
                                                InlineKeyboardButton("مشاهده محصول 👁", url = f"http://t.me/vajd_shop_bot?start={last_product[0]}")
                                            ]
                                        ])
                                    )




    #edit product information (main)
    if data == "edit-product-information":
        global sent_product
        app.edit_message_text(
                            chat_id,
                            message_id = sent_product.message_id,
                            text = "کدوم یک از مشخصات محصولت رو میخوای ویرایش کنی؟",
                            reply_markup = InlineKeyboardMarkup([
                                [
                                    InlineKeyboardButton("واحد", callback_data = "edit_product_unit"),
                                    InlineKeyboardButton("تعداد", callback_data = "edit_product_count"),
                                    InlineKeyboardButton("نام", callback_data = "edit_product_name"),

                                ],
                                [
                                    InlineKeyboardButton("توضیحات", callback_data = "edit_product_description"),
                                    InlineKeyboardButton("قیمت", callback_data = "edit_product_price"),

                                ],
                                [
                                    InlineKeyboardButton("برگشت »", callback_data = "back_to_submiting")
                                ]
                            ])
                        )

    global edit_product_info
    global variable_edit_after_submiting
    if data.startswith("edit_product"):
        global edit_type
        edit_dictionary = {
                            "name" :"نام",
                            "count" : "تعداد",
                            "unit" : "واحد",
                            "price" : "قیمت",
                            "description" : "توضیحات"
                        }
        edit_type = data.split("_")[-1]
        edit_product_info[edit_type] = True
        app.send_message(chat_id, f"لطفا {edit_dictionary[edit_type]} جدید رو بفرس🔖")

    #back to product management page
    if data == "back_to_product_management":
        product = {}
        db.execute("SELECT * FROM adminmessageid")
        message_id = db.fetchone()[1]
        app.delete_messages(chat_id, message_id)
        ProductMainMenu = app.send_message(
                            chat_id,
                            text = ProductMainMenu.text,
                            reply_markup = ProductMainMenu.reply_markup,
        )
        db.execute(f"UPDATE adminmessageid SET message_id = {ProductMainMenu.message_id}")
        mydb.commit()



    # back to submiting section
    if data == "back_to_submiting":
        try:
            sent_product = app.edit_message_text(
                        chat_id,
                        reply_markup = sent_product.reply_markup,
                        text = f"🔗{product['name']}\n\nتعداد موجودی : {product['count']} {product['unit']}\nقیمت : هر {product['unit']}, {product['price']}  هزار تومان\nتوضیحات : {product['description']}",
                        message_id  = sent_product.message_id
                    )

        except KeyError:
            caption = f"🔗{product['name']}\n\nتعداد موجودی : {product['count']} {product['unit']}\nقیمت : هر {product['unit']}, {product['price']}  هزار تومان"
            sent_product = app.edit_message_text(
                        chat_id,
                        reply_markup = sent_product.reply_markup,
                        text = caption,
                        message_id  = sent_product.message_id
                    )

    #manage for edit product with pannel
    global GetEditCode
    global variable_edit_after_submiting

    if data == "with_menu_edit_product":
        GetEditCode = True
        variable_edit_after_submiting = True
        get_code_message = app.send_message(chat_id, "لطفا کد محصول مورد نظرتو برای ویرایش بفرس🈁")


    #delete product
    if data == "delete_product":
        global GetDeleteCode
        GetDeleteCode = True
        app.send_message(chat_id, "لطفا کد محصول مورد نظرتو برای حذف بفرس❌")


    if data == "delete_product_button":
        db.execute(f"DELETE FROM product WHERE code = {delete_code}")
        mydb.commit()
        db.execute("SELECT * FROM adminmessageid")
        message_id = db.fetchone()[1]
        app.delete_messages(chat_id, message_id)
        app.send_message(chat_id, "محصول مورد نظر با موفقیت حذف شد ✅")


    #write all of the discounts in exel file
    if data == "see_all_pervios_discounts":
        counter_row = 1
        counter_column = 0


        wb = Workbook()
        sheet = wb.add_sheet("لیست تخفیف ها")
        sheet.cols_right_to_left = True
        db.execute("SELECT * FROM discounts")
        sheet.write(0,0, "آیدی")
        sheet.write(0,1, "درصد")
        sheet.write(0,2, "وضعیت")
        sheet.write(0,3, "دلیل")
        sheet.write(0,4, "تاریخ")

        for discount in db.fetchall():
            date = discount[-1]
            discount = list(discount)
            del discount[-1]
            date = str(date).split("-")
            date = jdatetime.date.fromgregorian(day = int(date[2]), month = int(date[1]), year = int(date[0]))
            date = str(date).split("-")[0] + "/" + str(date).split("-")[1] + "/" + str(date).split("-")[2]
            discount.append(date)

            discount = tuple(discount)


            for i in discount:
                sheet.write(counter_row,counter_column, f"{i}")
                counter_column += 1
            counter_column = 0
            counter_row += 1

        wb.save('کل تخفیف ها.xls')


        #send saved file to admin
        app.send_document(chat_id, 'کل تخفیف ها.xls', caption = "🔖همه تخفیف ها افزوده شده در فروشگاه شما از ابتدای راه اندازی\n📂به صورت فایل اکسل")

@app.on_message(filters.forwarded)
def Forwarded(client, message):
    global forward_to_all

    if forward_to_all == True:
        db.execute(f"SELECT name FROM settings WHERE name = '{message.chat.id}'")
        admin_id = db.fetchone()[0]
        db.execute("SELECT user_id FROM users")
        counter = 0
        counter2 = 0
        for i in db.fetchall():
            if i[0] != admin_id:
                try:
                    app.forward_messages(f"{i[0]}", f"{admin_id}", message.message_id)
                    counter += 1
                    print("yess")
                except BadRequest:
                    counter2 += 1

        app.send_message(int(admin_id), f"پیام فوق به کاربران ارسال شد ✅\n\n<strong>📌موفق : </strong>{counter} کاربر\n<strong>📌ناموفق : </strong>{counter2} کاربر")
        forward_to_all = False

    else:
        print("byyyyyy")


@app.on_message(filters.text)
def GetTexts(client, message):
    global get_new_password
    global get_connection_id
    global get_code_delete_cart
    global get_product_name_or_not
    global get_product_count_or_not
    global get_product_unit_or_not
    global get_product_price_or_not
    global get_product_description_or_not
    global sent_product
    global GetEditCode
    global code
    global GetDeleteCode
    global get_new_discount
    global set_shift
    global add_group_or_channel_to_bot
    global set_welcome_text
    global set_shop_name
    global get_auth_code
    global get_product_count_cart
    global get_code_add_to_cart
    global message_to_all


    #giving news password
    if get_new_password == True:
        db.execute("SELECT * FROM settings WHERE name = 'password'")
        if db.fetchone() == None:
            db.execute(f"INSERT INTO settings (name, value) VALUES ('password', '{message.text}')")
        else:
            db.execute(f"UPDATE settings SET value = '{message.text}' WHERE name = 'password'")
        mydb.commit()

        app.send_message(
                message.chat.id,
                f"رمز جدید ثبت شد✅\n\n<strong>رمز جدید : </strong>{message.text}",
                parse_mode = "html"
                )
        get_new_password = False

    #givin account id
    elif get_connection_id == True:
        db.execute("SELECT * FROM settings WHERE name = 'id'")
        if db.fetchone() == None:
            db.execute(f"INSERT INTO settings (name, value) VALUES ('id', '{message.text}')")
        else:
            db.execute(f"UPDATE settings SET value = '{message.text}' WHERE name = 'id'")
        mydb.commit()

        app.send_message(
                    message.chat.id,
                    f"آیدی ارتباط پشتیبانی فروشگاه تنظیم شد✅\n\n<strong>🆔آیدی پشتیبانی :</strong> @{message.text} 👤",
                    parse_mode = "html"
                )
        get_connection_id = False

    #givin code to delete product from cart
    elif get_code_delete_cart == True:
        delete_code2 = message.text
        if delete_code2.isdigit():
            #select product
            db.execute(f"SELECT * FROM product WHERE code = '{delete_code2}'")
            delete_product = db.fetchone()
            if delete_product != None:
                #select user
                db.execute(f"SELECT id FROM users WHERE user_id = '{message.from_user.id}'")
                user_id = db.fetchone()[0]

                #select from cart
                db.execute(f"SELECT * FROM cart WHERE product = '{delete_product[0]}' AND user = '{user_id}'")
                delete_product_cart = db.fetchone()

                if delete_product_cart != None:
                    product["photo"] = delete_product[1]
                    product["name"] = delete_product[2]
                    product["count"] = delete_product[3]
                    product["unit"] = delete_product[4]
                    product["price"] = delete_product[5]

                    text = f"🔗{product['name']}\n\nتعداد موجودی : {product['count']} {product['unit']}\nقیمت : هر {product['unit']}, {product['price']}  هزار تومان"


                    if len(delete_product) == 7:
                        product["description"] = fetched_data[6]
                        text = f"🔗{product['name']}\n\nتعداد موجودی : {product['count']} {product['unit']}\nقیمت : هر {product['unit']}, {product['price']}  هزار تومان\nتوضیحات : {product['description']}"

                    aa = app.send_photo(
                                    message.chat.id,
                                    photo = product["photo"],
                                    caption = text,
                                    reply_markup = InlineKeyboardMarkup([
                                        [InlineKeyboardButton("حذف از سبد خرید ❌", callback_data = f"delete_product_button_cart_{delete_product[0]}")],
                                        [InlineKeyboardButton("🔱 لغو کردن", callback_data = "cancel_delete_product")]

                                    ])
                                )
                    db.execute(f"UPDATE chat_id SET message_id = '{aa.message_id}'")
                    mydb.commit()

                elif delete_product_cart == None:
                    app.send_message(message.chat.id, "شما این محصول را در سبد خرید خود ندارید ⚠️")
            elif delete_product == None:
                app.send_message(message.chat.id, "محصول مورد نظر شما یافت نشد⛔️")

    #givin product name
    elif get_product_name_or_not == True:
        product["name"] = message.text
        get_product_name_or_not = False
        global NameMessage
        NameMessage = app.send_message(
                message.chat.id,
                "اسم محصولت رو هم گرفتم✅\n\nبزن رو دکمه زیر تا بریم مرحله بعدی",
                reply_markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton("مرحله بعد »", callback_data = "next-step-count")]
                ])
                )


    #giving product count
    elif get_product_count_or_not == True:
        if message.text.isdigit():
            product["count"] = message.text
            get_product_count_or_not = False
            global CountMessage

            CountMessage = app.send_message(
                            message.chat.id,
                            "تعداد موجودی محصولت رو هم گرفتم✅\n\nبزن رو دکمه زیر تا بریم مرحله بعدی",
                            reply_markup = InlineKeyboardMarkup([
                                [
                                    InlineKeyboardButton("مرحله بعد »", callback_data = "next-step-unit"),
                                ]
                            ])
                            )
            app.delete_messages(message.chat.id, NameMessage.message_id)

    elif get_product_unit_or_not == True:
        product["unit"] = message.text
        get_product_unit_or_not = False
        global UnitMessage
        UnitMessage = app.send_message(
            message.chat.id,
            "واحد محصولت هم دریافت شد✅\n\nبزن رو دکمه زیر تا بریم مرحله بعدی",
            reply_markup = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("مرحله بعد »", callback_data = "next-step-price"),
                ]
            ])
        )
        app.delete_messages(message.chat.id, CountMessage.message_id)


    elif get_product_price_or_not == True:
        if message.text.isdigit():
            product["price"] = message.text
            get_product_price_or_not = False
            global PriceMessage
            PriceMessage = app.send_message(
                    message.chat.id,
                    text = "قیمت هر واحد از محصولت رو هم گرفتم✅\n\nمیخای توضیحات اضافه کنی به محصولت؟🤔",
                    reply_markup = InlineKeyboardMarkup([
                                        [
                                            InlineKeyboardButton("آره میخام 📝", callback_data = "set_product_description"),
                                            InlineKeyboardButton("نه ❗️", callback_data = "dont_set_product_description")
                                        ]
                                    ])
            )
            app.delete_messages(message.chat.id, UnitMessage.message_id)

    elif get_product_description_or_not == True:
        product["description"] = message.text
        get_product_description_or_not = False
        app.send_message(
                message.chat.id,
                text  = "توضیحات محصولت رو هم گرفتم✅"
        )
        app.delete_messages(message.chat.id, PriceMessage.message_id)
        app.delete_messages(
                        message.chat.id,
                        AdminMainMessage.message_id,
                        )

        SendAddedProduct(client, message, message.chat.id)



    elif GetEditCode == True:
        code = message.text
        db.execute(f"SELECT * FROM product WHERE code = {code}")
        fetched_data = db.fetchone()
        product["photo"] = fetched_data[1]
        product["name"] = fetched_data[2]
        product["count"] = fetched_data[3]
        product["unit"] = fetched_data[4]
        product["price"] = fetched_data[5]

        text = f"🔗{product['name']}\n\nتعداد موجودی : {product['count']} {product['unit']}\nقیمت : هر {product['unit']}, {product['price']}  هزار تومان"


        if len(fetched_data) == 7:
            product["description"] = fetched_data[6]
            text = f"🔗{product['name']}\n\nتعداد موجودی : {product['count']} {product['unit']}\nقیمت : هر {product['unit']}, {product['price']}  هزار تومان\nتوضیحات : {product['description']}"


        sent_product = app.send_photo(message.chat.id, photo = product["photo"], caption = text,
                            reply_markup = InlineKeyboardMarkup([
                                [
                                    InlineKeyboardButton("واحد", callback_data = "edit_product_unit"),
                                    InlineKeyboardButton("تعداد", callback_data = "edit_product_count"),
                                    InlineKeyboardButton("نام", callback_data = "edit_product_name"),

                                ],
                                [
                                    InlineKeyboardButton("توضیحات", callback_data = "edit_product_description"),
                                    InlineKeyboardButton("قیمت", callback_data = "edit_product_price"),

                                ],
                                [
                                    InlineKeyboardButton("برگشت »", callback_data = "back_to_product_management")
                                ]
                            ]))
        db.execute(f"UPDATE adminmessageid SET message_id = {sent_product.message_id}")
        mydb.commit()

        GetEditCode = False

    elif GetDeleteCode == True:
        global delete_code
        delete_code = message.text
        db.execute(f"SELECT * FROM product WHERE code = {delete_code}")
        fetched_data = db.fetchone()

        product["photo"] = fetched_data[1]
        product["name"] = fetched_data[2]
        product["count"] = fetched_data[3]
        product["unit"] = fetched_data[4]
        product["price"] = fetched_data[5]

        text = f"🔗{product['name']}\n\nتعداد موجودی : {product['count']} {product['unit']}\nقیمت : هر {product['unit']}, {product['price']}  هزار تومان"


        if len(fetched_data) == 7:
            product["description"] = fetched_data[6]
            text = f"🔗{product['name']}\n\nتعداد موجودی : {product['count']} {product['unit']}\nقیمت : هر {product['unit']}, {product['price']}  هزار تومان\nتوضیحات : {product['description']}"

        sent_product = app.send_photo(
                                        message.chat.id,
                                        photo = product["photo"],
                                        caption = text,
                                        reply_markup = InlineKeyboardMarkup([
                                            [
                                                InlineKeyboardButton("❌ حذف محصول ❌", callback_data = "delete_product_button"),
                                                InlineKeyboardButton("🔱 لغو کردن", callback_data = "cancel_delete_product")
                                            ]
                                        ])
                                    )

        db.execute(f"UPDATE adminmessageid SET message_id = {sent_product.message_id}")
        mydb.commit()

        GetDeleteCode = False




    elif get_new_discount == True:
        percent = message.text.split()[0]
        cause = " ".join(message.text.split()[1:])
        db.execute(f"INSERT INTO discounts (percent, status, cause) VALUES ('{percent}', 'active', '{cause}')")
        mydb.commit()
        get_new_discount = False

        keys = []
        db.execute("SELECT * FROM discounts WHERE status = 'active'")
        if db.fetchone() == None:
            keys.append([InlineKeyboardButton("➕ افزودن تخفیف جدید 🔖", callback_data = "add_new_discount")])
        else:
            db.execute("SELECT id,percent FROM discounts WHERE status = 'active'")
            percent = db.fetchone()
            keys.append(
                [
                    InlineKeyboardButton(f"{percent[1]} ✅", callback_data = f"detail_discount_{percent[0]}"),
                    InlineKeyboardButton("تخفیف فعال : ", callback_data = "blank")
                ]
            )
            keys.append([InlineKeyboardButton("❌ غیرفعال کردن تخفیف فعال ❌", callback_data = "deactive_discount")])
            keys.append([InlineKeyboardButton("🗂 مشاهده همه تخفیف های قبلی فروشگاه 🗂", callback_data = "see_all_pervios_discounts")])
        #back button
        keys.append([InlineKeyboardButton("برگشت »", callback_data = "back_to_store_management")])
        db.execute('SELECT * FROM adminmessageid')
        message_id = db.fetchone()[1]

        app.send_message(message.chat.id, text = f"📌تخفیف {percent[1]} درصدی \n به مناسبت {cause}\n به همه محصولات فروشگاهت اضافه شد〽️")
        app.delete_messages(message.chat.id, message_id)
        app.send_message(
                        chat_id = message.chat.id,
                        text = "🔘 مدیریت تخفیف\n\nتو این بخش میتونی تنظیمات تخفیف ها رو انجام بدی👇",
                        reply_markup = InlineKeyboardMarkup(keys)
        )

        keys = []

    elif set_shift == True:
        db.execute("SELECT value FROM settings WHERE name = 'shif_text'")
        if db.fetchone() == None:
            db.execute(f"INSERT INTO settings (name, value) VALUES ('shif_text', '{message.text}')")
        else:
            db.execute(f"UPDATE settings SET value = '{message.text}' WHERE name = 'shif_text'")
        mydb.commit()

        message.reply_text("متن شیفت کاری با موفقیت ثبت شد✅")
        set_shift = False

    # giving id for set channel
    elif add_group_or_channel_to_bot == True:
        db.execute("SELECT value FROM settings WHERE name = 'bot_channel'")
        if db.fetchone() == None:
            db.execute(f"INSERT INTO settings (name, value) VALUES ('bot_channel', '{message.text}')")
        else:
            db.execute(f"UPDATE settings SET value = '{message.text}' WHERE name = 'bot_channel'")
        mydb.commit()

        app.send_message(message.chat.id, f"لینک کانال : {message.text}\n\n⛔️توجه⛔️\nربات رو حتما باید توی کانال مورد نظر ادمین کنی تا به درستی کار بکنه. یادت نره\n⚠️همین الان ادمینش کن")
        add_group_or_channel_to_bot = False

    elif set_welcome_text == True:
        db.execute("SELECT value FROM settings WHERE name = 'welcome_text'")
        if db.fetchone() != None:
            db.execute(f"UPDATE settings SET value = '{message.text}' WHERE name = 'welcome_text'")
        else:
            db.execute(f"INSERT INTO settings (name, value) VALUES ('welcome_text', '{message.text}')")
        mydb.commit()
        message.reply_text("متن خوشامدگویی فروشگاه دریافت شد ✅")
        set_welcome_text = False

    elif set_shop_name == True:
        db.execute("SELECT value FROM settings WHERE name = 'shop_name'")
        if db.fetchone() != None:
            db.execute(f"UPDATE settings SET value = '{message.text}' WHERE name = 'shop_name'")
        else:
            db.execute(f"INSERT INTO settings (name, value) VALUES ('shop_name', '{message.text}')")
        mydb.commit()
        message.reply_text("نام فروشگاه شما دریافت شد ✅")
        set_shop_name = False

    elif get_auth_code == True:
        get_code = message.text
        db.execute(f"SELECT code FROM cart_code WHERE chat_id = '{message.chat.id}'")
        db_code = db.fetchone()[0]
        if get_code.isdigit() and get_code == db_code:
            app.send_message(message.chat.id,"کد صحیح است✅\n\nحساب شما تایید شد💐")
            get_auth_code = False
            db.execute(f"DELETE FROM cart_code WHERE chat_id = '{message.chat.id}'")
            db.execute(f"UPDATE cart_info SET status = 'active' WHERE chat_id = '{message.chat.id}'")
            mydb.commit()
            db.execute("SELECT message_id FROM adminmessageid")
            message_id = db.fetchone()[0]

            app.delete_messages(message.chat.id, message_id)
            db.execute("SELECT value FROM settings WHERE name = 'welcome_text'")
            welcome_text = db.fetchone()[0]
            db.execute("SELECT value FROM settings WHERE name = 'id'")
            id = db.fetchone()[0]
            a = app.send_message(
                            message.chat.id,
                            text = welcome_text,
                            reply_markup = InlineKeyboardMarkup([
                                [InlineKeyboardButton("سبد خرید 🛒", callback_data = "customer_see_cart")],
                                [InlineKeyboardButton("ارتباط با پشتیبانی فروشگاه 👤", url = f"https://t.me/{id}")],
                                [InlineKeyboardButton("💻 ارتباط به برنامه نویس ربات 💻", url = "https://t.me/hasan_zltn9")]
                            ])
            )

            app.send_message(message.chat.id, "<strong>جستجوی محصول در ربات فعال است📌</strong>\n\nکافیه <strong>کد</strong> یا <strong>اسم </strong> محصول مورد نظرتو بفرستی👌\n\nیا خودش رو پیدا میکنم یا مشابه اش رو😉",
                            parse_mode = "html")
            db.execute(f"UPDATE adminmessageid SET message_id = '{a.message_id}'")
            mydb.commit()
        else:
            app.send_message(message.chat.id, "کد اشتباه است🚫\n\nکد صحیح را دوباره ارسال کنید")

    elif get_product_count_cart == True:
        count = message.text
        if count.isdigit():
            db.execute(f"SELECT count FROM product WHERE code = {add_to_cart_dict['product']}")
            product_count = db.fetchone()
            if (int(product_count[0]) - int(count)) >= 0:
                add_to_cart_dict["count"] = count
                #insert new product to cart
                try:
                    db.execute(f"INSERT INTO cart (product, user, count) VALUES ('{add_to_cart_dict['product']}', '{add_to_cart_dict['user']}', {add_to_cart_dict['count']})")
                    mydb.commit()


                    #get product name
                    db.execute(f"SELECT name,unit,code FROM product WHERE code = {add_to_cart_dict['product']}")
                    product_name = db.fetchone()

                    #add count to reserv column in product table
                    db.execute(f"UPDATE product SET reserv = {count} WHERE code = {product_name[2]}")
                    mydb.commit()

                    #get hour for delete product from cart
                    db.execute("SELECT value FROM settings WHERE name = 'cart_hour'")
                    cart_hour = db.fetchone()[0]

                    app.send_message(
                        message.chat.id,
                        f"🛍محصول <strong>[ {product_name[0]} ]</strong> کد <strong>[ {add_to_cart_dict['product']} ] به تعداد <strong> [ {count} ]</strong> {product_name[1]}</strong> به سبد خرید شما اضافه شد✅\n\n⚠️اگر محصول موجود در سبد خرید پرداخت نهایی نشود به صورت خودکار بعد از <strong>{cart_hour}</strong> ساعت از سبد شما حذف خواهد شد!"
                    )

                    db.execute(f"SELECT message_id FROM chat_id WHERE chat_id = '{message.chat.id}'")
                    message_id = db.fetchone()[0]
                    app.delete_messages(message.chat.id, message_id)
                except Exception as m:
                    if m.errno == 1062:
                        app.send_message(
                            message.chat.id,
                            "<strong>شما قبلا این محصول رو به سبد خریدتون اضافه کردین❗️</strong>",
                            parse_mode = "html",
                            reply_markup = InlineKeyboardMarkup([
                                [
                                    InlineKeyboardButton("مشاهده سبد خرید 🛒", callback_data = "customer_see_cart"),
                                    InlineKeyboardButton("حذف از سبد خرید ❌", callback_data = "delete_product_cart")
                                ]
                            ])
                        )
                        get_product_count_cart = False
                    else:
                        print(m)

            else:
                app.send_message(
                            message.chat.id,
                            f"تعداد درخواست شما بیشتر از موجودی این محصول است❌\nلطفا دوباره تعداد درخواست خودتون رو اسال کنید...\n\n<strong>تعداد موجودی : {product_count[0]}</strong>",
                            parse_mode = "html"
                            )

    elif get_code_add_to_cart == True:
        code = message.text
        if code.isdigit():
            add_to_cart_dict["code"] = code
            db.execute(f"SELECT * FROM product WHERE code = {int(add_to_cart_dict['code'])}")
            fetched_data = db.fetchone()

            if fetched_data != None:
                #get user
                db.execute(f"SELECT id FROM users WHERE user_id = '{message.from_user.id}'")
                user = db.fetchone()[0]

                #check cart
                db.execute(f"SELECT * FROM cart WHERE product = '{int(fetched_data[0])}' AND user = '{user}'")
                product_status = db.fetchone()

                if product_status == None:
                    product["photo"] = fetched_data[1]
                    product["name"] = fetched_data[2]
                    product["count"] = fetched_data[3]
                    product["unit"] = fetched_data[4]
                    product["price"] = fetched_data[5]

                    text = f"🔗{product['name']}\n\nتعداد موجودی : {product['count']} {product['unit']}\nقیمت : هر {product['unit']}, {product['price']}  هزار تومان"

                    if len(fetched_data) == 7:
                        product["description"] = fetched_data[6]
                        text = f"🔗{product['name']}\n\nتعداد موجودی : {product['count']} {product['unit']}\nقیمت : هر {product['unit']}, {product['price']}  هزار تومان\nتوضیحات : {product['description']}"

                    db.execute("SELECT percent, cause FROM discounts WHERE status = 'active'")
                    discount = db.fetchone()
                    product_see_keys = [
                        [
                            InlineKeyboardButton(f"{'افزودن به سبد خرید 🛒' if product_status == None else 'موجود در سبد خرید〽️'}", callback_data = f"{f'add_to_cart_{fetched_data[0]}' if product_status == None else 'blank'}"),
                            InlineKeyboardButton("خرید 💳", callback_data = "buy_product"),
                        ]
                    ]

                    if discount != None:
                        product_see_keys.append([InlineKeyboardButton("🎉 علت تخفیف 🎉", callback_data = "discount_cause")])
                        finally_price = int(product['price']) - (int(product['price']) // 100) * int(discount[0])
                        text += f"\n\n🔖<strong>{discount[0]} درصد تخفیف</strong>\n💰 قیمت نهایی : <strong>{finally_price}</strong> هزار تومان"

                    cc = app.send_photo(
                                    message.chat.id,
                                    photo = product["photo"],
                                    caption = text,
                                    reply_markup = InlineKeyboardMarkup(product_see_keys),
                                    parse_mode = "html"
                            )

                    db.execute(f"UPDATE chat_id SET message_id = '{cc.message_id}'")
                    mydb.commit()

                    get_code_add_to_cart = False

                else:
                    app.send_message(
                        message.chat.id,
                        "<strong>شما قبلا این محصول رو به سبد خریدتون اضافه کردین❗️</strong>\n\n",
                        parse_mode = "html",
                        reply_markup = InlineKeyboardMarkup([
                            [
                                InlineKeyboardButton("مشاهده سبد خرید 🛒", callback_data = "customer_see_cart"),
                                InlineKeyboardButton("حذف از سبد خرید ❌", callback_data = "delete_product_cart")
                            ]
                        ])
                    )
                    get_code_add_to_cart = False

            else:
                app.send_message(message.chat.id, "محصول مورد نظر شما یافت نشد🙅‍♂️⛔️")
        else:
            app.send_message(message.chat.id, "لطفا عدد بفرستید...")

    #giving message to send all users
    elif message_to_all == True:
        db.execute(f"SELECT name FROM settings WHERE name = '{message.chat.id}'")
        admin_id = db.fetchone()[0]
        db.execute("SELECT user_id FROM users")
        counter = 0
        counter2 = 0
        for i in db.fetchall():
            if i[0] != admin_id:
                try:
                    app.send_message(int(i[0]), f"{message.text}")
                    counter += 1
                except BadRequest:
                    counter2 += 1

        app.send_message(int(admin_id), f"پیام فوق به کاربران ارسال شد ✅\n\n<strong>📌موفق : </strong>{counter} کاربر\n<strong>📌ناموفق : </strong>{counter2} کاربر")
        message_to_all = False

    else:
        print(message.text)

    try:
        global edit_product_info
        global edit_type

        if edit_product_info[edit_type] == True:
            global variable_edit_after_submiting

            if variable_edit_after_submiting == True:
                db.execute(f"UPDATE product SET {edit_type} = '{message.text}' WHERE code = {code}")
                mydb.commit()
                edit_product_info[edit_type] = False

            else:
                product[edit_type] = message.text
                edit_product_info[edit_type] = False

            app.send_message(message.chat.id, "مقدار جدید ثبت شد〽️✅")

    except Exception as ex:
        print("nooo")

@app.on_message(filters.photo)
def GetProductImage(client, message):
    global get_product_image_or_not

    if get_product_image_or_not == True:
        product["photo"] = message.photo.file_id
        get_product_image_or_not = False

        app.send_message(message.chat.id, "عکس محصول رو گرفتم✅\n\nحالا اسم محصول رو برام بفرس...")
        global get_product_name_or_not
        get_product_name_or_not = True


def SendAddedProduct(client, message, chat_id):
    global sent_product
    try:
        sent_product = app.send_photo(
                    chat_id, photo = product["photo"],
                    caption = f"🔗{product['name']}\n\nتعداد موجودی : {product['count']} {product['unit']}\nقیمت : هر {product['unit']}, {product['price']}  هزار تومان\nتوضیحات : {product['description']}",
                    reply_markup = InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton("ثبت محصول ✅", callback_data = "submit-product"),
                                InlineKeyboardButton("ویرایش اطلاعات ✏️", callback_data = "edit-product-information")
                            ]
                        ]
                    )
                )

    except KeyError:
        sent_product = app.send_photo(
                        chat_id,
                        photo = product["photo"], caption = f"🔗{product['name']}\n\nتعداد موجودی : {product['count']} {product['unit']}\nقیمت : هر {product['unit']}, {product['price']}  هزار تومان",
                        reply_markup = InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton("ثبت محصول ✅", callback_data = "submit-product"),
                                    InlineKeyboardButton("ویرایش اطلاعات ✏️", callback_data = "edit-product-information")
                                ]
                            ]
                        )
                        )
    db.execute(f"UPDATE adminmessageid SET message_id = {sent_product.message_id}")
    mydb.commit()



app.run()

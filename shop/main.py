#mysql
import mysql.connector

#pyrogram
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

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





@app.on_message(filters.command(["start", "admin"]))
def main(client, message):
    command = message.command
    chat_id = message.chat.id

    if len(command) == 2:
        if (command[0], command[1]) == ("admin", "vajdi"):
            global AdminMainMessage
            AdminMainMessage = app.send_message(
                        chat_id,
                        "شما ادمین هستید",
                        reply_markup = InlineKeyboardMarkup([
                                                [InlineKeyboardButton("مدیریت محصولات 🛍", callback_data = "product_management")],
                                                [InlineKeyboardButton("مدیریت فروشگاه 🏪", callback_data = "store_management")]
                                            ])

                        )


            db.execute("SELECT MAX(id)  FROM adminmessageid")
            if db.fetchone()[0] == None:
                db.execute(f"INSERT INTO adminmessageid (message_id) VALUES ({AdminMainMessage.message_id})")
                mydb.commit()
            else:
                db.execute(f"UPDATE adminmessageid SET message_id = {AdminMainMessage.message_id}")
                mydb.commit()


#variable for product
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


global GetEditCode
GetEditCode = False

global GetDeleteCode
GetDeleteCode = False

variable_edit_after_submiting = False

#variable for edite product information
global edit_product_info
edit_product_info = {
                        "name" : False,
                        "count" : False,
                        "unit" : False,
                        "price" : False,
                        "description" : False
                    }

@app.on_callback_query()
def CallBack(client, message):
    callback_id = message.id
    chat_id = message.message.chat.id
    message_id = message.message.message_id
    data = message.data
    print(data)

    global get_product_image_or_not
    global get_product_name_or_not
    global get_product_count_or_not
    global get_product_description_or_not
    global get_product_unit_or_not
    global get_product_price_or_not

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
                                [InlineKeyboardButton("آمار فروش 📈", callback_data = "sell_amar")],
                                [InlineKeyboardButton("برگشت به منو اصلی 🔙", callback_data = "back_to_main_menu")]
                            ])
        )

        db.execute(f"UPDATE adminmessageid SET message_id = {store_management.message_id}")
        mydb.commit()


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
        keys = [
            [
                InlineKeyboardButton("➕ افزودن تخفیف جدید 🔖", callback_data = "add_new_discount")
            ]
        ]
        db.execute("SELECT * FROM discounts ORDER BY id DESC LIMIT 4")
        for discount in db.fetchall():
            text = f"{discount[1]} درصد"

            keys.append([InlineKeyboardButton(f"{text}", callback_data = f"detail_discount_{discount[0]}")])
        #add imoji for active discount
        keys[1][0].text += " ✅"

        #add active discount button to panel
        keys[1].append(InlineKeyboardButton("تخفیف فعال : ", callback_data = "blank"),)
        #add new button for help admin
        keys.insert(keys.index(keys[2]),[InlineKeyboardButton("3 تخفیف آخر👇 برا مشاهده جزییات کلیک کنید", callback_data = "None")])
        db.execute('SELECT * FROM adminmessageid')
        message_id = db.fetchone()[1]
        app.edit_message_text(
                        chat_id,
                        message_id = message_id,
                        text = "🔘 مدیریت تخفیف\n\nتو این بخش میتونی تنظیمات تخفیف ها رو انجام بدی👇",
                        reply_markup = InlineKeyboardMarkup(keys)
        )

    if data == "add_new_discount":
        client.answer_callback_query(
                                callback_id,
                                "⚠️ توجه : تخفیف افزوده شده به عنوان تخفیف فعال محسوب میشه و روی همه محصولات فروشگاهت اعمال میشه\n\n🔻درصد تخفیف و  علت تخفیف رو به صورت زیر بفرست :‌\n15 عید نوروز",
                                show_alert = True,
                                )
        db.execute('SELECT * FROM adminmessageid')
        message_id = db.fetchone()[1]

    if data.startswith("detail_discount_"):
        id = data.split("_")[-1]
        db.execute(f"SELECT * FROM discounts WHERE id = {int(id)}")
        discount_detail = db.fetchone()
        client.answer_callback_query(
                                    callback_id,
                                    f"وضعیت تخفیف : {'فعال' if discount_detail[2] == 'active' else 'غیر فعال'}\nمناسبت : {discount_detail[3]}\nتاریخ ثبت : {discount_detail[4]}",
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
        print(message_id)
        app.delete_messages(chat_id, message_id)



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

#a
#hasn vajdi add new comment for test github
@app.on_message(filters.text)
def GetTexts(client, message):

    #givin product name
    global get_product_name_or_not
    if get_product_name_or_not == True:
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
    global get_product_count_or_not
    if get_product_count_or_not == True:
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

    global get_product_unit_or_not
    if get_product_unit_or_not == True:
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


    global get_product_price_or_not
    if get_product_price_or_not == True:
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

    global get_product_description_or_not
    if get_product_description_or_not == True:
        global sent_product
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



    global GetEditCode
    if GetEditCode == True:
        global code
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

    global GetDeleteCode
    if GetDeleteCode == True:
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

    try:
        global edit_product_info
        global edit_type

        if edit_product_info[edit_type] == True:
            global variable_edit_after_submiting

            if variable_edit_after_submiting == True:
                print(edit_type)
                print(message.text)
                print(code)
                db.execute(f"UPDATE product SET {edit_type} = '{message.text}' WHERE code = {code}")
                mydb.commit()
                edit_product_info[edit_type] = False

            else:
                product[edit_type] = message.text
                edit_product_info[edit_type] = False

            app.send_message(message.chat.id, "مقدار جدید ثبت شد〽️✅")

    except Exception as ex:
        print(ex)

@app.on_message(filters.photo)
def GetProductImage(client, message):
    global get_product_image_or_not

    if get_product_image_or_not == True:
        product["photo"] = message.photo.file_id
        get_product_image_or_not = False

        app.send_message(message.chat.id, "عکس محصول رو گرفتم✅\n\nحالا اسم محصول رو برام بفرس...")
        global get_product_name_or_not
        get_product_name_or_not = True


def SendAddedProduct(client, messagem, chat_id):
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

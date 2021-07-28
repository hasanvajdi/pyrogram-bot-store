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
                                                [InlineKeyboardButton("تست", callback_data = "test")]
                                            ])
                        )




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

    global get_product_image_or_not
    global get_product_name_or_not
    global get_product_count_or_not
    global get_product_description_or_not
    global get_product_unit_or_not
    global get_product_price_or_not

    # edit firt admin message and show product management options
    if data == "product_management":
        client.answer_callback_query(callback_id, "شما به بخش مدیریت محصولا فروشگاه خود وارد شدید 📥")
        app.edit_message_text(
            chat_id = chat_id,
            message_id = AdminMainMessage.message_id,
            text = "🔘 مدیریت محصولات \n\n 🛍 تو این بخش میتونی عملکرد های زیر رو روی محصولات فروشگاهت داشته باشی 👇",
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ افزودن محصول", callback_data = "add_new_product")],
                [InlineKeyboardButton("✖️ حذف محصول", callback_data = "delete_product")],
                [InlineKeyboardButton("✏️ویرایش محصول", callback_data = "edit_product")],
                [InlineKeyboardButton("برشگت به منو اصلی 🔙", callback_data = "back_to_main_menu")]
            ])
        )

    # back to main menu
    if data == "back_to_main_menu":
        client.answer_callback_query(callback_id, "شما به منو اصلی پنل ادمین  برگشتید🔺")
        app.edit_message_text(
            chat_id = AdminMainMessage.chat.id,
            message_id = AdminMainMessage.message_id,
            text = AdminMainMessage.text,
            reply_markup = AdminMainMessage.reply_markup
        )




    #add new product
    if data == "add_new_product":
        get_product_image_or_not = True
        app.send_message(chat_id, "عکس محصولتو بفرس🖼📮")

        app.edit_message_text(
            chat_id,
            AdminMainMessage.message_id,
            "شما در حال اضافه کردن محصول به فروشگاه خودتون هستن\n\nبرای لغو کردن افزودن محصول دکمه زیر را فشار دهید",
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("لغو کردن", callback_data = "cancel-add-product")]
            ])
        )

    #cancel adding product

    if data == "cancel-add-product":
        get_product_image_or_not = False
        get_product_name_or_not = False
        get_product_count_or_not = False
        get_product_description_or_not = False
        get_product_unit_or_not = False
        get_product_price_or_not = False

        app.send_message(chat_id, "شما فرآیند افزودن محصول رو لغو کردین")

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
                                    '{product['count']}',
                                    '{product['unit']}',
                                    '{product['price']}',
                                    '{product['description']}')
                            """
            db.execute(query)


        #product without description
        else:
            query = f"""
                            INSERT INTO product
                            (photo, name, count, unit, price)
                            VALUES ('{str(product['photo'])}',
                                    '{product['name']}',
                                    '{product['count']}',
                                    '{product['unit']}',
                                    '{product['price']}',
                                    )
                            """
            db.execute(query)
        mydb.commit()

        # getting the last product code
        db.execute("SELECT MAX(code) FROM product")
        last_product = db.fetchone()
        app.send_message(chat_id,
                        f"محصول شما با موفقیت ثبت شد\n\nکد محصول : {last_product[0]}")



    #edit product information (main)
    if data == "edit-product-information":
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


    # back to submiting section
    if data == "back_to_submiting":
        try:
            caption = f"🔗{product['name']}\n\nتعداد موجودی : {product['count']} {product['unit']}\nقیمت : هر {product['unit']}, {product['price']}  هزار تومان\nتوضیحات : {product['description']}",
            sent_product = app.send_photo(
                        chat_id,
                        photo = sent_product.photo.file_id,
                        reply_markup = sent_product.reply_markup,
                        caption = caption
                    )
        except KeyError:
            caption = f"🔗{product['name']}\n\nتعداد موجودی : {product['count']} {product['unit']}\nقیمت : هر {product['unit']}, {product['price']}  هزار تومان",

            sent_product = app.send_photo(
                        chat_id,
                        photo = sent_product.photo.file_id,
                        reply_markup = sent_product.reply_markup,
                        caption = caption
                    )
        app.send_message(chat_id, "یــــــــــــــــا حسن")


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

    try:
        global edit_product_info
        global edit_type
        if edit_product_info[edit_type] == True:
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


app.run()

import sqlite3
import pandas as pd
import telebot
import re
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

# Telegram bot setup
bot_token = '6048352789:AAG5hIYOZpiSEf3YwUMUFFX3lLwQ6azNd88'
bot = telebot.TeleBot(bot_token)

# Create a database connection
conn = sqlite3.connect('orders.db', check_same_thread=False)
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute("CREATE TABLE IF NOT EXISTS shopkeepers "
               "(id INTEGER PRIMARY KEY AUTOINCREMENT, "
               "full_name TEXT, "
               "branch TEXT, "
               "phone_number TEXT)")

cursor.execute("CREATE TABLE IF NOT EXISTS orders "
               "(id INTEGER PRIMARY KEY AUTOINCREMENT, "
               "shopkeeper_id INTEGER, "
               "name TEXT, "
               "type TEXT, "
               "price REAL, "
               "weight REAL, "
               "quantity INTEGER, "
               "vehicle_license TEXT, "
               "FOREIGN KEY (shopkeeper_id) REFERENCES shopkeepers (id))")

# Commit the table creations
conn.commit()

# Create Excel file for logging
excel_file = 'order_logs.xlsx'
excel_file2 = 'info_logs.xlsx'

# Commands
@bot.message_handler(commands=['start'])
def start(message):
    reply_text = "Welcome to the Order Bot!\n\nYou can use the buttons below to interact with the bot."

    # Create a custom keyboard with buttons
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton('/help'), KeyboardButton('/addOrder'), KeyboardButton('/addInfo'))

    bot.send_message(message.chat.id, reply_text, reply_markup=markup)

@bot.message_handler(commands=['help'])
def help_command(message):
    reply_text = "Available commands:\n\n" \
                 "/help - Show this help message\n" \
                 "/addOrder - Register a new order\n" \
                 "/addInfo - Register shopkeeper information"

    bot.send_message(message.chat.id, reply_text)

class Order:
    def __init__(self):
        self.name = None
        self.order_type = None
        self.price = None
        self.weight = None
        self.quantity = None
        self.vehicle_license = None

order_dict = {}


class ShopkeeperInfo:
    def __init__(self):
        self.id = None
        self.full_name = None
        self.branch = None
        self.phone_number = None

info_dict = {}

@bot.message_handler(commands=['addOrder'])
def add_order(message):
    order = Order()
    order_dict[message.chat.id] = order

    bot.send_message(message.chat.id, "Please provide the order name:")
    bot.register_next_step_handler(message, process_order_name)

def process_order_name(message):
    order = order_dict[message.chat.id]
    order.name = message.text

    bot.send_message(message.chat.id, "Please provide the order type:")
    bot.register_next_step_handler(message, process_order_type)

def process_order_type(message):
    order = order_dict[message.chat.id]
    order.order_type = message.text

    bot.send_message(message.chat.id, "Please provide the order price:")
    bot.register_next_step_handler(message, process_order_price)

def process_order_price(message):
    order = order_dict[message.chat.id]
    order.price = message.text

    bot.send_message(message.chat.id, "Please provide the order weight:")
    bot.register_next_step_handler(message, process_order_weight)

def process_order_weight(message):
    order = order_dict[message.chat.id]
    order.weight = message.text

    bot.send_message(message.chat.id, "Please provide the order quantity:")
    bot.register_next_step_handler(message, process_order_quantity)

def process_order_quantity(message):
    order = order_dict[message.chat.id]
    order.quantity = message.text

    bot.send_message(message.chat.id, "Please provide the vehicle license:")
    bot.register_next_step_handler(message, process_vehicle_license)

def process_vehicle_license(message):
    order = order_dict[message.chat.id]
    order.vehicle_license = message.text

    # Create buttons for edit or submit options
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton('Edit'), KeyboardButton('Submit'))

    reply_text = "You have entered the following order information:\n\n" \
                 f"Name: {order.name}\n" \
                 f"Type: {order.order_type}\n" \
                 f"Price: {order.price}\n" \
                 f"Weight: {order.weight}\n" \
                 f"Quantity: {order.quantity}\n" \
                 f"Vehicle License: {order.vehicle_license}\n\n" \
                 "Please choose an option:"

    bot.send_message(message.chat.id, reply_text, reply_markup=markup)
    bot.register_next_step_handler(message, process_order_option)

def process_order_option(message):
    option = message.text.lower()

    if option == 'edit':
        bot.send_message(message.chat.id, "Please provide the order name:")
        bot.register_next_step_handler(message, process_order_name)
    elif option == 'submit':
        order = order_dict[message.chat.id]
        if message.chat.id in info_dict:
            shopkeeper_info = info_dict[message.chat.id]
            shopkeeper_id = shopkeeper_info.id

            # Save the order to the database
            cursor.execute("INSERT INTO orders (shopkeeper_id, name, type, price, weight, quantity, vehicle_license) "
                       "VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (shopkeeper_id, order.name, order.order_type, order.price, order.weight, order.quantity, order.vehicle_license))
            conn.commit()

            # Log the order to the excel file
            df = pd.read_sql_query("SELECT * FROM orders", conn)
            df.to_excel(excel_file, index=False)

            bot.send_message(message.chat.id, "Order successfully registered!")
        else:
            bot.send_message(message.chat.id, "Shopkeeper information is missing. Please provide shopkeeper information using the /addInfo command.")

    else:
        bot.send_message(message.chat.id, "Invalid option. Please choose 'Edit' or 'Submit'.")

    # Change the buttons to the default manner
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton('/help'), KeyboardButton('/addOrder'), KeyboardButton('/addInfo'))
    bot.send_message(message.chat.id, "Please use the buttons below to interact with the bot.", reply_markup=markup)


@bot.message_handler(commands=['addInfo'])
def add_info(message):
    shopkeeper_info = ShopkeeperInfo()
    info_dict[message.chat.id] = shopkeeper_info

    bot.send_message(message.chat.id, "Please provide your full name:")
    bot.register_next_step_handler(message, process_full_name)

def process_full_name(message):
    info = info_dict[message.chat.id]
    info.full_name = message.text

    bot.send_message(message.chat.id, "Please provide the branch of the shop:")
    bot.register_next_step_handler(message, process_branch)

def process_branch(message):
    info = info_dict[message.chat.id]
    info.branch = message.text

    bot.send_message(message.chat.id, "Please provide your phone number:")
    bot.register_next_step_handler(message, process_phone_number)

def process_phone_number(message):
    info = info_dict[message.chat.id]
    info.phone_number = message.text

    # Create buttons for edit or submit options
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton('Edit'), KeyboardButton('Submit'))

    reply_text = "You have entered the following shopkeeper information:\n\n" \
                 f"Full Name: {info.full_name}\n" \
                 f"Branch: {info.branch}\n" \
                 f"Phone Number: {info.phone_number}\n\n" \
                 "Please choose an option:"

    bot.send_message(message.chat.id, reply_text, reply_markup=markup)
    bot.register_next_step_handler(message, process_info_option)

def process_info_option(message):
    option = message.text.lower()

    if option == 'edit':
        # Prompt the user to enter the shopkeeper information again
        bot.send_message(message.chat.id, "Please provide your full name:")
        bot.register_next_step_handler(message, process_full_name)
    elif option == 'submit':
        info = info_dict[message.chat.id]

        # Save the shopkeeper info to the database
        cursor.execute("INSERT INTO shopkeepers (full_name, branch, phone_number) "
                       "VALUES (?, ?, ?)",
                       (info.full_name, info.branch, info.phone_number))
        conn.commit()

        # Log the shopkeeper info to the excel file
        df = pd.read_sql_query("SELECT * FROM shopkeepers", conn)
        df.to_excel(excel_file2, index=False)

        bot.send_message(message.chat.id, "Shopkeeper information successfully registered!")
    else:
        bot.send_message(message.chat.id, "Invalid option. Please choose 'Edit' or 'Submit'.")

    # Change the buttons to the default manner
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton('/help'), KeyboardButton('/addOrder'), KeyboardButton('/addInfo'))
    bot.send_message(message.chat.id, "Please use the buttons below to interact with the bot.", reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_input = message.text.lower()
    reply_text = generate_response(user_input)
    bot.send_message(message.chat.id, reply_text)

def generate_response(user_input):
    # Define a set of patterns and corresponding responses
    patterns = [
        (r"(?=.*\bhello\b)", "Hello! How can I assist you today?"),
        (r"(?=.*\border\b)(?=.*\bname\b)", "To place an order, please use the /addOrder command."),
        (r"(?=.*\binfo\b)", "To register shopkeeper information, please use the /addInfo command."),
        (r"(?=.*\bhelp\b)(?=.*\bcommand\b)", "You can use the following commands:\n\n"
                                            "/help - Show the available commands\n"
                                            "/addOrder - Register a new order\n"
                                            "/addInfo - Register shopkeeper information"),
        (r"(?=.*\border\b)(?=.*\bname\b)", "Please provide the name of the product you wish to order."),
        (r"(?=.*\bprice\b)(?=.*\border\b)", "Please provide the price of the product."),
        (r"(?=.*\bweight\b)(?=.*\border\b)", "Please provide the weight of the product."),
        (r"(?=.*\bquantity\b)(?=.*\border\b)", "Please provide the quantity of the product."),
        (r"(?=.*\bvehicle\b)(?=.*\blicense\b)", "Please provide the vehicle license for the order."),
        (r"(?=.*\bfull\b)(?=.*\bname\b)(?=.*\baddinfo\b)", "Please provide your full name."),
        (r"(?=.*\bbranch\b)(?=.*\baddinfo\b)", "Please provide the branch of the shop."),
        (r"(?=.*\bphone\b)(?=.*\bnumber\b)(?=.*\baddinfo\b)", "Please provide your phone number."),
        (r".*", "I'm sorry, I didn't understand that. Can you please rephrase your message?")
    ]

    # Check user input against the patterns and return the corresponding response
    for pattern, response in patterns:
        if re.search(pattern, user_input):
            return response

    return "I'm sorry, I'm currently unable to assist with that."

# Inline keyboard handler
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    if call.data == 'edit_order':
        bot.send_message(call.message.chat.id, "You have chosen to edit the order.")
        bot.send_message(call.message.chat.id, "Please provide the order name:")
        bot.register_next_step_handler(call.message, process_order_name)
    elif call.data == 'submit_order':
        bot.send_message(call.message.chat.id, "You have chosen to submit the order.")
        process_vehicle_license(call.message)
    elif call.data == 'edit_info':
        bot.send_message(call.message.chat.id, "You have chosen to edit the shopkeeper information.")
        bot.send_message(call.message.chat.id, "Please provide your full name:")
        bot.register_next_step_handler(call.message, process_full_name)
    elif call.data == 'submit_info':
        bot.send_message(call.message.chat.id, "You have chosen to submit the shopkeeper information.")
        process_phone_number(call.message)

# Start command handler
@bot.message_handler(commands=['start'])
def start_command(message):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("Edit Order", callback_data='edit_order'),
               InlineKeyboardButton("Submit Order", callback_data='submit_order'),
               InlineKeyboardButton("Edit Info", callback_data='edit_info'),
               InlineKeyboardButton("Submit Info", callback_data='submit_info'))

    bot.send_message(message.chat.id, "Welcome to the Order Bot!", reply_markup=markup)

# Start the bot
bot.polling()

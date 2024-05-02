import sqlite3
import re
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# Telegram bot setup
bot_token = '6048352789:AAG5hIYOZpiSEf3YwUMUFFX3lLwQ6azNd88'
bot = telebot.TeleBot(bot_token)

# Create a database connection
conn = sqlite3.connect('orders.db', check_same_thread=False)
cursor = conn.cursor()

# Create orders table
cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                type TEXT,
                price REAL,
                weight REAL,
                quantity INTEGER,
                vehicle_license TEXT)''')

# Create shopkeepers table
cursor.execute('''CREATE TABLE IF NOT EXISTS shopkeepers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT,
                branch TEXT,
                phone_number TEXT)''')

# Commit the table creations
conn.commit()

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

    # Save the order to the database
    cursor.execute("INSERT INTO orders (name, type, price, weight, quantity, vehicle_license) "
                   "VALUES (?, ?, ?, ?, ?, ?)",
                   (order.name, order.order_type, order.price, order.weight, order.quantity, order.vehicle_license))
    conn.commit()

    bot.send_message(message.chat.id, "Order successfully registered!")

class ShopkeeperInfo:
    def __init__(self):
        self.full_name = None
        self.branch = None
        self.phone_number = None

info_dict = {}

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

    # Save the shopkeeper info to the database
    cursor.execute("INSERT INTO shopkeepers (full_name, branch, phone_number) VALUES (?, ?, ?)",
                   (info.full_name, info.branch, info.phone_number))
    conn.commit()

    bot.send_message(message.chat.id, "Shopkeeper information successfully registered!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_input = message.text.lower()
    reply_text = generate_response(user_input)
    bot.send_message(message.chat.id, reply_text)

def generate_response(user_input):
    # Define a set of patterns and corresponding responses
    patterns = [
        (r"(?=.*\bhello\b)", "Hello! How can I assist you today?"),
        (r"(?=.*\bWhat's up\b)", "Hello! How can I assist you today?"),
        (r"(?=.*\bhey\b)", "Hello! How can I assist you today?"),
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

# Start the bot
bot.polling()

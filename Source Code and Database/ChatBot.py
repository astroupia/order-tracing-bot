import re
import telebot


bot_token = '6048352789:AAG5hIYOZpiSEf3YwUMUFFX3lLwQ6azNd88'
bot = telebot.TeleBot(bot_token)
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


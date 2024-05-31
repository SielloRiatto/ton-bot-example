# Logging module
import logging
import asyncio

# Aiogram imports
from aiogram import Bot, Dispatcher, Router, types
from aiogram import F
from aiogram.enums import ParseMode
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, \
                          InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
# Local modules to work with Database and Ton network
import config
import ton
import db


# Now all the info about bot work will be printed out to console
logging.basicConfig(level=logging.INFO)

# Initialize the bot
bot = Bot(token=config.BOT_TOKEN)

# Initialize the dispatcher
dp = Dispatcher()

# Initialize the router
router = Router()

# Регистрируем роутер в диспетчере
dp.include_router(router)

@router.message(Command("start", "help"))
async def welcome_handler(message: types.Message):
    # Function that sends the welcome message with main keyboard to user

    uid = message.from_user.id  # Not neccessary, just to make code shorter

    # If user doesn't exist in database, insert it
    if not db.check_user(uid):
        db.add_user(uid)

    # Keyboard with two main buttons: Deposit and Balance
    depositButton = KeyboardButton(text='Deposit')
    balanceButton = KeyboardButton(text='Balance')
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[depositButton, balanceButton]],
        resize_keyboard=True
    )

    await message.answer('Hi!\nI am example bot '
                         'made for [this article](https://'
                         'docs.ton.org/develop/dapps/tutorials'
                         '/accept-payments-in-a-telegram-bot-2).\n'
                         'My goal is to show how simple it is to receive '
                         'payments in TonCoin with Python.\n\n'
                         'Use keyboard to test my functionality.',
                         reply_markup=keyboard,
                         parse_mode=ParseMode.MARKDOWN)


@router.message(Command('balance'))
@router.message(F.text.regexp(r'[Bb]alance'))
async def balance_handler(message: types.Message):
    # Function that shows user his current balance

    uid = message.from_user.id

    # Get user balance from database
    # Also don't forget that 1 TON = 1e9 (billion) NanoTON
    user_balance = db.get_balance(uid) / 1e9

    # Format balance and send to user
    await message.answer(f'Your balance: *{user_balance:.2f} TON*',
                         parse_mode=ParseMode.MARKDOWN)


@router.message(Command('deposit'))
@router.message(F.text.regexp(r'[Dd]eposit'))
async def deposit_handler(message: types.Message):
    # Function that gives user the address to deposit

    uid = message.from_user.id

    # Keyboard with deposit URL
    button = InlineKeyboardButton(
        text='Deposit',
        url=f'ton://transfer/{config.DEPOSIT_ADDRESS}&text={uid}'
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])

    # Send text that explains how to make a deposit into bot to user
    await message.answer('It is very easy to top up your balance here.\n'
                         'Simply send any amount of TON to this address:\n\n'
                         f'`{config.DEPOSIT_ADDRESS}`\n\n'
                         f'And include the following comment: `{uid}`\n\n'
                         'You can also deposit by clicking the button below.',
                         reply_markup=keyboard,
                         parse_mode=ParseMode.MARKDOWN)


# Async function to start other tasks
async def start_ton(ton):
    await ton.start()

    
# Main function to start the bot
async def main():
    # Start other tasks
    asyncio.create_task(start_ton(ton))

    # Start the bot
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
    # Create Aiogram executor for our bot
    # ex = executor.Executor(dp) #asyncio

    # Launch the deposit waiter with our executor
    # ex.loop.create_task(ton.start())
    # asyncio.create_task(start_ton(ton))

    # Launch the bot
    # ex.start_polling()
    # dp.start_polling(bot)
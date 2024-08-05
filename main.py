from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import asyncio


API_TOKEN = ''

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Определение группы состояний
class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

# Создаём клавиатуру
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(KeyboardButton('Рассчитать'), KeyboardButton('Информация'))

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer('Привет! Я бот, помогающий твоему здоровью.', reply_markup=keyboard)

@dp.message_handler(Text(equals='Рассчитать', ignore_case=True), state='*')
async def set_age(message: types.Message):
    await UserState.age.set()
    await message.answer('Введите свой возраст:')

@dp.message_handler(Text(equals='Информация', ignore_case=True), state='*')
async def get_information(message: types.Message):
    await message.answer('Я бот для расчёта калорий по формуле Миффлина - Сан Жеора')

@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    await state.update_data(age=int(message.text))
    await UserState.growth.set()
    await message.answer('Введите свой рост:')

@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    await state.update_data(growth=int(message.text))
    await UserState.weight.set()
    await message.answer('Введите свой вес:')

@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    await state.update_data(weight=int(message.text))
    data = await state.get_data()

    age = data['age']
    growth = data['growth']
    weight = data['weight']

    # Формула Миффлина - Сан Жеора для мужчин:
    # Калорий = 10 * вес + 6.25 * рост - 5 * возраст + 5
    calories = 10 * weight + 6.25 * growth - 5 * age + 5

    await message.answer(f'Ваша норма калорий: {calories:.2f}')
    await state.finish()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.keyboard import InlineKeyboardBuilder
from qa_generation import pipeline

# Bot token can be obtained via https://t.me/BotFather
TOKEN = "7032499137:AAHX5Pxsnn2obqI_3nSkneSb29KBmunU1e8"

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()
bot = Bot(
    TOKEN,
    default=DefaultBotProperties(parse_mode="html", link_preview_is_disabled=True),
)

userdata: dict[str, dict] = {}

ID_TO_TOPIC = {"lesson_1": "Введение в тестирование ПО"}
QUESTIONS = {"lesson_1": ["Какова цель тестирования?", "Что означает функциональная целесообразность продукта или системы?", "Когда должно начинаться тестирование?"]}

current_topic = 0
step = 0
correct_total = 0
total = 0

@dp.message(CommandStart())
async def start_handler(message: Message, command: CommandObject) -> None:
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text="Введение в тестирование ПО", callback_data="topic_lesson_1"
        ),
#        types.InlineKeyboardButton(
#            text="Создание чек-листов", callback_data="topic_lesson2"
#        ),
#        types.InlineKeyboardButton(text="Тест-кейсы", callback_data="topic_lesson3"),
#        types.InlineKeyboardButton(
#            text="Техники тест-дизайна", callback_data="topic_lesson4"
#        ),
#        types.InlineKeyboardButton(
#            text="Виды тестирования", callback_data="topic_lesson5"
#        ),
#        types.InlineKeyboardButton(
#            text="Создание баг-репортов. Баг-трекинговые системы. Отчёты о тестировании",
#            callback_data="topic_lesson6",
#        ),
#        types.InlineKeyboardButton(
#            text="Этапы подготовки к тестированию мобильных приложений",
#            callback_data="topic_lection1",
#        ),
#        types.InlineKeyboardButton(
#            text="Основные инструменты тестирования: эмуляторы, симуляторы и мобильные фермы",
#            callback_data="topic_lection2",
#        ),
#        types.InlineKeyboardButton(
#            text="Открытые и закрытые тесты в сторах. Гайды мобильных сторов",
#            callback_data="topic_lection3",
#        ),
#       types.InlineKeyboardButton(
#           text="Функциональное тестирование", callback_data="topic_lection4"
#       ),
#      types.InlineKeyboardButton(
#            text="Нефункциональное тестирование", callback_data="topic_lection5"
#        ),
#        types.InlineKeyboardButton(
#            text="Проблемы и сложности при тестировании мобильных приложений",
#            callback_data="topic_lection6",
#        ),
    )
    await message.answer("Этот демо бот не рассчитан на использование более чем одним человеком! Это значит что только один человек может проходить тест одновременно.")
    await message.answer(
        "Выберите тему",
        reply_markup=builder.as_markup(),
    )

async def selector(message: Message) -> None:
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text="Введение в тестирование ПО", callback_data="topic_lesson_1"
        ),
#        types.InlineKeyboardButton(
#            text="Создание чек-листов", callback_data="topic_lesson2"
#        ),
#        types.InlineKeyboardButton(text="Тест-кейсы", callback_data="topic_lesson3"),
#        types.InlineKeyboardButton(
#            text="Техники тест-дизайна", callback_data="topic_lesson4"
#        ),
#        types.InlineKeyboardButton(
#            text="Виды тестирования", callback_data="topic_lesson5"
#        ),
#        types.InlineKeyboardButton(
#            text="Создание баг-репортов. Баг-трекинговые системы. Отчёты о тестировании",
#            callback_data="topic_lesson6",
#        ),
#        types.InlineKeyboardButton(
#            text="Этапы подготовки к тестированию мобильных приложений",
#            callback_data="topic_lection1",
#        ),
#        types.InlineKeyboardButton(
#            text="Основные инструменты тестирования: эмуляторы, симуляторы и мобильные фермы",
#            callback_data="topic_lection2",
#        ),
#        types.InlineKeyboardButton(
#            text="Открытые и закрытые тесты в сторах. Гайды мобильных сторов",
#            callback_data="topic_lection3",
#        ),
#       types.InlineKeyboardButton(
#           text="Функциональное тестирование", callback_data="topic_lection4"
#       ),
#      types.InlineKeyboardButton(
#            text="Нефункциональное тестирование", callback_data="topic_lection5"
#        ),
#        types.InlineKeyboardButton(
#            text="Проблемы и сложности при тестировании мобильных приложений",
#            callback_data="topic_lection6",
#        ),
    )
    await message.answer("Этот демо бот не рассчитан на использование более чем одним человеком! Это значит что только один человек может проходить тест одновременно.")
    await message.answer(
        "Выберите тему",
        reply_markup=builder.as_markup(),
    )

def get_question(topic: str, step: int):
    return QUESTIONS[topic][step - 1]

async def ask_question_initial(message: Message):
    global current_topic
    global step
    await message.answer(
        get_question(
            current_topic, 
            step
        )
    )


@dp.callback_query(F.data.startswith("topic"))
async def random_callback(callback: types.CallbackQuery):
    global current_topic
    global step
    topic = callback.data.split("_", 1)[1]

    current_topic = topic
    step = 1

    await callback.message.answer(f"Выбрана тема {ID_TO_TOPIC[topic]}")
    await ask_question_initial(callback.message)
    await callback.answer()


@dp.message()
async def answer_message(message: Message):
    global step
    global current_topic
    global total
    global correct_total
    correctness = pipeline(question=QUESTIONS[current_topic][step - 1], lesson=f"introduction_{current_topic}", user_input=message.text)
    print(correctness)
    total += 1
    if correctness == 1:
        correct_total += 1
        await message.answer("Вы ответили правильно! Так держать!")
    elif correctness == 0:
        await message.answer(f"Вы ответили неправильно, но не унывайте! Повторите этот урок: {ID_TO_TOPIC[current_topic]} - и попытайтесь снова!")
    if step+1 <= len(QUESTIONS[current_topic]):
        step += 1
        await ask_question_initial(message)
    else:
        await message.answer(f"Вы прошли демо-тест! Вы ответили правильно на {correct_total} из {total} вопросов!")
        await selector(message)


async def main() -> None:
    await dp.start_polling(bot)


def start_bot() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    asyncio.run(main())


if __name__ == "__main__":
    start_bot()

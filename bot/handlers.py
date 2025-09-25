import os
import time

import kb
from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from db import save_user_data
from dict import DICT as dict

router = Router()


bot = Bot(token=os.getenv("BOT_TOKEN"))


@router.message(F.text == "/start")
async def cmd_start(message: Message):
    await save_user_data(message.from_user.id, message.from_user.username, message.from_user.full_name)
    await message.answer(
        dict["hello"].format(name=message.from_user.first_name),
        reply_markup=kb.main_keyboard
    )


@router.callback_query(F.data == "main_cd")
async def handle_main_cd(callback: CallbackQuery):
    await callback.message.edit_text(
        text=dict["hello"].format(name=callback.from_user.first_name),
        reply_markup=kb.main_keyboard
    )


@router.callback_query(F.data == "button_1_cd")
async def handle_button_1_cd(callback: CallbackQuery):
    await callback.message.edit_text(
        text=dict["good_choise"],
        reply_markup=kb.go_home_keyboard
    )


@router.callback_query(F.data == "button_2_cd")
async def handle_button_2_cd(callback: CallbackQuery):
    await callback.message.edit_text(
        text=dict["self_hearing_intro"],
        reply_markup=kb.self_hearing_keyboard
    )


@router.callback_query(F.data == "button_3_cd")
async def handle_button_3_cd(callback: CallbackQuery):
    await callback.message.edit_text(
        text=dict["check_hearing_intro"],
        reply_markup=kb.check_hearing_keyboard
    )


@router.callback_query(F.data == "button_6_cd")
async def handle_button_6_cd(callback: CallbackQuery):
    await callback.message.edit_text(
        text=dict["check_hearing_links_intro"],
        reply_markup=kb.check_hearing_links_keyboard
    )

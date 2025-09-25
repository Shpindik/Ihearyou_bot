from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from dict import DICT_KB as dict_kb

main_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=dict_kb["button_1"], callback_data="button_1_cd"),
        ],
        [
            InlineKeyboardButton(text=dict_kb["button_2"], callback_data="button_2_cd"),
        ],
    ]
)

go_home_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=dict_kb["go_home"], callback_data="main_cd"),
        ],
    ]
)

self_hearing_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=dict_kb["button_3"], callback_data="button_3_cd"),
        ],
        [
            InlineKeyboardButton(text=dict_kb["button_4"], callback_data="button_4_cd"),
        ],
        [
            InlineKeyboardButton(text=dict_kb["button_5"], callback_data="button_5_cd"),
        ],
    ]
)

check_hearing_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=dict_kb["button_6"], callback_data="button_6_cd"),
        ],
        [
            InlineKeyboardButton(text=dict_kb["button_7"], callback_data="button_7_cd"),
        ],
    ]
)

check_hearing_links_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text=dict_kb["check_hearing_test"], web_app=WebAppInfo(url="https://hearing.ru/i-hear-you/")
            ),
        ],
        [
            InlineKeyboardButton(
                text=dict_kb["check_hearing_article"],
                web_app=WebAppInfo(
                    url="https://www.ihearyou.ru/materials/articles/8-prichin-postavit-proverku-slukha-na-pervoe-mesto-v-spiske-vashikh-del"
                ),
            ),
        ],
        [
            InlineKeyboardButton(text=dict_kb["go_home"], callback_data="main_cd"),
        ],
    ]
)

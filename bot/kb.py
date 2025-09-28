from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, WebAppInfo
from dict import DICT_KB as dict_kb
from typing import List, Dict, Optional

def create_dynamic_keyboard(
    menu_items: List[Dict], 
    parent_id: Optional[int] = None,
    show_navigation: bool = True
) -> InlineKeyboardMarkup:
    """Создает динамическую клавиатуру на основе данных из БД."""
    buttons = []
    
    # Добавляем кнопки меню
    for item in menu_items:
        button_text = item.get("title", "Без названия")
        callback_data = f"menu_item_{item['id']}_cd"
        buttons.append([InlineKeyboardButton(text=button_text, callback_data=callback_data)])
    
    # Добавляем навигационные кнопки
    if show_navigation:
        nav_buttons = []
        
        # Кнопка "Назад" только если есть родитель
        if parent_id is not None:
            nav_buttons.append(InlineKeyboardButton(text=dict_kb["go_back"], callback_data="go_back_cd"))
        
        # Кнопка "Задать вопрос"
        nav_buttons.append(InlineKeyboardButton(text=dict_kb["ask_question"], callback_data="ask_question_cd"))
        
        if nav_buttons:
            buttons.append(nav_buttons)
        
        # Кнопка "Главное меню"
        buttons.append([InlineKeyboardButton(text=dict_kb["go_home"], callback_data="main_cd")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def create_content_keyboard(content: Dict) -> InlineKeyboardMarkup:
    """Создает клавиатуру для отображения контента."""
    buttons = []
    
    # Кнопка "Оценить материал" если есть контент
    if content.get("content"):
        buttons.append([InlineKeyboardButton(text=dict_kb["rate_material"], callback_data="rate_material_cd")])
    
    # Навигационные кнопки
    buttons.extend([
        [
            InlineKeyboardButton(text=dict_kb["go_back"], callback_data="go_back_cd"),
            InlineKeyboardButton(text=dict_kb["ask_question"], callback_data="ask_question_cd"),
        ],
        [
            InlineKeyboardButton(text=dict_kb["go_home"], callback_data="main_cd"),
        ]
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Специальные клавиатуры для конкретных функций
def create_web_app_keyboard(url: str, button_text: str) -> InlineKeyboardMarkup:
    """Создает клавиатуру с WebApp кнопкой."""
    buttons = [
        [InlineKeyboardButton(text=button_text, web_app=WebAppInfo(url=url))],
        [
            InlineKeyboardButton(text=dict_kb["go_back"], callback_data="go_back_cd"),
            InlineKeyboardButton(text=dict_kb["ask_question"], callback_data="ask_question_cd"),
        ],
        [InlineKeyboardButton(text=dict_kb["go_home"], callback_data="main_cd")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Оценка материалов
rate_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=dict_kb["rate_1"], callback_data="rate_1_cd"),
            InlineKeyboardButton(text=dict_kb["rate_2"], callback_data="rate_2_cd"),
            InlineKeyboardButton(text=dict_kb["rate_3"], callback_data="rate_3_cd"),
        ],
        [
            InlineKeyboardButton(text=dict_kb["rate_4"], callback_data="rate_4_cd"),
            InlineKeyboardButton(text=dict_kb["rate_5"], callback_data="rate_5_cd"),
        ],
    ]
)
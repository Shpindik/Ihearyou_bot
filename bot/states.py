from aiogram.fsm.state import State, StatesGroup


class States(StatesGroup):
    """Состояния бота"""

    waiting_for_article_rating = State()  # Ожидание выбора оценки для статьи


class NavigationState:
    """Класс для отслеживания истории навигации пользователя"""

    def __init__(self):
        self.history = []  # Список предыдущих состояний

    def add_state(self, message_text: str, reply_markup=None, meta=None):
        """Добавляет текущее состояние в историю"""
        self.history.append({
            'message_text': message_text,
            'reply_markup': reply_markup,
            'meta': meta or {},
        })

    def go_back(self):
        """Возвращает предыдущее состояние"""
        if len(self.history) > 1:
            # Удаляем текущее состояние и возвращаем предыдущее
            self.history.pop()
            return self.history[-1]
        elif len(self.history) == 1:
            return self.history[-1]  # Возвращаем единственное состояние
        return None

    def clear_history(self):
        """Очищает историю навигации"""
        self.history.clear()

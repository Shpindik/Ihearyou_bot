#!/bin/bash

# Установка pre-commit
pip install pre-commit

# Установка хуков
pre-commit install

# Проверка на всех файлах
pre-commit run --all-files

echo "Pre-commit hooks установлены и готовы к использованию!"
echo "Теперь при каждом git commit будут автоматически применяться:"
echo "- black (форматирование кода)"
echo "- isort (сортировка импортов)"
echo "- flake8 (проверка стиля)"
echo "- pre-commit-hooks (удаление пробелов, фикс концов файлов)"

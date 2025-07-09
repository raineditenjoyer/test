#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# Добавляем путь к PyQt5
sys.path.append('/usr/lib/python3/dist-packages')

# Проверим, есть ли дисплей
if 'DISPLAY' not in os.environ:
    print("⚠️  Дисплей не найден. Игра может не запуститься визуально.")
    print("💡 Попробуйте запустить из терминала с графическим интерфейсом.")
    print("🖥️  Или используйте X11 forwarding для удаленного подключения.")
    print()

# Импортируем и запускаем игру
from galaga_game import main

if __name__ == "__main__":
    print("🚀 Запуск игры Galaga Redux...")
    print()
    main()
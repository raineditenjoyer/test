#!/usr/bin/env python3

import sys
sys.path.append('/usr/lib/python3/dist-packages')

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
import os

# Настройка для работы без дисплея
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
os.environ['XDG_RUNTIME_DIR'] = '/tmp/runtime-root'

# Создание приложения для тестирования
app = QApplication(sys.argv)

# Проверка импорта игры
try:
    from galaga_game import MainWindow
    print("✓ Все модули успешно импортированы")
    
    # Создание окна
    window = MainWindow()
    print("✓ Окно игры создано успешно")
    
    # Проверка игрового движка
    game_engine = window.game_widget.engine
    print(f"✓ Игровой движок инициализирован")
    print(f"  - Размер окна: {game_engine.settings.window_width}x{game_engine.settings.window_height}")
    print(f"  - Состояние игры: {game_engine.state}")
    print(f"  - Жизни игрока: {game_engine.player.lives}")
    print(f"  - Начальный счёт: {game_engine.score}")
    print(f"  - Рекорд: {game_engine.high_score}")
    
    # Симуляция запуска игры
    game_engine.start_game()
    print("✓ Игра запущена")
    
    # Симуляция нескольких кадров
    for i in range(10):
        game_engine.update()
    print("✓ Игровой цикл работает корректно")
    
    print("\n🎮 Игра Galaga Redux готова к запуску!")
    print("📋 Управление:")
    print("  - Движение: стрелки или WASD")
    print("  - Стрельба: пробел")
    print("  - Пауза: P")
    print("  - Начать игру: Enter")
    print("  - Новая игра: R (после окончания)")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()

app.quit()
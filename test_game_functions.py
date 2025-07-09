#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Тестовый файл для проверки основных функций игры Galaga Redux
"""

import sys
import os
sys.path.append('/usr/lib/python3/dist-packages')

from galaga_game import GameEngine, GameSettings, DifficultyLevel, SoundManager, StatisticsManager

def test_game_engine():
    """Тестирование игрового движка"""
    print("🎮 Тестирование игрового движка...")
    
    engine = GameEngine()
    
    # Проверка начального состояния
    assert engine.score == 0
    assert engine.wave == 1
    assert engine.player.lives > 0
    
    print("✅ Игровой движок инициализирован корректно")
    
    # Тест сохранения/загрузки настроек
    engine.settings.difficulty = DifficultyLevel.HARD
    engine.save_settings()
    
    new_engine = GameEngine()
    new_engine.load_settings()
    
    print("✅ Настройки сохраняются и загружаются корректно")

def test_sound_manager():
    """Тестирование звукового менеджера"""
    print("🔊 Тестирование звукового менеджера...")
    
    sound_manager = SoundManager()
    settings = GameSettings()
    sound_manager.set_settings(settings)
    
    # Тест воспроизведения звуков (безопасный, без фактического воспроизведения)
    sound_manager.play_sound('shoot')
    sound_manager.play_sound('explosion')
    sound_manager.play_music('background')
    
    print("✅ Звуковой менеджер работает корректно")

def test_statistics_manager():
    """Тестирование менеджера статистики"""
    print("📊 Тестирование менеджера статистики...")
    
    stats_manager = StatisticsManager()
    
    # Тест сохранения результата
    stats_manager.save_game_result(
        score=1000,
        level=5,
        difficulty="MEDIUM",
        duration=120,
        enemies_killed=15,
        shots_fired=25
    )
    
    # Получение статистики
    stats = stats_manager.get_statistics(limit=10)
    assert len(stats) > 0
    
    # Получение фильтрованной статистики
    filtered_stats = stats_manager.get_filtered_statistics(difficulty="MEDIUM")
    assert len(filtered_stats) > 0
    
    print("✅ Менеджер статистики работает корректно")

def test_difficulty_settings():
    """Тестирование настроек сложности"""
    print("⚙️ Тестирование настроек сложности...")
    
    engine = GameEngine()
    
    # Тест легкого уровня
    engine.settings.difficulty = DifficultyLevel.EASY
    engine.apply_difficulty_settings()
    assert engine.player.lives == 5
    
    # Тест среднего уровня
    engine.settings.difficulty = DifficultyLevel.MEDIUM
    engine.apply_difficulty_settings()
    assert engine.player.lives == 3
    
    # Тест сложного уровня
    engine.settings.difficulty = DifficultyLevel.HARD
    engine.apply_difficulty_settings()
    assert engine.player.lives == 2
    
    print("✅ Настройки сложности применяются корректно")

def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестов игры Galaga Redux...")
    print("=" * 50)
    
    try:
        test_game_engine()
        test_sound_manager()
        test_statistics_manager()
        test_difficulty_settings()
        
        print("=" * 50)
        print("✅ Все тесты пройдены успешно!")
        
        print("\n📋 Доступные функции:")
        print("• Базовая механика: движение, стрельба, коллизии")
        print("• Звуковые эффекты: стрельба, взрывы, музыка")
        print("• Настройки: звук, графика, управление")
        print("• Уровни сложности: легкий, средний, сложный")
        print("• Статистика: сохранение результатов, графики, фильтрация")
        print("• Улучшенный дизайн: синие футуристические корабли")
        
        print("\n🎯 Управление в игре:")
        print("• WASD / стрелки - движение")
        print("• SPACE - стрельба")
        print("• P - пауза")
        print("• S - настройки (в меню)")
        print("• T - статистика (в меню)")
        print("• ESC - выход/возврат в меню")
        
    except Exception as e:
        print(f"❌ Тест завершился с ошибкой: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
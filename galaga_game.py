#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import random
import math
import json
import sqlite3
import datetime
from typing import List, Tuple, Dict
from dataclasses import dataclass
from enum import Enum

# Добавляем путь к PyQt5
sys.path.append('/usr/lib/python3/dist-packages')

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QDialog, 
                             QDialogButtonBox, QTextEdit, QFrame, QGridLayout,
                             QSlider, QComboBox, QCheckBox, QTabWidget,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QGroupBox, QRadioButton, QButtonGroup, QSpinBox,
                             QMessageBox, QKeySequenceEdit, QProgressBar)
from PyQt5.QtCore import QTimer, Qt, QPoint, QRect, QSize, pyqtSignal, QThread
from PyQt5.QtGui import (QPainter, QColor, QBrush, QPen, QFont, QPixmap, 
                         QPolygon, QLinearGradient, QRadialGradient, QKeySequence)
from PyQt5.QtMultimedia import QSound, QSoundEffect, QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl

# Для графиков статистики
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Импорт диалогов
from dialogs import SettingsDialog, StatisticsDialog

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3
    PAUSED = 4
    SETTINGS = 5
    STATISTICS = 6
    DIFFICULTY_SELECT = 7

class DifficultyLevel(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3

@dataclass
class GameSettings:
    window_width: int = 800
    window_height: int = 600
    player_speed: int = 5
    bullet_speed: int = 8
    enemy_speed: int = 2
    enemy_bullet_speed: int = 4
    fps: int = 60
    
    # Звуковые настройки
    sound_enabled: bool = True
    music_enabled: bool = True
    sound_volume: float = 0.7
    music_volume: float = 0.5
    
    # Управление
    key_left: int = Qt.Key_Left
    key_right: int = Qt.Key_Right
    key_up: int = Qt.Key_Up
    key_down: int = Qt.Key_Down
    key_shoot: int = Qt.Key_Space
    key_alt_left: int = Qt.Key_A
    key_alt_right: int = Qt.Key_D
    key_alt_up: int = Qt.Key_W
    key_alt_down: int = Qt.Key_S
    
    # Графические настройки
    effects_enabled: bool = True
    particles_enabled: bool = True
    background_quality: int = 1  # 0-2 (низкое, среднее, высокое)
    
    # Настройки сложности
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.music_player = None
        self.settings = None
        self.init_sounds()
        
    def init_sounds(self):
        """Инициализация звуковых эффектов"""
        try:
            # Создаем простые звуки программно (так как у нас нет аудио файлов)
            self.create_synthetic_sounds()
        except Exception as e:
            print(f"Ошибка инициализации звуков: {e}")
            
    def create_synthetic_sounds(self):
        """Создаем синтетические звуки для игры"""
        # Здесь можно добавить генерацию звуков или использовать системные звуки
        # Пока используем заглушки для звуков
        self.sounds = {
            'shoot': None,
            'explosion': None,
            'hit': None,
            'powerup': None
        }
        
    def play_sound(self, sound_name: str):
        """Воспроизведение звука"""
        if not self.settings or not self.settings.sound_enabled:
            return
            
        if sound_name in self.sounds and self.sounds[sound_name]:
            try:
                # Здесь был бы код воспроизведения звука
                pass
            except Exception as e:
                print(f"Ошибка воспроизведения звука {sound_name}: {e}")
                
    def play_music(self, music_name: str):
        """Воспроизведение фоновой музыки"""
        if not self.settings or not self.settings.music_enabled:
            return
            
        try:
            # Здесь был бы код воспроизведения музыки
            pass
        except Exception as e:
            print(f"Ошибка воспроизведения музыки {music_name}: {e}")
            
    def stop_music(self):
        """Остановка музыки"""
        if self.music_player:
            try:
                self.music_player.stop()
            except:
                pass
                
    def set_settings(self, settings: GameSettings):
        """Установка настроек"""
        self.settings = settings

class StatisticsManager:
    def __init__(self):
        self.db_path = "game_stats.db"
        self.init_database()
        
    def init_database(self):
        """Инициализация базы данных статистики"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                score INTEGER NOT NULL,
                level INTEGER NOT NULL,
                difficulty TEXT NOT NULL,
                duration INTEGER NOT NULL,
                enemies_killed INTEGER NOT NULL,
                shots_fired INTEGER NOT NULL,
                accuracy REAL NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def save_game_result(self, score: int, level: int, difficulty: str, 
                        duration: int, enemies_killed: int, shots_fired: int):
        """Сохранение результата игры"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        accuracy = enemies_killed / max(shots_fired, 1) * 100
        date = datetime.datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO game_results 
            (date, score, level, difficulty, duration, enemies_killed, shots_fired, accuracy)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (date, score, level, difficulty, duration, enemies_killed, shots_fired, accuracy))
        
        conn.commit()
        conn.close()
        
    def get_statistics(self, limit: int = 100) -> List[Dict]:
        """Получение статистики игр"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM game_results 
            ORDER BY date DESC 
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'date': row[1],
                'score': row[2],
                'level': row[3],
                'difficulty': row[4],
                'duration': row[5],
                'enemies_killed': row[6],
                'shots_fired': row[7],
                'accuracy': row[8]
            }
            for row in results
        ]
        
    def get_filtered_statistics(self, difficulty: str = None, 
                              date_from: str = None, date_to: str = None) -> List[Dict]:
        """Получение отфильтрованной статистики"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM game_results WHERE 1=1"
        params = []
        
        if difficulty:
            query += " AND difficulty = ?"
            params.append(difficulty)
            
        if date_from:
            query += " AND date >= ?"
            params.append(date_from)
            
        if date_to:
            query += " AND date <= ?"
            params.append(date_to)
            
        query += " ORDER BY date DESC"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'date': row[1],
                'score': row[2],
                'level': row[3],
                'difficulty': row[4],
                'duration': row[5],
                'enemies_killed': row[6],
                'shots_fired': row[7],
                'accuracy': row[8]
            }
            for row in results
        ]
    
class GameObject:
    def __init__(self, x: float, y: float, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.active = True
        
    def get_rect(self) -> QRect:
        return QRect(int(self.x), int(self.y), self.width, self.height)
        
    def collides_with(self, other) -> bool:
        return self.get_rect().intersects(other.get_rect())

class Player(GameObject):
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 40, 30)
        self.lives = 3
        self.invulnerable_time = 0
        
    def update(self):
        if self.invulnerable_time > 0:
            self.invulnerable_time -= 1
            
    def take_damage(self):
        if self.invulnerable_time <= 0:
            self.lives -= 1
            self.invulnerable_time = 60  # 1 секунда неуязвимости
            
    def is_invulnerable(self) -> bool:
        return self.invulnerable_time > 0

class Bullet(GameObject):
    def __init__(self, x: float, y: float, velocity_y: float, is_player_bullet: bool = True):
        super().__init__(x, y, 4, 8)
        self.velocity_y = velocity_y
        self.is_player_bullet = is_player_bullet
        
    def update(self):
        self.y += self.velocity_y
        
    def is_off_screen(self, screen_height: int) -> bool:
        return self.y < -self.height or self.y > screen_height

class Enemy(GameObject):
    def __init__(self, x: float, y: float, enemy_type: str = "basic"):
        super().__init__(x, y, 30, 25)
        self.enemy_type = enemy_type
        self.points = 100 if enemy_type == "basic" else 200
        self.shoot_timer = random.randint(60, 180)
        self.move_pattern = random.choice(['straight', 'wave', 'diagonal'])
        self.angle = 0
        
    def update(self):
        # Движение в зависимости от паттерна
        if self.move_pattern == 'straight':
            self.y += 1
        elif self.move_pattern == 'wave':
            self.y += 1
            self.x += math.sin(self.angle) * 2
            self.angle += 0.1
        elif self.move_pattern == 'diagonal':
            self.y += 1
            self.x += 0.5 if self.x < 400 else -0.5
            
        self.shoot_timer -= 1
        
    def should_shoot(self) -> bool:
        return self.shoot_timer <= 0
        
    def reset_shoot_timer(self):
        self.shoot_timer = random.randint(120, 300)

class PowerUp(GameObject):
    def __init__(self, x: float, y: float, power_type: str):
        super().__init__(x, y, 20, 20)
        self.power_type = power_type  # 'rapid_fire', 'double_shot', 'shield'
        self.velocity_y = 2
        
    def update(self):
        self.y += self.velocity_y

class ParticleEffect:
    def __init__(self, x: float, y: float, color: QColor, lifetime: int = 30):
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.velocity_x = random.uniform(-3, 3)
        self.velocity_y = random.uniform(-3, 3)
        self.active = True
        
    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.active = False
            
    def get_alpha(self) -> int:
        return int(255 * (self.lifetime / self.max_lifetime))

class GameEngine:
    def __init__(self):
        self.settings = GameSettings()
        self.state = GameState.MENU
        self.score = 0
        self.high_score = self.load_high_score()
        self.wave = 1
        self.game_start_time = 0
        self.enemies_killed = 0
        self.shots_fired = 0
        
        # Менеджеры
        self.sound_manager = SoundManager()
        self.sound_manager.set_settings(self.settings)
        self.stats_manager = StatisticsManager()
        
        # Игровые объекты
        self.player = Player(self.settings.window_width // 2 - 20, 
                           self.settings.window_height - 50)
        self.bullets: List[Bullet] = []
        self.enemies: List[Enemy] = []
        self.power_ups: List[PowerUp] = []
        self.particles: List[ParticleEffect] = []
        
        # Управление
        self.keys_pressed = set()
        
        # Таймеры
        self.enemy_spawn_timer = 0
        self.power_up_spawn_timer = 0
        self.shoot_cooldown = 0
        
        # Настройки сложности
        self.apply_difficulty_settings()
        
    def apply_difficulty_settings(self):
        """Применение настроек сложности"""
        if self.settings.difficulty == DifficultyLevel.EASY:
            self.settings.player_speed = 6
            self.settings.bullet_speed = 10
            self.settings.enemy_speed = 1
            self.settings.enemy_bullet_speed = 3
            self.player.lives = 5
        elif self.settings.difficulty == DifficultyLevel.MEDIUM:
            self.settings.player_speed = 5
            self.settings.bullet_speed = 8
            self.settings.enemy_speed = 2
            self.settings.enemy_bullet_speed = 4
            self.player.lives = 3
        else:  # HARD
            self.settings.player_speed = 4
            self.settings.bullet_speed = 7
            self.settings.enemy_speed = 3
            self.settings.enemy_bullet_speed = 5
            self.player.lives = 2
        
    def load_high_score(self) -> int:
        try:
            with open('high_score.json', 'r') as f:
                data = json.load(f)
                return data.get('high_score', 0)
        except:
            return 0
            
    def save_high_score(self):
        try:
            with open('high_score.json', 'w') as f:
                json.dump({'high_score': self.high_score}, f)
        except:
            pass
            
    def save_settings(self):
        """Сохранение настроек в файл"""
        try:
            settings_dict = {
                'sound_enabled': self.settings.sound_enabled,
                'music_enabled': self.settings.music_enabled,
                'sound_volume': self.settings.sound_volume,
                'music_volume': self.settings.music_volume,
                'key_left': self.settings.key_left,
                'key_right': self.settings.key_right,
                'key_up': self.settings.key_up,
                'key_down': self.settings.key_down,
                'key_shoot': self.settings.key_shoot,
                'key_alt_left': self.settings.key_alt_left,
                'key_alt_right': self.settings.key_alt_right,
                'key_alt_up': self.settings.key_alt_up,
                'key_alt_down': self.settings.key_alt_down,
                'effects_enabled': self.settings.effects_enabled,
                'particles_enabled': self.settings.particles_enabled,
                'background_quality': self.settings.background_quality,
                'difficulty': self.settings.difficulty.value
            }
            
            with open('game_settings.json', 'w') as f:
                json.dump(settings_dict, f)
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")
            
    def load_settings(self):
        """Загрузка настроек из файла"""
        try:
            with open('game_settings.json', 'r') as f:
                settings_dict = json.load(f)
                
            self.settings.sound_enabled = settings_dict.get('sound_enabled', True)
            self.settings.music_enabled = settings_dict.get('music_enabled', True)
            self.settings.sound_volume = settings_dict.get('sound_volume', 0.7)
            self.settings.music_volume = settings_dict.get('music_volume', 0.5)
            self.settings.key_left = settings_dict.get('key_left', Qt.Key_Left)
            self.settings.key_right = settings_dict.get('key_right', Qt.Key_Right)
            self.settings.key_up = settings_dict.get('key_up', Qt.Key_Up)
            self.settings.key_down = settings_dict.get('key_down', Qt.Key_Down)
            self.settings.key_shoot = settings_dict.get('key_shoot', Qt.Key_Space)
            self.settings.key_alt_left = settings_dict.get('key_alt_left', Qt.Key_A)
            self.settings.key_alt_right = settings_dict.get('key_alt_right', Qt.Key_D)
            self.settings.key_alt_up = settings_dict.get('key_alt_up', Qt.Key_W)
            self.settings.key_alt_down = settings_dict.get('key_alt_down', Qt.Key_S)
            self.settings.effects_enabled = settings_dict.get('effects_enabled', True)
            self.settings.particles_enabled = settings_dict.get('particles_enabled', True)
            self.settings.background_quality = settings_dict.get('background_quality', 1)
            
            difficulty_value = settings_dict.get('difficulty', DifficultyLevel.MEDIUM.value)
            self.settings.difficulty = DifficultyLevel(difficulty_value)
            
            self.sound_manager.set_settings(self.settings)
            
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")
            
    def start_game(self):
        self.state = GameState.PLAYING
        self.score = 0
        self.wave = 1
        self.game_start_time = datetime.datetime.now().timestamp()
        self.enemies_killed = 0
        self.shots_fired = 0
        
        self.apply_difficulty_settings()
        self.player = Player(self.settings.window_width // 2 - 20, 
                           self.settings.window_height - 50)
        self.bullets.clear()
        self.enemies.clear()
        self.power_ups.clear()
        self.particles.clear()
        
        # Запуск фоновой музыки
        self.sound_manager.play_music('background')
        
    def end_game(self):
        """Завершение игры и сохранение статистики"""
        if self.state == GameState.PLAYING:
            game_duration = int(datetime.datetime.now().timestamp() - self.game_start_time)
            
            # Сохранение результата
            self.stats_manager.save_game_result(
                score=self.score,
                level=self.wave,
                difficulty=self.settings.difficulty.name,
                duration=game_duration,
                enemies_killed=self.enemies_killed,
                shots_fired=self.shots_fired
            )
            
            self.state = GameState.GAME_OVER
            self.sound_manager.stop_music()
            
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
        
    def spawn_enemy_wave(self):
        for i in range(5 + self.wave):
            x = random.randint(0, self.settings.window_width - 30)
            y = random.randint(-100, -30)
            enemy_type = "basic" if random.random() < 0.7 else "advanced"
            self.enemies.append(Enemy(x, y, enemy_type))
            
    def update(self):
        if self.state != GameState.PLAYING:
            return
            
        # Обновление игрока
        self.player.update()
        
        # Обновление кулдауна стрельбы
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        # Движение игрока
        if (self.settings.key_left in self.keys_pressed or 
            self.settings.key_alt_left in self.keys_pressed):
            self.player.x = max(0, self.player.x - self.settings.player_speed)
        if (self.settings.key_right in self.keys_pressed or 
            self.settings.key_alt_right in self.keys_pressed):
            self.player.x = min(self.settings.window_width - self.player.width, 
                               self.player.x + self.settings.player_speed)
        if (self.settings.key_up in self.keys_pressed or 
            self.settings.key_alt_up in self.keys_pressed):
            self.player.y = max(0, self.player.y - self.settings.player_speed)
        if (self.settings.key_down in self.keys_pressed or 
            self.settings.key_alt_down in self.keys_pressed):
            self.player.y = min(self.settings.window_height - self.player.height, 
                               self.player.y + self.settings.player_speed)
            
        # Стрельба
        if self.settings.key_shoot in self.keys_pressed and self.shoot_cooldown <= 0:
            if len([b for b in self.bullets if b.is_player_bullet]) < 5:
                bullet = Bullet(self.player.x + self.player.width // 2, 
                               self.player.y, -self.settings.bullet_speed)
                self.bullets.append(bullet)
                self.shots_fired += 1
                self.shoot_cooldown = 10  # Кулдаун стрельбы
                self.sound_manager.play_sound('shoot')
                
        # Обновление пуль
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_off_screen(self.settings.window_height):
                self.bullets.remove(bullet)
                
        # Обновление врагов
        for enemy in self.enemies[:]:
            enemy.update()
            if enemy.y > self.settings.window_height:
                self.enemies.remove(enemy)
                continue
                
            # Стрельба врагов
            if enemy.should_shoot():
                bullet = Bullet(enemy.x + enemy.width // 2, 
                               enemy.y + enemy.height, 
                               self.settings.enemy_bullet_speed, False)
                self.bullets.append(bullet)
                enemy.reset_shoot_timer()
                
        # Спавн врагов
        self.enemy_spawn_timer += 1
        if self.enemy_spawn_timer > 120 and len(self.enemies) < 10:
            self.spawn_enemy_wave()
            self.enemy_spawn_timer = 0
            
        # Коллизии
        self.check_collisions()
        
        # Обновление частиц
        if self.settings.particles_enabled:
            for particle in self.particles[:]:
                particle.update()
                if not particle.active:
                    self.particles.remove(particle)
                
        # Обновление power-ups
        for power_up in self.power_ups[:]:
            power_up.update()
            if power_up.y > self.settings.window_height:
                self.power_ups.remove(power_up)
                
        # Проверка окончания игры
        if self.player.lives <= 0:
            self.end_game()
            
    def check_collisions(self):
        # Коллизии пуль игрока с врагами
        for bullet in self.bullets[:]:
            if not bullet.is_player_bullet:
                continue
                
            for enemy in self.enemies[:]:
                if bullet.collides_with(enemy):
                    self.bullets.remove(bullet)
                    self.enemies.remove(enemy)
                    self.score += enemy.points
                    self.enemies_killed += 1
                    
                    self.sound_manager.play_sound('explosion')
                    
                    # Эффект взрыва
                    if self.settings.effects_enabled:
                        for _ in range(8):
                            particle = ParticleEffect(
                                enemy.x + enemy.width // 2,
                                enemy.y + enemy.height // 2,
                                QColor(255, 165, 0)
                            )
                            self.particles.append(particle)
                        
                    # Шанс выпадения power-up
                    if random.random() < 0.1:
                        power_type = random.choice(['rapid_fire', 'double_shot', 'shield'])
                        power_up = PowerUp(enemy.x, enemy.y, power_type)
                        self.power_ups.append(power_up)
                    break
                    
        # Коллизии пуль врагов с игроком
        for bullet in self.bullets[:]:
            if bullet.is_player_bullet:
                continue
                
            if bullet.collides_with(self.player) and not self.player.is_invulnerable():
                self.bullets.remove(bullet)
                self.player.take_damage()
                self.sound_manager.play_sound('hit')
                
                # Эффект попадания
                if self.settings.effects_enabled:
                    for _ in range(5):
                        particle = ParticleEffect(
                            self.player.x + self.player.width // 2,
                            self.player.y + self.player.height // 2,
                            QColor(255, 0, 0)
                        )
                        self.particles.append(particle)
                    
        # Коллизии врагов с игроком
        for enemy in self.enemies[:]:
            if enemy.collides_with(self.player) and not self.player.is_invulnerable():
                self.enemies.remove(enemy)
                self.player.take_damage()
                self.sound_manager.play_sound('hit')
                
        # Коллизии power-ups с игроком
        for power_up in self.power_ups[:]:
            if power_up.collides_with(self.player):
                self.power_ups.remove(power_up)
                self.score += 50
                self.sound_manager.play_sound('powerup')

class GameWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.engine = GameEngine()
        self.engine.load_settings()  # Загрузка настроек
        self.setFixedSize(self.engine.settings.window_width, 
                         self.engine.settings.window_height)
        self.setFocusPolicy(Qt.StrongFocus)
        
        # Таймер для обновления игры
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_game)
        self.timer.start(1000 // self.engine.settings.fps)
        
        # Фон
        self.background_stars = []
        self.init_background()
        
        # Диалоги
        self.settings_dialog = None
        self.difficulty_dialog = None
        self.statistics_dialog = None
        
    def init_background(self):
        """Инициализация фона в зависимости от настроек качества"""
        star_count = [50, 100, 150][self.engine.settings.background_quality]
        
        self.background_stars = []
        for _ in range(star_count):
            self.background_stars.append({
                'x': random.randint(0, self.engine.settings.window_width),
                'y': random.randint(0, self.engine.settings.window_height),
                'speed': random.uniform(0.5, 2.0),
                'size': random.randint(1, 3),
                'brightness': random.randint(100, 255)
            })
            
    def update_game(self):
        self.engine.update()
        self.update_background()
        self.update()
        
    def update_background(self):
        for star in self.background_stars:
            star['y'] += star['speed']
            if star['y'] > self.engine.settings.window_height:
                star['y'] = -5
                star['x'] = random.randint(0, self.engine.settings.window_width)
                
    def keyPressEvent(self, event):
        self.engine.keys_pressed.add(event.key())
        
        # Обработка состояний
        if self.engine.state == GameState.MENU:
            if event.key() == Qt.Key_Return:
                self.engine.state = GameState.DIFFICULTY_SELECT
            elif event.key() == Qt.Key_S:
                self.show_settings()
            elif event.key() == Qt.Key_T:
                self.show_statistics()
            elif event.key() == Qt.Key_Escape:
                QApplication.quit()
                
        elif self.engine.state == GameState.DIFFICULTY_SELECT:
            if event.key() == Qt.Key_Return:
                self.engine.start_game()
            elif event.key() == Qt.Key_Escape:
                self.engine.state = GameState.MENU
                
        elif self.engine.state == GameState.PLAYING:
            if event.key() == Qt.Key_P:
                self.engine.state = GameState.PAUSED
            elif event.key() == Qt.Key_Escape:
                self.engine.state = GameState.MENU
                
        elif self.engine.state == GameState.PAUSED:
            if event.key() == Qt.Key_P:
                self.engine.state = GameState.PLAYING
            elif event.key() == Qt.Key_Escape:
                self.engine.state = GameState.MENU
                
        elif self.engine.state == GameState.GAME_OVER:
            if event.key() == Qt.Key_R:
                self.engine.state = GameState.DIFFICULTY_SELECT
            elif event.key() == Qt.Key_Escape:
                self.engine.state = GameState.MENU
                
    def keyReleaseEvent(self, event):
        self.engine.keys_pressed.discard(event.key())
        
    def show_settings(self):
        """Показ диалога настроек"""
        if not self.settings_dialog:
            self.settings_dialog = SettingsDialog(self.engine.settings, self)
            
        if self.settings_dialog.exec_() == QDialog.Accepted:
            self.engine.save_settings()
            self.engine.sound_manager.set_settings(self.engine.settings)
            self.init_background()  # Обновляем фон
            
    def show_statistics(self):
        """Показ диалога статистики"""
        if not self.statistics_dialog:
            self.statistics_dialog = StatisticsDialog(self.engine.stats_manager, self)
        else:
            self.statistics_dialog.update_statistics()
            
        self.statistics_dialog.exec_()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Фон
        self.draw_background(painter)
        
        if self.engine.state == GameState.MENU:
            self.draw_menu(painter)
        elif self.engine.state == GameState.DIFFICULTY_SELECT:
            self.draw_difficulty_select(painter)
        elif self.engine.state == GameState.PLAYING:
            self.draw_game(painter)
        elif self.engine.state == GameState.PAUSED:
            self.draw_game(painter)
            self.draw_pause_screen(painter)
        elif self.engine.state == GameState.GAME_OVER:
            self.draw_game_over(painter)
            
    def draw_background(self, painter):
        """Отрисовка фона"""
        # Градиент
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(5, 5, 30))
        gradient.setColorAt(0.5, QColor(10, 10, 50))
        gradient.setColorAt(1, QColor(20, 20, 80))
        painter.fillRect(self.rect(), gradient)
        
        # Звёзды
        for star in self.background_stars:
            color = QColor(255, 255, 255, star['brightness'])
            painter.setPen(QPen(color, 1))
            painter.drawEllipse(int(star['x']), int(star['y']), 
                              int(star['size']), int(star['size']))
            
    def draw_menu(self, painter):
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.setFont(QFont('Arial', 36, QFont.Bold))
        painter.drawText(self.rect(), Qt.AlignCenter, "GALAGA REDUX")
        
        painter.setFont(QFont('Arial', 16))
        y_offset = 320
        
        painter.drawText(QRect(0, y_offset, self.width(), 30), Qt.AlignCenter, 
                        "ENTER - Начать игру")
        painter.drawText(QRect(0, y_offset + 30, self.width(), 30), Qt.AlignCenter, 
                        "S - Настройки")
        painter.drawText(QRect(0, y_offset + 60, self.width(), 30), Qt.AlignCenter, 
                        "T - Статистика")
        painter.drawText(QRect(0, y_offset + 90, self.width(), 30), Qt.AlignCenter, 
                        "ESC - Выход")
        
        painter.drawText(QRect(0, y_offset + 140, self.width(), 30), Qt.AlignCenter, 
                        f"Рекорд: {self.engine.high_score}")
        
    def draw_difficulty_select(self, painter):
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.setFont(QFont('Arial', 24, QFont.Bold))
        painter.drawText(QRect(0, 150, self.width(), 50), Qt.AlignCenter, 
                        "Выберите сложность")
        
        painter.setFont(QFont('Arial', 16))
        y_offset = 250
        
        difficulties = [
            ("1 - Легкий", "Больше жизней, медленные враги"),
            ("2 - Средний", "Стандартные параметры"),
            ("3 - Сложный", "Меньше жизней, быстрые враги")
        ]
        
        for i, (title, desc) in enumerate(difficulties):
            color = QColor(0, 255, 0) if i == self.engine.settings.difficulty.value - 1 else QColor(255, 255, 255)
            painter.setPen(QPen(color, 2))
            painter.drawText(QRect(0, y_offset + i * 60, self.width(), 30), Qt.AlignCenter, title)
            painter.setFont(QFont('Arial', 12))
            painter.drawText(QRect(0, y_offset + i * 60 + 25, self.width(), 30), Qt.AlignCenter, desc)
            painter.setFont(QFont('Arial', 16))
            
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.drawText(QRect(0, y_offset + 200, self.width(), 30), Qt.AlignCenter, 
                        "ENTER - Начать  |  ESC - Назад")
        
    def draw_game(self, painter):
        # Игрок
        self.draw_player(painter)
        
        # Пули
        for bullet in self.engine.bullets:
            self.draw_bullet(painter, bullet)
            
        # Враги
        for enemy in self.engine.enemies:
            self.draw_enemy(painter, enemy)
            
        # Power-ups
        for power_up in self.engine.power_ups:
            self.draw_power_up(painter, power_up)
            
        # Частицы
        if self.engine.settings.particles_enabled:
            for particle in self.engine.particles:
                self.draw_particle(painter, particle)
            
        # HUD
        self.draw_hud(painter)
        
    def draw_player(self, painter):
        """Улучшенная отрисовка игрока в стиле синего футуристического корабля"""
        if self.engine.player.is_invulnerable() and (self.engine.player.invulnerable_time // 5) % 2:
            return  # Мигание при неуязвимости
            
        x = self.engine.player.x
        y = self.engine.player.y
        w = self.engine.player.width
        h = self.engine.player.height
        
        # Основной корпус - синий градиент
        gradient = QLinearGradient(0, y, 0, y + h)
        gradient.setColorAt(0, QColor(100, 150, 255))
        gradient.setColorAt(0.5, QColor(50, 100, 255))
        gradient.setColorAt(1, QColor(20, 80, 200))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(150, 200, 255), 2))
        
        # Основной корпус (овал)
        painter.drawEllipse(int(x), int(y), w, h)
        
        # Боковые крылья
        wing_gradient = QLinearGradient(0, y, 0, y + h//2)
        wing_gradient.setColorAt(0, QColor(80, 120, 255))
        wing_gradient.setColorAt(1, QColor(40, 80, 200))
        painter.setBrush(QBrush(wing_gradient))
        
        # Левое крыло
        painter.drawEllipse(int(x - 8), int(y + h//3), 12, h//2)
        # Правое крыло
        painter.drawEllipse(int(x + w - 4), int(y + h//3), 12, h//2)
        
        # Кокпит
        painter.setBrush(QBrush(QColor(200, 220, 255, 150)))
        painter.drawEllipse(int(x + w//4), int(y + h//4), w//2, h//3)
        
        # Двигатели (эффект свечения)
        if self.engine.settings.effects_enabled:
            painter.setBrush(QBrush(QColor(255, 255, 255, 100)))
            painter.drawEllipse(int(x + w//4), int(y + h - 5), w//4, 8)
            painter.drawEllipse(int(x + w//2), int(y + h - 5), w//4, 8)
            
    def draw_enemy(self, painter, enemy):
        """Улучшенная отрисовка врагов"""
        x = enemy.x
        y = enemy.y
        w = enemy.width
        h = enemy.height
        
        if enemy.enemy_type == "basic":
            # Красный враг
            gradient = QLinearGradient(0, y, 0, y + h)
            gradient.setColorAt(0, QColor(255, 100, 100))
            gradient.setColorAt(1, QColor(200, 50, 50))
            painter.setBrush(QBrush(gradient))
            painter.setPen(QPen(QColor(255, 150, 150), 2))
        else:
            # Фиолетовый враг (продвинутый)
            gradient = QLinearGradient(0, y, 0, y + h)
            gradient.setColorAt(0, QColor(255, 100, 255))
            gradient.setColorAt(1, QColor(200, 50, 200))
            painter.setBrush(QBrush(gradient))
            painter.setPen(QPen(QColor(255, 150, 255), 2))
            
        # Основной корпус
        painter.drawEllipse(int(x), int(y), w, h)
        
        # Антенны
        painter.drawLine(int(x + w//4), int(y), int(x + w//4), int(y - 8))
        painter.drawLine(int(x + 3*w//4), int(y), int(x + 3*w//4), int(y - 8))
        
        # Глаза (для продвинутых врагов)
        if enemy.enemy_type == "advanced":
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.drawEllipse(int(x + w//4), int(y + h//3), 4, 4)
            painter.drawEllipse(int(x + 3*w//4 - 4), int(y + h//3), 4, 4)
            
    def draw_bullet(self, painter, bullet):
        """Отрисовка пуль"""
        if bullet.is_player_bullet:
            # Пули игрока - яркие желтые
            painter.setBrush(QBrush(QColor(255, 255, 100)))
            painter.setPen(QPen(QColor(255, 255, 200), 1))
        else:
            # Пули врагов - красные
            painter.setBrush(QBrush(QColor(255, 100, 100)))
            painter.setPen(QPen(QColor(255, 150, 150), 1))
            
        painter.drawEllipse(bullet.get_rect())
        
    def draw_power_up(self, painter, power_up):
        """Отрисовка бонусов"""
        rect = power_up.get_rect()
        
        # Эффект мерцания
        alpha = int(200 + 55 * math.sin(self.engine.enemy_spawn_timer * 0.1))
        
        if power_up.power_type == "rapid_fire":
            color = QColor(255, 255, 0, alpha)
        elif power_up.power_type == "double_shot":
            color = QColor(0, 255, 255, alpha)
        else:  # shield
            color = QColor(255, 255, 255, alpha)
            
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(color, 2))
        painter.drawEllipse(rect)
        
        # Символ в центре
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.setFont(QFont('Arial', 12, QFont.Bold))
        symbol = "R" if power_up.power_type == "rapid_fire" else "D" if power_up.power_type == "double_shot" else "S"
        painter.drawText(rect, Qt.AlignCenter, symbol)
        
    def draw_particle(self, painter, particle):
        """Отрисовка частиц"""
        color = QColor(particle.color)
        color.setAlpha(particle.get_alpha())
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(color, 1))
        painter.drawEllipse(int(particle.x), int(particle.y), 3, 3)
        
    def draw_hud(self, painter):
        """Отрисовка HUD"""
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.setFont(QFont('Arial', 14, QFont.Bold))
        
        # Счёт
        painter.drawText(10, 25, f"Счёт: {self.engine.score}")
        
        # Жизни
        painter.drawText(10, 50, f"Жизни: {self.engine.player.lives}")
        
        # Волна
        painter.drawText(10, 75, f"Волна: {self.engine.wave}")
        
        # Сложность
        diff_text = self.engine.settings.difficulty.name
        painter.drawText(10, 100, f"Сложность: {diff_text}")
        
        # Рекорд
        painter.drawText(self.width() - 150, 25, f"Рекорд: {self.engine.high_score}")
        
        # Статистика стрельбы
        accuracy = (self.engine.enemies_killed / max(self.engine.shots_fired, 1)) * 100
        painter.drawText(self.width() - 150, 50, f"Точность: {accuracy:.1f}%")
        
    def draw_pause_screen(self, painter):
        # Полупрозрачный фон
        painter.setBrush(QBrush(QColor(0, 0, 0, 150)))
        painter.drawRect(self.rect())
        
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.setFont(QFont('Arial', 24, QFont.Bold))
        painter.drawText(self.rect(), Qt.AlignCenter, "ПАУЗА\n\nP - Продолжить\nESC - В меню")
        
    def draw_game_over(self, painter):
        # Полупрозрачный фон
        painter.setBrush(QBrush(QColor(0, 0, 0, 150)))
        painter.drawRect(self.rect())
        
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.setFont(QFont('Arial', 24, QFont.Bold))
        
        # Вычисление статистики
        accuracy = (self.engine.enemies_killed / max(self.engine.shots_fired, 1)) * 100
        game_duration = int(datetime.datetime.now().timestamp() - self.engine.game_start_time)
        
        text = f"""ИГРА ОКОНЧЕНА

Счёт: {self.engine.score}
Рекорд: {self.engine.high_score}
Точность: {accuracy:.1f}%
Время: {game_duration} сек
Убито врагов: {self.engine.enemies_killed}

R - Новая игра
ESC - В меню"""
        
        painter.drawText(self.rect(), Qt.AlignCenter, text)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Galaga Redux - Космический Шутер")
        self.setFixedSize(800, 600)
        
        # Основной виджет
        self.game_widget = GameWidget()
        self.setCentralWidget(self.game_widget)
        
        # Стиль окна
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000020;
            }
            QDialog {
                background-color: #1a1a2e;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #4a4a6a;
                background-color: #2a2a3a;
            }
            QTabWidget::tab-bar {
                alignment: center;
            }
            QTabBar::tab {
                background-color: #3a3a4a;
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #4a4a6a;
            }
            QPushButton {
                background-color: #4a4a6a;
                color: #ffffff;
                border: 1px solid #6a6a8a;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5a5a7a;
            }
            QPushButton:pressed {
                background-color: #3a3a5a;
            }
            QSlider::groove:horizontal {
                border: 1px solid #4a4a6a;
                height: 8px;
                background: #2a2a3a;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #6a6a8a;
                border: 1px solid #8a8aaa;
                width: 18px;
                border-radius: 9px;
            }
            QCheckBox {
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QRadioButton {
                color: #ffffff;
            }
            QGroupBox {
                color: #ffffff;
                border: 1px solid #4a4a6a;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QTableWidget {
                background-color: #2a2a3a;
                color: #ffffff;
                gridline-color: #4a4a6a;
                border: 1px solid #4a4a6a;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QTableWidget::item:selected {
                background-color: #4a4a6a;
            }
            QHeaderView::section {
                background-color: #3a3a4a;
                color: #ffffff;
                padding: 4px;
                border: 1px solid #4a4a6a;
            }
            QComboBox {
                background-color: #3a3a4a;
                color: #ffffff;
                border: 1px solid #4a4a6a;
                padding: 4px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
            }
            QSpinBox {
                background-color: #3a3a4a;
                color: #ffffff;
                border: 1px solid #4a4a6a;
                padding: 4px;
            }
        """)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Galaga Redux")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
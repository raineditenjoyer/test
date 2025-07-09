#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import random
import math
import json
from typing import List, Tuple, Dict
from dataclasses import dataclass
from enum import Enum

# Добавляем путь к PyQt5
sys.path.append('/usr/lib/python3/dist-packages')

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QDialog, 
                             QDialogButtonBox, QTextEdit, QFrame)
from PyQt5.QtCore import QTimer, Qt, QPoint, QRect, QSize, pyqtSignal
from PyQt5.QtGui import (QPainter, QColor, QBrush, QPen, QFont, QPixmap, 
                         QPolygon, QLinearGradient, QRadialGradient)
# from PyQt5.QtOpenGL import QOpenGLWidget  # Не используется в этой версии

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3
    PAUSED = 4

@dataclass
class GameSettings:
    window_width: int = 800
    window_height: int = 600
    player_speed: int = 5
    bullet_speed: int = 8
    enemy_speed: int = 2
    enemy_bullet_speed: int = 4
    fps: int = 60
    
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
            
    def start_game(self):
        self.state = GameState.PLAYING
        self.score = 0
        self.wave = 1
        self.player = Player(self.settings.window_width // 2 - 20, 
                           self.settings.window_height - 50)
        self.bullets.clear()
        self.enemies.clear()
        self.power_ups.clear()
        self.particles.clear()
        
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
        
        # Движение игрока
        if Qt.Key_Left in self.keys_pressed or Qt.Key_A in self.keys_pressed:
            self.player.x = max(0, self.player.x - self.settings.player_speed)
        if Qt.Key_Right in self.keys_pressed or Qt.Key_D in self.keys_pressed:
            self.player.x = min(self.settings.window_width - self.player.width, 
                               self.player.x + self.settings.player_speed)
        if Qt.Key_Up in self.keys_pressed or Qt.Key_W in self.keys_pressed:
            self.player.y = max(0, self.player.y - self.settings.player_speed)
        if Qt.Key_Down in self.keys_pressed or Qt.Key_S in self.keys_pressed:
            self.player.y = min(self.settings.window_height - self.player.height, 
                               self.player.y + self.settings.player_speed)
            
        # Стрельба
        if Qt.Key_Space in self.keys_pressed:
            if len([b for b in self.bullets if b.is_player_bullet]) < 5:
                bullet = Bullet(self.player.x + self.player.width // 2, 
                               self.player.y, -self.settings.bullet_speed)
                self.bullets.append(bullet)
                
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
            self.state = GameState.GAME_OVER
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
                
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
                    
                    # Эффект взрыва
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
                
                # Эффект попадания
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
                
        # Коллизии power-ups с игроком
        for power_up in self.power_ups[:]:
            if power_up.collides_with(self.player):
                self.power_ups.remove(power_up)
                # Здесь можно добавить логику применения power-up
                self.score += 50

class GameWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.engine = GameEngine()
        self.setFixedSize(self.engine.settings.window_width, 
                         self.engine.settings.window_height)
        self.setFocusPolicy(Qt.StrongFocus)
        
        # Таймер для обновления игры
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_game)
        self.timer.start(1000 // self.engine.settings.fps)
        
        # Фон
        self.background_stars = []
        for _ in range(100):
            self.background_stars.append({
                'x': random.randint(0, self.engine.settings.window_width),
                'y': random.randint(0, self.engine.settings.window_height),
                'speed': random.uniform(0.5, 2.0),
                'size': random.randint(1, 3)
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
        
        if event.key() == Qt.Key_P and self.engine.state == GameState.PLAYING:
            self.engine.state = GameState.PAUSED
        elif event.key() == Qt.Key_P and self.engine.state == GameState.PAUSED:
            self.engine.state = GameState.PLAYING
        elif event.key() == Qt.Key_Return and self.engine.state == GameState.MENU:
            self.engine.start_game()
        elif event.key() == Qt.Key_R and self.engine.state == GameState.GAME_OVER:
            self.engine.start_game()
            
    def keyReleaseEvent(self, event):
        self.engine.keys_pressed.discard(event.key())
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Фон
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(0, 0, 20))
        gradient.setColorAt(1, QColor(0, 0, 80))
        painter.fillRect(self.rect(), gradient)
        
        # Звёзды
        painter.setPen(QPen(QColor(255, 255, 255, 180), 1))
        for star in self.background_stars:
            painter.drawEllipse(star['x'], star['y'], star['size'], star['size'])
            
        if self.engine.state == GameState.MENU:
            self.draw_menu(painter)
        elif self.engine.state == GameState.PLAYING:
            self.draw_game(painter)
        elif self.engine.state == GameState.PAUSED:
            self.draw_game(painter)
            self.draw_pause_screen(painter)
        elif self.engine.state == GameState.GAME_OVER:
            self.draw_game_over(painter)
            
    def draw_menu(self, painter):
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.setFont(QFont('Arial', 36, QFont.Bold))
        painter.drawText(self.rect(), Qt.AlignCenter, "GALAGA REDUX")
        
        painter.setFont(QFont('Arial', 16))
        painter.drawText(QRect(0, 300, self.width(), 100), Qt.AlignCenter, 
                        "Нажмите ENTER для начала игры")
        painter.drawText(QRect(0, 350, self.width(), 100), Qt.AlignCenter, 
                        f"Рекорд: {self.engine.high_score}")
        
    def draw_game(self, painter):
        # Игрок
        self.draw_player(painter)
        
        # Пули
        painter.setBrush(QBrush(QColor(255, 255, 0)))
        for bullet in self.engine.bullets:
            if bullet.is_player_bullet:
                painter.setBrush(QBrush(QColor(255, 255, 0)))
            else:
                painter.setBrush(QBrush(QColor(255, 0, 0)))
            painter.drawEllipse(bullet.get_rect())
            
        # Враги
        for enemy in self.engine.enemies:
            self.draw_enemy(painter, enemy)
            
        # Power-ups
        for power_up in self.engine.power_ups:
            self.draw_power_up(painter, power_up)
            
        # Частицы
        for particle in self.engine.particles:
            color = QColor(particle.color)
            color.setAlpha(particle.get_alpha())
            painter.setBrush(QBrush(color))
            painter.drawEllipse(particle.x, particle.y, 3, 3)
            
        # HUD
        self.draw_hud(painter)
        
    def draw_player(self, painter):
        if self.engine.player.is_invulnerable() and (self.engine.player.invulnerable_time // 5) % 2:
            return  # Мигание при неуязвимости
            
        # Корпус корабля
        painter.setBrush(QBrush(QColor(0, 255, 0)))
        painter.setPen(QPen(QColor(0, 200, 0), 2))
        
        # Основной корпус
        rect = self.engine.player.get_rect()
        painter.drawEllipse(rect)
        
        # Крылья
        painter.setBrush(QBrush(QColor(0, 200, 0)))
        painter.drawEllipse(rect.x() - 5, rect.y() + 10, 10, 15)
        painter.drawEllipse(rect.x() + rect.width() - 5, rect.y() + 10, 10, 15)
        
    def draw_enemy(self, painter, enemy):
        rect = enemy.get_rect()
        
        if enemy.enemy_type == "basic":
            painter.setBrush(QBrush(QColor(255, 0, 0)))
            painter.setPen(QPen(QColor(200, 0, 0), 2))
        else:
            painter.setBrush(QBrush(QColor(255, 0, 255)))
            painter.setPen(QPen(QColor(200, 0, 200), 2))
            
        # Основной корпус
        painter.drawEllipse(rect)
        
        # Антенны
        painter.drawLine(rect.x() + 5, rect.y(), rect.x() + 5, rect.y() - 5)
        painter.drawLine(rect.x() + rect.width() - 5, rect.y(), 
                        rect.x() + rect.width() - 5, rect.y() - 5)
        
    def draw_power_up(self, painter, power_up):
        rect = power_up.get_rect()
        
        if power_up.power_type == "rapid_fire":
            painter.setBrush(QBrush(QColor(255, 255, 0)))
        elif power_up.power_type == "double_shot":
            painter.setBrush(QBrush(QColor(0, 255, 255)))
        else:  # shield
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            
        painter.drawEllipse(rect)
        
    def draw_hud(self, painter):
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.setFont(QFont('Arial', 14))
        
        # Счёт
        painter.drawText(10, 25, f"Счёт: {self.engine.score}")
        
        # Жизни
        painter.drawText(10, 50, f"Жизни: {self.engine.player.lives}")
        
        # Волна
        painter.drawText(10, 75, f"Волна: {self.engine.wave}")
        
        # Рекорд
        painter.drawText(self.width() - 150, 25, f"Рекорд: {self.engine.high_score}")
        
    def draw_pause_screen(self, painter):
        # Полупрозрачный фон
        painter.setBrush(QBrush(QColor(0, 0, 0, 150)))
        painter.drawRect(self.rect())
        
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.setFont(QFont('Arial', 24, QFont.Bold))
        painter.drawText(self.rect(), Qt.AlignCenter, "ПАУЗА\n\nНажмите P для продолжения")
        
    def draw_game_over(self, painter):
        # Полупрозрачный фон
        painter.setBrush(QBrush(QColor(0, 0, 0, 150)))
        painter.drawRect(self.rect())
        
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.setFont(QFont('Arial', 24, QFont.Bold))
        
        text = f"ИГРА ОКОНЧЕНА\n\nСчёт: {self.engine.score}\nРекорд: {self.engine.high_score}\n\nНажмите R для новой игры"
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
        """)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Galaga Redux")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
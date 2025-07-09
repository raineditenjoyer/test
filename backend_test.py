#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Backend Test Suite for Galaga Redux
This file tests the backend components of the Galaga Redux game.
"""

import sys
import os
import unittest
import json
import sqlite3
import tempfile
import shutil
from pathlib import Path

# Add PyQt5 path
sys.path.append('/usr/lib/python3/dist-packages')

# Import game components
from galaga_game import (
    GameEngine, GameSettings, DifficultyLevel, 
    SoundManager, StatisticsManager, Player, Enemy, Bullet
)

class TestGameSettings(unittest.TestCase):
    """Test the GameSettings class and its functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.settings_file = os.path.join(self.temp_dir, 'game_settings.json')
        self.original_dir = os.getcwd()
        os.chdir(self.temp_dir)
        
    def tearDown(self):
        """Clean up after tests"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.temp_dir)
        
    def test_default_settings(self):
        """Test default settings values"""
        settings = GameSettings()
        self.assertEqual(settings.window_width, 800)
        self.assertEqual(settings.window_height, 600)
        self.assertEqual(settings.player_speed, 5)
        self.assertTrue(settings.sound_enabled)
        self.assertTrue(settings.music_enabled)
        self.assertEqual(settings.difficulty, DifficultyLevel.MEDIUM)
        
    def test_save_load_settings(self):
        """Test saving and loading settings"""
        # Create engine with modified settings
        engine = GameEngine()
        engine.settings.sound_enabled = False
        engine.settings.music_enabled = False
        engine.settings.sound_volume = 0.3
        engine.settings.music_volume = 0.2
        engine.settings.difficulty = DifficultyLevel.HARD
        
        # Save settings
        engine.save_settings()
        
        # Verify file exists
        self.assertTrue(os.path.exists('game_settings.json'))
        
        # Create new engine and load settings
        new_engine = GameEngine()
        new_engine.load_settings()
        
        # Verify settings were loaded correctly
        self.assertFalse(new_engine.settings.sound_enabled)
        self.assertFalse(new_engine.settings.music_enabled)
        self.assertEqual(new_engine.settings.sound_volume, 0.3)
        self.assertEqual(new_engine.settings.music_volume, 0.2)
        self.assertEqual(new_engine.settings.difficulty, DifficultyLevel.HARD)

class TestSoundManager(unittest.TestCase):
    """Test the SoundManager class"""
    
    def test_initialization(self):
        """Test sound manager initialization"""
        sound_manager = SoundManager()
        self.assertIsNotNone(sound_manager)
        self.assertIsNotNone(sound_manager.sounds)
        
    def test_set_settings(self):
        """Test setting game settings in sound manager"""
        sound_manager = SoundManager()
        settings = GameSettings()
        settings.sound_enabled = False
        settings.music_enabled = False
        
        sound_manager.set_settings(settings)
        self.assertEqual(sound_manager.settings, settings)
        
    def test_play_sound_methods(self):
        """Test sound playing methods (without actual playback)"""
        sound_manager = SoundManager()
        settings = GameSettings()
        sound_manager.set_settings(settings)
        
        # These should not raise exceptions
        sound_manager.play_sound('shoot')
        sound_manager.play_sound('explosion')
        sound_manager.play_music('background')
        sound_manager.stop_music()
        
        # Test with sound disabled
        settings.sound_enabled = False
        settings.music_enabled = False
        sound_manager.set_settings(settings)
        sound_manager.play_sound('shoot')  # Should do nothing
        sound_manager.play_music('background')  # Should do nothing

class TestStatisticsManager(unittest.TestCase):
    """Test the StatisticsManager class"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.temp_dir)
        self.stats_manager = StatisticsManager()
        
    def tearDown(self):
        """Clean up after tests"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.temp_dir)
        
    def test_database_creation(self):
        """Test database creation"""
        self.assertTrue(os.path.exists('game_stats.db'))
        
        # Verify table structure
        conn = sqlite3.connect('game_stats.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='game_results'")
        self.assertIsNotNone(cursor.fetchone())
        
        # Check columns
        cursor.execute("PRAGMA table_info(game_results)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        expected_columns = [
            'id', 'date', 'score', 'level', 'difficulty', 
            'duration', 'enemies_killed', 'shots_fired', 'accuracy'
        ]
        
        for col in expected_columns:
            self.assertIn(col, column_names)
            
        conn.close()
        
    def test_save_game_result(self):
        """Test saving game results"""
        self.stats_manager.save_game_result(
            score=1000,
            level=5,
            difficulty="MEDIUM",
            duration=120,
            enemies_killed=15,
            shots_fired=25
        )
        
        # Verify data was saved
        conn = sqlite3.connect('game_stats.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM game_results")
        results = cursor.fetchall()
        conn.close()
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][2], 1000)  # score
        self.assertEqual(results[0][3], 5)     # level
        self.assertEqual(results[0][4], "MEDIUM")  # difficulty
        
    def test_get_statistics(self):
        """Test retrieving statistics"""
        # Add multiple entries
        for i in range(3):
            self.stats_manager.save_game_result(
                score=1000 * (i + 1),
                level=i + 1,
                difficulty="MEDIUM" if i % 2 == 0 else "HARD",
                duration=120,
                enemies_killed=15,
                shots_fired=25
            )
            
        # Get all statistics
        stats = self.stats_manager.get_statistics()
        self.assertEqual(len(stats), 3)
        
        # Test limit
        stats = self.stats_manager.get_statistics(limit=2)
        self.assertEqual(len(stats), 2)
        
    def test_filtered_statistics(self):
        """Test filtered statistics"""
        # Add entries with different difficulties
        difficulties = ["EASY", "MEDIUM", "HARD", "MEDIUM"]
        for i, diff in enumerate(difficulties):
            self.stats_manager.save_game_result(
                score=1000 * (i + 1),
                level=i + 1,
                difficulty=diff,
                duration=120,
                enemies_killed=15,
                shots_fired=25
            )
            
        # Filter by difficulty
        medium_stats = self.stats_manager.get_filtered_statistics(difficulty="MEDIUM")
        self.assertEqual(len(medium_stats), 2)
        
        hard_stats = self.stats_manager.get_filtered_statistics(difficulty="HARD")
        self.assertEqual(len(hard_stats), 1)

class TestGameEngine(unittest.TestCase):
    """Test the GameEngine class"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.temp_dir)
        
    def tearDown(self):
        """Clean up after tests"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.temp_dir)
        
    def test_initialization(self):
        """Test game engine initialization"""
        engine = GameEngine()
        self.assertEqual(engine.score, 0)
        self.assertEqual(engine.wave, 1)
        self.assertIsNotNone(engine.player)
        self.assertIsNotNone(engine.sound_manager)
        self.assertIsNotNone(engine.stats_manager)
        
    def test_difficulty_settings(self):
        """Test applying difficulty settings"""
        engine = GameEngine()
        
        # Test EASY difficulty
        engine.settings.difficulty = DifficultyLevel.EASY
        engine.apply_difficulty_settings()
        self.assertEqual(engine.player.lives, 5)
        self.assertEqual(engine.settings.player_speed, 6)
        self.assertEqual(engine.settings.enemy_speed, 1)
        
        # Test MEDIUM difficulty
        engine.settings.difficulty = DifficultyLevel.MEDIUM
        engine.apply_difficulty_settings()
        self.assertEqual(engine.player.lives, 3)
        self.assertEqual(engine.settings.player_speed, 5)
        self.assertEqual(engine.settings.enemy_speed, 2)
        
        # Test HARD difficulty
        engine.settings.difficulty = DifficultyLevel.HARD
        engine.apply_difficulty_settings()
        self.assertEqual(engine.player.lives, 2)
        self.assertEqual(engine.settings.player_speed, 4)
        self.assertEqual(engine.settings.enemy_speed, 3)
        
    def test_high_score(self):
        """Test high score functionality"""
        engine = GameEngine()
        
        # Set a score and save high score
        engine.score = 1000
        engine.high_score = 1000
        engine.save_high_score()
        
        # Verify file exists
        self.assertTrue(os.path.exists('high_score.json'))
        
        # Verify content
        with open('high_score.json', 'r') as f:
            data = json.load(f)
            self.assertEqual(data['high_score'], 1000)
            
        # Create new engine and check if high score is loaded
        new_engine = GameEngine()
        self.assertEqual(new_engine.high_score, 1000)
        
    def test_game_objects(self):
        """Test game objects creation and interaction"""
        # Test Player
        player = Player(400, 500)
        self.assertEqual(player.x, 400)
        self.assertEqual(player.y, 500)
        self.assertEqual(player.lives, 3)
        self.assertFalse(player.is_invulnerable())
        
        # Test taking damage
        player.take_damage()
        self.assertEqual(player.lives, 2)
        self.assertTrue(player.is_invulnerable())
        
        # Test Enemy
        enemy = Enemy(300, 100)
        self.assertEqual(enemy.x, 300)
        self.assertEqual(enemy.y, 100)
        self.assertEqual(enemy.points, 100)  # Basic enemy
        
        # Test Bullet
        bullet = Bullet(400, 500, -8, True)
        self.assertEqual(bullet.x, 400)
        self.assertEqual(bullet.y, 500)
        self.assertEqual(bullet.velocity_y, -8)
        self.assertTrue(bullet.is_player_bullet)
        
        # Test bullet movement
        bullet.update()
        self.assertEqual(bullet.y, 492)  # 500 - 8
        
        # Test collision detection
        player = Player(100, 100)
        enemy = Enemy(100, 100)
        self.assertTrue(player.collides_with(enemy))
        
        enemy = Enemy(200, 200)  # Move enemy away
        self.assertFalse(player.collides_with(enemy))

class TestGameFunctions(unittest.TestCase):
    """Test the game functions from test_game_functions.py"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.temp_dir)
        
    def tearDown(self):
        """Clean up after tests"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.temp_dir)
        
    def test_game_engine_function(self):
        """Test game engine function from test_game_functions.py"""
        from test_game_functions import test_game_engine
        test_game_engine()
        
    def test_sound_manager_function(self):
        """Test sound manager function from test_game_functions.py"""
        from test_game_functions import test_sound_manager
        test_sound_manager()
        
    def test_statistics_manager_function(self):
        """Test statistics manager function from test_game_functions.py"""
        from test_game_functions import test_statistics_manager
        test_statistics_manager()
        
    def test_difficulty_settings_function(self):
        """Test difficulty settings function from test_game_functions.py"""
        from test_game_functions import test_difficulty_settings
        test_difficulty_settings()

def run_tests():
    """Run all tests"""
    print("🚀 Running backend tests for Galaga Redux...")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestGameSettings))
    test_suite.addTest(unittest.makeSuite(TestSoundManager))
    test_suite.addTest(unittest.makeSuite(TestStatisticsManager))
    test_suite.addTest(unittest.makeSuite(TestGameEngine))
    test_suite.addTest(unittest.makeSuite(TestGameFunctions))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print("=" * 50)
    if result.wasSuccessful():
        print("✅ All backend tests passed successfully!")
    else:
        print(f"❌ {len(result.failures)} tests failed.")
        
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
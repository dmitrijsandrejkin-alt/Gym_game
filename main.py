#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle

# Настройки окна для мобильных устройств
Window.clearcolor = (0.1, 0.12, 0.15, 1)  # тёмный фон

# ===================== ФАЙЛ СОХРАНЕНИЯ =====================
# Для Android: сохраняем в приватную папку приложения
if hasattr(os, 'getenv') and os.getenv('ANDROID_PRIVATE'):
    SAVE_FILE = os.path.join(os.getenv('ANDROID_PRIVATE'), 'gym_save.json')
else:
    SAVE_FILE = 'gym_save.json'

# ===================== ДАННЫЕ ИГРЫ =====================
muscle_levels = [
    {"name": "Новичок", "weight_required": 0, "weight_limit": 10, "max_reps": 6, "color": (0.5, 0.5, 0.5, 1)},
    {"name": "Начинающий", "weight_required": 300, "weight_limit": 20, "max_reps": 8, "color": (0.3, 0.6, 0.3, 1)},
    {"name": "Любитель", "weight_required": 800, "weight_limit": 35, "max_reps": 10, "color": (0.3, 0.5, 0.8, 1)},
    {"name": "Продвинутый", "weight_required": 1800, "weight_limit": 55, "max_reps": 12, "color": (0.6, 0.4, 0.8, 1)},
    {"name": "Профессионал", "weight_required": 3500, "weight_limit": 80, "max_reps": 15, "color": (0.9, 0.7, 0.2, 1)},
    {"name": "Элита", "weight_required": 6000, "weight_limit": 110, "max_reps": 18, "color": (0.9, 0.4, 0.2, 1)},
    {"name": "Легенда", "weight_required": 10000, "weight_limit": 150, "max_reps": 20, "color": (0.9, 0.2, 0.2, 1)},
]

shop_items = {
    "protein_1": {"name": "🍫 Сывороточный", "price": 300, "bonus": 20, "duration": 5, "desc": "+20% силы на 5 подходов"},
    "protein_2": {"name": "🥛 Казеин", "price": 500, "bonus": 15, "duration": 8, "desc": "+15% силы на 8 подходов"},
    "protein_3": {"name": "🌱 Растительный", "price": 400, "bonus": 10, "duration": 10, "desc": "+10% силы на 10 подходов"},
    "creatine": {"name": "⚡ Креатин", "price": 1500, "bonus": 10, "desc": "+10% ко всем тренировкам НАВСЕГДА"},
}

gyms = {
    "1": {"name": "🏋️ Гантели", "current_weight": 3, "icon": "🏋️"},
    "2": {"name": "🏋️ Штанга", "current_weight": 10, "icon": "🏋️"},
    "3": {"name": "🦵 Жим ногами", "current_weight": 20, "icon": "🦵"},
}

# ===================== ГЛАВНЫЙ КЛАСС ИГРЫ =====================
class GameData:
    """Хранит состояние игры"""
    def __init__(self):
        self.currency = 300
        self.active_protein = None
        self.protein_remaining = 0
        self.permanent_bonus = 0
        self.stats = {
            "total_weight_lifted": 0,
            "total_workouts": 0,
            "max_weight_per_workout": 0,
            "total_currency_earned": 0,
            "proteins_bought": 0,
            "creatine_bought": False
        }
        self.gyms = {
            "1": {"name": "🏋️ Гантели", "current_weight": 3},
            "2": {"name": "🏋️ Штанга", "current_weight": 10},
            "3": {"name": "🦵 Жим ногами", "current_weight": 20},
        }
    
    def get_muscle_level(self):
        total = self.stats["total_weight_lifted"]
        current = muscle_levels[0]
        for level in muscle_levels:
            if total >= level["weight_required"]:
                current = level
            else:
                break
        return current
    
    def save(self):
        try:
            data = {
                "currency": self.currency,
                "active_protein": self.active_protein,
                "protein_remaining": self.protein_remaining,
                "permanent_bonus": self.permanent_bonus,
                "stats": self.stats,
                "gyms": self.gyms,
                "version": 2  # версия сохранения для совместимости
            }
            with open(SAVE_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False
    
    def load(self):
        if not os.path.exists(SAVE_FILE):
            return False
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.currency = data.get("currency", 300)
            self.active_protein = data.get("active_protein", None)
            self.protein_remaining = data.get("protein_remaining", 0)
            self.permanent_bonus = data.get("permanent_bonus", 0)
            self.stats = data.get("stats", self.stats)
            saved_gyms = data.get("gyms", {})
            for key in self.gyms:
                if key in saved_gyms:
                    self.gyms[key]["current_weight"] = saved_gyms[key]["current_weight"]
            return True
        except:
            return False

# ===================== КАСТОМНЫЕ ВИДЖЕТЫ =====================
class RoundedButton(Button):
    """Кнопка со скруглёнными углами"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ''
        with self.canvas.before:
            Color(0.2, 0.6, 0.8, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[10])
        self.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

# ===================== ЭКРАНЫ =====================
class MainMenuScreen(Screen):
    def __init__(self, game_data, **kwargs):
        super().__init__(**kwargs)
        self.game_data = game_data
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Заголовок
        title = Label(text="🏋️‍♂️ ТРЕНАЖЁРНЫЙ ЗАЛ 🏋️‍♂️", font_size='24sp', size_hint_y=0.15)
        layout.add_widget(title)
        
        # Статус
        self.status_label = Label(text="", font_size='16sp', size_hint_y=0.2)
        layout.add_widget(self.status_label)
        
        # Кнопки меню
        buttons = [
            ("🏋️ Спортзал", self.go_to_gym),
            ("🛒 Магазин", self.go_to_shop),
            ("🏠 Дом", self.go_to_home),
            ("📊 Статистика", self.go_to_stats),
            ("⚙️ Настройки", self.go_to_settings),
        ]
        
        for text, callback in buttons:
            btn = RoundedButton(text=text, font_size='18sp', size_hint_y=0.1)
            btn.bind(on_press=callback)
            layout.add_widget(btn)
        
        self.add_widget(layout)
    
    def on_enter(self):
        self.update_status()
    
    def update_status(self):
        muscle = self.game_data.get_muscle_level()
        self.status_label.text = (
            f"💰 {self.game_data.currency}\n"
            f"💪 {muscle['name']} | {self.game_data.stats['total_weight_lifted']} кг\n"
            f"📊 Лимит: {muscle['weight_limit']} кг"
        )
    
    def go_to_gym(self, instance):
        self.manager.current = 'gym'
    
    def go_to_shop(self, instance):
        self.manager.current = 'shop'
    
    def go_to_home(self, instance):
        self.manager.current = 'home'
    
    def go_to_stats(self, instance):
        self.manager.current = 'stats'
    
    def go_to_settings(self, instance):
        self.manager.current = 'settings'

class GymScreen(Screen):
    def __init__(self, game_data, **kwargs):
        super().__init__(**kwargs)
        self.game_data = game_data
        self.selected_gym = None
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Заголовок
        title = Label(text="🏋️ СПОРТЗАЛ 🏋️", font_size='22sp', size_hint_y=0.1)
        layout.add_widget(title)
        
        # Информация
        self.info_label = Label(text="", font_size='14sp', size_hint_y=0.15)
        layout.add_widget(self.info_label)
        
        # Кнопки тренажёров
        gyms_layout = GridLayout(cols=1, spacing=10, size_hint_y=0.5)
        self.gym_buttons = {}
        for key, gym in game_data.gyms.items():
            btn = RoundedButton(text=f"{gym['name']} - {gym['current_weight']} кг", font_size='16sp')
            btn.bind(on_press=lambda x, k=key: self.select_gym(k))
            gyms_layout.add_widget(btn)
            self.gym_buttons[key] = btn
        
        layout.add_widget(gyms_layout)
        
        # Кнопка начала тренировки
        self.start_btn = RoundedButton(text="▶ НАЧАТЬ ТРЕНИРОВКУ", font_size='18sp', size_hint_y=0.1, disabled=True)
        self.start_btn.bind(on_press=self.start_workout)
        layout.add_widget(self.start_btn)
        
        # Кнопка назад
        back_btn = RoundedButton(text="◀ НАЗАД", font_size='16sp', size_hint_y=0.08)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def on_enter(self):
        self.update_info()
        self.selected_gym = None
        self.start_btn.disabled = True
    
    def update_info(self):
        muscle = self.game_data.get_muscle_level()
        self.info_label.text = (
            f"Уровень: {muscle['name']}\n"
            f"Лимит веса: {muscle['weight_limit']} кг\n"
            f"Макс повторений: {muscle['max_reps']}\n"
            f"Бонус: +{self.game_data.permanent_bonus}%"
        )
        # Обновляем текст кнопок
        for key, gym in self.game_data.gyms.items():
            if key in self.gym_buttons:
                self.gym_buttons[key].text = f"{gym['name']} - {gym['current_weight']} кг"
    
    def select_gym(self, key):
        self.selected_gym = key
        self.start_btn.disabled = False
    
    def start_workout(self, instance):
        if self.selected_gym:
            self.manager.current = 'workout'
            self.manager.get_screen('workout').setup_workout(self.selected_gym)

class WorkoutScreen(Screen):
    def __init__(self, game_data, **kwargs):
        super().__init__(**kwargs)
        self.game_data = game_data
        self.gym_key = None
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        self.title_label = Label(text="🏋️ ТРЕНИРОВКА 🏋️", font_size='22sp', size_hint_y=0.1)
        layout.add_widget(self.title_label)
        
        self.info_label = Label(text="", font_size='14sp', size_hint_y=0.15)
        layout.add_widget(self.info_label)
        
        # Вес
        weight_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        weight_layout.add_widget(Label(text="Вес (кг):", font_size='16sp', size_hint_x=0.3))
        self.weight_input = TextInput(text="", input_filter='int', multiline=False, font_size='16sp')
        weight_layout.add_widget(self.weight_input)
        layout.add_widget(weight_layout)
        
        # Подходы
        sets_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        sets_layout.add_widget(Label(text="Подходы (2-20):", font_size='16sp', size_hint_x=0.4))
        self.sets_slider = Slider(min=2, max=20, value=3, step=1)
        self.sets_label = Label(text="3", font_size='16sp', size_hint_x=0.2)
        self.sets_slider.bind(value=self.update_sets_label)
        sets_layout.add_widget(self.sets_slider)
        sets_layout.add_widget(self.sets_label)
        layout.add_widget(sets_layout)
        
        # Повторения
        reps_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        reps_layout.add_widget(Label(text="Повторения:", font_size='16sp', size_hint_x=0.4))
        self.reps_slider = Slider(min=2, max=6, value=5, step=1)
        self.reps_label = Label(text="5", font_size='16sp', size_hint_x=0.2)
        self.reps_slider.bind(value=self.update_reps_label)
        reps_layout.add_widget(self.reps_slider)
        reps_layout.add_widget(self.reps_label)
        layout.add_widget(reps_layout)
        
        # Кнопка выполнения
        self.workout_btn = RoundedButton(text="💪 ВЫПОЛНИТЬ 💪", font_size='18sp', size_hint_y=0.1)
        self.workout_btn.bind(on_press=self.do_workout)
        layout.add_widget(self.workout_btn)
        
        # Кнопка назад
        back_btn = RoundedButton(text="◀ НАЗАД", font_size='16sp', size_hint_y=0.08)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'gym'))
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def update_sets_label(self, instance, value):
        self.sets_label.text = str(int(value))
    
    def update_reps_label(self, instance, value):
        self.reps_label.text = str(int(value))
    
    def setup_workout(self, gym_key):
        self.gym_key = gym_key
        muscle = self.game_data.get_muscle_level()
        gym = self.game_data.gyms[gym_key]
        self.weight_input.text = str(gym['current_weight'])
        self.reps_slider.max = muscle['max_reps']
        self.update_info()
    
    def update_info(self):
        muscle = self.game_data.get_muscle_level()
        self.info_label.text = (
            f"Текущий вес: {self.weight_input.text} кг\n"
            f"Лимит: {muscle['weight_limit']} кг\n"
            f"Макс повторений: {muscle['max_reps']}"
        )
    
    def do_workout(self, instance):
        try:
            muscle = self.game_data.get_muscle_level()
            gym = self.game_data.gyms[self.gym_key]
            
            weight = int(self.weight_input.text)
            if weight > muscle['weight_limit']:
                self.show_popup("Ошибка", f"Слишком тяжело! Максимум {muscle['weight_limit']} кг")
                return
            
            sets = int(self.sets_slider.value)
            reps = int(self.reps_slider.value)
            
            if reps > muscle['max_reps']:
                self.show_popup("Ошибка", f"Максимум {muscle['max_reps']} повторений!")
                return
            
            # Сохраняем новый вес
            gym['current_weight'] = weight
            
            # Расчёт
            base_earning = (weight * reps) // 10
            if base_earning < 1:
                base_earning = 1
            
            workout_weight = weight * sets * reps
            
            bonus = 1 + self.game_data.permanent_bonus / 100
            bonus_text = ""
            if self.game_data.active_protein and self.game_data.protein_remaining > 0:
                for item in shop_items.values():
                    if item['name'] == self.game_data.active_protein and 'bonus' in item:
                        bonus += item['bonus'] / 100
                        bonus_text = f" + протеин {item['bonus']}%"
                        break
                self.game_data.protein_remaining -= 1
                if self.game_data.protein_remaining == 0:
                    self.game_data.active_protein = None
            
            total_earning = int(base_earning * bonus)
            
            # Обновление статистики
            old_level = self.game_data.get_muscle_level()['name']
            self.game_data.stats['total_weight_lifted'] += workout_weight
            self.game_data.stats['total_workouts'] += 1
            self.game_data.stats['total_currency_earned'] += total_earning
            if workout_weight > self.game_data.stats['max_weight_per_workout']:
                self.game_data.stats['max_weight_per_workout'] = workout_weight
            self.game_data.currency += total_earning
            
            new_level = self.game_data.get_muscle_level()['name']
            
            # Сохраняем
            self.game_data.save()
            
            result = f"🏋️ Тренировка завершена!\n"
            result += f"{gym['name']}: {sets}×{reps} = {workout_weight} кг\n"
            result += f"💰 Заработано: {total_earning}\n"
            result += f"💪 Всего поднято: {self.game_data.stats['total_weight_lifted']} кг"
            
            if old_level != new_level:
                result += f"\n\n🔥 НОВЫЙ УРОВЕНЬ: {new_level}! 🔥"
                result += f"\n📈 Лимит веса: {muscle['weight_limit']} кг"
            
            self.show_popup("Результат", result)
            
            # Возврат в спортзал
            self.manager.current = 'gym'
            
        except ValueError:
            self.show_popup("Ошибка", "Введите корректный вес!")
    
    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message, font_size='14sp'))
        btn = Button(text="OK", size_hint_y=0.3)
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.5))
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()

class ShopScreen(Screen):
    def __init__(self, game_data, **kwargs):
        super().__init__(**kwargs)
        self.game_data = game_data
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        self.title_label = Label(text="🛒 МАГАЗИН 🛒", font_size='22sp', size_hint_y=0.08)
        layout.add_widget(self.title_label)
        
        self.currency_label = Label(text="", font_size='18sp', size_hint_y=0.08)
        layout.add_widget(self.currency_label)
        
        scroll = ScrollView()
        items_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        items_layout.bind(minimum_height=items_layout.setter('height'))
        
        for key, item in shop_items.items():
            if key.startswith('protein'):
                btn_text = f"{item['name']}\n💰 {item['price']} | +{item['bonus']}% на {item['duration']} подходов"
            else:
                status = "КУПЛЕНО" if self.game_data.stats['creatine_bought'] else f"💰 {item['price']}"
                btn_text = f"{item['name']}\n{status} | +{item['bonus']}% навсегда"
            
            btn = RoundedButton(text=btn_text, font_size='14sp', size_hint_y=None, height=80)
            btn.bind(on_press=lambda x, k=key: self.buy_item(k))
            items_layout.add_widget(btn)
        
        scroll.add_widget(items_layout)
        layout.add_widget(scroll)
        
        # Кнопка назад
        back_btn = RoundedButton(text="◀ НАЗАД", font_size='16sp', size_hint_y=0.08)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def on_enter(self):
        self.update_ui()
    
    def update_ui(self):
        self.currency_label.text = f"💰 {self.game_data.currency}"

class HomeScreen(Screen):
    def __init__(self, game_data, **kwargs):
        super().__init__(**kwargs)
        self.game_data = game_data
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        title = Label(text="🏠 ДОМ 🏠", font_size='22sp', size_hint_y=0.08)
        layout.add_widget(title)
        
        self.info_label = Label(text="", font_size='16sp', size_hint_y=0.3)
        layout.add_widget(self.info_label)
        
        tips = Label(
            text="💡 СОВЕТЫ:\n\n"
                 "• Чем больше поднимаешь — тем сильнее мышцы\n"
                 "• Протеин даёт временную силу\n"
                 "• Креатин даёт вечный бонус +10%\n"
                 "• Постепенно увеличивай вес на тренажёрах\n"
                 "• Прогресс сохраняется автоматически",
            font_size='14sp', size_hint_y=0.5
        )
        layout.add_widget(tips)
        
        back_btn = RoundedButton(text="◀ НАЗАД", font_size='16sp', size_hint_y=0.08)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def on_enter(self):
        muscle = self.game_data.get_muscle_level()
        self.info_label.text = (
            f"💪 Уровень: {muscle['name']}\n"
            f"🏋️ Всего поднято: {self.game_data.stats['total_weight_lifted']} кг\n"
            f"💰 В кошельке: {self.game_data.currency}"
        )

class StatsScreen(Screen):
    def __init__(self, game_data, **kwargs):
        super().__init__(**kwargs)
        self.game_data = game_data
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        title = Label(text="📊 СТАТИСТИКА 📊", font_size='22sp', size_hint_y=0.08)
        layout.add_widget(title)
        
        scroll = ScrollView()
        self.stats_label = Label(text="", font_size='14sp', size_hint_y=None, markup=True)
        scroll.add_widget(self.stats_label)
        layout.add_widget(scroll)
        
        back_btn = RoundedButton(text="◀ НАЗАД", font_size='16sp', size_hint_y=0.08)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def on_enter(self):
        muscle = self.game_data.get_muscle_level()
        text = (
            f"🏋️ Тренировок: {self.game_data.stats['total_workouts']}\n\n"
            f"🏋️ Общий вес: {self.game_data.stats['total_weight_lifted']} кг\n\n"
            f"🏆 Рекорд: {self.game_data.stats['max_weight_per_workout']} кг\n\n"
            f"💰 Заработано: {self.game_data.stats['total_currency_earned']}\n\n"
            f"🥤 Протеинов: {self.game_data.stats['proteins_bought']}\n\n"
            f"⚡ Креатин: {'✅ Да' if self.game_data.stats['creatine_bought'] else '❌ Нет'}\n\n"
            f"{'='*30}\n\n"
            f"📈 ТЕКУЩИЙ УРОВЕНЬ: {muscle['name']}\n"
            f"📊 Лимит веса: {muscle['weight_limit']} кг\n"
            f"🔄 Макс повторений: {muscle['max_reps']}"
        )
        
        # Следующий уровень
        for i, level in enumerate(muscle_levels):
            if level['name'] == muscle['name'] and i + 1 < len(muscle_levels):
                need = muscle_levels[i+1]['weight_required'] - self.game_data.stats['total_weight_lifted']
                if need > 0:
                    text += f"\n\n📈 До {muscle_levels[i+1]['name']}: {need} кг"
                break
        
        self.stats_label.text = text

class SettingsScreen(Screen):
    def __init__(self, game_data, main_app, **kwargs):
        super().__init__(**kwargs)
        self.game_data = game_data
        self.main_app = main_app
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        title = Label(text="⚙️ НАСТРОЙКИ ⚙️", font_size='22sp', size_hint_y=0.08)
        layout.add_widget(title)
        
        info_label = Label(
            text=f"📁 Файл сохранения:\n{SAVE_FILE}\n\n"
                 f"💾 Сохранение автоматическое\n"
                 f"📦 Версия приложения: 2.0\n\n"
                 f"⚠️ Удаление сохранения:\n"
                 f"Нажмите кнопку ниже",
            font_size='12sp', size_hint_y=0.4
        )
        layout.add_widget(info_label)
        
        delete_btn = RoundedButton(text="🗑️ УДАЛИТЬ СОХРАНЕНИЕ", font_size='16sp', size_hint_y=0.1)
        delete_btn.bind(on_press=self.delete_save)
        layout.add_widget(delete_btn)
        
        # Кнопка назад
        back_btn = RoundedButton(text="◀ НАЗАД", font_size='16sp', size_hint_y=0.08)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def delete_save(self, instance):
        def confirm_delete(btn):
            if os.path.exists(SAVE_FILE):
                os.remove(SAVE_FILE)
            self.main_app.stop()
            popup.dismiss()
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text="ВНИМАНИЕ!\n\nВЕСЬ ПРОГРЕСС БУДЕТ УДАЛЁН!\n\nПродолжить?", font_size='14sp'))
        btn_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=0.3)
        yes_btn = Button(text="ДА")
        no_btn = Button(text="НЕТ")
        yes_btn.bind(on_press=confirm_delete)
        no_btn.bind(on_press=lambda x: popup.dismiss())
        btn_layout.add_widget(yes_btn)
        btn_layout.add_widget(no_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(title="Подтверждение", content=content, size_hint=(0.8, 0.4))
        popup.open()

# ===================== ГЛАВНОЕ ПРИЛОЖЕНИЕ =====================
class GymApp(App):
    def build(self):
        self.game_data = GameData()
        self.game_data.load()
        
        sm = ScreenManager()
        sm.add_widget(MainMenuScreen(name='main', game_data=self.game_data))
        sm.add_widget(GymScreen(name='gym', game_data=self.game_data))
        sm.add_widget(WorkoutScreen(name='workout', game_data=self.game_data))
        sm.add_widget(ShopScreen(name='shop', game_data=self.game_data))
        sm.add_widget(HomeScreen(name='home', game_data=self.game_data))
        sm.add_widget(StatsScreen(name='stats', game_data=self.game_data))
        sm.add_widget(SettingsScreen(name='settings', game_data=self.game_data, main_app=self))
        
        return sm
    
    def on_stop(self):
        self.game_data.save()

if __name__ == '__main__':
    GymApp().run()

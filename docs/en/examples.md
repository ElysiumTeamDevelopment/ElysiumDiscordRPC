# Examples

Ready-to-use examples of ElysiumDiscordRPC in various scenarios.

## 📋 Contents

- 🎮 **[Basic Integration](#basic-integration)** - simple game usage
- 🎭 **[Character Tracking](#character-tracking)** - dialogue statuses
- 📖 **[Chapter System](#chapter-system)** - chapter progress
- 🎛️ **[Custom UI](#custom-ui)** - custom settings interface
- 🔄 **[Automation](#automation)** - automatic tracking
- 🎯 **[Advanced Scenarios](#advanced-scenarios)** - complex cases

## 🎮 Basic Integration

### Simplest Usage

```python
# script.rpy
label start:
    # Set initial status
    $ discord_set_custom("Adventure begins", config.name)

    "Welcome to our game world!"

    # Main menu status on return
    $ discord_set_main_menu()

    return

# Интеграция в главное меню
# screens.rpy
screen main_menu():
    # ... ваш существующий код ...
    
    # Обновить статус при показе главного меню
    on "show" action Function(discord_set_main_menu)
```

### Базовые переходы между состояниями

```python
label game_start:
    $ discord_set_loading()
    
    "Загрузка мира..."
    
    $ discord_set_in_game("Пролог")
    
    scene bg forest
    
    "Вы просыпаетесь в лесу..."
    
    menu:
        "Что делать?"
        
        "Исследовать":
            $ discord_set_custom("Исследует лес", "Поиск выхода")
            jump exploration
            
        "Отдохнуть":
            $ discord_set_paused()
            "Вы решили отдохнуть..."
            $ discord_set_in_game("Пролог")  # Возврат к игре
            
        "Настройки":
            $ discord_set_menu("Настройки")
            call screen preferences
            $ discord_set_in_game("Пролог")  # Возврат к игре
```

## 🎭 Отслеживание персонажей

### Автоматическое обновление при диалогах

```python
# Определение персонажей с Discord интеграцией
define alice = Character("Алиса", callback=discord_character_callback)
define bob = Character("Боб", callback=discord_character_callback)

init python:
    def discord_character_callback(event, interact=True, **kwargs):
        if event == "begin":
            # Обновить статус при начале диалога
            character_name = kwargs.get('who', 'Неизвестный')
            discord_set_dialogue(character_name)

# Использование в скрипте
label chapter1:
    $ discord_set_in_game("Глава 1")
    
    scene bg park
    
    alice "Привет! Как дела?"  # Автоматически: "Диалог с Алиса"
    
    "Вы встретили Алису в парке."
    
    bob "О, привет вам обоим!"  # Автоматически: "Диалог с Боб"
```

### Ручное управление статусами персонажей

```python
label character_interaction:
    $ current_character = "Алиса"
    $ current_scene = "Парк"
    
    $ discord_set_dialogue(current_character, current_scene)
    
    alice "Хочешь прогуляться?"
    
    menu:
        alice "Что скажешь?"
        
        "Конечно!":
            $ discord_set_custom("Прогулка с Алисой", "Романтическая сцена")
            alice "Отлично!"
            jump romantic_walk
            
        "Может быть позже":
            $ discord_set_custom("Вежливый отказ", "Диалог с Алисой")
            alice "Хорошо, понимаю."
```

## 📖 Система глав

### Автоматическое отслеживание прогресса

```python
# Переменные для отслеживания прогресса
default current_chapter = 1
default chapter_start_time = 0

init python:
    import time
    
    def start_chapter(chapter_num, chapter_name):
        global current_chapter, chapter_start_time
        current_chapter = chapter_num
        chapter_start_time = int(time.time())
        
        # Обновить Discord статус с временной меткой
        drpc.set_with_timestamp(
            f"Глава {chapter_num}: {chapter_name}",
            config.name,
            chapter_start_time
        )

# Использование в игре
label chapter1_start:
    $ start_chapter(1, "Пробуждение")
    
    "Глава 1: Пробуждение"
    
    # ... содержимое главы ...

label chapter2_start:
    $ start_chapter(2, "Первые шаги")
    
    "Глава 2: Первые шаги"
    
    # ... содержимое главы ...
```

### Система достижений с Discord

```python
init python:
    # Отслеживание достижений
    achievements = {
        "first_choice": False,
        "met_alice": False,
        "chapter1_complete": False
    }
    
    def unlock_achievement(achievement_id, description):
        if not achievements.get(achievement_id, False):
            achievements[achievement_id] = True
            
            # Показать в Discord
            discord_set_custom("Достижение разблокировано!", description)
            
            # Уведомление игроку
            renpy.notify(f"Достижение: {description}")
            
            # Вернуть обычный статус через 3 секунды
            renpy.call_in_new_context("restore_normal_status")

label restore_normal_status:
    $ renpy.pause(3.0)
    $ discord_set_in_game(f"Глава {current_chapter}")
    return

# Использование
label first_important_choice:
    menu:
        "Важный выбор:"
        
        "Вариант А":
            $ unlock_achievement("first_choice", "Первый выбор")
            jump path_a
            
        "Вариант Б":
            $ unlock_achievement("first_choice", "Первый выбор")
            jump path_b
```

## 🎛️ Кастомный UI

### Минималистичный интерфейс

```python
# Простой переключатель в настройках
screen preferences():
    # ... ваш существующий код ...
    
    vbox:
        label "Discord Rich Presence"
        
        textbutton "Discord RPC: [discord_status_text()]":
            action Function(toggle_discord_with_notification)

init python:
    def discord_status_text():
        if not discord_rpc.enabled:
            return "Отключен"
        elif discord_rpc.connected:
            return "Подключен"
        else:
            return "Подключается..."
    
    def toggle_discord_with_notification():
        if discord_rpc.enabled:
            discord_rpc.disable()
            renpy.notify("Discord RPC отключен")
        else:
            discord_rpc.enable()
            renpy.notify("Discord RPC включен")
```

### Продвинутый интерфейс настроек

```python
screen advanced_discord_settings():
    modal True
    
    frame:
        xalign 0.5
        yalign 0.5
        xsize 600
        ysize 500
        
        vbox:
            spacing 20
            
            label "Настройки Discord RPC" xalign 0.5
            
            # Основной переключатель
            hbox:
                text "Discord RPC:"
                textbutton "Включен" action Function(discord_rpc.enable) selected discord_rpc.enabled
                textbutton "Отключен" action Function(discord_rpc.disable) selected not discord_rpc.enabled
            
            if discord_rpc.enabled:
                # Статус подключения
                $ status_info = discord_rpc.get_status_info()
                text "Статус: {color=[status_info['color']]}[status_info['status']]{/color}"
                
                # Управление подключением
                hbox:
                    textbutton "Подключить" action Function(discord_rpc.connect) sensitive not discord_rpc.connected
                    textbutton "Переподключить" action Function(reconnect_discord)
                
                # Настройка Client ID
                vbox:
                    text "Discord Application ID:"
                    input:
                        value VariableInputValue("persistent.discord_rpc_client_id")
                        length 20
                        allow "0123456789"
                    
                    textbutton "Применить ID" action Function(apply_new_client_id)
                
                # Дополнительные настройки
                textbutton "Синхронизация при запуске: [sync_status_text()]":
                    action ToggleVariable("persistent.discord_rpc_sync_startup")
            
            # Кнопки управления
            hbox:
                textbutton "Закрыть" action Return()
                textbutton "Тест" action Function(test_discord_status)

init python:
    def reconnect_discord():
        discord_rpc.disconnect()
        discord_rpc.connect()
        renpy.notify("Переподключение...")
    
    def apply_new_client_id():
        if persistent.discord_rpc_client_id != discord_rpc.client_id:
            discord_rpc.client_id = persistent.discord_rpc_client_id
            reconnect_discord()
    
    def sync_status_text():
        return "Включена" if persistent.discord_rpc_sync_startup else "Отключена"
    
    def test_discord_status():
        discord_set_custom("Тестирование", "Проверка настроек")
        renpy.notify("Тестовый статус отправлен")
```

## 🔄 Автоматизация

### Автоматическое отслеживание лейблов

```python
# Настройка в discord_rpc_config.rpy
define discord_config.label_patterns = {
    "ch": "Глава {ch}",
    "scene": "Сцена: {scene}",
    "ending": "Концовка: {ending}",
    "minigame": "Мини-игра: {minigame}"
}

# Автоматический коллбэк для лейблов
init python:
    original_call_in_new_context = renpy.call_in_new_context
    
    def tracked_call_in_new_context(label, *args, **kwargs):
        # Обновить Discord статус на основе лейбла
        formatted_name = format_label_name(label)
        discord_set_custom(formatted_name, config.name)
        
        return original_call_in_new_context(label, *args, **kwargs)
    
    # Заменить функцию (осторожно!)
    # renpy.call_in_new_context = tracked_call_in_new_context

# Лейблы в игре автоматически обновят статус
label ch1_forest:          # → "Глава 1 Forest"
    "В лесу..."

label scene_village:       # → "Сцена: Village"
    "В деревне..."

label ending_good:         # → "Концовка: Good"
    "Хорошая концовка!"
```

### Система событий

```python
init python:
    class DiscordEventTracker:
        def __init__(self):
            self.events = []
            self.current_activity = "Главное меню"
        
        def track_event(self, event_type, description):
            self.events.append({
                'type': event_type,
                'description': description,
                'time': time.time()
            })
            
            # Обновить Discord статус
            if event_type == "story":
                discord_set_custom("Читает историю", description)
            elif event_type == "choice":
                discord_set_custom("Делает выбор", description)
            elif event_type == "minigame":
                discord_set_custom("Мини-игра", description)
        
        def set_activity(self, activity):
            self.current_activity = activity
            discord_set_custom(activity, config.name)
    
    # Глобальный трекер
    discord_tracker = DiscordEventTracker()

# Использование в игре
label story_event:
    $ discord_tracker.track_event("story", "Встреча с принцессой")
    
    "Вы встречаете принцессу..."

label choice_event:
    $ discord_tracker.track_event("choice", "Выбор пути")
    
    menu:
        "Куда идти?"
        
        "В лес":
            jump forest_path
            
        "В город":
            jump city_path
```

## 🎯 Продвинутые сценарии

### Мультиплеерная поддержка (концептуально)

```python
# Для игр с элементами мультиплеера или совместного прохождения
init python:
    def set_party_status(current_players, max_players, activity="Играет"):
        discord_rpc.update_presence(
            state=activity,
            details=config.name,
            party_size=[current_players, max_players],
            large_image="game_icon"
        )

# Использование
label multiplayer_session:
    $ set_party_status(2, 4, "Совместное прохождение")
    
    "Вы играете с друзьями..."
```

### Интеграция с системой сохранений

```python
init python:
    def update_discord_on_save():
        save_name = renpy.current_save_name() or "Быстрое сохранение"
        discord_set_custom("Сохранение игры", f"Слот: {save_name}")
        
        # Вернуть обычный статус через 2 секунды
        renpy.call_in_new_context("restore_game_status")
    
    def update_discord_on_load():
        discord_set_loading()
        # Статус обновится автоматически после загрузки

# Интеграция в экраны сохранения/загрузки
screen save():
    # ... ваш код экрана сохранения ...
    
    # При сохранении
    on "save" action Function(update_discord_on_save)

screen load():
    # ... ваш код экрана загрузки ...
    
    # При загрузке
    on "load" action Function(update_discord_on_load)
```

### Система настроения/эмоций

```python
init python:
    # Отслеживание эмоционального состояния игры
    current_mood = "neutral"
    mood_descriptions = {
        "happy": "Радостная сцена",
        "sad": "Грустная сцена", 
        "tense": "Напряжённая сцена",
        "romantic": "Романтическая сцена",
        "action": "Экшн сцена"
    }
    
    def set_scene_mood(mood, custom_description=None):
        global current_mood
        current_mood = mood
        
        description = custom_description or mood_descriptions.get(mood, "Игровая сцена")
        
        # Выбрать подходящее изображение
        mood_images = {
            "happy": "happy_scene",
            "sad": "sad_scene",
            "tense": "tense_scene",
            "romantic": "romantic_scene",
            "action": "action_scene"
        }
        
        large_image = mood_images.get(mood, "game_icon")
        
        discord_rpc.update_presence(
            state=description,
            details=config.name,
            large_image=large_image,
            small_image="playing"
        )

# Использование в сценах
label romantic_scene:
    $ set_scene_mood("romantic", "Свидание под звёздами")
    
    scene bg starry_night
    
    "Романтическая сцена под звёздным небом..."

label action_sequence:
    $ set_scene_mood("action", "Погоня на крышах")
    
    "Начинается захватывающая погоня!"
```

### Интеграция с музыкальной системой

```python
init python:
    current_track = None
    
    def play_music_with_discord(track_name, discord_description=None):
        global current_track
        current_track = track_name
        
        # Воспроизвести музыку
        renpy.music.play(track_name)
        
        # Обновить Discord статус
        if discord_description:
            discord_set_custom("Слушает музыку", discord_description)
        else:
            # Автоматическое описание на основе имени файла
            clean_name = track_name.replace("_", " ").replace(".ogg", "").title()
            discord_set_custom("Слушает музыку", clean_name)

# Использование
label music_scene:
    $ play_music_with_discord("romantic_theme.ogg", "Романтическая тема")
    
    "Играет красивая мелодия..."
    
    $ play_music_with_discord("battle_theme.ogg", "Боевая музыка")
    
    "Начинается битва!"
```

## 💡 Советы по примерам

### Адаптация под вашу игру
1. **Измените названия** лейблов, персонажей и сцен под вашу игру
2. **Настройте изображения** в Discord Developer Portal
3. **Адаптируйте тексты** статусов под тематику игры
4. **Тестируйте функции** перед внедрением в основную игру

### Производительность
1. **Не обновляйте статус слишком часто** - Discord имеет лимиты
2. **Используйте коллбэки** вместо постоянных проверок
3. **Кэшируйте данные** для избежания повторных вычислений

### Отладка
1. **Добавляйте логирование** для отслеживания обновлений статуса
2. **Используйте try/except** для обработки ошибок
3. **Тестируйте на разных устройствах** и версиях Discord

## 🔗 Связанные разделы

- **[API Reference](api-reference.md)** - полный список функций
- **[Configuration](configuration.md)** - настройка шаблонов и изображений
- **[UI Integration](ui-integration.md)** - создание интерфейсов

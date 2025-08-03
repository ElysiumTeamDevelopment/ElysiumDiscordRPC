# API Reference

Полный справочник всех функций и методов ElysiumDiscordRPC модуля.

## 📋 Обзор API

ElysiumDiscordRPC предоставляет несколько уровней API:

- 🎮 **Простые функции** - `discord_set_*()` для быстрого использования
- 🔧 **Класс DiscordRPCAPI** - `drpc.*()` для продвинутого использования  
- ⚙️ **Основной класс** - `discord_rpc.*()` для полного контроля
- 📊 **Вспомогательные функции** - утилиты конфигурации

## 🎮 Простые функции

### discord_set_main_menu()
Устанавливает статус главного меню.

```python
$ discord_set_main_menu()
```

**Использует шаблон:** `discord_config.main_menu_presence`

### discord_set_in_game(chapter=None, character=None)
Устанавливает статус игрового процесса.

```python
$ discord_set_in_game()                           # Базовый статус
$ discord_set_in_game("Глава 1")                  # С указанием главы
$ discord_set_in_game("Глава 1", "Эйлин")         # С главой и персонажем
$ discord_set_in_game(character="Алиса")          # Только персонаж
```

**Параметры:**
- `chapter` (str, optional) - название главы/сцены
- `character` (str, optional) - имя персонажа

### discord_set_dialogue(character=None, scene=None)
Устанавливает статус чтения диалога.

```python
$ discord_set_dialogue()                          # Базовый статус
$ discord_set_dialogue("Эйлин")                   # С персонажем
$ discord_set_dialogue("Эйлин", "Комната")        # С персонажем и сценой
$ discord_set_dialogue(scene="Парк")              # Только сцена
```

**Параметры:**
- `character` (str, optional) - имя говорящего персонажа
- `scene` (str, optional) - название текущей сцены

### discord_set_menu(menu_name="Меню")
Устанавливает статус навигации по меню.

```python
$ discord_set_menu()                              # "В меню: Меню"
$ discord_set_menu("Настройки")                   # "В меню: Настройки"
$ discord_set_menu("Сохранение")                  # "В меню: Сохранение"
```

### discord_set_paused()
Устанавливает статус паузы.

```python
$ discord_set_paused()
```

**Использует шаблон:** `discord_config.paused_presence`

### discord_set_loading()
Устанавливает статус загрузки.

```python
$ discord_set_loading()
```

### discord_set_custom(state, details=None, **kwargs)
Устанавливает произвольный статус.

```python
$ discord_set_custom("Мой статус")                           # Только state
$ discord_set_custom("Играет", "Глава 1")                    # State + details
$ discord_set_custom("Битва", "Финальный босс", 
                     large_image="battle_bg")                # С дополнительными параметрами
```

**Параметры:**
- `state` (str) - основной текст статуса
- `details` (str, optional) - дополнительный текст
- `**kwargs` - любые дополнительные параметры Discord RPC

### discord_clear()
Очищает Discord Rich Presence.

```python
$ discord_clear()
```

## 🔧 Класс DiscordRPCAPI (drpc)

### drpc.set_main_menu()
Аналогично `discord_set_main_menu()`.

### drpc.set_in_game(chapter_name=None, character_name=None)
Расширенная версия `discord_set_in_game()`.

```python
$ drpc.set_in_game("Пролог", "Главный герой")
```

### drpc.set_reading_dialogue(character_name=None, scene_name=None)
Расширенная версия `discord_set_dialogue()`.

### drpc.set_in_menu(menu_name="Меню")
Аналогично `discord_set_menu()`.

### drpc.set_paused()
Аналогично `discord_set_paused()`.

### drpc.set_loading()
Аналогично `discord_set_loading()`.

### drpc.set_custom(state_text, details_text=None, **kwargs)
Расширенная версия `discord_set_custom()`.

```python
$ drpc.set_custom("Кастомный статус", "Детали", 
                  large_image="custom_bg",
                  small_image="custom_icon",
                  buttons=[{"label": "Кнопка", "url": "https://example.com"}])
```

### drpc.set_with_timestamp(state_text, details_text=None, start_time=None)
Устанавливает статус с временной меткой.

```python
import time

$ drpc.set_with_timestamp("Играет", "Глава 1")                    # Текущее время
$ drpc.set_with_timestamp("Играет", "Глава 1", int(time.time()))  # Конкретное время
```

**Параметры:**
- `state_text` (str) - основной текст
- `details_text` (str, optional) - дополнительный текст  
- `start_time` (int, optional) - Unix timestamp начала

### drpc.clear()
Очищает статус.

## ⚙️ Основной класс DiscordRPC

### discord_rpc.enable()
Включает Discord RPC.

```python
$ discord_rpc.enable()
```

**Возвращает:** `True` если успешно, `False` если ошибка

### discord_rpc.disable()
Отключает Discord RPC.

```python
$ discord_rpc.disable()
```

### discord_rpc.connect(sync_startup=None)
Подключается к Discord.

```python
$ discord_rpc.connect()                    # Использует настройки из конфига
$ discord_rpc.connect(sync_startup=True)   # Принудительно синхронное подключение
$ discord_rpc.connect(sync_startup=False)  # Принудительно асинхронное подключение
```

**Параметры:**
- `sync_startup` (bool, optional) - тип подключения

### discord_rpc.disconnect()
Отключается от Discord.

```python
$ discord_rpc.disconnect()
```

### discord_rpc.get_status()
Получает текущий статус подключения.

```python
$ status = discord_rpc.get_status()
$ print(status)  # "Подключен", "Подключение", "Отключен", etc.
```

**Возможные значения:**
- `"Отключен"` - Discord RPC отключен
- `"Подключение"` - Идёт подключение
- `"Подключен"` - Успешно подключен
- `"Переподключение"` - Идёт переподключение
- `"Ошибка"` - Произошла ошибка
- `"Таймаут"` - Превышен таймаут

### discord_rpc.get_status_info()
Получает детальную информацию о статусе.

```python
$ info = discord_rpc.get_status_info()
$ print(info)
# {
#     'status': 'Подключен',
#     'enabled': True,
#     'connected': True,
#     'retry_count': 0,
#     'last_error': None,
#     'color': '#00ff00'
# }
```

### discord_rpc.update_presence(**kwargs)
Обновляет Discord Rich Presence.

```python
$ discord_rpc.update_presence(
    state="Играет",
    details="Моя игра",
    large_image="game_icon",
    small_image="playing"
)
```

**Параметры Discord RPC:**
- `state` (str) - нижняя строка текста
- `details` (str) - верхняя строка текста
- `large_image` (str) - большое изображение
- `large_text` (str) - подсказка большого изображения
- `small_image` (str) - маленькое изображение  
- `small_text` (str) - подсказка маленького изображения
- `start` (int) - Unix timestamp начала
- `end` (int) - Unix timestamp окончания
- `party_size` (list) - размер группы [текущий, максимум]
- `buttons` (list) - кнопки (максимум 2)

### discord_rpc.clear_presence()
Очищает Rich Presence.

```python
$ discord_rpc.clear_presence()
```

### discord_rpc.add_status_callback(callback)
Добавляет коллбэк для изменений статуса.

```python
def my_callback(old_status, new_status):
    print(f"Статус изменился: {old_status} → {new_status}")

$ discord_rpc.add_status_callback(my_callback)
```

### discord_rpc.remove_status_callback(callback)
Удаляет коллбэк статуса.

```python
$ discord_rpc.remove_status_callback(my_callback)
```

## 📊 Вспомогательные функции

### get_discord_config(key, default=None)
Получает значение из конфигурации.

```python
$ timeout = get_discord_config('connection.startup_timeout', 5.0)
$ app_id = get_discord_config('application_id')
$ images = get_discord_config('large_images', {})
```

### get_game_name()
Получает название игры.

```python
$ name = get_game_name()  # Из discord_config.game_name или config.name
```

### get_presence_template(template_name)
Получает шаблон статуса.

```python
$ template = get_presence_template('main_menu_presence')
$ discord_rpc.update_presence(**template)
```

### resolve_image_asset(image_key, image_type="large")
Преобразует ключ изображения в имя ресурса.

```python
$ large_img = resolve_image_asset('game_icon', 'large')    # → "main_logo"
$ small_img = resolve_image_asset('playing', 'small')     # → "play_button"
```

### format_label_name(label_name)
Форматирует имя лейбла по паттернам.

```python
$ formatted = format_label_name('chapter_1')      # → "Глава 1"
$ formatted = format_label_name('scene_park')     # → "Сцена Park"
$ formatted = format_label_name('custom_label')   # → "Custom Label"
```

### get_character_display_name(character_obj)
Получает отображаемое имя персонажа.

```python
$ name = get_character_display_name(e)           # → "Эйлин"
$ name = get_character_display_name("alice")     # → "Алиса"
```

## 🛡️ Функции надёжности (если включён reliability модуль)

### discord_safe_update(**kwargs)
Безопасное обновление статуса с обработкой ошибок.

```python
$ discord_safe_update(state="Безопасный статус", details="Тест")
```

### discord_safe_connect()
Безопасное подключение с обработкой ошибок.

```python
$ discord_safe_connect()
```

### get_discord_error_info()
Получает информацию об ошибках.

```python
$ error_info = get_discord_error_info()
# {
#     'last_error': 'Connection failed',
#     'retry_count': 2,
#     'max_retries': 3
# }
```

## 🎯 Примеры использования

### Базовое использование
```python
label start:
    $ discord_set_custom("Начало игры", config.name)
    
    "Добро пожаловать!"
    
    $ discord_set_dialogue("Рассказчик", "Пролог")
    
    menu:
        "Что делать?"
        
        "Играть":
            $ discord_set_in_game("Глава 1")
            jump chapter1
            
        "Настройки":
            $ discord_set_menu("Настройки")
            call screen preferences
```

### Продвинутое использование
```python
label chapter1:
    $ drpc.set_with_timestamp("Глава 1", "Начало приключения")
    
    scene forest
    
    $ drpc.set_custom("В лесу", "Исследование", 
                      large_image="forest_bg",
                      small_image="exploring")
    
    "Вы входите в тёмный лес..."
```

### Управление подключением
```python
screen discord_settings():
    vbox:
        textbutton "Включить Discord RPC":
            action Function(discord_rpc.enable)
            sensitive not discord_rpc.enabled
            
        textbutton "Отключить Discord RPC":
            action Function(discord_rpc.disable)
            sensitive discord_rpc.enabled
            
        textbutton "Переподключить":
            action [Function(discord_rpc.disconnect), 
                   Function(discord_rpc.connect)]
            
        text "Статус: [discord_rpc.get_status()]"
```

## 📝 Заметки по использованию

### Порядок вызовов
1. Сначала убедитесь, что Discord RPC включён: `discord_rpc.enabled`
2. Проверьте подключение: `discord_rpc.connected`
3. Затем обновляйте статус любыми функциями

### Обработка ошибок
```python
# Безопасное обновление
if discord_rpc.enabled and discord_rpc.connected:
    discord_set_custom("Мой статус")
else:
    print("Discord RPC недоступен")
```

### Производительность
- Функции `discord_set_*()` быстрые и безопасные
- Избегайте частых обновлений (чаще раза в секунду)
- Используйте `discord_clear()` при выходе из игры

## 🔗 Связанные разделы

- **[Configuration](configuration.md)** - настройка шаблонов и параметров
- **[UI Integration](ui-integration.md)** - интеграция API в интерфейс
- **[Examples](examples.md)** - готовые примеры использования

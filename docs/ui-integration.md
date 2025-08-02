# UI Integration

Руководство по интеграции ElysiumDiscordRPC в пользовательский интерфейс RenPy игр.

## 📋 Обзор

ElysiumDiscordRPC предоставляет гибкие возможности интеграции:

- 🎛️ **Готовый UI** - встроенный экран настроек (`discord_rpc_settings.rpy`)
- 🔧 **Кастомная интеграция** - функции для создания собственного интерфейса
- 📊 **Мониторинг статуса** - отображение состояния подключения
- ⚡ **Быстрые действия** - кнопки включения/отключения

## 🎛️ Использование встроенного UI

### Подключение готового экрана

Если вы используете `discord_rpc_settings.rpy`, добавьте в главное меню:

```python
# В screens.rpy
screen main_menu():
    # ... ваш существующий код ...
    
    textbutton _("Discord RPC") action ShowMenu("discord_rpc_settings")
```

### Возможности встроенного UI

- ✅ Включение/отключение Discord RPC
- ✅ Настройка Client ID
- ✅ Отображение статуса подключения с цветовой индикацией
- ✅ Кнопки переподключения
- ✅ Настройка синхронизации при запуске
- ✅ Отображение последних ошибок

## 🔧 Создание кастомного интерфейса

### Базовые элементы управления

#### Переключатель включения/отключения
```python
screen my_discord_settings():
    vbox:
        # Переключатель
        textbutton "Discord RPC: [discord_rpc_status_text()]":
            action Function(toggle_discord_rpc)
            
        # Или отдельные кнопки
        if discord_rpc.enabled:
            textbutton "Отключить Discord RPC":
                action Function(discord_rpc.disable)
        else:
            textbutton "Включить Discord RPC":
                action Function(discord_rpc.enable)

# Вспомогательная функция
init python:
    def discord_rpc_status_text():
        return "Включен" if discord_rpc.enabled else "Отключен"
        
    def toggle_discord_rpc():
        if discord_rpc.enabled:
            discord_rpc.disable()
        else:
            discord_rpc.enable()
```

#### Отображение статуса подключения
```python
screen discord_status_display():
    frame:
        has vbox
        
        # Статус с цветовой индикацией
        $ status_info = discord_rpc.get_status_info()
        text "Discord RPC: {color=[status_info['color']]}[status_info['status']]{/color}"
        
        # Дополнительная информация
        if status_info['last_error']:
            text "Ошибка: [status_info['last_error']]" size 12 color "#ff0000"
            
        if status_info['retry_count'] > 0:
            text "Попыток переподключения: [status_info['retry_count']]" size 12
```

#### Кнопки управления подключением
```python
screen discord_connection_controls():
    hbox:
        spacing 10
        
        textbutton "Подключить":
            action Function(discord_rpc.connect)
            sensitive not discord_rpc.connected and discord_rpc.enabled
            
        textbutton "Отключить":
            action Function(discord_rpc.disconnect)
            sensitive discord_rpc.connected
            
        textbutton "Переподключить":
            action Function(reconnect_discord_rpc)

init python:
    def reconnect_discord_rpc():
        discord_rpc.disconnect()
        discord_rpc.connect()
```

### Продвинутые элементы

#### Настройка Client ID
```python
screen discord_client_id_input():
    frame:
        has vbox
        
        text "Discord Application ID:"
        
        input:
            value VariableInputValue("persistent.discord_rpc_client_id")
            length 20
            allow "0123456789"
            xsize 300
            
        textbutton "Применить":
            action Function(apply_client_id_change)

init python:
    def apply_client_id_change():
        if discord_rpc.client_id != persistent.discord_rpc_client_id:
            discord_rpc.client_id = persistent.discord_rpc_client_id
            if discord_rpc.connected:
                reconnect_discord_rpc()
```

#### Настройки синхронизации
```python
screen discord_sync_settings():
    frame:
        has vbox
        
        text "Синхронизация при запуске:"
        
        textbutton "Включена" action [
            SetVariable("persistent.discord_rpc_sync_startup", True),
            SetField(discord_rpc, "startup_sync_enabled", True)
        ] selected persistent.discord_rpc_sync_startup
        
        textbutton "Отключена" action [
            SetVariable("persistent.discord_rpc_sync_startup", False),
            SetField(discord_rpc, "startup_sync_enabled", False)
        ] selected not persistent.discord_rpc_sync_startup
        
        text "Включение замедляет запуск, но гарантирует подключение" size 12
```

#### Мониторинг в реальном времени
```python
screen discord_live_monitor():
    frame:
        has vbox
        
        # Обновляется каждую секунду
        timer 1.0 repeat True action Function(renpy.restart_interaction)
        
        text "Статус: [discord_rpc.get_status()]"
        text "Подключен: [discord_rpc.connected]"
        text "Включен: [discord_rpc.enabled]"
        
        if discord_rpc.last_update:
            text "Последний статус:"
            for key, value in discord_rpc.last_update.items():
                text "  [key]: [value]" size 12
```

## 📊 Интеграция в игровой интерфейс

### Индикатор в главном меню
```python
screen main_menu():
    # ... ваш существующий код ...
    
    # Небольшой индикатор в углу
    frame:
        xalign 1.0
        yalign 0.0
        xsize 200
        
        $ status_info = discord_rpc.get_status_info()
        text "Discord: {color=[status_info['color']]}[status_info['status']]{/color}" size 14
```

### Быстрые действия в настройках
```python
screen preferences():
    # ... ваш существующий код настроек ...
    
    # Секция Discord RPC
    vbox:
        label "Discord Rich Presence"
        
        textbutton "Discord RPC: [discord_rpc_status_text()]":
            action Function(toggle_discord_rpc)
            
        if discord_rpc.enabled:
            textbutton "Настроить":
                action ShowMenu("my_discord_settings")
```

### Уведомления о статусе
```python
# Показать уведомление при изменении статуса
init python:
    def discord_status_notification(old_status, new_status):
        if new_status == "Подключен":
            renpy.notify("Discord RPC подключен")
        elif new_status == "Ошибка":
            renpy.notify("Ошибка Discord RPC")
    
    # Добавить коллбэк
    discord_rpc.add_status_callback(discord_status_notification)
```

## 🎮 Интеграция в игровой процесс

### Автоматическое обновление статуса
```python
# В script.rpy
label start:
    $ discord_set_custom("Начало игры", config.name)
    
    "Добро пожаловать в игру!"
    
    call update_discord_for_scene("prologue")
    
    # ... остальной код ...

label update_discord_for_scene(scene_name):
    # Автоматическое обновление на основе сцены
    if scene_name == "prologue":
        $ discord_set_custom("Пролог", "Знакомство с миром")
    elif scene_name == "chapter1":
        $ discord_set_in_game("Глава 1", "Главный герой")
    # ... другие сцены ...
    
    return
```

### Контекстные статусы
```python
# Обновление статуса в зависимости от действий игрока
label choice_menu:
    menu:
        "Что делать?"
        
        "Исследовать лес":
            $ discord_set_custom("Исследует лес", "Поиск приключений")
            jump forest_exploration
            
        "Идти в город":
            $ discord_set_custom("В городе", "Общение с жителями")
            jump city_visit
            
        "Отдохнуть":
            $ discord_set_paused()
            jump rest_scene
```

## 🔧 Продвинутые техники

### Кастомные Screen Actions
```python
init python:
    class ToggleDiscordRPC(Action):
        def __call__(self):
            toggle_discord_rpc()
            renpy.restart_interaction()
            
        def get_selected(self):
            return discord_rpc.enabled
            
        def get_sensitive(self):
            return True

    class UpdateDiscordStatus(Action):
        def __init__(self, state, details=None):
            self.state = state
            self.details = details
            
        def __call__(self):
            discord_set_custom(self.state, self.details)

# Использование
screen my_menu():
    textbutton "Toggle Discord RPC" action ToggleDiscordRPC()
    textbutton "Set Gaming Status" action UpdateDiscordStatus("Играет", "В меню")
```

### Условное отображение
```python
screen conditional_discord_ui():
    # Показывать только если Discord RPC доступен
    if PYPRESENCE_AVAILABLE:
        vbox:
            text "Discord Rich Presence"
            
            if discord_rpc.enabled:
                textbutton "Настройки Discord" action ShowMenu("discord_settings")
            else:
                textbutton "Включить Discord RPC" action Function(discord_rpc.enable)
    else:
        text "Discord RPC недоступен" color "#888888"
```

### Сохранение настроек
```python
init python:
    def save_discord_settings():
        """Сохранить все настройки Discord RPC"""
        persistent.discord_rpc_enabled = discord_rpc.enabled
        persistent.discord_rpc_client_id = discord_rpc.client_id
        persistent.discord_rpc_sync_startup = discord_rpc.startup_sync_enabled
        
    def load_discord_settings():
        """Загрузить настройки Discord RPC"""
        if hasattr(persistent, 'discord_rpc_enabled'):
            if persistent.discord_rpc_enabled != discord_rpc.enabled:
                if persistent.discord_rpc_enabled:
                    discord_rpc.enable()
                else:
                    discord_rpc.disable()
```

## 📱 Адаптивный интерфейс

### Компактный режим для мобильных устройств
```python
screen discord_settings_mobile():
    if renpy.variant("mobile"):
        # Компактная версия для мобильных
        vbox:
            textbutton "Discord: [discord_rpc_status_text()]" action Function(toggle_discord_rpc)
            if discord_rpc.enabled and not discord_rpc.connected:
                textbutton "Подключить" action Function(discord_rpc.connect)
    else:
        # Полная версия для десктопа
        use discord_settings_full
```

### Настройки по умолчанию
```python
# Определение persistent переменных с умолчаниями
default persistent.discord_rpc_enabled = True
default persistent.discord_rpc_client_id = ""
default persistent.discord_rpc_sync_startup = True
default persistent.discord_rpc_show_in_menu = True

# Применение настроек при запуске
init python:
    def apply_persistent_discord_settings():
        discord_rpc.startup_sync_enabled = persistent.discord_rpc_sync_startup
        if persistent.discord_rpc_client_id:
            discord_rpc.client_id = persistent.discord_rpc_client_id
    
    apply_persistent_discord_settings()
```

## 💡 Советы по интеграции

### Лучшие практики
1. **Делайте UI опциональным** - не все игроки используют Discord
2. **Показывайте статус подключения** - пользователи должны понимать, что происходит
3. **Предоставьте быстрые действия** - включить/отключить одной кнопкой
4. **Обрабатывайте ошибки gracefully** - не ломайте игру при проблемах с Discord

### Производительность
1. **Не обновляйте UI слишком часто** - используйте timer с разумными интервалами
2. **Кэшируйте статус** - не вызывайте `get_status()` на каждый кадр
3. **Используйте коллбэки** - для реакции на изменения статуса

### UX рекомендации
1. **Объясняйте функции** - добавляйте подсказки о том, что делает Discord RPC
2. **Предоставьте ссылки** - на Discord Developer Portal для настройки
3. **Делайте настройки доступными** - не прячьте глубоко в меню

## 🔗 Связанные разделы

- **[API Reference](api-reference.md)** - полный список доступных функций
- **[Configuration](configuration.md)** - настройка шаблонов для UI
- **[Examples](examples.md)** - готовые примеры интеграции

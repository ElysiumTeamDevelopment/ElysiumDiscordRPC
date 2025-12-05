# ElysiumDiscordRPC

**Продвинутый модуль Discord Rich Presence для Ren'Py игр**

[![License](https://img.shields.io/badge/License-Custom-blue.svg)](#лицензия)
[![RenPy](https://img.shields.io/badge/RenPy-8.1%2B-blue.svg)](https://www.renpy.org/)
[![Python](https://img.shields.io/badge/Python-3.9%2B-green.svg)](https://www.python.org/)
[![pypresence](https://img.shields.io/badge/using-pypresence-00bb88.svg?style=flat&logo=discord&logoWidth=20)](https://github.com/qwertyquerty/pypresence)

**[English](../README.md) | Русский**

## 🚀 Возможности

- ✅ **Модульная архитектура** — используйте только нужное (3-6 файлов)
- ✅ **Богатый API** — 15+ функций для любых сценариев
- ✅ **CDS синтаксис** — чистые команды без Python
- ✅ **Централизованная конфигурация** — все настройки в одном файле
- ✅ **Встроенный UI настроек** — опциональный готовый экран
- ✅ **Система надёжности** — авто-переподключение и обработка ошибок
- ✅ **Подробная документация** — полная Wiki с примерами

## 📦 Быстрая установка

### 1. Скачайте
Скачайте [последний релиз](https://github.com/ElysiumTeamDevelopment/ElysiumDiscordRPC/releases).

### 2. Скопируйте файлы в проект
```
your_renpy_project/
└── game/
    ├── discord_rpc_ren.py          # Основной модуль (обязательно)
    ├── discord_rpc_api_ren.py      # API функции (обязательно)
    ├── discord_rpc_config.rpy      # Конфигурация (обязательно)
    ├── discord_rpc_settings.rpy    # UI настроек (опционально)
    ├── discord_rpc_reliability_ren.py  # Надёжность (опционально)
    └── python-packages/
        └── pypresence/             # Библиотека Discord RPC
```

### 3. Установите pypresence
```bash
pip install pypresence --target game/python-packages
```

### 4. Настройте
Отредактируйте `discord_rpc_config.rpy`:
```python
define discord_config.application_id = "ВАШ_DISCORD_APP_ID"
define discord_config.game_name = "Название Вашей Игры"
```

## 🎮 Быстрый старт

```renpy
label start:
    # CDS синтаксис (чистый)
    discord custom "Начало приключения" "Пролог"
    
    "Добро пожаловать в игру!"
    
    discord dialogue "Алиса" "Парк"
    alice "Привет! Рада познакомиться!"
    
    discord in_game "Глава 1" "Алиса"
    
    menu:
        "Что делать?"
        "Продолжить":
            discord custom "Продолжает историю" "Глава 1"
            jump chapter1
```

Или используйте Python функции:
```python
$ discord_set_custom("Начало приключения", "Пролог")
$ discord_set_dialogue("Алиса", "Парк")
$ discord_set_in_game("Глава 1", "Алиса")
```

## 📁 Структура модуля

| Файл | Назначение | Обязательно |
|------|------------|-------------|
| `discord_rpc_ren.py` | Основной модуль | ✅ Да |
| `discord_rpc_api_ren.py` | API функции | ✅ Да |
| `discord_rpc_config.rpy` | Конфигурация | ✅ Да |
| `discord_rpc_settings.rpy` | UI настроек | ❌ Опционально |
| `discord_rpc_reliability_ren.py` | Надёжность | ❌ Опционально |
| `libs/01-discord-rpc_ren.py` | CDS команды | ❌ Опционально |

## 📚 Документация

**Полная документация доступна в [Wiki](https://github.com/ElysiumTeamDevelopment/ElysiumDiscordRPC/wiki)**

- [Quick Start](https://github.com/ElysiumTeamDevelopment/ElysiumDiscordRPC/wiki/Quick-Start)
- [Installation](https://github.com/ElysiumTeamDevelopment/ElysiumDiscordRPC/wiki/Installation)
- [Basic Configuration](https://github.com/ElysiumTeamDevelopment/ElysiumDiscordRPC/wiki/Basic-Configuration)
- [API Functions](https://github.com/ElysiumTeamDevelopment/ElysiumDiscordRPC/wiki/API-Functions)
- [CDS Commands](https://github.com/ElysiumTeamDevelopment/ElysiumDiscordRPC/wiki/CDS-Commands)
- [Common Errors](https://github.com/ElysiumTeamDevelopment/ElysiumDiscordRPC/wiki/Common-Errors)
- [FAQ](https://github.com/ElysiumTeamDevelopment/ElysiumDiscordRPC/wiki/FAQ)

## ⚙️ Требования

- **Ren'Py:** 8.1+
- **Python:** 3.9+
- **Discord:** Установлен и запущен
- **ОС:** Windows, macOS, Linux

## 📄 Лицензия

**Бесплатно для использования, но указание авторства обязательно.**

При использовании этого модуля в вашем проекте, вы должны добавить следующее упоминание в титры, README или раздел "О игре":

> **Используется Elysium Discord RPC от Elysium Development**

## 🆘 Поддержка

- **Wiki:** [Документация](https://github.com/ElysiumTeamDevelopment/ElysiumDiscordRPC/wiki)
- **Issues:** [GitHub Issues](https://github.com/ElysiumTeamDevelopment/ElysiumDiscordRPC/issues)

## 🙏 Благодарности

- [pypresence](https://github.com/qwertyquerty/pypresence) — библиотека Discord RPC
- [Lezalith](https://github.com/Lezalith/RenPy_Discord_Presence) — вдохновение
- Сообщество Ren'Py за поддержку и тестирование

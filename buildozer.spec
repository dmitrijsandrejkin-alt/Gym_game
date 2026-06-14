[app]

# Название приложения
title = Тренажёрный зал

# Внутреннее имя пакета
package.name = gymgame
package.domain = org.example

# Версия
version = 2.0.0

# Какие файлы включать
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# Библиотеки
requirements = python3,kivy==2.1.0

# Ориентация
orientation = portrait

# Разрешения
android.permissions = INTERNET

# Настройки Android
android.api = 30
android.minapi = 21
android.sdk = 30
android.ndk = 23b
android.archs = arm64-v8a, armeabi-v7a

# Тип сборки
android.release_artifact = apk

# Логи
log_level = 2

# Для Kivy
fullscreen = 1
window.size = (360, 640)

# Автор
author = Your Name
description = Симулятор тренажёрного зала

[buildozer]
log_level = 2
android.accept_sdk_license = True

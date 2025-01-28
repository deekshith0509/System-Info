[app]
title = System Info
package.name = info
source.main = main.py
package.domain = kivy.system
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,dm
fullscreen = 0
android.archs = arm64-v8a
android.release_artifact = apk
android.accept_sdk_license = True
android.api = 33
android.ndk = 25c
android.presplash_color = #FFFFFF
orientation = portrait
android.permissions = MANAGE_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET, READ_MEDIA_IMAGES, READ_MEDIA_VIDEO, READ_MEDIA_AUDIO
# Versioning
version = 0.1
requirements = python3,kivy,kivymd

# Debug mode
debug = 1

[buildozer]
log_level = 2
warn_on_root = 1
source.include_dirs = bin
source.include_patterns = bin/*
android.allow_backup = True
android.logcat = True

[app]
# App info
title = System Info
package.name = info
package.domain = kivy.system
source.main = main.py
source.dir = .

# Version
version = 0.1

# Source files
source.include_exts = py,png,jpg,kv,atlas,dm
source.include_dirs = bin
source.include_patterns = bin/*

# Display settings
fullscreen = 0
orientation = portrait
icon.filename = icon.png
android.presplash_color = #FFFFFF

# Android specific
android.archs = arm64-v8a
android.api = 33
android.ndk = 25c
android.release_artifact = apk
android.accept_sdk_license = True
android.skip_update = False

# Permissions - expanded list
android.permissions = MANAGE_EXTERNAL_STORAGE,
    WRITE_EXTERNAL_STORAGE,
    READ_EXTERNAL_STORAGE,
    INTERNET,
    READ_MEDIA_IMAGES,
    READ_MEDIA_VIDEO,
    READ_MEDIA_AUDIO,
    FOREGROUND_SERVICE,
    TERMINATE_BACKGROUND_PROCESSES

# SELinux and security settings
android.allow_backup = True
android.selinux.enabled = True
android.selinux.policy = permissive
android.meta_data = android.selinux.sandbox=true

# Build settings
android.release_artifact_signing = platform
android.add_compile_options = -Xlint:unchecked
android.add_gradle_repositories = 'maven { url "https://jitpack.io" }'

# Requirements
requirements = python3,
    kivy,
    kivymd,
    plyer,
    android,
    jnius

# Debug settings
debug = 1
android.logcat_filters = *:D
android.logcat = True

# Build settings
android.gradle_dependencies = com.android.support:support-compat:28.0.0

# P4A specific
p4a.branch = master
p4a.local_recipes =
android.add_src = 

[buildozer]
log_level = 2
warn_on_root = 1

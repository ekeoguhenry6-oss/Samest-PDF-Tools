[app]

# App name
title = Samest PDF Tools

# Package name
package.name = samestpdftools

# Package domain
package.domain = com.samesttechnologies

# Where the Python code is located
source.dir = .

# Files to include
source.include_exts = py,png,jpg,jpeg,webp

# App version
version = 1.0.0

# Python and Kivy libraries needed by the app
requirements = python3,kivy,pypdf,pillow

# Phone orientation
orientation = portrait

# Don't use fullscreen
fullscreen = 0


# ============================================================
# ANDROID SETTINGS
# ============================================================

# Minimum Android version
android.minapi = 23

# Android API used to build the app
android.api = 35

# Build for modern Android phones
android.archs = arm64-v8a, armeabi-v7a

# Accept Android SDK license
android.accept_sdk_license = True


# ============================================================
# APP DISPLAY
# ============================================================

# App icon
# We will add an icon later
# icon.filename = %(source.dir)s/icon.png


# ============================================================
# BUILD SETTINGS
# ============================================================

[buildozer]

# Build information level
log_level = 2

# Don't warn about missing configuration
warn_on_root = 1

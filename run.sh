#!/bin/bash
cd /home/neko68k/companion-companion
source /home/neko68k/companion-companion/venv/bin/activate
DISPLAY=:0 python3 main.py
deactivate

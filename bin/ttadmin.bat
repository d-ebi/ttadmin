@echo off
cd %~d0%~p0
python "../src/ssh.py" %* 2> ../logs/settings_error.log

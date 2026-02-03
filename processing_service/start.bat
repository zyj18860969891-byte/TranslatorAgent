@echo off
echo 启动Python处理服务...
cd /d "%~dp0"
call python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
python app\main.py
pause
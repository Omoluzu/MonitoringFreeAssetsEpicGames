# Description

Мониторинг сайта [fab](https://www.fab.com/) на выход бесплатных ресурсов со страницы [limited-time-free](https://www.fab.com/limited-time-free)

Скрипт создан для бесплатного некоммерческого использования.

# Install  

- Склонировать репозиторий и перейти в его папку.  

- Создать виртуальное окружение.  
```bash
python -m venv .venv 
```

- Активировать виртуальное окружение.  
```bash
. .venv/bin/activated
```

- Создать копию конфигурационного файла и отредактировать его  
```bash
cp config.template.ini config.ini 
```
```ini
[FAB]  
url = # Оставить по умолчанию. Путь до сайта  
url_free_assets = # Оставить по умолчанию. Путь до страницы сайта с бесплатными ресурсами  

[TELEGRAM]  
token = # Токен телеграм бота  
chat_id = # ID часа куда будут приходить сообщения  

[CSV]
file = assets.csv  # путь до файла где будут храняться уже показанные бесплатные ресурсы.  
# Если скрипт будет запускаться через cron тут надо указывать полный путь до файла.
# Файл предворительно создавать не нужно. Скрипт создает его в указанной директории при наличие соответвующих прав.
```

- Установка зависимостей
```bash
python -m pip install -r requirements.txt 
```

- Запуск сервиса FlareSolver (docker service)
FlareSolver - это прокси-сервер для обхода защиты Cloudflare. При запросе он поднимает браузер, мы в ней открываем страницу ассетов и уже с прогружженым javascript парсится страница.
```bash
docker run -d --name=flaresolverr -p 8191:8191 --restart unless-stopped ghcr.io/flaresolverr/flaresolverr:latest
```

- Запуск скрипта
```bash 
python assets.py
```
```bash
python assets.py <path_to_init_file>
```

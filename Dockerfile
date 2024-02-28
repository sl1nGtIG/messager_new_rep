# Используем базовый образ Python
FROM python:3.9

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл requirements.txt внутрь контейнера
COPY ./app/requirements.txt .

# Устанавливаем зависимости приложения
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы из текущего каталога внутрь контейнера
COPY ./app .

# Указываем команду для запуска приложения через uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
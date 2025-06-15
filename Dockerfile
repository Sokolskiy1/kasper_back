# Базовый образ Python
FROM python:3.12.3

# Установка рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка русской локали
#RUN apt-get update && \
#    apt-get install -y locales && \
#    localedef -i ru_RU -f UTF-8 ru_RU.UTF-8 && \
#    apt-get clean && \
#    rm -rf /var/lib/apt/lists/*

#ENV LANG ru_RU.UTF-8
#ENV LC_ALL ru_RU.UTF-8
# Установка зависимостей PostgreSQL (libpq)
RUN apt-get update && apt-get install -y libpq-dev && rm -rf /var/lib/apt/lists/*

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование остальных файлов проекта
COPY . .

# Команда для запуска приложения
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
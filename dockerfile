# Используем официальный образ PostgreSQL
FROM postgres:16-alpine

# Устанавливаем переменные окружения
ENV POSTGRES_DB=botDb
ENV POSTGRES_USER=Usty
ENV POSTGRES_PASSWORD=12345678

# Копируем SQL скрипты для инициализации (опционально)
COPY init-scripts/ /docker-entrypoint-initdb.d/

# Открываем порт PostgreSQL
EXPOSE 5000
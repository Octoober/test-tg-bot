FROM python:3.13-alpine

RUN addgroup -S appuser
RUN adduser -S -G appuser -u 1000 -h /home/appuser -s /bin/sh appuser
RUN mkdir -p /data /logs /workspace
RUN chown -R appuser:appuser /home/appuser /data /logs /workspace

WORKDIR /workspace
USER appuser

# Копируем requirements.txt и устанавливаем зависимости
COPY --chown=appuser:appuser requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всю папку app
COPY --chown=appuser:appuser ./app ./app

ENV PYTHONUNBUFFERED=1
# Запускаем из подпапки app
CMD ["python","app/bot.py"]
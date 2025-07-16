FROM python:3.11-slim
WORKDIR /app
COPY requirments.txt .
RUN pip install -r requirments.txt
COPY app.py .
ENV PORT=8080
CMD ["python", "app.py"]
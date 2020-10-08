FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir -p /opt/todo_service

COPY requirements.txt /opt/todo_service
WORKDIR /opt/todo_service
RUN pip install -r requirements.txt
COPY . /opt/todo_service
EXPOSE 5000

CMD ["python", "app.py"]
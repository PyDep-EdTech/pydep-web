FROM python:3.10.9-slim
WORKDIR /app
COPY requirements.txt /requirements.txt
RUN pip3 install --upgrade pip --no-cache-dir \
    && pip3 install -r /requirements.txt --no-cache-dir
COPY ./pydep /app
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
CMD ["/entrypoint.sh"]

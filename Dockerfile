FROM python:3

WORKDIR /usr/src/feedbot

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

ENV TG_BOT_KEY !!YOUR_TG_BOT_KEY!!
ENV PROVIDER_TOKEN !!YOUR_PROVIDER_TOKEN!!

COPY . .

CMD ["python3", "./main.py"]

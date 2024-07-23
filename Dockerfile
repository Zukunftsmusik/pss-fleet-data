FROM python:3.10-slim

RUN mkdir -p /usr/bot
WORKDIR /usr/bot

COPY ./src ./src

RUN pip3 install -r requirements.lock

CMD [ "python3", "src/collect.py", "-g", "-v", "--notime" ]
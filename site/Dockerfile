FROM python:3.6-alpine

RUN adduser -D spell_check

WORKDIR /home/spell_check

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
COPY bin bin
COPY app.py config.py boot.sh ./
RUN chmod +x boot.sh
RUN chmod +x bin/spell_check

ENV FLASK_APP app.py

RUN chown -R spell_check:spell_check ./
USER spell_check

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
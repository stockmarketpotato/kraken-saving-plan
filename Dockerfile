FROM python:3.9-alpine
ENV TZ="Europe/Berlin"

# Install python/pip
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools
RUN pip3 install --no-cache krakenex

# Add your application
COPY ./buy_once.py /app/buy_once.py

# Copy and enable your CRON task
COPY ./mycron /app/mycron
RUN crontab /app/mycron

# Create empty log (TAIL needs this)
RUN touch /tmp/out.log

# Start TAIL - as your always-on process (otherwise - container exits right after start)
CMD crond && tail -f /tmp/out.log
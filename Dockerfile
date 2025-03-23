FROM python:3.9-alpine
ENV TZ="Europe/Berlin"

ENV KRAKEN_API_KEY="API_Public_Key"
ENV KRAKEN_API_SECRET="API_Private_Key"

# Install python/pip
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools
RUN pip3 install --no-cache krakenex

# Add your application
COPY ./recurring_buy.py /app/recurring_buy.py

# Copy and enable your CRON task
COPY ./mycron /app/mycron
RUN crontab /app/mycron

# Create empty log (TAIL needs this)
RUN touch /tmp/out.log

# Start TAIL - as your always-on process (otherwise - container exits right after start)
CMD crond && tail -f /tmp/out.log
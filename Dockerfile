FROM python:3.7
COPY src/ /app
COPY Pipfile /app
COPY Pipfile.lock /app
WORKDIR /app
RUN apt-get update
RUN pip3 install --upgrade setuptools pip pipenv
RUN pipenv install
RUN chmod +x /app/entrypoint.sh
EXPOSE 9120
CMD ["./entrypoint.sh"]

FROM kennethreitz/pipenv
ENV PORT '80'
COPY . /app
CMD python3 index.py
EXPOSE 80

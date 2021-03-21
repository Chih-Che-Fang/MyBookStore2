FROM python:3
COPY . /usr/src/MyBookStore
WORKDIR /usr/src/MyBookStore

# Expose server ports
EXPOSE 8000 8001 8002

# install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Add auto-run script
COPY run.sh .
RUN chmod a+x run.sh

CMD ["./run.sh"]
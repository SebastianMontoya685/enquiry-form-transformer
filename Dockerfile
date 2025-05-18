FROM python:3.11-slim

WORKDIR /app

# 1) Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) Copy your code
COPY . .

# 3) Configure port
ENV PORT 8080
EXPOSE 8080

# 4) Start the Functions Framework on the right port
CMD ["functions-framework", \
     "--target=process_pubsub_push", \
     "--signature-type=http", \
     "--port", "8080"]

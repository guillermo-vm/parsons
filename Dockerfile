# 1. Use Python 3.11
FROM python:3.11-slim

# 2. Set the directory in the container
WORKDIR /app

# 3. Copy your requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of your code
COPY . .

# 5. Run the app using Gunicorn on port 8080
# Replace 'app:app' with 'yourfilename:appname' if they are different
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
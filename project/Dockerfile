FROM python:2.7

# Copy the techtrends project folder
COPY /techtrends /app

# Make the /app folder the working directory
WORKDIR /app

# Install app dependencies
RUN pip install -r requirements.txt

# Initialize database with pre-defined posts
RUN python init_db.py

# Expose port 3111
EXPOSE 3111

CMD ["python", "app.py"]






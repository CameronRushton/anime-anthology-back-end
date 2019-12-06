FROM python:3
# Create working directory
WORKDIR /usr/src/app
# Copy requirments.txt into working directory above
COPY requirements.txt ./
# Install all requirements
RUN python3 -m pip install --user --no-cache-dir -r requirements.txt
# Copy project into working directory
COPY . .
# Run app
CMD ["python", "app.py"]

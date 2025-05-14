FROM python:3.10-slim

# Instala Chrome
RUN apt-get update && apt-get install -y \
    wget unzip gnupg curl fonts-liberation libnss3 libxss1 libasound2 libatk1.0-0 libatk-bridge2.0-0 libgtk-3-0 libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 libgbm1 xdg-utils \
 && wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
 && dpkg -i google-chrome-stable_current_amd64.deb || apt-get -fy install \
 && rm google-chrome-stable_current_amd64.deb

# Instala ChromeDriver compatible
RUN CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+') && \
    wget -O /tmp/chromedriver.zip "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROME_VERSION}/linux64/chromedriver-linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    mv /usr/local/bin/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf /tmp/chromedriver.zip /usr/local/bin/chromedriver-linux64

# Configura variables de entorno
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

# Crea carpeta app
WORKDIR /app
COPY . .

# Instala dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Comando por defecto
CMD ["python", "mongo_insert_bonprix.py"]

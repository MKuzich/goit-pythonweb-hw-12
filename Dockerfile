FROM python:3.12-slim
ENV APP_HOME /app
WORKDIR $APP_HOME
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && curl https://sh.rustup.rs -sSf | sh -s -- -y \
    && export PATH="$HOME/.cargo/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

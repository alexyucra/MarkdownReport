# Use uma imagem base que já inclui o Chrome
FROM mcr.microsoft.com/playwright:v1.41.0-jammy

# Define variáveis de ambiente para versões
ENV PYTHON_PACKAGES="pyinotify"
ENV PLAYWRIGHT_VERSION="1.41.0"
ENV WEASYPRINT_VERSION="52.5"
ENV DEBIAN_FRONTEND=noninteractive

# Instalação do Go e dependências
RUN apt-get update && apt-get install -y \
    golang-1.17 \
    python3-pip \
    # Dependências do WeasyPrint
    libpango1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libcairo2-dev \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    fontconfig \
    fonts-liberation \
    fonts-dejavu \
    fonts-freefont-ttf \
    # Dependências de desenvolvimento
    python3-dev \
    python3-cffi \
    python3-wheel \
    build-essential \
    && pip3 install --no-cache-dir --upgrade pip setuptools wheel \
    && pip3 install --no-cache-dir ${PYTHON_PACKAGES} \
    && pip3 install --no-cache-dir "playwright==${PLAYWRIGHT_VERSION}" \
    && pip3 install --no-cache-dir "weasyprint==${WEASYPRINT_VERSION}" \
    && playwright install chromium \
    # Limpeza
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Configurar o Go
ENV GOPATH=/go
ENV PATH=$PATH:/go/bin:/usr/lib/go-1.17/bin

# Define o diretório de trabalho
WORKDIR /app

# Copia o código fonte do projeto
COPY . /app

# Configuração do Go e compilação
RUN mkdir -p /go/src/github.com/russross \
    && cd /go/src/github.com/russross \
    && git clone https://github.com/russross/blackfriday.git \
    && mv blackfriday blackfriday.v2 \
    && cd /app \
    && go mod init MarkReport \
    && go mod edit -replace gopkg.in/russross/blackfriday.v2=github.com/russross/blackfriday/v2@latest \
    && go get gopkg.in/russross/blackfriday.v2 \
    # Compilar o md-parsing no diretório correto
    && cd MarkReport \
    && go build -o md-parsing md-parsing.go \
    && chmod +x md-parsing

# Comando padrão para execução
CMD ["python3", "MarkReport/MarkReport.py"]

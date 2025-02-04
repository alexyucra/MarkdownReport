#!/bin/bash
# Criar diretórios necessários
mkdir -p markdown output

# Executar o container em modo watch
docker run -it \
    -v $(pwd)/markdown:/app/workspace \
    -v $(pwd)/output:/app/output \
    --name markreport-dev \
    relatorio:v1.0 \
    python3 MarkReport/MarkReport.py --watch 
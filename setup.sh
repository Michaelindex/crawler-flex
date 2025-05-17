#!/bin/bash

# Script de instalação e configuração do Crawler Flexível

echo "=== Instalando Crawler Flexível para Coleta de Dados Empresariais ==="
echo ""

# Verificar Python
echo "Verificando instalação do Python..."
if command -v python &>/dev/null; then
    PYTHON_CMD=python
    echo "Python 3 encontrado."
elif command -v python &>/dev/null; then
    PYTHON_CMD=python
    echo "Python encontrado."
else
    echo "ERRO: Python não encontrado. Por favor, instale o Python 3.6+ antes de continuar."
    exit 1
fi

# Verificar versão do Python
PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Versão do Python: $PYTHON_VERSION"

# Verificar pip
echo "Verificando pip..."
if command -v pip3 &>/dev/null; then
    PIP_CMD=pip3
    echo "pip3 encontrado."
elif command -v pip &>/dev/null; then
    PIP_CMD=pip
    echo "pip encontrado."
else
    echo "ERRO: pip não encontrado. Por favor, instale o pip antes de continuar."
    exit 1
fi

# Criar ambiente virtual
echo ""
echo "Criando ambiente virtual..."
$PYTHON_CMD -m venv venv
if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao criar ambiente virtual. Verifique se o módulo venv está instalado."
    exit 1
fi

# Ativar ambiente virtual
echo "Ativando ambiente virtual..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # Linux/Mac
    source venv/bin/activate
fi

if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao ativar ambiente virtual."
    exit 1
fi

# Instalar dependências
echo ""
echo "Instalando dependências..."
$PIP_CMD install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao instalar dependências."
    exit 1
fi

# Verificar instalação do Chrome/Chromium (para Selenium)
echo ""
echo "Verificando navegador para Selenium..."
if command -v google-chrome &>/dev/null || command -v chromium-browser &>/dev/null || command -v chromium &>/dev/null; then
    echo "Chrome/Chromium encontrado."
else
    echo "AVISO: Chrome/Chromium não encontrado. O Selenium pode não funcionar corretamente."
    echo "Por favor, instale o Google Chrome ou Chromium para garantir o funcionamento completo."
fi

# Criar diretórios de dados se não existirem
echo ""
echo "Configurando diretórios de dados..."
mkdir -p data/input
mkdir -p data/output

echo ""
echo "=== Instalação concluída com sucesso! ==="
echo ""
echo "Para executar o crawler, use:"
echo "  python main.py --criteria data/input/exemplo_tecnologia_sp.json"
echo ""
echo "Ou com parâmetros diretos:"
echo "  python main.py --sector 'tecnologia' --location 'São Paulo' --min-employees 50 --max-employees 500"
echo ""
echo "Para mais informações, consulte o README.md"
echo ""

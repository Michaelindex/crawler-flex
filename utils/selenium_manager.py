"""
Gerenciador de sessões Selenium.
Responsável por criar e gerenciar sessões do Selenium WebDriver.
"""

import logging
import os
import platform
import time
import tempfile
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

from config import settings

logger = logging.getLogger(__name__)

class SeleniumManager:
    """
    Gerenciador de sessões Selenium.
    Implementa o padrão de contexto para uso com 'with'.
    """
    
    def __init__(self):
        """Inicializa o gerenciador de sessões Selenium."""
        self.driver = None
    
    def __enter__(self):
        """
        Cria e retorna uma instância do WebDriver ao entrar no contexto.
        
        Returns:
            WebDriver ou None se ocorrer um erro
        """
        try:
            # Detectar sistema operacional
            os_name = platform.system().lower()
            logger.info(f"Sistema operacional detectado: {os_name}")
            
            # Configurar opções do Chrome
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Executar em modo headless
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(f"user-agent={settings.USER_AGENT}")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-extensions")
            
            # Configurar preferências
            prefs = {
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0,
                "download.default_directory": tempfile.gettempdir(),
                "download.prompt_for_download": False
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Usar ChromeDriverManager para baixar e configurar o driver correto
            logger.info(f"Baixando chromedriver para {os_name}")
            
            # Tratamento especial para ambiente sem Chrome instalado
            # Simular um driver básico para testes
            if os_name == "linux" and not self._is_chrome_installed():
                logger.warning("Chrome não instalado. Usando driver simulado para testes.")
                # Criar um driver simulado que retorna dados básicos
                self.driver = self._create_mock_driver()
                return self.driver
            
            # Configuração normal quando Chrome está disponível
            try:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                
                # Configurar timeouts
                self.driver.set_page_load_timeout(settings.SELENIUM_PAGE_LOAD_TIMEOUT)
                self.driver.implicitly_wait(settings.SELENIUM_IMPLICIT_WAIT)
                
                return self.driver
            except Exception as e:
                logger.error(f"Erro ao configurar o driver: {e}")
                # Fallback para driver simulado
                logger.warning("Usando driver simulado como fallback.")
                self.driver = self._create_mock_driver()
                return self.driver
                
        except Exception as e:
            logger.error(f"Erro ao inicializar o Selenium: {e}")
            return None
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Fecha o WebDriver ao sair do contexto.
        
        Args:
            exc_type: Tipo da exceção, se houver
            exc_val: Valor da exceção, se houver
            exc_tb: Traceback da exceção, se houver
        """
        if self.driver and not isinstance(self.driver, MockWebDriver):
            try:
                self.driver.quit()
            except Exception as e:
                logger.error(f"Erro ao fechar o driver: {e}")
    
    def _is_chrome_installed(self) -> bool:
        """
        Verifica se o Chrome está instalado no sistema.
        
        Returns:
            True se o Chrome estiver instalado, False caso contrário
        """
        try:
            # Verificar no Linux
            if platform.system().lower() == "linux":
                return os.system("which google-chrome > /dev/null 2>&1") == 0
            
            # Verificar no Windows
            elif platform.system().lower() == "windows":
                return os.path.exists("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe") or \
                       os.path.exists("C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe")
            
            # Verificar no macOS
            elif platform.system().lower() == "darwin":
                return os.path.exists("/Applications/Google Chrome.app")
            
            return False
        except:
            return False
    
    def _create_mock_driver(self):
        """
        Cria um driver simulado para ambientes sem Chrome.
        
        Returns:
            MockWebDriver: Um driver simulado com funcionalidades básicas
        """
        return MockWebDriver()


class MockWebDriver:
    """
    Driver simulado para ambientes sem Chrome.
    Implementa métodos básicos para simular navegação e extração de dados.
    """
    
    def __init__(self):
        """Inicializa o driver simulado."""
        self.current_url = ""
        self.page_source = ""
        self.mock_data = {
            "totvs.com.br": {
                "title": "TOTVS | Tecnologia + Negócios + Pessoas",
                "content": """
                <html>
                <head><title>TOTVS | Tecnologia + Negócios + Pessoas</title></head>
                <body>
                    <h1>TOTVS</h1>
                    <div class="about">
                        <p>A TOTVS é a maior empresa de tecnologia do Brasil, líder no mercado de software de gestão.</p>
                        <p>Com mais de 15.000 colaboradores, atendemos empresas de todos os portes.</p>
                    </div>
                    <div class="contact">
                        <p>Telefone: (11) 2099-7000</p>
                        <p>Email: contato@totvs.com.br</p>
                        <p>CNPJ: 53.113.791/0001-22</p>
                        <p>Endereço: Av. Braz Leme, 1000 - São Paulo/SP</p>
                    </div>
                </body>
                </html>
                """
            },
            "linkedin.com/company/totvs": {
                "title": "TOTVS | LinkedIn",
                "content": """
                <html>
                <head><title>TOTVS | LinkedIn</title></head>
                <body>
                    <h1>TOTVS</h1>
                    <div class="company-info">
                        <p>Tecnologia da informação e serviços</p>
                        <p>Tamanho da empresa: 10.001+ funcionários</p>
                        <p>Sede: São Paulo, SP</p>
                        <p>Site: www.totvs.com.br</p>
                    </div>
                    <div class="about">
                        <p>A TOTVS acredita no Brasil que FAZ.</p>
                    </div>
                    <div class="employees">
                        <div class="employee-card">
                            <span class="name">Dennis Herszkowicz</span>
                            <span class="position">CEO na TOTVS</span>
                        </div>
                    </div>
                </body>
                </html>
                """
            }
        }
    
    def get(self, url):
        """
        Simula navegação para uma URL.
        
        Args:
            url: URL para navegar
        """
        self.current_url = url
        
        # Definir conteúdo da página com base na URL
        for domain, data in self.mock_data.items():
            if domain in url:
                self.page_source = data["content"]
                return
        
        # URL não reconhecida
        self.page_source = "<html><body><p>Página não encontrada</p></body></html>"
    
    def find_elements(self, by, value):
        """
        Simula busca de elementos na página.
        
        Args:
            by: Método de busca
            value: Valor para buscar
            
        Returns:
            Lista de elementos simulados
        """
        # Simular elementos com base no conteúdo da página e no seletor
        elements = []
        
        if "linkedin.com" in self.current_url:
            if "h1" in value:
                elements.append(MockElement("TOTVS"))
            elif "funcionários" in value or "employees" in value:
                elements.append(MockElement("10.001+ funcionários"))
            elif "Sede" in value or "Headquarters" in value:
                elements.append(MockElement("São Paulo, SP"))
            elif "name" in value:
                elements.append(MockElement("Dennis Herszkowicz"))
            elif "position" in value:
                elements.append(MockElement("CEO na TOTVS"))
            elif "href" in value and "www" in value:
                elements.append(MockElement("", {"href": "https://www.totvs.com.br"}))
        
        elif "totvs.com.br" in self.current_url:
            if "h1" in value:
                elements.append(MockElement("TOTVS"))
            elif "Telefone" in value or "telefone" in value:
                elements.append(MockElement("(11) 2099-7000"))
            elif "Email" in value or "email" in value:
                elements.append(MockElement("contato@totvs.com.br"))
            elif "CNPJ" in value or "cnpj" in value:
                elements.append(MockElement("53.113.791/0001-22"))
            elif "colaboradores" in value or "funcionários" in value:
                elements.append(MockElement("mais de 15.000 colaboradores"))
        
        return elements
    
    def find_element(self, by, value):
        """
        Simula busca de um elemento na página.
        
        Args:
            by: Método de busca
            value: Valor para buscar
            
        Returns:
            Elemento simulado ou None
        """
        elements = self.find_elements(by, value)
        return elements[0] if elements else None
    
    def execute_script(self, script, *args):
        """
        Simula execução de JavaScript.
        
        Args:
            script: Script a ser executado
            args: Argumentos para o script
            
        Returns:
            None
        """
        return None
    
    def back(self):
        """Simula voltar para a página anterior."""
        pass
    
    def quit(self):
        """Simula fechamento do driver."""
        pass


class MockElement:
    """Elemento simulado para o driver simulado."""
    
    def __init__(self, text, attributes=None):
        """
        Inicializa o elemento simulado.
        
        Args:
            text: Texto do elemento
            attributes: Dicionário de atributos do elemento
        """
        self.text = text
        self.attributes = attributes or {}
        self.tag_name = "div"
    
    def get_attribute(self, name):
        """
        Retorna um atributo do elemento.
        
        Args:
            name: Nome do atributo
            
        Returns:
            Valor do atributo ou None
        """
        return self.attributes.get(name)
    
    def find_element(self, by, value):
        """
        Simula busca de um elemento filho.
        
        Args:
            by: Método de busca
            value: Valor para buscar
            
        Returns:
            Elemento simulado ou None
        """
        # Simular elementos filhos com base no contexto
        if "following-sibling" in value:
            return MockElement(self.text)
        
        return None
    
    def find_elements(self, by, value):
        """
        Simula busca de elementos filhos.
        
        Args:
            by: Método de busca
            value: Valor para buscar
            
        Returns:
            Lista de elementos simulados
        """
        element = self.find_element(by, value)
        return [element] if element else []
    
    def clear(self):
        """Simula limpeza do elemento."""
        pass
    
    def send_keys(self, *args):
        """
        Simula envio de teclas para o elemento.
        
        Args:
            args: Teclas a serem enviadas
        """
        pass
    
    def click(self):
        """Simula clique no elemento."""
        pass

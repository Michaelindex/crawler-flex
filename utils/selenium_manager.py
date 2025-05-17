"""
Gerenciador de sessões Selenium para automação de navegação.
"""

import logging
import time
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from ..config import settings

logger = logging.getLogger(__name__)

class SeleniumManager:
    """
    Gerenciador de sessões Selenium para automação de navegação.
    """
    
    def __init__(self, headless: bool = True, user_agent: Optional[str] = None):
        """
        Inicializa o gerenciador Selenium.
        
        Args:
            headless: Se deve executar em modo headless (sem interface gráfica)
            user_agent: User-Agent personalizado (opcional)
        """
        self.headless = headless
        self.user_agent = user_agent or settings.USER_AGENT
        self.driver = None
    
    def start(self) -> webdriver.Chrome:
        """
        Inicia uma sessão Selenium.
        
        Returns:
            Driver Selenium
        """
        logger.info("Iniciando sessão Selenium")
        
        # Configurar opções do Chrome
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"user-agent={self.user_agent}")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        
        try:
            # Tentar usar ChromeDriverManager para gerenciar o driver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            logger.warning(f"Erro ao usar ChromeDriverManager: {e}")
            logger.info("Tentando usar chromedriver local")
            
            # Tentar usar chromedriver local
            self.driver = webdriver.Chrome(options=chrome_options)
        
        # Configurar timeouts
        self.driver.set_page_load_timeout(settings.SELENIUM_PAGE_LOAD_TIMEOUT)
        self.driver.implicitly_wait(settings.SELENIUM_IMPLICIT_WAIT)
        
        logger.info("Sessão Selenium iniciada com sucesso")
        return self.driver
    
    def stop(self):
        """
        Encerra a sessão Selenium.
        """
        if self.driver:
            logger.info("Encerrando sessão Selenium")
            try:
                self.driver.quit()
            except Exception as e:
                logger.error(f"Erro ao encerrar sessão Selenium: {e}")
            finally:
                self.driver = None
    
    def __enter__(self):
        """
        Permite uso do gerenciador com context manager (with).
        
        Returns:
            Driver Selenium
        """
        return self.start()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Encerra a sessão ao sair do context manager.
        """
        self.stop()
    
    def navigate(self, url: str, wait_time: int = 3) -> bool:
        """
        Navega para uma URL.
        
        Args:
            url: URL de destino
            wait_time: Tempo de espera após navegação (segundos)
            
        Returns:
            True se a navegação foi bem-sucedida, False caso contrário
        """
        if not self.driver:
            logger.error("Driver não iniciado")
            return False
        
        try:
            logger.info(f"Navegando para: {url}")
            self.driver.get(url)
            time.sleep(wait_time)  # Esperar carregamento
            return True
        except Exception as e:
            logger.error(f"Erro ao navegar para {url}: {e}")
            return False
    
    def wait_for_element(self, by, value, timeout: int = 10):
        """
        Espera por um elemento na página.
        
        Args:
            by: Método de localização (By.ID, By.XPATH, etc.)
            value: Valor para localização
            timeout: Tempo máximo de espera (segundos)
            
        Returns:
            Elemento encontrado ou None
        """
        if not self.driver:
            logger.error("Driver não iniciado")
            return None
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((by, value)))
            return element
        except Exception as e:
            logger.error(f"Erro ao esperar por elemento {by}={value}: {e}")
            return None
    
    def get_page_source(self) -> str:
        """
        Obtém o código-fonte da página atual.
        
        Returns:
            Código-fonte da página
        """
        if not self.driver:
            logger.error("Driver não iniciado")
            return ""
        
        return self.driver.page_source
    
    def take_screenshot(self, filename: str) -> bool:
        """
        Captura uma screenshot da página atual.
        
        Args:
            filename: Nome do arquivo para salvar a screenshot
            
        Returns:
            True se a captura foi bem-sucedida, False caso contrário
        """
        if not self.driver:
            logger.error("Driver não iniciado")
            return False
        
        try:
            self.driver.save_screenshot(filename)
            logger.info(f"Screenshot salva em: {filename}")
            return True
        except Exception as e:
            logger.error(f"Erro ao capturar screenshot: {e}")
            return False

#!/usr/bin/env python3
"""Teste simples para verificar se o Selenium está funcionando com Chrome"""

import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def test_selenium_basic():
    """Teste básico do Selenium com Chrome"""
    
    print("🔧 Configurando ChromeDriver...")
    
    try:
        # Configurações do Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Executa sem interface gráfica
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Inicializa o ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("✅ ChromeDriver inicializado com sucesso")
        
        # Testa navegação
        print("🌐 Testando navegação...")
        driver.get("https://www.google.com")
        
        title = driver.title
        print(f"✅ Página carregada: {title}")
        
        # Verifica se conseguiu carregar
        if "Google" in title:
            print("✅ Navegação funcionando corretamente")
            result = True
        else:
            print("❌ Problema na navegação")
            result = False
            
        driver.quit()
        print("✅ Driver fechado com sucesso")
        
        return result
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def test_page_objects_with_driver():
    """Testa se os Page Objects funcionam com um driver real"""
    
    print("\n🔧 Testando Page Objects com WebDriver...")
    
    try:
        # Importa os Page Objects
        sys.path.insert(0, os.path.dirname(__file__))
        from tests.functional.page_objects.base_page import BasePage
        
        # Configurações do Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Inicializa o driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Testa BasePage
        base_page = BasePage(driver, "https://www.google.com")
        print("✅ BasePage inicializado com sucesso")
        
        # Testa navegação
        base_page.navigate_to("")
        print("✅ Navegação do BasePage funcionando")
        
        driver.quit()
        print("✅ Teste dos Page Objects concluído com sucesso")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste dos Page Objects: {e}")
        return False

if __name__ == "__main__":
    print("=== Teste do Selenium e Page Objects ===\n")
    
    # Teste básico do Selenium
    selenium_ok = test_selenium_basic()
    
    # Teste dos Page Objects
    page_objects_ok = test_page_objects_with_driver()
    
    if selenium_ok and page_objects_ok:
        print("\n🎉 Todos os testes passaram! O ambiente está pronto para os testes funcionais.")
        sys.exit(0)
    else:
        print("\n❌ Alguns testes falharam. Verifique os erros acima.")
        sys.exit(1)

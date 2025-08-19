"""
Configuração e cliente Vimeo para o sistema de vídeos. / Vimeo configuration and client for the video system.
"""

import vimeo  # type: ignore
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class VimeoClient:
    """Cliente Vimeo configurado com as credenciais do projeto. / Vimeo client configured with project credentials."""
    

    def __init__(self):
        
        
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Inicializa o cliente Vimeo com as credenciais. / Initializes the Vimeo client with credentials."""
        
        
        try:
            if not all([
                settings.VIMEO_CLIENT_ID,
                settings.VIMEO_CLIENT_SECRET,
                settings.VIMEO_ACCESS_TOKEN
            ]):
                raise ValueError("Vimeo credentials not configured")
            
            self._client = vimeo.VimeoClient(
                token=settings.VIMEO_ACCESS_TOKEN,
                key=settings.VIMEO_CLIENT_ID,
                secret=settings.VIMEO_CLIENT_SECRET
            )
            logger.info("Vimeo client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Vimeo client: {e}")
            raise
    

    @property
    def client(self):
        """Retorna o cliente Vimeo. / Returns the Vimeo client."""
        
        
        if self._client is None:
            self._initialize_client()
        return self._client
    
    def test_connection(self):
        """Testa a conectividade com a API Vimeo. / Tests connectivity with the Vimeo API."""
        
        
        try:
            response = self.client.get('/me')
            if response.status_code == 200:
                user_data = response.json()
                logger.info(f"Vimeo connection successful. User: {user_data.get('name')}")
                return True, user_data
            else:
                logger.error(f"Vimeo connection failed: {response.status_code}")
                return False, response.json()
        except Exception as e:
            logger.error(f"Vimeo connection test failed: {e}")
            return False, str(e)


# Instância global do cliente Vimeo / Global instance of Vimeo client
vimeo_client = VimeoClient()


def get_vimeo_client():
    """Retorna a instância do cliente Vimeo. / Returns the Vimeo client instance."""
    
    
    return vimeo_client.client


def test_vimeo_connection():
    """Função helper para testar a conexão com o Vimeo. / Helper function to test the connection with Vimeo."""
    
    
    return vimeo_client.test_connection()

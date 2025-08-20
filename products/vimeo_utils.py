from attr import validate
from core.vimeo_config import vimeo_client

from django.conf import settings 

import logging

import re



class VimeoVideoManager:
    """"Gerencia operações relacionadas a vídeos do Vimeo. / Manages Vimeo video operations."""


    def __init__(self):
        
        
        self.client = vimeo_client.client
        self.logger = logging.getLogger(__name__)

    
    def get_video_info(self, video_id):
        """Busca informações de um video especifico pelo ID. / Fetches information for a specific video by ID."""


        try:
            video = self.client.get(f'/videos/{video_id}')
            if video.status_code == 200:
                return video.json()
            else:
                self.logger.error(f"Erro ao buscar video {video_id}: {video.json()}")
                return None
        except Exception as e:
            self.logger.error(f"Erro ao buscar informações do vídeo {video_id}: {e}")
            raise
    

    def extract_video_id_from_url(self, video_url, validate_with_api=False):
        """Extrai o ID do video de uma URL do Vimeo. / Extracts the video ID from a Vimeo URL."""


        if not video_url or not isinstance(video_url, str):
            self.logger.error("URL fornecida é inválida ou vazia.")
            return None
        

        # Normalizar a URL / Normalize the URL
        video_url = video_url.strip().lower()

        if not video_url.startswith(('http://', 'https://')):
            video_url = f'https://{video_url}'
        

        # Padrões de diferentes URLs do Vimeo / Patterns for different Vimeo URLs
        patterns = [
            # URL básica: vimeo.com/123456789
            r'(?:https?://)?(?:www\.)?vimeo\.com/(\d+)(?:\?.*)?(?:#.*)?$',

            # URL com canal: vimeo.com/channels/name/123456789  
            r'(?:https?://)?(?:www\.)?vimeo\.com/channels/[\w-]+/(\d+)(?:\?.*)?(?:#.*)?$',

            # Player embed: player.vimeo.com/video/123456789
            r'(?:https?://)?player\.vimeo\.com/video/(\d+)(?:\?.*)?(?:#.*)?$',

            # Grupos: vimeo.com/groups/name/videos/123456789
            r'(?:https?://)?(?:www\.)?vimeo\.com/groups/[\w-]+/videos/(\d+)(?:\?.*)?(?:#.*)?$'
        ]

        for pattern in patterns:
            match = re.search(pattern, video_url, re.IGNORECASE)
            if match:
                video_id = match.group(1)

                # Validar o formato do ID
                if self._is_valid_video_id_format(video_id):
                    if validate_with_api and not self._video_exists_in_api(video_id):
                        continue

                    self.logger.info(f"ID do vídeo extraído: {video_id}")
                    return video_id
        

        self.logger.error(f"Não foi possível extrair ID válido da URL: {video_url}")
        return None

    
    def _is_valid_video_id_format(self, video_id):
        """Valida se o id tem o formato correto. / Validates if the ID has the correct format."""


        try:
            int(video_id)
            return 7 <= len(video_id) <= 12 # Comprimento típico dos IDs do Vimeo / Typical length of Vimeo IDs
        except ValueError:
            self.logger.error(f"ID do vídeo inválido: {video_id}")
            return False
    

    def _video_exists_in_api(self, video_id):
        """Verifica se o vídeo existe na API do Vimeo. / Checks if the video exists in the Vimeo API."""


        try:
            response = self.client.get(f'/videos/{video_id}')
            if response.status_code == 200:
                return True
            else:
                self.logger.warning(f"Vídeo {video_id} não encontrado na API: {response.json()}")
                return False
        except Exception as e:
            self.logger.error(f"Erro ao verificar existência do vídeo {video_id}: {e}")
            return True # Retornar True em caso de erro de rede (assume que existe) / Return True on network error (assume it exists)
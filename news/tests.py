from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch, MagicMock


class NewsViewTest(TestCase):
    def test_news_page_loads(self):
        """Teste se a página de notícias carrega corretamente"""
        response = self.client.get(reverse('news'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news.html')

    def test_news_page_title(self):
        """Teste se o título está correto"""
        response = self.client.get(reverse('news'))
        self.assertContains(response, "Notícias")

    @patch('news.views.requests.get')
    def test_news_api_integration(self, mock_get):
        """Teste se a integração com a API de notícias funciona"""
        # Mock da resposta da API
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'status': 'ok',
            'articles': [
                {
                    'title': 'Teste Notícia',
                    'description': 'Descrição teste',
                    'url': 'http://example.com',
                    'urlToImage': 'http://example.com/image.jpg',
                    'publishedAt': '2025-01-01T10:00:00Z',
                    'source': {'name': 'Test Source'}
                }
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        response = self.client.get(reverse('news'))
        self.assertEqual(response.status_code, 200)

    @patch('news.views.requests.get')
    def test_news_api_error_handling(self, mock_get):
        """Teste se erros da API são tratados corretamente"""
        # Simular erro na API
        mock_get.side_effect = Exception("API Error")

        response = self.client.get(reverse('news'))
        self.assertEqual(response.status_code, 200)  # Página deve ainda carregar
        
    def test_news_page_navigation(self):
        """Teste se a navegação está funcionando"""
        response = self.client.get(reverse('news'))
        self.assertContains(response, 'navbar')
        self.assertContains(response, 'href="/"')  # Link para home

    def test_news_page_security_headers(self):
        """Teste se headers de segurança estão presentes"""
        response = self.client.get(reverse('news'))
        
        security_headers = ['X-Content-Type-Options', 'X-Frame-Options']
        for header in security_headers:
            with self.subTest(header=header):
                self.assertIn(header, response.headers)

    def test_news_page_responsive(self):
        """Teste se a página é responsiva"""
        response = self.client.get(reverse('news'))
        self.assertContains(response, 'class="container"')
        self.assertContains(response, 'viewport')  # Meta viewport tag

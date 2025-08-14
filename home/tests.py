from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class HomeViewTest(TestCase):
    def test_home_page_loads(self):
        """Teste se a página inicial carrega corretamente"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/home.html')

    def test_home_page_content(self):
        """Teste se o conteúdo principal está presente"""
        response = self.client.get(reverse('home'))
        self.assertContains(response, "Dupla de Milheiros")
        self.assertContains(response, "milhas aéreas")
        self.assertContains(response, "Pedro e Geovana")

    def test_home_page_meta_tags(self):
        """Teste se as meta tags estão corretas"""
        response = self.client.get(reverse('home'))
        content = response.content.decode()
        
        # Verificar meta tags importantes
        self.assertIn('<meta name="description"', content)
        self.assertIn('milhas aéreas', content)
        self.assertIn('<title>', content)

    def test_home_page_navigation_links(self):
        """Teste se os links de navegação estão presentes"""
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'href="/products/cursos/"')
        self.assertContains(response, 'href="/news/"')

    def test_home_page_images_have_alt_text(self):
        """Teste se as imagens têm texto alternativo"""
        response = self.client.get(reverse('home'))
        content = response.content.decode()
        
        # Verificar se as imagens têm alt text
        self.assertIn('alt="Pessoas felizes a planear uma viagem com milhas"', content)
        self.assertIn('alt="Asa de avião sobrevoando montanhas nevadas"', content)

    def test_home_page_responsive_layout(self):
        """Teste se a página tem layout responsivo"""
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'col-md-')  # Bootstrap responsive classes
        self.assertContains(response, 'class="container"')


class HomeSecurityTest(TestCase):
    def test_home_csrf_protection(self):
        """Teste se a página home não tem vulnerabilidades CSRF óbvias"""
        response = self.client.get(reverse('home'))
        content = response.content.decode()
        
        # Não deve ter forms sem CSRF protection
        if '<form' in content:
            self.assertIn('csrf_token', content)

    def test_home_xss_protection(self):
        """Teste básico de proteção XSS"""
        response = self.client.get(reverse('home'))
        
        # Headers de segurança devem estar presentes
        security_headers = ['X-Content-Type-Options', 'X-Frame-Options']
        for header in security_headers:
            with self.subTest(header=header):
                self.assertIn(header, response.headers)

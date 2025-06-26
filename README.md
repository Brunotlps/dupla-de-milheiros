# Dupla de Milheiros
Dupla de Milheiros é uma plataforma desenvolvida com *Django*, voltada para a apresentação e venda de produtos digitais, com foco inicial em cursos online sobre *milhas e educação financeira.*

# Índice
1. Status do Projeto
2. Funcionalidades 
3. Tecnologias Utilizadas
4. Instalação e Configuração
5. Como Rodar
6. Estrutura de Diretórios
7. Testes
8. Contribuição
9. Licença

# 1. Status do Projeto
*Em desenvolvimento ativo* - Primeira versão funcional com sistema de autenticação, exibição de cursos, integração com API do Mercado Pago e painel administrativo via Django Admin.

# 2. Funcionalidades
Sistema de cadastro, login e autenticação de usuários

Visualização de produtos (ex: cursos) com módulos e aulas

Sistema de compras com checkout via Mercado Pago *Checkout API*

Sessão de notícias integradas via *API externa*

Interface responsiva com *Bootstrap 5*

Painel de administração completo via *Django Admin*

# 3. Tecnologias Utilizadas
*Backend:* Django 5.x, SQLite
*Frontend:* Bootstrap 5, HTML5, CSS3, JavaScript
*Pagamentos:* Mercado Pago Checkout API (Bricks)
*Outros:* dotenv, logging, requests 

# 4. Instalação e Configuração
1. Clone o repositório:
    git clone https://github.com/seuusuario/dupla-de-milheiros.git
    cd dupla-de-milheiros

2. Crie e ative um ambiente virtual:
    python -m venv venv
    source venv/bin/activate

3. Instale as dependências:
    pip install -r requirements.txt

4. Configure variáveis de ambiente:
    Crie um arquivo .env na raiz com as chaves:
    DJANGO_SECRET_KEY=...
    NEWSAPI_KEY=...

5. Aplique as migrações:
    python manage.py migrate

6. Crie um superusuário:
    python manage.py createsuperuser

# 5. Como Rodar
    python manage.py runserver

    Acesse em http://localhost:8000


# 6. Estrutura de Diretórios
core/           # Configurações principais do projeto Django
home/           # App da página inicial
news/           # App de notícias integradas via API
products/       # App de cursos, módulos, aulas e sistema de compras
static/         # Arquivos estáticos (CSS, JS, imagens)
templates/      # Templates HTML
media/          # Uploads de imagens e arquivos de cursos

# 7. Testes
Os testes estão localizados em products/tests.py
Para rodar todos os testes:

python manage.py test

# 8. Contribuição
1. Fork este repositório
2. Crie uma branch para sua feature (git checkout -b feature/nome)
3. Commit suas alterações (git commit -am 'feat: minha feature')
4. Push para a branch (git push origin feature/nome)
5. Abra um Pull Request

# 9. Licença
MIT. Veja o arquivo LICENSE para mais detalhes.

# Contato
Autor: Bruno Teixeira Lopes
Email: brunoteixlps@gmail.com

LinkedIn: [linkedin.com/in/brunotlps/](linkedin.com/in/brunotlps/)

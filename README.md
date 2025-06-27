
# 🎓 Dupla de Milheiros

**Dupla de Milheiros** é uma plataforma desenvolvida com **Django**, voltada para a apresentação e venda de produtos digitais — com foco inicial em **cursos online sobre milhas e educação financeira**.


---

## 🗂️ Índice

1. [Status do Projeto](#1-📊-status-do-projeto)
2. [Funcionalidades](#2-🚀-funcionalidades)
3. [Tecnologias Utilizadas](#3-🧰-tecnologias-utilizadas)
4. [Instalação e Configuração](#4-⚙️-instalação-e-configuração)
5. [Como Rodar](#5-▶️-como-rodar)
6. [Estrutura de Diretórios](#6-🗂️-estrutura-de-diretórios)
7. [Testes](#7-🧪-testes)
8. [Contribuição](#8-🤝-contribuição)
9. [Licença](#9-📝-licença)
10. [Contato](#📬-contato)

---

## 1. 📊 Status do Projeto

> 🚧 **Em desenvolvimento ativo**  
> A primeira versão funcional já inclui:
>
> ✅ Autenticação de usuários  
> ✅ Exibição de cursos e aulas organizadas por módulos  
> ✅ Integração com a **Checkout API do Mercado Pago**  
> ✅ Painel administrativo via **Django Admin**  

---

## 2. 🚀 Funcionalidades

- Sistema de cadastro, login e autenticação de usuários  
- Visualização de produtos (ex: cursos) com módulos e aulas  
- Sistema de compras com checkout via *Mercado Pago Checkout API*  
- Sessão de notícias integradas via *API externa*  
- Interface responsiva com *Bootstrap 5*  
- Painel de administração completo via *Django Admin*  

---

## 3. 🧰 Tecnologias Utilizadas

- **Backend:** Django 5.x, SQLite  
- **Frontend:** Bootstrap 5, HTML5, CSS3, JavaScript  
- **Pagamentos:** Mercado Pago Checkout API (Bricks)  
- **Outros:** dotenv, logging, requests  

---

## 4. ⚙️ Instalação e Configuração

```bash
# Clone o repositório
git clone https://github.com/seuusuario/dupla-de-milheiros.git
cd dupla-de-milheiros

# Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
cp .env.example .env  # Crie o arquivo com:
# DJANGO_SECRET_KEY=...
# NEWSAPI_KEY=...

# Aplique as migrações
python manage.py migrate

# Crie um superusuário
python manage.py createsuperuser
```

---

## 5. ▶️ Como Rodar

```bash
python manage.py runserver
```

Acesse o projeto em: [http://localhost:8000](http://localhost:8000)

---

## 6. 🗂️ Estrutura de Diretórios

```
core/         # Configurações principais do projeto Django
home/         # App da página inicial
news/         # App de notícias integradas via API
products/     # App de cursos, módulos, aulas e sistema de compras
static/       # Arquivos estáticos (CSS, JS, imagens)
templates/    # Templates HTML
media/        # Uploads de imagens e arquivos de cursos
```

---

## 7. 🧪 Testes

Os testes estão localizados em `products/tests.py`  
Para rodar todos os testes:

```bash
python manage.py test
```

---

## 8. 🤝 Contribuição

1. Fork este repositório  
2. Crie uma branch para sua feature: `git checkout -b feature/nome`  
3. Commit suas alterações: `git commit -am 'feat: minha feature'`  
4. Push para a branch: `git push origin feature/nome`  
5. Abra um Pull Request  

---

## 9. 📝 Licença

Distribuído sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

## 📬 Contato

- **Autor:** Bruno Teixeira Lopes  
- **Email:** brunoteixlps@gmail.com  
- **LinkedIn:** [linkedin.com/in/brunotlps](https://linkedin.com/in/brunotlps)

---
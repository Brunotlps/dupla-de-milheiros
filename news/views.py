from django.shortcuts import render
import requests
from django.conf import settings


def get_news(request):
    print(f"Chave: {settings.NEWSAPI_KEY}")
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": "milhas OR finanças",
        "language": "pt",
        "sortBy": "publishedAt",
        "pageSize": 10,
        "apiKey": settings.NEWSAPI_KEY,

    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status() # Mostra o erro caso a resposta for diferente de 200
        data = response.json()
        news = data.get("articles", [])
    except requests.exceptions.RequestException as e:
        print(f"Erro: {e}")
        news = []

    return render(request, 'news.html', {"noticias": news})
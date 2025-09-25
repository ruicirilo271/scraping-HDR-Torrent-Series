from flask import Flask, render_template, request, redirect
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

HDR_SERIES_URL = "https://hdrtorrent.com/series/"

# Função para buscar séries
def buscar_series():
    response = requests.get(HDR_SERIES_URL)
    soup = BeautifulSoup(response.content, "html.parser")

    series = []
    for div in soup.select(".capa-img"):
        try:
            link = div.find("a")["href"]
            img = div.find("img")["src"]
            titulo = div.find("h2").text.strip()
            tipo = div.find("span", class_="box_midia").text.strip()
            qualidade = div.find("span", class_="box_qual").text.strip()
            series.append({
                "link": link,
                "img": img,
                "titulo": titulo,
                "tipo": tipo,
                "qualidade": qualidade
            })
        except Exception:
            continue
    return series

# Função para obter episódios de uma série
def get_episodios(serie_url):
    response = requests.get(serie_url)
    soup = BeautifulSoup(response.content, "html.parser")

    episodios = []
    download_div = soup.find("div", id=lambda x: x and "lista_download" in x)
    if download_div:
        for p_tag in download_div.select("p.text-center"):
            try:
                titulo_ep = p_tag.get_text().split("\n")[0].strip()
                magnet_tag = p_tag.select_one("a.btn-success.botao")
                magnet = magnet_tag["href"] if magnet_tag else "#"
                episodios.append({
                    "titulo": titulo_ep,
                    "magnet": magnet
                })
            except Exception:
                continue
    return episodios

# Rota principal
@app.route("/", methods=["GET"])
def index():
    series = buscar_series()
    return render_template("index.html", series=series)

# Rota detalhes
@app.route("/detalhes")
def detalhes():
    serie_url = request.args.get("url")
    if not serie_url:
        return redirect("/")
    
    episodios = get_episodios(serie_url)
    
    response = requests.get(serie_url)
    soup = BeautifulSoup(response.content, "html.parser")
    titulo_tag = soup.find("h1")
    titulo = titulo_tag.text.strip() if titulo_tag else "Detalhes da Série"
    img_tag = soup.find("img")
    img = img_tag["src"] if img_tag else ""

    return render_template("detalhes.html", titulo=titulo, img=img, episodios=episodios)

if __name__ == "__main__":
    app.run(debug=True)

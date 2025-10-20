from flask import Flask, request, render_template, Response
import requests
import re
import os

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        topic = request.form['topic']
        return Response(download_pdfs(topic), content_type='text/html; charset=utf-8')
    return render_template('index.html')

def download_pdfs(topic):
    json_data = {
        'mode': 'articles',
        'q': topic,
        'size': 12,
        'from': 0,
    }

    response = requests.post('https://cyberleninka.ru/api/search', headers={}, json=json_data)
    search_results = response.json().get('articles', [])
    
    links = [(r['link'], re.sub(r'[\\/*?:"<>|]', '', re.sub(r"<.*?>", '', r['name']))) for r in search_results]

    url = 'https://cyberleninka.ru{}/pdf'
    
    count = 1
    for link in links:
        url_ = url.format(link[0])
        response_ = requests.get(url_)
        
        if response_.status_code == 200:
            filename = f"{link[1]}.pdf"
            with open(os.path.join(DOWNLOAD_FOLDER, filename), 'wb') as f:
                f.write(response_.content)
            yield f'{count}/12: Downloaded: {filename}<br>'
            count += 1
        else:
            yield f'Failed to download: {link[1]}<br>'

    yield 'Download complete.<br>'


if __name__ == '__main__':
    app.run(debug=True)

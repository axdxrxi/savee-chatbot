from flask import Flask, request, jsonify, render_template, send_from_directory
import requests
import os

app = Flask(__name__, template_folder='templates')
app.config['JSON_AS_ASCII'] = False  # Pour bien gérer les accents dans JSON

# Récupération de la clé API Mistral depuis les variables d'environnement
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY")
if not MISTRAL_API_KEY:
    raise ValueError("La clé MISTRAL_API_KEY n'est pas définie dans les variables d'environnement.")

API_URL = "https://api.mistral.ai/v1/chat/completions"

def query_mistral(prompt):
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    json_data = {
        "model": "mistral-instruct-beta-v0.1",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 512,
        "temperature": 0.2
    }

    try:
        response = requests.post(API_URL, headers=headers, json=json_data)
        response.raise_for_status()
        response_json = response.json()
        # Extraction de la réponse textuelle
        answer = response_json["choices"][0]["message"]["content"]
        return answer, None
    except requests.exceptions.RequestException as e:
        return None, str(e)
    except (KeyError, IndexError):
        return None, "Réponse inattendue de l'API"

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    prompt = data.get('message', '')
    response, error = query_mistral(prompt)
    if error:
        return jsonify({'response': f"Erreur IA : {error}"})
    return jsonify({'response': response or "Pas de réponse."})

@app.route('/style.css')
def serve_css():
    return send_from_directory('static', 'style.css')

@app.route('/chat.js')
def serve_js():
    return send_from_directory('static', 'chat.js')

@app.route('/')
def index():
    return render_template('chat.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

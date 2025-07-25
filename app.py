import os
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

def query_ollama(prompt):
    import subprocess
    import json
    try:
        result = subprocess.run(
            ['ollama', 'run', 'llama3', '--quiet', prompt],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            return None, f"Erreur Ollama: {result.stderr.strip()}"
        # Ollama ne renvoie pas de JSON, on récupère stdout brut
        return result.stdout.strip(), None
    except Exception as e:
        return None, str(e)

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    prompt = data.get('message', '')
    response, error = query_ollama(prompt)
    if error:
        return jsonify({'response': f"Erreur IA, veuillez réessayer. Détails: {error}"})
    return jsonify({'response': response or "Pas de réponse."})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

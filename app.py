from flask import Flask, request, jsonify, render_template, send_from_directory
import subprocess
import os

app = Flask(__name__, template_folder='templates')
app.config['JSON_AS_ASCII'] = False  # Pour bien gérer les accents dans JSON

def query_ollama(prompt):
    try:
        result = subprocess.run(
            ['ollama', 'run', 'llama3'],
            input=prompt,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        if result.returncode != 0:
            return None, f"Erreur Ollama: {result.stderr.strip()}"
        response_text = result.stdout.strip()
        return response_text, None
    except Exception as e:
        return None, str(e)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    prompt = data.get('message', '')
    response, error = query_ollama(prompt)
    if error:
        return jsonify({'response': f"Erreur IA, veuillez réessayer. Détails: {error}"})
    return jsonify({'response': response or "Pas de réponse."})

@app.route('/style.css')
def serve_css():
    return send_from_directory('.', 'style.css')

@app.route('/')
def index():
    return render_template('chat.html')

if __name__ == '__main__':
    app.run(debug=True)

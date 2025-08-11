from flask import Flask, request, jsonify, render_template
import requests
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['JSON_AS_ASCII'] = False

# ==== Remplace par ta clé OpenRouter (sk-or-...) ====
MISTRAL_API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {MISTRAL_API_KEY}",
    "Content-Type": "application/json",
    "X-Title": "assistant-savee"
}

def query_openrouter(prompt):
    try:
        payload = {
            "model": "mistralai/mistral-small",
            "messages": [
                {"role": "system", "content": "Tu es un assistant qui aide les employés à comprendre les données de consommation d'électricité et de gaz dans l'application Savee."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }

        resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=30)

        if resp.status_code != 200:
            # essayer d'extraire un message d'erreur significatif
            try:
                err = resp.json()
                err_msg = err.get("detail") or err.get("error") or str(err)
            except Exception:
                err_msg = resp.text
            return None, f"OpenRouter {resp.status_code}: {err_msg}"

        data = resp.json()

        # parsing robuste
        text = None
        choices = data.get("choices") or []
        if choices:
            first = choices[0]
            msg = first.get("message")
            if isinstance(msg, dict):
                content = msg.get("content")
                if isinstance(content, str):
                    text = content
                elif isinstance(content, dict):
                    text = content.get("text")
                elif isinstance(content, list):
                    parts = []
                    for p in content:
                        if isinstance(p, str):
                            parts.append(p)
                        elif isinstance(p, dict):
                            parts.append(p.get("text", ""))
                    text = "".join(parts).strip()
            if not text:
                text = first.get("text") or first.get("message", {}).get("content")

        if not text:
            text = data.get("completion") or data.get("text") or str(data)

        return text, None

    except Exception as e:
        return None, str(e)


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    prompt = data.get('message', '').strip()
    if not prompt:
        return jsonify({'response': "Veuillez fournir un message."})

    text, err = query_openrouter(prompt)
    if err:
        # on renvoie systématiquement JSON {response: ...}
        return jsonify({'response': f"Erreur IA : {err}"})
    return jsonify({'response': text or "Pas de réponse."})


@app.route('/')
def index():
    return render_template('chat.html')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

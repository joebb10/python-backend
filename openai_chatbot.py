from flask import Flask, request
import openai
import os

openai.api_key = ''  # Add your OpenAI Key

app = Flask(__name__)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()

    try:
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant. Give it short answers'},
                {'role': 'user', 'content': data['prompt']},
            ]
        )
        return {
            'status': 1,
            'response': response['choices'][0]['message']['content']
        }
    except:
        return {
            'status': 0,
            'response': ''
        }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 6000)) # Use port if it's there, or set default port to 5000
    app.run(host='0.0.0.0', port=port, debug=True)

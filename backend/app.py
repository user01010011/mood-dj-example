from flask import Flask, request, jsonify
from flask_cors import CORS
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
import yaml
import json

def load_prompts(file_path):
    with open(file_path, "r") as file:
        prompts = yaml.safe_load(file)
    return prompts

prompts = load_prompts("../mood_dj.prompt.yml")
system_prompt = prompts['messages'][0]['content']
user_prompt_template = prompts['messages'][1]['content']

endpoint = "https://models.github.ai/inference"
model = "openai/gpt-4.1"
token = "XXXXXXXXXXXXXXXXX"
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/", methods=["GET"])
def home():
    return "Backend is running!"

@app.route("/playlist", methods=["POST"])
def get_playlist():
    data = request.get_json()
    mood = data.get("mood", "neutral")

    try:
        playlist = get_music_from_mood(mood)
        return jsonify({"mood": mood, "playlist": playlist})
    except Exception as e:
        return jsonify({"error": "Failed to fetch playlist", "details": str(e)}), 400

def get_music_from_mood(mood):
    client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token))

    response = client.complete(
        messages=[
            SystemMessage(content=system_prompt),
            UserMessage(content=user_prompt_template.replace("{{mood}}", mood))
        ],
        temperature=1.0,
        top_p=1.0,
        model=model
    )

    song_json = response.choices[0].message.content.strip("```json").strip("```")
    return json.loads(song_json)

if __name__ == "__main__":
    app.run(port=3001, debug=True)
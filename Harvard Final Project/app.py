from flask import Flask, request, jsonify, render_template
from rag_model import get_response, routing_agent
from flask_cors import CORS
import pandas as pd
from dotenv import load_dotenv
load_dotenv(dotenv_path='.env') 


app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing, required for frontend-backend communication


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/rag-model', methods=['POST'])
def rag_model():
    data = request.get_json()
    query = data.get('query', '')
    model = data.get('model', '')
    print(model)

    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    if model == "gpt-4o-mini":
        import openai
        from langchain_openai import ChatOpenAI   
        llm = ChatOpenAI(model="gpt-4o-mini",
                        temperature=0)
        print("Loaded OpenAI's gpt-4o-mini model.")

    elif model == "open-mixtral-8x7b":
        from langchain_mistralai import ChatMistralAI
        llm = ChatMistralAI(model='open-mixtral-8x7b', 
                            temperature=0)
        print("Loaded Mistral AI's open-mixtral-8x7b model.")

    else:
        return jsonify({"error": "Model can't be loaded"}), 400

    try:
        # Call your RAG model to generate a response and return the document
        response, market = get_response(query, llm)
        data = pd.read_csv(f"data/{market}.csv")
        table_html = data.to_html(classes='table table-bordered table-striped table-hover', index=False)
        return jsonify({'response': response, 'table': table_html}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)  # Run Flask app in debug mode for development

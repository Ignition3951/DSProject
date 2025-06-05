from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os,json,getpass
from langchain.chat_models import init_chat_model
from src.app.schema.schema import Person
from src.app.service.prompt_service import prompt_template
from langchain_mistralai import ChatMistralAI
from src.app.schema.message_schema import MessageJson
from src.app.service.message_prompt import system_message,json_structure
from langchain_core.prompts import ChatPromptTemplate
from kafka import KafkaProducer

load_dotenv()

# api_key = os.getenv("MISTRAL_API_KEY")

app = Flask(__name__)

@app.route('/api/data', methods=['GET'])
def get_data():
    if not os.environ.get("MISTRAL_API_KEY"):
        os.environ["MISTRAL_API_KEY"] = getpass.getpass("Enter API key for Mistral AI: ")
    llm = init_chat_model("mistral-large-latest", model_provider="mistralai")
    structured_llm = llm.with_structured_output(schema=Person)
    text = "Alan Smith is 6 feet tall and has blond hair."
    prompt = prompt_template.invoke({"text": text})
    data = structured_llm.invoke(prompt).__dict__
    json_data = json.dumps(data, indent=2)
    return json_data

@app.route('/api/v1/messages', methods=['POST'])
def post_message_data():
    body = request.get_json()
    message = str(body.get("message", ""))
    if not os.environ.get("MISTRAL_API_KEY"):
        os.environ["MISTRAL_API_KEY"] = getpass.getpass("Enter API key for Mistral AI: ")
    llm = ChatMistralAI(
        model="mistral-large-latest",
        temperature=0.1,
        api_key=os.environ.get("MISTRAL_API_KEY")
    )
    structured_llm = llm.with_structured_output(schema=MessageJson,method="json_mode")
    system_prompt = system_message.format(json_structure=json_structure)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )
    few_shot_structured_llm = prompt | structured_llm
    input_prompt = f"raw texts: {message}"
    data = few_shot_structured_llm.invoke({"input": input_prompt}).__dict__
    response_data = json.dumps(data, indent=2)
    producer = KafkaProducer(
        bootstrap_servers=['192.168.1.47:9092'],  # Replace with your Kafka broker(s)
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    producer.send('expense_topic', value=response_data)
    return response_data

if __name__ == '__main__':
    app.run(debug=True)

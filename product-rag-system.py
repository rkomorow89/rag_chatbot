# Benötigte Bibliotheken
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
import cohere

# Langchain Imports
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers.string import StrOutputParser
from langchain_core.runnables.passthrough import RunnablePassthrough
from langchain_community.vectorstores import FAISS
from langchain_cohere import CohereEmbeddings
from langchain_cohere import ChatCohere

# Lade Umgebungsvariablen
load_dotenv()

api_key = os.getenv("COHERE_API_KEY")
if api_key is None:
    raise ValueError("API key not found. Please set the COHERE_API_KEY environment variable.")

# Flask App initialisieren
app = Flask(__name__)

# Konfiguration
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
EMBEDDING_MODEL = "embed-multilingual-v2.0"
LLM_MODEL = "command-r-plus"

# Initialisierung des Embedding-Modells
embeddings = CohereEmbeddings(
    model=EMBEDDING_MODEL,
    cohere_api_key=api_key,
    user_agent="rag_chatbot"
)

chat_model = ChatCohere(
    cohere_api_key=COHERE_API_KEY,
    model=LLM_MODEL,
    temperature=0.3
)

# Lade den FAISS Index als LangChain VectorStore
def load_vectorstore(index_dir="indexes"):
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        index_dir = os.path.join(current_dir, index_dir)
        
        # Überprüfe ob Verzeichnis existiert
        if not os.path.exists(index_dir):
            print(f"Verzeichnis nicht gefunden: {index_dir}")
            return None
            
        # Überprüfe ob Index-Dateien existieren
        index_file = os.path.join(index_dir, "index.faiss")  # Geändert zu index.faiss
        pkl_file = os.path.join(index_dir, "index.pkl")
        
        if not os.path.exists(index_file) or not os.path.exists(pkl_file):
            print(f"Index-Dateien nicht gefunden in: {index_dir}")
        
        # Lade den bestehenden FAISS Index
        vectorstore = FAISS.load_local(
            folder_path=index_dir,
            embeddings=embeddings,
            allow_dangerous_deserialization=True
        )
        
        print(f"VectorStore erfolgreich geladen mit {vectorstore.index.ntotal} Dokumenten")
        return vectorstore
    except Exception as e:
        print(f"Fehler beim Laden des VectorStore: {str(e)}")
        print(f"Aktuelles Verzeichnis: {current_dir}")
        print(f"Index Verzeichnis: {index_dir}")
        return None

# Definiere das Retrieval QA System
def setup_retrieval_qa_chain():
    # Lade den VectorStore
    vectorstore = load_vectorstore()
    if not vectorstore:
        raise Exception("VectorStore konnte nicht geladen werden")
    
    # Definiere das Prompt mit freundlichem, verkäuferähnlichem Stil
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", """Du bist ein freundlicher und kompetenter Verkäufer im Laden. 
         Beantworte Kundenfragen zu Produkten basierend auf den bereitgestellten Kontextinformationen.
         Klinge dabei natürlich, zuvorkommend und überzeugend, als würdest du persönlich im Geschäft beraten.
         Wenn du unsicher bist oder die Antwort nicht im Kontext findest, sage höflich, dass du es nicht weißt.
         
         Kontext: {context}"""),
        ("human", "{question}")
    ])
    
    # Erstelle die Chain
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    
    retrieval_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | qa_prompt
        | chat_model
        | StrOutputParser()
    )
    
    return retrieval_chain

# Initialisiere die Chain beim Start
retrieval_qa_chain = None  # Will be initialized after app startup

# Flask Route für die Startseite
@app.route('/')
def index():
    return render_template('index.html')

# Flask Route für Anfragen
@app.route('/query', methods=['POST'])
def query():
    try:
        data = request.json
        query_text = data.get('query', '')
        
        if not query_text:
            return jsonify({"error": "Keine Suchanfrage angegeben"}), 400
        
        # Prüfe, ob Chain initialisiert ist
        global retrieval_qa_chain
        if retrieval_qa_chain is None:
            retrieval_qa_chain = setup_retrieval_qa_chain()
        
        # Führe die Retrieval Chain aus
        answer = retrieval_qa_chain.invoke(query_text)
        
        return jsonify({
            "answer": answer,
            "context": []
        })
        
    except Exception as e:
        print(f"Fehler bei der Anfrage: {str(e)}")
        return jsonify({
            "error": f"Fehler bei der Verarbeitung: {str(e)}"
        }), 500

# Hauptfunktion
if __name__ == '__main__':
    print("Starting RAG Chatbot with custom Cohere embeddings...")
    app.run(debug=True, host='0.0.0.0', port=5000)

#Fragen:
#Welche Damenparfums habt ihr im Angebot?
#Gibt es Produkte von der Marke „4711“ oder „109f“?
#Gibt es das „Cologne Fragrance“ in anderen Größen?
#Wie viel kostet das „womens v-neck short dress - yellow“ aktuell?
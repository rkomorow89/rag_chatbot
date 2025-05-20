import os
from pymongo import MongoClient
from dotenv import load_dotenv
from langchain.schema import Document
#from langchain.vectorstores import FAISS
from langchain_community.vectorstores import FAISS
from langchain_cohere import CohereEmbeddings

# Lade Umgebungsvariablen
load_dotenv()

# Konfiguration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
DB_NAME = os.getenv("DB_NAME", "produktdatenbank")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "produkte")


def connect_to_mongodb():
    try:
        client = MongoClient(MONGODB_URI)
        db = client[DB_NAME]
        return db[COLLECTION_NAME]
    except Exception as e:
        print(f"❌ MongoDB-Verbindungsfehler: {e}")
        return None


def process_xml_products(collection):
    """Extrahiere Texte und Metadaten aus MongoDB-Dokumenten"""
    texts = []
    metadata_list = []

    print("\n🔍 Suche nach Produkten in MongoDB:")
    try:
        cursor = collection.find({})
        count = collection.count_documents({})
        print(f"   - {count} Dokumente gefunden")

        for doc in cursor:
            try:
                product_info = []
                metadata = {}

                for key, value in doc.items():
                    if key not in ["_id", "created_at", "source_type"]:
                        if isinstance(value, str) and value.strip():
                            product_info.append(f"{key}: {value}")
                        metadata[key] = value

                if product_info:
                    text = ". ".join(product_info)
                    texts.append(text)
                    metadata_list.append(metadata)
            except Exception as e:
                print(f"   - Fehler bei Dokument: {e}")
                continue

        print(f"   - {len(texts)} Produkte erfolgreich verarbeitet")
        return texts, metadata_list

    except Exception as e:
        print(f"❌ Fehler bei der Verarbeitung: {e}")
        return [], []


def create_faiss_index_from_mongodb():
    """Erzeuge LangChain-kompatiblen FAISS-Index aus MongoDB-Produktdaten"""
    try:
        collection = connect_to_mongodb()
        if collection is None:
            raise Exception("MongoDB-Verbindung konnte nicht hergestellt werden")

        texts, metadata_list = process_xml_products(collection)
        if not texts:
            raise Exception("Keine Produkte gefunden")

        # Initialisiere Embedding-Modell
        embedding_model = CohereEmbeddings(
            model="embed-multilingual-v2.0",
            cohere_api_key=COHERE_API_KEY
        )

        # Erzeuge LangChain Document-Objekte
        documents = [
            Document(page_content=text, metadata=meta)
            for text, meta in zip(texts, metadata_list)
        ]

        print(f"\n📦 Erzeuge FAISS Index mit {len(documents)} Dokumenten...")
        vectorstore = FAISS.from_documents(documents, embedding=embedding_model)

        # Speichere FAISS Index lokal
        vectorstore.save_local("indexes")
        print("✅ FAISS Index gespeichert unter: indexes/")
        return True

    except Exception as e:
        print(f"\n❌ Fehler beim Erstellen des Index: {e}")
        return False


if __name__ == "__main__":
    print("\n📊 FAISS Index Creator (LangChain-kompatibel)")
    print("=============================================")
    result = create_faiss_index_from_mongodb()
    if not result:
        print("❌ Index-Erstellung fehlgeschlagen")

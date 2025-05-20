import pandas as pd
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Lade Umgebungsvariablen
load_dotenv()

# Konfigurationsvariablen
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "produktdatenbank")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "produkte")  # Separate Collection für Rohdaten

def connect_to_mongodb():
    """Establish MongoDB Atlas connection"""
    try:
        # Atlas connection settings
        client = MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=5000,
            retryWrites=True,
            w='majority'
        )
        # Test the connection
        client.server_info()
        
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        print("\n🔌 MongoDB Atlas Verbindung:")
        print(f"   - Status: Verbunden")
        print(f"   - Datenbank: {DB_NAME}")
        print(f"   - Collection: {COLLECTION_NAME}")
        print("   - Cluster: MongoDB Atlas")
        
        return collection
    except Exception as e:
        print("\n🔴 MongoDB Atlas Verbindungsfehler:")
        print(f"   - Error: {str(e)}")
        print("\n💡 Troubleshooting:")
        print("   1. Überprüfe die Internetverbindung")
        print("   2. Stelle sicher, dass die IP-Adresse in MongoDB Atlas freigegeben ist")
        print("   3. Überprüfe Username und Passwort")
        return None

def process_csv_data(df):
    """Process CSV data by taking values as-is"""
    products = []
    
    for _, row in df.iterrows():
        # Direkte Übernahme der Zeile als Dictionary und entferne leere Strings
        product = {
            k: str(v).strip() 
            for k, v in row.to_dict().items() 
            if pd.notna(v) and str(v).strip()  # Nur nicht-leere Werte übernehmen
        }
        
        if product:  # Nur hinzufügen wenn Produkt nicht leer ist
            products.append(product)
    
    return products

def import_csv_to_mongodb(file_path, limit_rows=None):
    """
    Import CSV data to MongoDB
    
    Args:
        file_path (str): Path to CSV file
        limit_rows (int, optional): Limit number of rows to import. None imports all rows.
    """
    try:
        # MongoDB Verbindung herstellen
        client = MongoClient(MONGODB_URI)
        db = client[DB_NAME]
        
        # Bestehende Collection komplett löschen und warten
        if COLLECTION_NAME in db.list_collection_names():
            print("\n🗑️ Lösche bestehende Collection...")
            db.drop_collection(COLLECTION_NAME)
        
        # Neue Collection erstellen
        collection = db[COLLECTION_NAME]
        
        # CSV-Datei laden und verarbeiten
        print("\n📥 Lade CSV-Datei...")
        df = pd.read_csv(
            file_path,
            encoding='utf-8',
            escapechar='\\',
            quotechar='"',
            quoting=1,
            doublequote=True,
            nrows=limit_rows  # Limit number of rows to read
        )
        
        if limit_rows:
            print(f"   - Begrenze Import auf {limit_rows} Zeilen")
            
        products = process_csv_data(df)
        
        if not products:
            return False, "Keine Daten zum Importieren gefunden"
        
        # In MongoDB speichern
        print(f"\n💾 Importiere {len(products)} Produkte...")
        result = collection.insert_many(products)
        
        return True, f"{len(products)} Produkte erfolgreich importiert"
        
    except Exception as e:
        error_msg = f"Fehler beim CSV-Import: {str(e)}"
        print(error_msg)
        return False, error_msg

def print_import_result(success, message):
    """Print formatted import result"""
    if success:
        print("\n✅ Import erfolgreich:")
        print(f"   {message}")
    else:
        print("\n❌ Import fehlgeschlagen:")
        print(f"   {message}")

if __name__ == "__main__":
    # Beispiel CSV-Datei
    sample_file = "datasets/Message Group - Product.csv"
    
    print("\n📊 CSV Importer")
    print("================")
    
    if not os.path.exists(sample_file):
        print(f"\n❌ Beispieldatei nicht gefunden: {sample_file}")
        print("   Bitte stelle sicher, dass die Datei im 'datasets' Ordner liegt.")
        exit(1)
    
    print(f"\n📁 Verarbeite: {sample_file}")
    
    # Import ausführen (mit Begrenzung auf 10 Zeilen)
    success, message = import_csv_to_mongodb(sample_file, limit_rows=10)
    print_import_result(success, message)
    
    if success:
        # MongoDB Verbindung für Statusanzeige
        collection = connect_to_mongodb()
        if collection is not None:  # Changed from if collection
            count = collection.count_documents({})
            print(f"\n📈 Status:")
            print(f"   - Gesamt Dokumente in Collection: {count}")
            print(f"   - Datenbank: {DB_NAME}")
            print(f"   - Collection: {COLLECTION_NAME}")
            print(f"   - MongoDB URI: {MONGODB_URI}")
# README: Produkt-RAG-System mit MongoDB und Cohere

Dieses System ermöglicht es, Produktdaten aus einer CSV-Datei in eine MongoDB zu importieren und über ein RAG (Retrieval-Augmented Generation) System mit einem Cohere LLM abzufragen.

## Voraussetzungen

Python 3.8+ und folgende Bibliotheken werden benötigt (in der requirements.txt enthalten):

```bash
# Installation der Abhängigkeiten
pip install -r requirements.txt
```

Die requirements.txt enthält:
```
pandas
pymongo==4.6.2
python-dotenv==1.1.0
Flask==3.1.1
cohere==5.15.0
langchain==0.3.25
langchain_core==0.3.60
langchain-community==0.3.24
langchain-cohere==0.4.4
faiss-cpu==1.11.0
```

Außerdem müssen folgende Dienste installiert/verfügbar sein:
- MongoDB Server (lokale Installation oder Cloud-Dienst)
- MongoDB Compass (für die Visualisierung der Daten)
- Cohere API-Zugang (Registrierung unter cohere.com erforderlich)

## Konfiguration

Erstelle eine `.env` Datei im selben Verzeichnis mit folgendem Inhalt:

```
MONGODB_URI=mongodb://localhost:27017
COHERE_API_KEY=dein-api-key-hier
DB_NAME=produktdatenbank
COLLECTION_NAME=produkte
```

Passe die MongoDB-URI und den Cohere API-Key entsprechend an. Die Datenbankname und Collection-Name können optional angepasst werden.

## MongoDB Atlas URI erstellen

Um eine MongoDB Atlas URI für die `.env` Datei zu erstellen, folge diesen Schritten:

1. **Atlas Konto erstellen**:
   - Gehe zu [MongoDB Atlas](https://cloud.mongodb.com)
   - Registriere dich oder melde dich an
   - Erstelle ein neues Projekt (falls nötig)

2. **Cluster erstellen**:
   - Klicke auf "Build a Database"
   - Wähle die kostenlose M0-Option ("Shared" Cluster)
   - Wähle einen Cloud-Provider und eine Region
   - Klicke auf "Create"

3. **Netzwerkzugriff einrichten**:
   - Gehe zu "Network Access" im Menü
   - Klicke auf "Add IP Address"
   - Wähle "Allow Access from Anywhere" (0.0.0.0/0) für Entwicklungszwecke
   - Bestätige mit "Confirm"

4. **Datenbankbenutzer erstellen**:
   - Gehe zu "Database Access"
   - Klicke auf "Add New Database User"
   - Wähle "Password" als Authentifizierungsmethode
   - Vergebe Benutzername und Passwort
   - Wähle "Built-in Role: Atlas admin"
   - Bestätige mit "Add User"

5. **Connection String kopieren**:
   - Gehe zurück zur Cluster-Übersicht
   - Klicke auf "Connect"
   - Wähle "Connect your application"
   - Kopiere den Connection String

6. **URI anpassen**:
   - Ersetze `<username>` mit deinem Benutzernamen
   - Ersetze `<password>` mit deinem Passwort
   - Die fertige URI sollte so aussehen:
     ```
     mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
     ```

7. **In `.env` einfügen**:
   ```
   MONGODB_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```

**Wichtig**: Stelle sicher, dass du deine Zugangsdaten sicher aufbewahrst und nicht im Code versionierst.

## System-Komponenten

Das System besteht aus drei Hauptkomponenten:

1. **CSV Importer** (`csv_importer.py`)
   - Importiert Produktdaten aus CSV-Dateien in MongoDB
   - Bereinigt und strukturiert die Daten
   - Löscht bestehende Collections vor dem Import

2. **Embedding Creator** (`create_embeddings.py`)
   - Generiert Embeddings mit Cohere's multilingual-v2.0 Modell
   - Erstellt LangChain Document-Objekte
   - Speichert FAISS Index für schnelle Ähnlichkeitssuche

3. **RAG System** (`product-rag-system.py`)
   - Flask Web-Interface für Benutzerinteraktion
   - Verwendet LangChain für RAG-Implementierung
   - Nutzt ChatCohere und CohereEmbeddings
   - Implementiert einen freundlichen, verkäuferähnlichen Beratungsstil

## Funktionsweise

Das System besteht aus folgenden Hauptkomponenten:

1. **CSV-Import**: Liest Produktdaten aus einer CSV-Datei und speichert sie in MongoDB
2. **Embedding-Generierung**: Erstellt für jedes Produkt Embeddings mit Cohere's embed-english-v3.0 Modell
3. **Ähnlichkeitssuche**: Findet ähnliche Produkte basierend auf der Benutzeranfrage
4. **RAG-System**: Nutzt Cohere LLM, um Fragen zu beantworten, basierend auf den gefundenen Produkten
5. **Web-Interface**: Stellt eine Benutzeroberfläche zum Hochladen von CSV-Dateien und zum Stellen von Fragen bereit

Das System verwendet folgende Technologien und Prozesse:

1. **Daten-Management**: 
   - MongoDB Atlas für die Cloud-basierte Datenspeicherung
   - Automatische Datensynchronisation und Backup
   - Zugriff über MongoDB Atlas Interface

2. **KI-Komponenten**:
   - Cohere's multilingual-v2.0 für Embedding-Generierung
   - Cohere's command-r-plus für Antwortgenerierung
   - LangChain für RAG-Pipeline-Integration
   - FAISS für effiziente Vektorsuche

3. **Benutzerinteraktion**:
   - Modernes Web-Interface mit Flask
   - Echtzeit-Antworten auf Produktanfragen
   - Nutzerfreundliche Chat-Oberfläche

## FAISS Index

FAISS (Facebook AI Similarity Search) ist eine Bibliothek für effiziente Ähnlichkeitssuche und Clustering von dichten Vektoren. In unserem System wird sie folgendermaßen eingesetzt:

1. **Funktionsweise**:
   - FAISS konvertiert Produktbeschreibungen in hochdimensionale Vektoren
   - Diese Vektoren werden in einem Index gespeichert
   - Bei einer Suchanfrage wird der ähnlichste Vektor gefunden

2. **Index-Struktur**:
   ```
   indexes/
   ├── index.faiss     # Binärer FAISS Index mit Vektoren
   └── index.pkl       # Pickle-Datei mit Index-Metadaten
   ```

3. **Vorteile**:
   - Extrem schnelle Ähnlichkeitssuche (ms-Bereich)
   - Effiziente Speichernutzung
   - Skalierbar für Millionen von Produkten

Der FAISS Index wird automatisch beim Start der Anwendung geladen und für alle Ähnlichkeitssuchen verwendet. Die Metadata-Datei (`index.pkl`) enthält die Zuordnung zwischen den Vektor-IDs im Index und den tatsächlichen Produktdaten.

## Verwendung

1. Starte die Anwendung:
   ```
   python product-rag-system.py
   ```

2. Öffne den Browser und navigiere zu `http://localhost:5000`

3. Stelle Fragen zu den hochgeladenen Produkten

## Dateistruktur

```
rag_chatbot/
├── product-rag-system.py    # Hauptanwendung mit Flask-Server
├── create_embeddings.py     # Skript zur Embedding-Generierung
├── csv_importer.py         # Skript zum Import von CSV-Daten
├── requirements.txt        # Python-Abhängigkeiten
├── .env                   # Konfigurationsdatei (muss erstellt werden)
├── indexes/              # FAISS Indexe und Metadaten
│   ├── index.faiss
│   └── index.pkl
├── templates/            # Flask HTML Templates
│   └── index.html       # Chat-Interface
```

Die wichtigsten Dateien und ihre Funktionen:
- `product-rag-system.py` - Hauptanwendung mit Flask-Server und RAG-Logik
- `create_embeddings.py` - Generiert und speichert Embeddings mit Cohere
- `csv_importer.py` - Importiert und bereinigt CSV-Daten für MongoDB Atlas
- `requirements.txt` - Liste aller benötigten Python-Pakete
- `.env` - Enthält Konfigurationsvariablen (MongoDB URI, API-Keys)

## Anpassungen

- **Datenbank-Struktur**: Die Datenbank heißt standardmäßig "produktdatenbank" und die Collection "produkte". Dies kann in der `.env`-Datei angepasst werden.
- **Embedding-Modell**: Das System verwendet Cohere's "embed-english-v3.0" Modell für die Generierung von Embeddings.
- **Cohere-Modell**: Das System verwendet "command-r-plus" für die Generierung von Antworten. Andere Modelle können durch Änderung des Parameters `model` in der `generate_rag_response`-Funktion ausgewählt werden.

## CSV-Format

Die hochgeladene CSV-Datei sollte folgende Eigenschaften haben:
- Kopfzeile mit Spaltennamen
- Textdaten zu Produkten (Name, Beschreibung, Kategorie usw.)
- UTF-8-Kodierung empfohlen

Beispiel für eine gültige CSV-Struktur:
```
id,name,beschreibung,kategorie,preis
1,"Smartphone XYZ","Hochauflösendes Display mit 120Hz","Elektronik",599.99
2,"Kaffeemaschine Deluxe","Vollautomatisch mit Mahlwerk","Haushaltsgeräte",299.50
```

## Zugriff auf MongoDB Atlas

Die Produktdaten werden ausschließlich in MongoDB Atlas gespeichert und können dort eingesehen werden:

1. **Atlas Zugang**:
   - Melde dich bei [MongoDB Atlas](https://cloud.mongodb.com) an
   - Wähle dein Cluster aus
   - Navigiere zur "Collections"-Ansicht

2. **Daten einsehen**:
   - Wähle die Datenbank "produktdatenbank" aus
   - Öffne die Collection "produkte"
   - Nutze die Atlas-Suchfunktion für Abfragen

3. **Daten analysieren**:
   - Verwende die Atlas Data Explorer Funktionen
   - Nutze die integrierten Analysewerkzeuge
   - Erstelle benutzerdefinierte Abfragen

## Zugriff auf die Daten mit MongoDB Compass

Die hochgeladenen Produktdaten können mit MongoDB Compass, einem grafischen Interface für MongoDB, eingesehen und verwaltet werden:

1. **Installation**: [MongoDB Compass herunterladen und installieren](https://www.mongodb.com/try/download/compass)

2. **Verbindung herstellen**:
   - Starte MongoDB Compass
   - Gib die gleiche MongoDB URI ein, die in der `.env` Datei verwendet wird
   - Klicke auf "Connect"

3. **Daten anzeigen**:
   - Wähle die Datenbank "produktdatenbank" aus (oder den in der .env konfigurierten Namen)
   - Öffne die Collection "produkte"
   - Alle importierten Produktdaten werden angezeigt, einschließlich der generierten Embeddings

4. **Daten abfragen und filtern**:
   - Nutze die Filter-Funktion von MongoDB Compass, um spezifische Produkte zu finden
   - Verwende das "Aggregation"-Tab für komplexere Abfragen

5. **Daten exportieren**:
   - Du kannst die Daten direkt aus MongoDB Compass als JSON oder CSV exportieren
  ```

# Usa l'immagine Python 3.12.8 ufficiale (se disponibile)
FROM python:3.12.8-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    graphviz \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Imposta la directory di lavoro
WORKDIR /app

# Copia i file necessari
COPY requirements.txt ./requirements.txt
COPY home.py ./home.py
COPY pages  ./pages
copy utils.py ./utils.py
copy utils_xml.py ./utils_xml.py


# Installa le dipendenze
RUN pip install --no-cache-dir -r requirements.txt

# Espone la porta utilizzata da Streamlit
EXPOSE 8501

# Comando di default per avviare Streamlit
CMD ["streamlit", "run", "home.py", "--server.port=8501", "--server.enableCORS=false"]

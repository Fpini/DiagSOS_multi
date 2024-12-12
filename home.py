import streamlit as st
from utils import upload_file, process_csv_file
from utils_xml import process_xml_file

st.set_page_config(
    page_title="Home - Analisi Segnalazioni",
    page_icon="📄",
    layout="wide"
)

st.title("Home - Analisi Segnalazioni SOS")

file = upload_file()

if file:
    context_data = process_xml_file(file)
    if context_data is not None:
        st.session_state["context_data"] = context_data
        st.success("File caricato con successo!")
    else:
        st.error("Errore durante l'elaborazione del file.")
else:
    st.warning("Carica un file per iniziare.")

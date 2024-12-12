import streamlit as st
from utils import visualizza_grafo, dati_segnalazione

st.set_page_config(
    page_title="2. Grafo delle Operazioni",
    page_icon="📄",
    layout="wide"
)

st.title("Grafo delle Operazioni")

if "context_data" in st.session_state:
    context_data = st.session_state["context_data"]
    report_data = {"Header_01": dati_segnalazione(context_data)}
    visualizza_grafo(context_data, report_data)
else:
    st.warning("Carica un file nella pagina Home per accedere a questa sezione.")

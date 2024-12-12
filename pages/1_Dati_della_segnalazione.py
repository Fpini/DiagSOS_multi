import streamlit as st
from utils import dati_segnalazione, visualizza_dati_segnalazione

st.set_page_config(
    page_title="1. Dati della Segnalazione",
    page_icon="📄",
    layout="wide"
)

st.title("Dati della Segnalazione")

if "context_data" in st.session_state:
    context_data = st.session_state["context_data"]
    report_data = {"Header_01": dati_segnalazione(context_data)}
    visualizza_dati_segnalazione(context_data, report_data)
else:
    st.warning("Carica un file nella pagina Home per accedere a questa sezione.")

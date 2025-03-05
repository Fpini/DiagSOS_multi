import streamlit as st
from utils import dati_segnalazione, dati_mancanti


st.set_page_config(
    page_title="4. Dati mancanti",
    page_icon="📄",
    layout="wide"
)

st.title("Dati mancanti")

if "context_data" in st.session_state:
    context_data = st.session_state["context_data"]
    report_data = {"Header_01": dati_segnalazione(context_data)}
    dati_mancanti(context_data)
else:
    st.warning("Carica un file nella pagina Home per accedere a questa sezione.")
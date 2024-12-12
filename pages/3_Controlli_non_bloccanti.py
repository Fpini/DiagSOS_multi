import streamlit as st
from utils import diagnostico_segnalazioni, dati_segnalazione

st.set_page_config(
    page_title="3. Controlli non Bloccanti",
    page_icon="📄",
    layout="wide"
)

st.title("Controlli non Bloccanti")

if "context_data" in st.session_state:
    context_data = st.session_state["context_data"]
    report_data = {"Header_01": dati_segnalazione(context_data)}
    diagnostico_segnalazioni(context_data, report_data)
else:
    st.warning("Carica un file nella pagina Home per accedere a questa sezione.")

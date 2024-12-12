import streamlit as st
from utils import upload_file, process_csv_file
from utils_xml import process_xml_file
# based on https://discuss.streamlit.io/t/pip-installing-from-github/21484/5
import subprocess
import sys
import time

st.set_page_config(page_title="Home - Analisi Segnalazioni", page_icon="📄", layout="wide")
try:
    import streamlit_random_generator

# This block executes only on the first run when your package isn't installed
except ModuleNotFoundError as e:
    sleep_time = 30
    dependency_warning = st.warning(
        f"Installing dependencies, this takes {sleep_time} seconds."
    )
    subprocess.Popen(
        [
            f"{sys.executable} -m pip install git+https://${{github_token}}@github.com/sTomerG/streamlit_random_generator.git",
        ],
        shell=True,
    )

    # wait for subprocess to install package before running your actual code below
    time.sleep(sleep_time)
    # remove the installing dependency warning
    dependency_warning.empty()



#st.title("Home - Analisi Segnalazioni SOS")

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

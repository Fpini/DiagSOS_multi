import pandas as pd
import streamlit as st
import hashlib
import networkx as nx
import tempfile
import datetime
import matplotlib.pyplot as plt
from collections import deque
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from io import BytesIO
from reportlab.lib.utils import simpleSplit
from reportlab.lib.colors import Color, black
from mitosheet.streamlit.v1 import spreadsheet



def upload_file():
#    return st.sidebar.file_uploader("Carica un file (CSV/XML)", type=["csv", "xml"])
    return st.sidebar.file_uploader("Carica un file (XML)", type=["xml"])

def save_pdf(buffer, file_name="output.pdf"):
    st.download_button("Scarica il PDF", buffer, file_name=file_name, mime="application/pdf")

@st.cache_data
def process_csv_file(file):
    try:
        context_data = pd.read_csv(file)
        if context_data.empty:
            st.error("Il file caricato è vuoto.")
            return None
        return context_data
    except Exception as e:
        st.error(f"Errore durante la lettura del file: {e}")
        return None

def dati_segnalazione(df):
    # (Definizione della funzione dati_segnalazione)
    segnalazione_df = df[df['Context ID'].str.startswith("SEGNALAZIONE")]
    
    # Verifica se esiste almeno una riga corrispondente
    if segnalazione_df.empty:
        st.write("Nessuna segnalazione trovata.")
        return
    
    # Prendi la prima riga corrispondente
    row = segnalazione_df.iloc[0]
    
    # Estrai e converti i valori con gestione dei valori NaN
    prog_sos = str(int(row['IDSOS_PROG'])) if pd.notna(row['IDSOS_PROG']) else "N/A"
    anno_sos = str(int(row['IDSOS_ANNO'])) if pd.notna(row['IDSOS_ANNO']) else "N/A"
    segn_sos = str(int(row['CODICE_SEGNALANTE_SOS_SEGNALAZIONE'])) if pd.notna(row['CODICE_SEGNALANTE_SOS_SEGNALAZIONE']) else "N/A"
    impo_sos = row['IMPORTO_TOT_OP_SOSP_SOS_SEGNALAZIONE'] if pd.notna(row['IMPORTO_TOT_OP_SOSP_SOS_SEGNALAZIONE']) else "N/A"
    numopo_sos = str(int(row['NUMERO_TOT_OP_SOSP_SOS_SEGNALAZIONE'])) if pd.notna(row['NUMERO_TOT_OP_SOSP_SOS_SEGNALAZIONE']) else "N/A"

    # Visualizza le informazioni di segnalazione
    header_01 = f"Segnalazione n. {prog_sos} anno {anno_sos} da {segn_sos}" 
    st.header(header_01)
#    st.markdown(f"<div style='text-align: center;'>{header_02}</div>", unsafe_allow_html=True)
    return header_01

def visualizza_dati_segnalazione(context_data, report_data):
        context_data = context_data.drop('Unnamed: 0',axis=1)
    # SEGNALAZIONE
        segnalazione_df = context_data[context_data['Context ID'].str.startswith("SEGNALAZIONE")].dropna(axis=1, how="all")
        segnalazione_df['Identifier'] = segnalazione_df['Identifier'].astype(int) 
        segnalazione_df['IDSOS_ANNO'] = segnalazione_df['IDSOS_ANNO'].astype(int) 
        segnalazione_df['IDSOS_PROG'] = segnalazione_df['IDSOS_PROG'].astype(int)
        segnalazione_df['CODICE_SEGNALANTE_SOS_SEGNALAZIONE'] = segnalazione_df['CODICE_SEGNALANTE_SOS_SEGNALAZIONE'].astype(int)  
        segnalazione_df['Identifier'] = segnalazione_df['Identifier'].astype(str) 
        segnalazione_df['IDSOS_ANNO'] = segnalazione_df['IDSOS_ANNO'].astype(str) 
        segnalazione_df['IDSOS_PROG'] = segnalazione_df['IDSOS_PROG'].astype(str)
        segnalazione_df['CODICE_SEGNALANTE_SOS_SEGNALAZIONE'] = segnalazione_df['CODICE_SEGNALANTE_SOS_SEGNALAZIONE'].astype(str)  
        st.write ("SEGNALAZIONE")
        st.write(segnalazione_df)

    # NOTA_01
        nota_01 = context_data[context_data['Context ID'].str.startswith("NOTA_01")].dropna(axis=1, how="all")
        st.write ("NOTA_01")
        st.write(nota_01['TESTO_NOTA_SOS_NOTA'])

    # NOTA_02
        nota_02 = context_data[context_data['Context ID'].str.startswith("NOTA_02")].dropna(axis=1, how="all")
        st.write ("NOTA_02")
        st.write(nota_02['TESTO_NOTA_SOS_NOTA'])

    # OPERAZIONI
        operazioni = context_data[context_data['Context ID'].str.startswith("OPERAZIONE")].dropna(axis=1, how="all")
        st.write ("OPERAZIONI n. " + str(operazioni.shape[0]))
        if 'DATA_CONT_OPERAZ_SOS_OPERAZIONE' in operazioni.columns:
            operazioni['DATA_CONT_OPERAZ_SOS_OPERAZIONE'] = operazioni['DATA_CONT_OPERAZ_SOS_OPERAZIONE'].fillna(0).astype(int).astype(str)
        if 'COMUNE_ESEC_SOS_OPERAZIONE' in operazioni.columns:
            operazioni['COMUNE_ESEC_SOS_OPERAZIONE'] = operazioni['COMUNE_ESEC_SOS_OPERAZIONE'].fillna(0).astype(int).astype(str) 
        if 'DATA_CONT_PRIMA_C_SOS_OPERAZIONE' in operazioni.columns:
            operazioni['DATA_CONT_PRIMA_C_SOS_OPERAZIONE'] = operazioni['DATA_CONT_PRIMA_C_SOS_OPERAZIONE'].fillna(0).astype(int).astype(str)
        if 'DATA_CONT_ULTIMA_C_SOS_OPERAZIONE' in operazioni.columns:
            operazioni['DATA_CONT_ULTIMA_C_SOS_OPERAZIONE'] = operazioni['DATA_CONT_ULTIMA_C_SOS_OPERAZIONE'].fillna(0).astype(int).astype(str) 
        operazioni = operazioni.drop(columns=['Identifier', 'Period Instant'])
        #operazioni= spreadsheet(operazioni)
        st.write(operazioni)
        st.write ("OPERAZIONI + TIPO OPERAZIONE")
        st.bar_chart(operazioni, x='PROG_OPERAZIONE', y='IMPORTO_OPERAZ_SOS_OPERAZIONE', color='TIPO_OPERAZIONE_SOS_OPERAZIONE')

    # SOGGETTI
        soggetti = context_data[context_data['Context ID'].str.startswith("SOGGETTO")].dropna(axis=1, how="all")
        st.write ("SOGGETTI n. " + str(soggetti.shape[0]))
        soggetti = soggetti.drop(columns=['Identifier', 'Period Instant'])
        soggetti = soggetti.fillna({
            "NUMERO_REA_SOS_SOGGETTO": 0,
            "NPF_PARTITAIVA_SOS_SOGGETTO": 0,
            "NPF_SEDELEG_IND_CAP_SOS_SOGGETTO": 0,
            "NPF_SEDELEG_IND_COMUNE_SOS_SOGGETTO": 0,
            "CODICE_ATECO_SOS_SOGGETTO": 0,
            "PF_DATANASCITA_SOS_SOGGETTO": 0
        })
        if 'NUMERO_REA_SOS_SOGGETTO' in soggetti.columns:
            soggetti['NUMERO_REA_SOS_SOGGETTO'] = soggetti['NUMERO_REA_SOS_SOGGETTO'].astype(int).astype(str) 
        if 'NPF_PARTITAIVA_SOS_SOGGETTO' in soggetti.columns:
            soggetti['NPF_PARTITAIVA_SOS_SOGGETTO'] = soggetti['NPF_PARTITAIVA_SOS_SOGGETTO'].astype(int).astype(str)     
            soggetti['NPF_SEDELEG_IND_CAP_SOS_SOGGETTO'] = soggetti['NPF_SEDELEG_IND_CAP_SOS_SOGGETTO'].astype(int).astype(str) 
            soggetti['NPF_SEDELEG_IND_COMUNE_SOS_SOGGETTO'] = soggetti['NPF_SEDELEG_IND_COMUNE_SOS_SOGGETTO'].astype(int).astype(str) 
        if 'CODICE_ATECO_SOS_SOGGETTO' in soggetti.columns:
            soggetti['CODICE_ATECO_SOS_SOGGETTO'] = soggetti['CODICE_ATECO_SOS_SOGGETTO'].astype(int).astype(str) 
        if 'PF_DATANASCITA_SOS_SOGGETTO' in soggetti.columns:
            soggetti['PF_DATANASCITA_SOS_SOGGETTO'] = soggetti['PF_DATANASCITA_SOS_SOGGETTO'].astype(int).astype(str) 
        soggetti = soggetti.dropna(axis=1, how='all')
        st.write(soggetti)

    # RAPPORTI
        rapporti = context_data[context_data['Context ID'].str.startswith("RAPPORTO")].dropna(axis=1, how="all")
        st.write ("RAPPORTI n. " + str(rapporti.shape[0]))
        rapporti = rapporti.drop(columns=['Identifier', 'Period Instant'])
        rapporti = rapporti.fillna({
            "NUMERO_RAPPORTO_SOS_RAPPORTO": 0, 
            "DATA_ACCENSIONE_SOS_RAPPORTO": 0, 
            "FILIALE_SOS_RAPPORTO": 0 }) 
        if 'NUMERO_RAPPORTO_SOS_RAPPORTO' in rapporti.columns:
            rapporti['NUMERO_RAPPORTO_SOS_RAPPORTO'] = rapporti['NUMERO_RAPPORTO_SOS_RAPPORTO'].astype(int).astype(str) 
            rapporti['DATA_ACCENSIONE_SOS_RAPPORTO'] = rapporti['DATA_ACCENSIONE_SOS_RAPPORTO'].astype(int).astype(str) 
            rapporti['FILIALE_SOS_RAPPORTO'] = rapporti['FILIALE_SOS_RAPPORTO'].astype(int).astype(str) 
        rapporti = rapporti.dropna(axis=1, how='all')
        st.write(rapporti)

        # LEGAMI OPERAZIONI - RAPPORTI
        ope_rap = context_data[context_data['Context ID'].str.startswith("LEGAME_OPERAZIONE_RAPPORTO")].dropna(axis=1, how="all")
        st.write ("LEGAMI OPERAZIONI - RAPPORTI n. " + str(ope_rap.shape[0]))
        ope_rap = ope_rap.drop(columns=['Identifier', 'Period Instant'])
        ope_rap = ope_rap.dropna(axis=1, how='all')
        st.write(ope_rap)


        # LEGAMI OPERAZIONI - SOGGETTI
        ope_sogg = context_data[context_data['Context ID'].str.startswith("LEGAME_OPERAZIONE__SOGGETTO")].dropna(axis=1, how="all")
        st.write ("LEGAMI OPERAZIONI - SOGGETTI n. " + str(ope_sogg.shape[0]))
        ope_sogg = ope_sogg.drop(columns=['Identifier', 'Period Instant'])
        ope_sogg = ope_sogg.dropna(axis=1, how='all')
        st.write(ope_sogg)
        result = operazioni.merge(ope_sogg, how="inner", on="PROG_OPERAZIONE")
        st.write ("LEGAMI OPERAZIONE - SOGGETTI stacked per TIPO LEGAME")    
        #st.bar_chart(result, x='PROG_OPERAZIONE', y='IMPORTO_OPERAZ_SOS_OPERAZIONE', color='TIPO_LEGAME_OPER_SOGG', stack= True)
        grouped_result = (
            result.groupby(["PROG_OPERAZIONE", "TIPO_LEGAME_OPER_SOGG"])
                .agg(count=("TIPO_LEGAME_OPER_SOGG", "size"))
                .reset_index()
        )
        st.bar_chart(grouped_result, x='PROG_OPERAZIONE', y='count', color='TIPO_LEGAME_OPER_SOGG', stack= True)

        # LEGAMI RAPPORTI - SOGGETTI
        rap_sogg = context_data[context_data['Context ID'].str.startswith("LEGAME_RAPPORTO_SOGGETTO")].dropna(axis=1, how="all")
        st.write ("LEGAMI RAPPORTI - SOGGETTI n. " + str(rap_sogg.shape[0]))
        rap_sogg = rap_sogg.drop(columns=['Identifier', 'Period Instant'])
        rap_sogg = rap_sogg.dropna(axis=1, how='all')
        st.write(rap_sogg)



def visualizza_grafo(context_data, report_data):
    # (Definizione della funzione visualizza_grafo)
        cripta_dati = st.sidebar.checkbox("Visualizza dati criptati")
        soggetti = context_data[context_data['Context ID'].str.startswith("SOGGETTO")]
        oper_sogg = context_data[context_data['Context ID'].str.startswith("LEGAME_OPERAZIONE__SOGGETTO")]
        operazioni = context_data[context_data['Context ID'].str.startswith("OPERAZIONE")]
        segnalazione = context_data[context_data['Context ID'].str.startswith("SEGNALAZIONE")]

        operazioni['BIN'] = pd.qcut(operazioni['IMPORTO_OPERAZ_SOS_OPERAZIONE'], q=5, labels=["1", "2", "3", "4", "5"])
        G = crea_grafo(soggetti, oper_sogg, operazioni, cripta_dati)

        #st.subheader("Visualizzazione del Grafo")
        fig, ax = plt.subplots(figsize=(12, 8))
        pos = nx.nx_pydot.pydot_layout(G, prog="sfdp")
        nx.draw_networkx_nodes(G, pos, node_size=700, node_color="lightblue", ax=ax)
        spessori = [G[u][v].get('peso', 1) for u, v in G.edges()]
        nx.draw_networkx_edges(G, pos, edgelist=G.edges(), edge_color="gray", width=spessori, ax=ax)
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight="bold", ax=ax)
        plt.axis("off")
        st.pyplot(fig)

        pdf_buffer = salva_grafo_pdf(G, titolo(segnalazione.iloc[0]))
        st.download_button("Scarica il PDF del Grafo", data=pdf_buffer, file_name="grafo_output.pdf", mime="application/pdf")


def salva_grafo_pdf(grafo, titolo):
    from pydot import Dot
    P = nx.nx_pydot.to_pydot(grafo)
    P.set("label", titolo)
    P.set("labelloc", "top")
    P.set("fontsize", "20")
    P.set("fontcolor", "blue")

    # Scrivi il PDF in un file temporaneo e poi caricalo in memoria
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
        temp_filename = tmpfile.name
        P.write_pdf(temp_filename)
    
    with open(temp_filename, "rb") as pdf_file:
        pdf_buffer = pdf_file.read()
    
    return pdf_buffer


def diagnostico_segnalazioni(context_data, report_data):
    # (Definizione della funzione diagnostico_segnalazioni)
        if is_sublist(lst_campi_segn, context_data.columns):
            with st.expander(TEST_HEADER, expanded=True):
                        # Struttura dati per il report
                report_data = {
                    "Header_01": dati_segnalazione(context_data),
                    "Titolo del report": "Diagnostico segnalazioni",
                    "data": datetime.datetime.now().strftime("%Y-%m-%d"),
                    "controlli": []
                }
                test_cases = [
                    {
                        "nome": "Presenza soggetto PF collegato a soggetto NPF cliente del segnalante",
                        "desc": '''
                            Per i SOGGETTI NPF, se il campo “Posizione contrattuale rispetto al segnalante” 
                            è valorizzato con uno dei seguenti:
                            - 003 - Cliente recente (da meno di un anno)
                            - 004 - Cliente sperimentato (da 1 a 5 anni)
                            - 005 - Cliente consolidato (da più di 5 anni)
                            allora deve essere presente un altro SOGGETTO PF collegato al SOGGETTO NPF
                        ''',
                        "test_func": esegui_test_01,
                        "categoria": "soggetto",
                        "tipo": "SOGG"
                    },
                    {
                        "nome": "Uguaglianza tra codice fiscale ditta individuale e codice fiscale del Titolare",
                        "desc": '''
                            Se un SOGGETTO NPF ha “Specie giuridica” = “0015 - Ditta individuale”
                            ed è collegato con legame “024 - Titolare ditta individuale” a un SOGGETTO PF,
                            allora i due soggetti devono avere lo stesso codice fiscale.
                        ''',
                        "test_func": esegui_test_02,
                        "categoria": "soggetto",
                        "tipo": "SOGG"
                    },
                    {
                        "nome": "Presenza esecutore e controparte per bonifici, cambi contraenza e ...",
                        "desc": '''
                            Se “Stato operazione” = ESEGUITA e la Tipologia della operazione è una delle seguenti:
                            - 26 - Bonifico in partenza - 48 - Bonifico in arrivo 
                            - 10 - Emissione assegni circolari e titoli similari, vaglia 
                            - AA - Bonifico estero - AM - Bonifico nazionale per cassa 
                            - AE - Bonifico estero per cassa 
                            - R081 - Cambio di contraenza polizze assicurative ramo vita 
                            - R082 - Variazione del beneficiario polizze assicurative ramo vita 
                            Allora devono essere presenti almeno due soggetti collegati alla operazione:
                            a.	- un soggetto con legame “001 - soggetto che ha eseguito la operazione in proprio”  
                            oppure “002 - soggetto che ha eseguito la operazione per conto terzi” 
                            b.	- un soggetto con legame “004 - Controparte”  ''',
                        "test_func": esegui_test_03,
                        "categoria": "operazione",
                        "tipo": "OPE"
                    },
                    {
                        "nome": "Presenza rapporti e valorizzazione coordinate bancarie",
                        "desc": '''
                            Se “Stato operazione” = ESEGUITA e la Tipologia dell’operazione è una delle seguenti: 
                            - 26 - Bonifico in partenza - 48 - Bonifico in arrivo - AA - Bonifico estero 
                            - AF - Disposizione di trasferimento stesso intermediario  
                            allora devono essere presenti due rapporti collegati all’operazione 
                            con legame “001 - Movimentazione rapporto gestito dal segnalante” 
                            oppure “002 - movimentazione rapporto gestito dall’intermediario diverso dal segnalante”. 
                            Inoltre, i rapporti di tipo diverso da “061 - Amministrazione fiduciaria dei beni”, 
                            “050 - Polizza assicurativa” oppure “051 - Polizza vita”, dovranno avere valorizzati: 
                            - IBAN, se con legame operazione - rapporto di tipo 001;  
                            - IBAN oppure ABICAB oppure BIC, se con legame operazione - rapporto di tipo 002.''',
                        "test_func": esegui_test_04,
                        "categoria": "operazione",
                        "tipo": "OPE"
                    },
                    {
                        "nome": "Presenza legami tra rapporti e soggetti per causali 26, 48, AA e AF",
                        "desc": '''
                            Se “Stato operazione” = ESEGUITA e la Tipologia dell’operazione è una delle seguenti:
                            - 26 - Bonifico in partenza - 48 - Bonifico in arrivo - AA - Bonifico estero 
                            - AF - Disposizione di trasferimento stesso intermediario 
                            Allora per ognuna delle entità rapporto richieste, 
                            deve essere presente almeno un soggetto con uno dei seguenti legami: 
                                - 001 - Intestatario - 002 - Delegato a operare - 003 - Rappresentante legale dell’intestatario 
                                - 004 - Titolare effettivo - 005 - Esecutore delegato ad operare occasionalmente 
                                - 010 - Fiduciante - 011 - Beneficiario (polizze assicurative) 
                                - 012 - Contraente (polizze assicurative) - 013 - Assicurato (polizze assicurative)
                            .''',
                        "test_func": esegui_test_05,
                        "categoria": "operazione",
                        "tipo": "OPE"
                    },
                ]

                for test_case in test_cases:
                    st.subheader(test_case["nome"])
                    st.write(test_case["desc"])
                    esiti_test, esiti_cod_ent, esito_out = test_case["test_func"](context_data)
                    gestione_esiti(esito_out, esiti_cod_ent, esiti_test, test_case["categoria"])
                    create_and_add_controllo(
                        report_data, 
                        test_case["nome"], 
                        test_case["desc"], 
                        esiti_test, 
                        esiti_cod_ent, 
                        esito_out, 
                        test_case["tipo"]
                    )



                pdf_buffer = generate_pdf(report_data)
                save_pdf(pdf_buffer, file_name="diagnostico.pdf")

# Funzioni specifiche per la pagina "Visualizzazione del Grafo"
def titolo(row):
    prog_sos = str(int(row['IDSOS_PROG'])) 
    anno_sos = str(int(row['IDSOS_ANNO'])) 
    segn_sos = str(int(row['CODICE_SEGNALANTE_SOS_SEGNALAZIONE']))
    testo = f"Segnalazione n. {prog_sos} del {anno_sos} da {segn_sos}"
    return testo 

def cripta(stringa):
    hash_object = hashlib.sha256(stringa.encode())
    return hash_object.hexdigest()

def nominativo(row):
    if row['NATURA_GIURIDICA_SOS_SOGGETTO'] == 'NPF':
        return row['NPF_DENOMINAZIONE_SOS_SOGGETTO']
    else:
        return row['PF_NOME_SOS_SOGGETTO'] + ' ' + row['PF_COGNOME_SOS_SOGGETTO']

def crea_grafo(soggetti, oper_sogg, operazioni, cripta_dati):
    G = nx.DiGraph()
    for _, row in soggetti.iterrows():
        nome = nominativo(row)
        if cripta_dati:
            nome = cripta(nome)
        nome = nome[:10]
        G.add_node(nome)
        oper_sogg_ord = oper_sogg[
            (oper_sogg['PROG_SOGGETTO'] == row['PROG_SOGGETTO']) &
            (oper_sogg['TIPO_LEGAME_OPER_SOGG'].isin([1, 2, 3]))
        ]
        for _, row in oper_sogg_ord.iterrows():
            prog_oper = row['PROG_OPERAZIONE']
            oper_sogg_ben = oper_sogg[
                (oper_sogg['PROG_OPERAZIONE'] == prog_oper) &
                (oper_sogg['TIPO_LEGAME_OPER_SOGG'].isin([4]))
            ]
            if oper_sogg_ben.empty:
                G.add_edge(nome, nome, peso=1)
            else:
                for _, row in oper_sogg_ben.iterrows():
                    prog_sog = row['PROG_SOGGETTO']
                    beneficiario = soggetti[soggetti['PROG_SOGGETTO'] == prog_sog]
                    if not beneficiario.empty:
                        dest = nominativo(beneficiario.iloc[0])
                        if cripta_dati:
                            dest = cripta(dest)
                        dest = dest[:10]
                        importo = operazioni[operazioni['PROG_OPERAZIONE'] == prog_oper]['BIN']
                        G.add_edge(nome, dest, peso=int(importo))
    return G

lst_campi_segn = [
    'IDSOS_ANNO', 'IDSOS_PROG', 'IDSOS_MOD_INOLTRO', 
    'CODICE_SEGNALANTE_SOS_SEGNALAZIONE', 'TIPO_SOS_SOS_SEGNALAZIONE', 
    'CATEGORIA_SOS_SOS_SEGNALAZIONE', 'ORIGINE_SOS_SOS_SEGNALAZIONE', 
    'RICHIESTA_SOSP_SOS_SEGNALAZIONE', 'RISCHIO_SOS_SEGNALAZIONE', 
    'IMPORTO_TOT_OP_SOSP_SOS_SEGNALAZIONE', 'NUMERO_TOT_OP_SOSP_SOS_SEGNALAZIONE'
]

def is_sublist(sublist, main_list):
    sublist_deque = deque(sublist)
    for i in range(len(main_list) - len(sublist) + 1):
        if deque(main_list[i:i + len(sublist)]) == sublist_deque:
            return True
    return False

# Costanti
APP_TITLE = "Analisi Segnalazioni SOS"
TEST_HEADER = "Risultati dei Test Effettuati su Controlli non bloccanti"
APP_TITLE = "Diagnostico segnalazioni UIF SOS"
ERROR_UPLOAD_MSG = "Errore upload file!"
PDF_FILENAME = "report_controlli.pdf"

# Funzione per creare cerchi colorati
def colored_circle(color):
    return f'<span style="color:{color};">⬤</span>'

# Funzione per scrivere messaggi con icone
# Funzione per creare cerchi colorati
def colored_circle(color):
    return f'<span style="color:{color};">⬤</span>'

# Funzione per formattare l'esito
def format_esito(esito, categoria, numero, color="magenta"):
    icon = colored_circle("green") if esito else colored_circle(color)
    return f"{icon} {categoria} n. {numero}"

def esegui_test_01(df):
    esito_out = None
    esiti_test = []
    esiti_cod_sogg = []
    df1 = df[df['Context ID'].str.startswith("SOGGETTO")]
    df1_NPF = df1[(df1['NATURA_GIURIDICA_SOS_SOGGETTO'] == 'NPF') & (df1['POS_COMMERCIALE_SOS_SOGGETTO'].isin([3, 4, 5]))]
    for _, row in df1_NPF.iterrows():
        cod_sogg_NPF = row['PROG_SOGGETTO']
        df2 = df[df['Context ID'].str.startswith("LEGAME_SOGGETTO_SOGGETTO")]
        if not df2.empty:
            df2_NPF_PF = df2[(df2['PROG_SOGG_PRIM'] == row['PROG_SOGGETTO']) | (df2['PROG_SOGG_SEC'] == row['PROG_SOGGETTO'])]
            if df2_NPF_PF.empty:
                esiti_test.append(False)
                esiti_cod_sogg.append(str(int(cod_sogg_NPF)))
            else:
                for _, row in df2_NPF_PF.iterrows():
                    df3_PF = df1[df1['NATURA_GIURIDICA_SOS_SOGGETTO'] == 'PF']
                    if  df3_PF.empty:
                        esiti_test.append(False)
                        esiti_cod_sogg.append(str(int(cod_sogg_NPF)))
                    else:
                        if not esito_out == True:
                            esiti_test.append(True)
                            esiti_cod_sogg.append(str(int(cod_sogg_NPF)))
                            esito_out = True
        else:
            esiti_test.append(False)
            esiti_cod_sogg.append(str(int(cod_sogg_NPF)))
    return esiti_test, esiti_cod_sogg, esito_out

def esegui_test_02(df):
    esito_out = None
    esiti_test = []
    esiti_cod_sogg = []
    df1 = df[df['Context ID'].str.startswith("SOGGETTO")]
    df1_NPF = df1[(df1['NATURA_GIURIDICA_SOS_SOGGETTO'] == 'NPF')]
    for _, row in df1_NPF.iterrows():
        if 'NPF_SPECIEGIUR_SOS_SOGGETTO' in df1_NPF.columns:
            if row['NPF_SPECIEGIUR_SOS_SOGGETTO'] == 15:
                cod_sogg_NPF = row['PROG_SOGGETTO']
                df2 = df[df['Context ID'].str.startswith("LEGAME_SOGGETTO_SOGGETTO")]
                df2_NPF_PF = df2[
                    (
                        (df2['PROG_SOGG_PRIM'] == row['PROG_SOGGETTO']) 
                        | (df2['PROG_SOGG_SEC'] == row['PROG_SOGGETTO'])
                    )
                    & (df2['TIPO_LEGAME_SOGG_SOGG'] == 24)
                ]
                if not df2_NPF_PF.empty:
                    if not esito_out == True:
                        esiti_test.append(True)
                        esiti_cod_sogg.append(str(int(cod_sogg_NPF)))
                        esito_out = True
                else:
                    esiti_test.append(False)
                    esiti_cod_sogg.append(str(int(cod_sogg_NPF)))
                    esito_out = False
    if esito_out == None:
        esiti_test.append(True)
        esiti_cod_sogg.append(999)    
    return esiti_test, esiti_cod_sogg, esito_out

def esegui_test_03(df):
    esito_out = None
    esiti_test = []
    esiti_cod_sogg = []
    
    # Filtra operazioni che soddisfano determinate condizioni
    df1 = df[df['Context ID'].str.startswith("OPERAZIONE")]
    if df1['TIPO_OPERAZIONE_SOS_OPERAZIONE'].dtype == "float64":
        df1['TIPO_OPERAZIONE_SOS_OPERAZIONE'] = df1['TIPO_OPERAZIONE_SOS_OPERAZIONE'].astype(int)  
        df1['TIPO_OPERAZIONE_SOS_OPERAZIONE'] = df1['TIPO_OPERAZIONE_SOS_OPERAZIONE'].astype(str)
    df1_OPE = df1[
        (df1['STATO_OPERAZ_SOS_OPERAZIONE'] == 'SI') &
        (df1['TIPO_OPERAZIONE_SOS_OPERAZIONE'].isin([
            '26', '48', '10', 'AA', 'AM', 'AE', 'R081', 'R082'
        ]))
    ]
    print('df1_OPE: ', df1_OPE.shape)
    # Test non eseguibile per assenza di operazioni in ambito
    if df1_OPE.empty:
        esito_out = None
        esiti_test.append(True)
        esiti_cod_sogg.append(999)  # Corretto esiti_cod_ent -> esiti_cod_sogg
    else:
        # Verifica presenza soggetto controparte legato all'operazione
        for _, row in df1_OPE.iterrows():
            cod_ope = (int(row['PROG_OPERAZIONE']))
            df2_OPE_SOGG = df[
                (df['Context ID'].str.startswith("LEGAME_OPERAZIONE__SOGGETTO")) &
                (df['PROG_OPERAZIONE'] == cod_ope) & 
                (df['TIPO_LEGAME_OPER_SOGG'] == 4)
            ]
            # Errore su operazione cod_ope per assenza legame tra operazione e soggetto controparte
            if df2_OPE_SOGG.empty:
                esiti_test.append(False)
                esiti_cod_sogg.append(cod_ope)
                esito_out = False
                print(f"Errore operazione {cod_ope}: assenza legame tra operazione e soggetto controparte")
            else:
                # Verifica presenza legame tra operazione e soggetto che ha eseguito l'operazione in proprio
                df2_OPE_SOGG = df[
                    (df['Context ID'].str.startswith("LEGAME_OPERAZIONE__SOGGETTO")) &
                    (df['PROG_OPERAZIONE'] == cod_ope) & 
                    (df['TIPO_LEGAME_OPER_SOGG'] == 1)
                ]
                
                if df2_OPE_SOGG.empty:
                    # Verifica presenza legame tra operazione e soggetto che ha eseguito l'operazione per conto terzi
                    df2_OPE_SOGG = df[
                        (df['Context ID'].str.startswith("LEGAME_OPERAZIONE__SOGGETTO")) &
                        (df['PROG_OPERAZIONE'] == cod_ope) & 
                        (df['TIPO_LEGAME_OPER_SOGG'] == 2)
                    ]
                    
                    if df2_OPE_SOGG.empty:
                        # Errore su operazione cod_ope per assenza legame tra operazione e soggetto esecutore
                        esiti_test.append(False)
                        esiti_cod_sogg.append(cod_ope)
                        esito_out = False
                        print("Errore: assenza legame tra operazione e soggetto esecutore")
                    else:
                        # Test OK per operazione cod_ope per presenza legame tra operazione e soggetto esecutore per conto terzi
                        esiti_test.append(True)
                        esiti_cod_sogg.append(cod_ope)
                        esito_out = True
                else:
                    # Test OK per operazione cod_ope per presenza legame tra operazione e soggetto esecutore in conto proprio
                    esiti_test.append(True)
                    esiti_cod_sogg.append(cod_ope)
                    esito_out = True
    return esiti_test, esiti_cod_sogg, esito_out

def esegui_test_04(df):
    esito_out = None
    esiti_test = []
    esiti_cod_ent = []  
    # Filtra operazioni che soddisfano determinate condizioni
    df1 = df[df['Context ID'].str.startswith("OPERAZIONE")]
    if df1['TIPO_OPERAZIONE_SOS_OPERAZIONE'].dtype == "float64":
        df1['TIPO_OPERAZIONE_SOS_OPERAZIONE'] = df1['TIPO_OPERAZIONE_SOS_OPERAZIONE'].astype(int)  
        df1['TIPO_OPERAZIONE_SOS_OPERAZIONE'] = df1['TIPO_OPERAZIONE_SOS_OPERAZIONE'].astype(str)
    df1_OPE = df1[
        (df1['STATO_OPERAZ_SOS_OPERAZIONE'] == 'SI') &
        (df1['TIPO_OPERAZIONE_SOS_OPERAZIONE'].isin([
            '26', '48', 'AA', 'AF'
        ]))
    ]  
    # Test non eseguibile per assenza di operazioni in ambito
    if df1_OPE.empty:
        esito_out = None
        esiti_test.append(True)
        esiti_cod_ent.append(999)  # Corretto esiti_cod_ent -> esiti_cod_sogg
    else:
        for _, row in df1_OPE.iterrows():
            cod_ope = (int(row['PROG_OPERAZIONE']))
            df2_OPE_RAPP = df[
                (df['Context ID'].str.startswith("LEGAME_OPERAZIONE_RAPPORTO")) &
                (df['PROG_OPERAZIONE'] == cod_ope) & 
                (df['TIPO_LEGAME_OPER_RAPP_SOS_LEGAME_OPER_RAPP'].isin([1, 2]))]        
            if df2_OPE_RAPP.shape[0] < 2:
                print("df2_OPE_RAPP ", df2_OPE_RAPP.shape[0])
                esito_out = False
                esiti_test.append(False)
                esiti_cod_ent.append(row['PROG_OPERAZIONE'])  
            else:
                for _, row in df2_OPE_RAPP.iterrows():
                    print(row)
                    prog_rapp = int(row['PROG_RAPPORTO'])
                    leg_ope_rapp = row['TIPO_LEGAME_OPER_RAPP_SOS_LEGAME_OPER_RAPP']
                    df3_RAPP = df[
                        (df['Context ID'].str.startswith("RAPPORTO")) &
                        (df['PROG_RAPPORTO'] == prog_rapp) &
                        (~df['CAT_RAPPORTO_SOS_RAPPORTO'].isin([61, 50, 51]))
                    ]
                    if not df3_RAPP.empty:
                        for _, row in df3_RAPP.iterrows():
                            if leg_ope_rapp == 1:
                                iban_col = 'IBAN_SOS_RAPPORTO' 
                                if iban_col in df3_RAPP.columns:
                                    if pd.isnull(df3_RAPP[iban_col].all()):
                                        esito_out = False
                                        esiti_test.append(False)
                                        esiti_cod_ent.append(str(cod_ope) + ' - rapporto n. ' + str(prog_rapp) + ' - legame 001')
                                    else:
                                        esito_out = True
                                        esiti_test.append(True)
                                        esiti_cod_ent.append(str(cod_ope) + ' - rapporto n.' + str(prog_rapp) + ' - legame 001')
                            else:
                                bic_col = 'BIC_SOS_RAPPORTO'
                                abicab_col = 'FILIALE_SOS_RAPPORTO'
                                if (
                                    (bic_col in df3_RAPP.columns and pd.isnull(df3_RAPP[bic_col]).all()) or
                                    (bic_col not in df3_RAPP.columns)
                                ):
                                    if (
                                    (abicab_col in df3_RAPP.columns and pd.isnull(df3_RAPP[abicab_col]).all()) or
                                    (abicab_col not in df3_RAPP.columns)
                                ):
                                        esito_out = False
                                        esiti_test.append(False)
                                        esiti_cod_ent.append(str(cod_ope) + ' - rapporto n.' + str(prog_rapp) + ' - legame 002')
                                    else:
                                        esito_out = True
                                        esiti_test.append(True)
                                        esiti_cod_ent.append(str(cod_ope) + ' - rapporto n.' + str(prog_rapp) + ' - legame 002')
                                else:
                                        esito_out = True
                                        esiti_test.append(True)
                                        esiti_cod_ent.append(str(cod_ope) + ' - rapporto n.' + str(prog_rapp) + ' - legame 002')
    return esiti_test, esiti_cod_ent, esito_out

def esegui_test_05(df):
    esito_out = None
    esiti_test = []
    esiti_cod_ent = []  
    # Filtra operazioni che soddisfano determinate condizioni
    df1 = df[df['Context ID'].str.startswith("OPERAZIONE")]
    if df1['TIPO_OPERAZIONE_SOS_OPERAZIONE'].dtype == "float64":
        df1['TIPO_OPERAZIONE_SOS_OPERAZIONE'] = df1['TIPO_OPERAZIONE_SOS_OPERAZIONE'].astype(int)  
        df1['TIPO_OPERAZIONE_SOS_OPERAZIONE'] = df1['TIPO_OPERAZIONE_SOS_OPERAZIONE'].astype(str)
    df1_OPE = df1[
        (df1['STATO_OPERAZ_SOS_OPERAZIONE'] == 'SI') &
        (df1['TIPO_OPERAZIONE_SOS_OPERAZIONE'].isin([
            '26', '48', 'AA', 'AF'
        ]))
    ]  
    # Test non eseguibile per assenza di operazioni in ambito
    if df1_OPE.empty:
        esito_out = None
        esiti_test.append(True)
        esiti_cod_ent.append(999)  # Corretto esiti_cod_ent -> esiti_cod_sogg
    else:
        for _, row in df1_OPE.iterrows():
            cod_ope = (int(row['PROG_OPERAZIONE']))
            df2_OPE_RAPP = df[
                (df['Context ID'].str.startswith("LEGAME_OPERAZIONE_RAPPORTO")) &
                (df['PROG_OPERAZIONE'] == cod_ope)
                ]                 
            for _, row in df2_OPE_RAPP.iterrows():
                    prog_rapp = int(row['PROG_RAPPORTO'])
                    leg_ope_rapp = row['TIPO_LEGAME_OPER_RAPP_SOS_LEGAME_OPER_RAPP']
                    df3_RAPP_SOGG = df[
                        (df['Context ID'].str.startswith("LEGAME_RAPPORTO_SOGGETTO")) &
                        (df['PROG_RAPPORTO'] == prog_rapp) &
                        (df['TIPO_LEGAME_RAPP_SOGG_SOS_LEGAME_RAPP_SOGG'].isin([1, 2, 3, 4, 5, 10, 11, 12, 13]))
                    ]
                    if df3_RAPP_SOGG.empty:
                        esito_out = False
                        esiti_test.append(False)
                        esiti_cod_ent.append(str(cod_ope) + ' - rapporto n.' + str(prog_rapp) + ' - legame ' + leg_rapp_sogg)
                    else:
                        for _, row in df3_RAPP_SOGG.iterrows():
                            if 'TIPO_LEGAME_RAPP_SOGG_SOS_LEGAME_RAPP_SOGG' in df3_RAPP_SOGG.columns:
                                leg_rapp_sogg = str(int(row['TIPO_LEGAME_RAPP_SOGG_SOS_LEGAME_RAPP_SOGG']))
                            else:
                                leg_rapp_sogg = ''
                            esito_out = True
                            esiti_test.append(True)
                            esiti_cod_ent.append(str(cod_ope) + ' - rapporto n.' + str(prog_rapp) + ' - legame ' + leg_rapp_sogg)

    return esiti_test, esiti_cod_ent, esito_out                            

# Funzione per la gestione degli esiti
def gestione_esiti(esito_out, esiti_ent, esiti_test, categoria):
    if esito_out is None:
        icon_2 = colored_circle("orange")
        testo_out = f"**Esito:** {icon_2} Test non eseguito per casistica non riscontrata"
        st.markdown(testo_out, unsafe_allow_html=True)
    else:
        for i, esito in enumerate(esiti_test):
            formatted_esito = format_esito(esito, categoria, esiti_ent[i])
            st.markdown(f"**Esito:** {formatted_esito}", unsafe_allow_html=True)

# Unified function to create and optionally add a control to report_data
def create_and_add_controllo(report_data, nome, descrizione, esiti, ent, esito_out, cat, append_to_report=True):
    # Calculate statistics for the footer based on `esiti`
    if esito_out is not None:
        numero_controlli_eseguiti = len(esiti)
        numero_controlli_positivi = sum(1 for esito in esiti if esito is True)
        numero_controlli_negativi = sum(1 for esito in esiti if esito is False)
        numero_controlli_non_applicabili = numero_controlli_eseguiti - numero_controlli_positivi - numero_controlli_negativi
    else:
        numero_controlli_eseguiti = 0
        numero_controlli_positivi = 0
        numero_controlli_negativi = 0
        numero_controlli_non_applicabili = 0

    # Build the control structure
    controllo = {
        "testata": {
            "nome": nome,
            "descrizione": descrizione,
            "data_e_ora_esecuzione": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        "corpo": [
            {"esiti": esiti_controllo(esiti, ent, esito_out, cat)}
        ],
        "coda": {
            "numero_controlli_eseguiti": numero_controlli_eseguiti,
            "numero_controlli_positivi": numero_controlli_positivi,
            "numero_controlli_negativi": numero_controlli_negativi,
            "numero_controlli_non_applicabili": numero_controlli_non_applicabili
        }
    }
    
    # Append the control to the report if specified
    if append_to_report:
        report_data["controlli"].append(controllo)  
    return controllo

# Define the esiti_controllo function
def esiti_controllo(esiti, ent, esito_out, cat):
    esiti_rep = []
    if esito_out is None:
        esiti_rep.append("Esito: 🟡 Test non eseguito per casistica non riscontrata")
    else:
        for esito, entity in zip(esiti, ent):
            if esito:
                esiti_rep.append(f"Esito: 🟢 OK per {cat} n. {entity}")
            else:
                esiti_rep.append(f"Esito: 🔴 KO per {cat} n. {entity}")
    return esiti_rep

def generate_pdf(data):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 50
    line_height = 14
    max_line_width = width - 2 * margin  # Maximum width for each line within margins

    # Define colors
    green = Color(0, 1, 0)  # Define green color
    red = Color(1, 0, 0)    # Define red color
    blu = Color(0, 0, 1)    # Define blue color

    # Function to split text into multiple lines to fit within max_line_width
    def split_text_to_lines(text, pdf, max_width):
        return simpleSplit(text, pdf._fontname, pdf._fontsize, max_width)

    # Function to handle new page creation and apply color when needed
    def draw_text(pdf, text, x, y, color=black):
        pdf.setFillColor(color) 
        pdf.drawString(x, y, text)
        return y - line_height

    # Function to draw the header on each page
    def draw_header(pdf):
        header_y = height - margin  # Starting y position for the header
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(margin, header_y, f"{data['Header_01']}")
        
        # Move down for the next line
        pdf.setFont("Helvetica", 12)
        pdf.drawString(margin, header_y - line_height, f"{data['Titolo del report']}")
        
        # Move down again for the next line
        pdf.drawString(margin, header_y - 2 * line_height, f"Data di generazione: {data['data']}")
        
        # Draw a horizontal line under the header
        pdf.line(margin, header_y - 3 * line_height, width - margin, header_y - 3 * line_height)

    # Draw the initial header
    draw_header(pdf)
    y = height - margin - 4 * line_height  # Adjust starting y position for content
    pdf.setFont("Helvetica", 10)
    
    # Control Section
    for controllo in data["controlli"]:
        # Header for each control
        pdf.setFont("Helvetica-Bold", 12)
        y = draw_text(pdf, f"{controllo['testata']['nome']}", margin, y)
        
        # Multi-line handling for Descrizione
        pdf.setFont("Helvetica", 10)
        descrizione_lines = split_text_to_lines(controllo['testata']['descrizione'], pdf, max_line_width)
        for line in descrizione_lines:
            y = draw_text(pdf, line, margin, y)
            if y <= margin:  # Check if the page is full
                pdf.showPage()
                draw_header(pdf)
                y = height - margin - 4 * line_height

        # Date and time of execution
        y = draw_text(pdf, f"Data e ora di esecuzione: {controllo['testata']['data_e_ora_esecuzione']}", margin, y)
        
        # Body with each result in "esiti"
        for item in controllo["corpo"][0]["esiti"]:
            esiti_lines = split_text_to_lines(item, pdf, max_line_width)
            for esiti_line in esiti_lines:
                color = green if "OK" in esiti_line else red if "KO" in esiti_line else blu
                y = draw_text(pdf, f"- {esiti_line}", margin + 20, y, color=color)
                if y <= margin:
                    pdf.showPage()
                    draw_header(pdf)
                    y = height - margin - 4 * line_height

        # Footer for each control
        pdf.setFont("Helvetica-Bold", 10)
        y = draw_text(pdf, f"Numero controlli eseguiti: {controllo['coda']['numero_controlli_eseguiti']}", margin, y)
        y = draw_text(pdf, f"Numero controlli positivi: {controllo['coda']['numero_controlli_positivi']}", margin, y)
        y = draw_text(pdf, f"Numero controlli negativi: {controllo['coda']['numero_controlli_negativi']}", margin, y)
        y = draw_text(pdf, f"Numero controlli non applicabili: {controllo['coda']['numero_controlli_non_applicabili']}", margin, y)
        
        # Add space between controls
        y -= 2 * line_height
        if y <= margin:
            pdf.showPage()
            draw_header(pdf)
            y = height - margin - 4 * line_height

    # Report Footer
    y -= 2 * line_height
    if y <= margin:
        pdf.showPage()
        draw_header(pdf)
        y = height - margin - 4 * line_height
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(margin, y, "Fine del Rapporto")

    # Finalize and save the PDF
    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer


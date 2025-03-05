import xml.etree.ElementTree as ET
import pandas as pd
import streamlit as st

def check_and_add_namespace(root, namespace_dict):
    # Verifica che tutti i prefissi richiesti siano presenti, in particolare xbrldi
    if 'xbrldi' not in namespace_dict:
        namespace_dict['xbrldi'] = 'http://xbrl.org/2006/xbrldi'

def extract_context_data(root, namespaces):
    context_data = []
    for context in root.findall(".//xbrli:context", namespaces):
        context_id = context.attrib.get("id", "N/A")
        context_info = {"Context ID": context_id}

        identifier = context.find("xbrli:entity/xbrli:identifier", namespaces)
        period_instant = context.find("xbrli:period/xbrli:instant", namespaces)
        context_info["Identifier"] = identifier.text if identifier is not None else "N/A"
        context_info["Period Instant"] = period_instant.text if period_instant is not None else "N/A"

        scenario = context.find("xbrli:scenario", namespaces)
        if scenario is not None:
            for member in scenario.findall("xbrldi:typedMember", namespaces):
                dimension = member.attrib.get("dimension", "N/A").split(':')[-1]
                value = member.find(".//*").text if member.find(".//*") is not None else "N/A"
                context_info[dimension] = value
            
            # Estrai dati da explicitMember come richiesto
            for explicit in scenario.findall("xbrldi:explicitMember", namespaces):
                dimension = explicit.attrib.get("dimension", "N/A").split(':')[-1]
                value = explicit.text.split("_")[-1] if explicit.text else "N/A"
                context_info[dimension] = value

        context_data.append(context_info)
    return context_data

def extend_with_context_ref_data(root, context_data, namespaces):
    context_dict = {item["Context ID"]: item for item in context_data}
    for element in root.findall(".//p-common:*", namespaces) + root.findall(".//p-SOS:*", namespaces):
        context_ref = element.attrib.get("contextRef", "N/A")
        tag_name = element.tag.split('}')[-1]
        value = element.text if element.text is not None else "N/A"
        if context_ref in context_dict:
            context_dict[context_ref][tag_name] = value
    return list(context_dict.values())

@st.cache_data
def process_xml_file(file):
    try:
        # Carica e analizza il file XML
        tree = ET.parse(file)

        root = tree.getroot()

        # Definisci i namespace, inclusi eventuali prefissi mancanti
        namespaces = {
            'xbrli': 'http://www.xbrl.org/2003/instance',
            'p-SOS': 'http://www.bancaditalia.it/uif/xbrlTaxonomy/p-SOS',
            'p-common': 'http://www.bancaditalia.it/uif/common',
        }
        check_and_add_namespace(root, namespaces)
        # Estrai i dati dei context-id
        context_data = extract_context_data(root, namespaces)
        extended_data = extend_with_context_ref_data(root, context_data, namespaces)

        # Trasforma i dati in un dataframe
        df = pd.DataFrame(extended_data)
        df.to_csv('temp.csv')
        df = pd.read_csv('temp.csv')
        return df
    except Exception as e:
        st.error(f"Errore durante la lettura del file: {e}")
        return None

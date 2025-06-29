
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

st.set_page_config(page_title="Piano Ammortamento v4", layout="centered")
st.title("📊 Piano di Ammortamento – Web App")

os.makedirs("piani_salvati", exist_ok=True)
os.makedirs("ricevute", exist_ok=True)

scelta = st.radio("Cosa vuoi fare?", ["📁 Carica piano esistente", "🆕 Crea nuovo piano"])

def calcola_piano(importo, rate, tasso_annuo, frequenza, data_inizio):
    tasso_periodico = tasso_annuo / 100 / (12 / frequenza)
    quota = importo * (tasso_periodico * (1 + tasso_periodico) ** rate) / ((1 + tasso_periodico) ** rate - 1)
    scadenze = []
    capitale_residuo = importo
    for i in range(1, rate + 1):
        interesse = round(capitale_residuo * tasso_periodico, 2)
        capitale = round(quota - interesse, 2)
        data_scadenza = data_inizio + timedelta(days=(i - 1) * 30 * (frequenza / 1))
        scadenze.append({
            "Rata N°": i,
            "Data Scadenza": data_scadenza.date(),
            "Quota Capitale": capitale,
            "Quota Interessi": interesse,
            "Rata Totale": round(capitale + interesse, 2),
            "Pagato": False,
            "Data Pagamento": "",
            "Ricevuta File": ""
        })
        capitale_residuo -= capitale
    return pd.DataFrame(scadenze)

if scelta == "🆕 Crea nuovo piano":
    st.subheader("🆕 Creazione Nuovo Piano")

    nome_piano = st.text_input("Nome file piano (es. cliente1.xlsx)")
    importo = st.number_input("Importo totale €", min_value=0.0, value=10000.0, step=100.0)
    rate = st.number_input("Numero di rate", min_value=1, max_value=100, value=12)
    tasso = st.number_input("Tasso interesse annuo (%)", min_value=0.0, value=5.0)
    frequenza = st.selectbox("Frequenza rata", [1, 2, 3, 6, 12], format_func=lambda x: f"Ogni {x} mese(i)")
    data_inizio = st.date_input("Data prima rata", value=datetime.today())

    if st.button("📅 Genera Piano"):
        df = calcola_piano(importo, rate, tasso, frequenza, datetime.combine(data_inizio, datetime.min.time()))
        if nome_piano:
            path = f"piani_salvati/{nome_piano if nome_piano.endswith('.xlsx') else nome_piano + '.xlsx'}"
            df.to_excel(path, index=False)
            st.success(f"Piano creato e salvato come: {path}")
        else:
            st.error("Inserisci un nome file valido.")

elif scelta == "📁 Carica piano esistente":
    file_list = [f for f in os.listdir("piani_salvati") if f.endswith(".xlsx")]
    if not file_list:
        st.warning("Nessun piano salvato disponibile.")
    else:
        piano_selezionato = st.selectbox("Seleziona un piano:", file_list)
        df = pd.read_excel(f"piani_salvati/{piano_selezionato}")

        st.subheader(f"📄 Piano: {piano_selezionato}")
        for i in range(len(df)):
            with st.expander(f"Rata {df.loc[i, 'Rata N°']} – {df.loc[i, 'Data Scadenza']}"):
                df.at[i, "Pagato"] = st.checkbox("Pagato", value=bool(df.loc[i, "Pagato"]), key=f"pagato_{i}")
                if df.at[i, "Pagato"]:
                    df.at[i, "Data Pagamento"] = st.date_input("Data Pagamento", value=pd.to_datetime(df.loc[i, "Data Pagamento"]) if pd.notna(df.loc[i, "Data Pagamento"]) else datetime.today(), key=f"data_{i}")
                ricevuta = st.file_uploader("Carica ricevuta (PDF, JPG, PNG)", type=["pdf", "jpg", "png"], key=f"ricevuta_{i}")
                if ricevuta:
                    filename = f"ricevute/{piano_selezionato}_rata_{i+1}.{ricevuta.name.split('.')[-1]}"
                    with open(filename, "wb") as f:
                        f.write(ricevuta.read())
                    df.at[i, "Ricevuta File"] = filename

        if st.button("💾 Salva modifiche"):
            df.to_excel(f"piani_salvati/{piano_selezionato}", index=False)
            st.success("Modifiche salvate con successo!")

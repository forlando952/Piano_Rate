
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from fpdf import FPDF
import os

st.set_page_config(page_title="Piano Ammortamento", layout="wide")
st.title("📅 Crea un Piano di Ammortamento")

def calcola_piano(importo, rate, tasso_annuo, frequenza, data_inizio):
    tasso_periodico = tasso_annuo / 100 / (12 / frequenza)
    if tasso_periodico == 0:
        quota = importo / rate
    else:
        quota = importo * (tasso_periodico * (1 + tasso_periodico) ** rate) / ((1 + tasso_periodico) ** rate - 1)

    scadenze = []
    capitale_residuo = importo

    for i in range(1, rate + 1):
        if tasso_periodico == 0:
            interesse = 0
            capitale = quota
        else:
            interesse = round(capitale_residuo * tasso_periodico, 2)
            capitale = round(quota - interesse, 2)

        data_scadenza = data_inizio + timedelta(days=(i - 1) * 30 * (frequenza / 1))
        scadenze.append({
            "Rata N°": i,
            "Data Scadenza": data_scadenza.date(),
            "Quota Capitale": round(capitale, 2),
            "Quota Interessi": round(interesse, 2),
            "Rata Totale": round(capitale + interesse, 2),
            "Pagato": False,
            "Data Pagamento": "",
            "Ricevuta File": None
        })
        capitale_residuo -= capitale

    return pd.DataFrame(scadenze)

def esporta_pdf(importo, rate, tasso, frequenza, df, nome_file):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, txt="Riepilogo Piano di Ammortamento", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=f"Importo Finanziato: € {importo:,.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Numero Rate: {rate}", ln=True)
    pdf.cell(200, 10, txt=f"Frequenza Rate: ogni {frequenza} mese/i", ln=True)
    pdf.cell(200, 10, txt=f"Tasso Annuo: {tasso:.2f}%", ln=True)
    pdf.cell(200, 10, txt=f"Rata Stimata: € {df['Rata Totale'][0]:,.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Totale da Restituire: € {df['Rata Totale'].sum():,.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Interessi Totali: € {df['Quota Interessi'].sum():,.2f}", ln=True)

    percorso_pdf = f"{nome_file}.pdf"
    pdf.output(percorso_pdf)
    return percorso_pdf

importo = st.number_input("💰 Importo Totale", min_value=0.0, step=100.0)
rate = st.number_input("📆 Numero Rate (max 100)", min_value=1, max_value=100, step=1)
tasso = st.number_input("📈 Tasso Annuo (%)", min_value=0.0, step=0.1)
frequenza = st.selectbox("⏱️ Frequenza Rate (mesi)", [1, 2, 3, 6, 12])
data_inizio = st.date_input("🗓️ Data Inizio")
nome_piano = st.text_input("💾 Nome File Piano (senza estensione)", value="piano_ammortamento")

if st.button("📅 Genera Piano"):
    df = calcola_piano(importo, rate, tasso, frequenza, datetime.combine(data_inizio, datetime.min.time()))

    st.subheader("📝 Dettaglio Interattivo Piano")
    for i in range(len(df)):
        with st.expander(f"Rata {df.loc[i, 'Rata N°']} - Scadenza {df.loc[i, 'Data Scadenza']}"):
            df.at[i, "Pagato"] = st.checkbox("Pagato", key=f"pagato_{i}")
            if df.at[i, "Pagato"]:
                df.at[i, "Data Pagamento"] = st.date_input("Data Pagamento", key=f"data_pagamento_{i}")
            file_ricevuta = st.file_uploader("📎 Carica Ricevuta", type=["pdf", "jpg", "png"], key=f"ricevuta_{i}")
            if file_ricevuta:
                df.at[i, "Ricevuta File"] = file_ricevuta.name

    st.markdown("### 📊 Riepilogo Piano")
    st.markdown(f'''
- **Importo Finanziato:** € {importo:,.2f}
- **Numero Rate:** {rate}
- **Frequenza Rate:** ogni {frequenza} mese/i
- **Tasso Annuo:** {tasso:.2f}%
- **Rata Stimata:** € {df['Rata Totale'][0]:,.2f}
- **Totale da Restituire:** € {df['Rata Totale'].sum():,.2f}
- **Interessi Totali:** € {df['Quota Interessi'].sum():,.2f}
''')

    st.success("✅ Piano aggiornato.")
    pdf_path = esporta_pdf(importo, rate, tasso, frequenza, df, nome_piano)
    with open(pdf_path, "rb") as f:
        st.download_button("📄 Scarica PDF Piano", f, file_name=pdf_path)

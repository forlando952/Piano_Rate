
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from fpdf import FPDF
import os

st.set_page_config(page_title="Piano Ammortamento", layout="centered")
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
            "Ricevuta File": ""
        })
        capitale_residuo -= capitale

    return pd.DataFrame(scadenze)

def esporta_pdf(df, filename):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, "Piano di Ammortamento", ln=True, align="C")
    pdf.set_font("Arial", "", 10)

    col_names = list(df.columns)
    col_widths = [18, 28, 28, 28, 28, 18, 30, 30]

    pdf.set_fill_color(200, 200, 200)
    for i, col in enumerate(col_names):
        pdf.cell(col_widths[i], 8, col, border=1, fill=True)
    pdf.ln()

    for _, row in df.iterrows():
        for i, col in enumerate(col_names):
            pdf.cell(col_widths[i], 8, str(row[col]), border=1)
        pdf.ln()

    pdf.output(filename)
    return filename

# Input utente
importo = st.number_input("💰 Importo Totale", min_value=0.0, step=100.0)
rate = st.number_input("📆 Numero Rate (max 100)", min_value=1, max_value=100, step=1)
tasso = st.number_input("📈 Tasso Annuo (%)", min_value=0.0, step=0.1)
frequenza = st.selectbox("⏱️ Frequenza Rate (mesi)", [1, 2, 3, 6, 12])
data_inizio = st.date_input("🗓️ Data Inizio")
nome_piano = st.text_input("💾 Nome File Piano (senza estensione)", value="piano_ammortamento")

if st.button("📅 Genera Piano"):
    df = calcola_piano(importo, rate, tasso, frequenza, datetime.combine(data_inizio, datetime.min.time()))

    if nome_piano:
        if not os.path.exists("piani_salvati"):
            os.makedirs("piani_salvati")
        excel_path = f"piani_salvati/{nome_piano}.xlsx"
        pdf_path = f"piani_salvati/{nome_piano}.pdf"

        df.to_excel(excel_path, index=False)
        esporta_pdf(df, pdf_path)

        st.success(f"Piano creato e salvato come: {excel_path}")
        st.download_button("📤 Scarica PDF", open(pdf_path, "rb"), file_name=f"{nome_piano}.pdf")

        st.subheader("📋 Anteprima Piano di Ammortamento")
        st.dataframe(df)
    else:
        st.error("Inserisci un nome file valido.")

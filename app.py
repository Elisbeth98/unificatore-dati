import streamlit as st
import pandas as pd

# Configurazione pagina
st.set_page_config(page_title="DataMaster Pro", layout="wide", page_icon="📊")

# --- SIDEBAR: MENU DI NAVIGAZIONE ---
with st.sidebar:
    st.title("🛠️ Strumenti Dati")
    scelta = st.radio(
        "Cosa vuoi fare?",
        ("Unisci più File", "Analizza Singolo File (Pivot)")
    )
    st.write("---")
    st.info("Sviluppato da: **Elisabetta**\n\nContattami per personalizzazioni su misura.")

# --- FUNZIONE PER EXPORT ITA ---
def convert_df(df):
    return df.to_csv(index=False, sep=';', decimal=',').encode('utf-8-sig')

# --- MODALITÀ 1: UNIFICAZIONE ---
if scelta == "Unisci più File":
    st.title("🔄 Unificatore di Dati")
    st.write("Carica i file, scegli la colonna ponte e crea il tuo database unico.")
    
    uploaded_files = st.file_uploader("Carica file Excel o CSV", accept_multiple_files=True, type=['xlsx', 'csv'], key="unificatore")
    
    if uploaded_files:
        dfs = {f.name: (pd.read_excel(f) if f.name.endswith('.xlsx') else pd.read_csv(f, sep=None, engine='python', decimal=',')) for f in uploaded_files}
        
        main_file = st.selectbox("Scegli il file BASE (Master):", list(dfs.keys()))
        final_df = dfs[main_file].copy()
        
        for name, df in dfs.items():
            if name != main_file:
                with st.expander(f"Unisci dati da: {name}"):
                    c1, c2 = st.columns(2)
                    col_l = c1.selectbox(f"Ponte nel Master", final_df.columns, key=f"L_{name}")
                    col_r = c2.selectbox(f"Ponte in {name}", df.columns, key=f"R_{name}")
                    cols = st.multiselect(f"Colonne da aggiungere", [c for c in df.columns if c != col_r], key=f"C_{name}")
                    
                    if st.button(f"Applica Unione {name}"):
                        final_df = pd.merge(final_df, df[[col_r] + cols], left_on=col_l, right_on=col_r, how='left')
                        if col_l != col_r and col_r in final_df.columns:
                            final_df.drop(columns=[col_r], inplace=True)
                        st.success("Unito!")

        st.markdown("---")
        st.subheader("Anteprima Risultato")
        st.dataframe(final_df.head(20))
        st.download_button("📥 Scarica File Unito", convert_df(final_df), "file_unito.csv")

# --- MODALITÀ 2: ANALISI (PIVOT) ---
else:
    st.title("📊 Analizzatore Rapido")
    st.write("Carica un file per generare tabelle riassuntive (Pivot) in pochi clic.")
    
    single_file = st.file_uploader("Carica il file da analizzare", type=['xlsx', 'csv'], key="analizzatore")
    
    if single_file:
        df_analisi = pd.read_excel(single_file) if single_file.name.endswith('.xlsx') else pd.read_csv(single_file, sep=None, engine='python', decimal=',')
        
        st.write("### Anteprima Dati")
        st.dataframe(df_analisi.head(10))
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            raggruppa = st.selectbox("Raggruppa per (Righe):", df_analisi.columns)
        with col2:
            # Filtriamo solo le colonne numeriche per la somma
            numeric_cols = df_analisi.select_dtypes(include=['number']).columns.tolist()
            valore = st.selectbox("Cosa vuoi sommare? (Valori):", numeric_cols)
            
        if raggruppa and valore:
            pivot = df_analisi.groupby(raggruppa)[valore].sum().reset_index()
            st.write(f"#### Risultato: Somma di {valore} per {raggruppa}")
            st.table(pivot)
            
            st.download_button("📥 Scarica Tabella Pivot", convert_df(pivot), "analisi_pivot.csv")

import streamlit as st
import pandas as pd

# Configurazione pagina
st.set_page_config(page_title="DataMaster Pro ITA", layout="wide", page_icon="📊")

# --- SIDEBAR: MENU DI NAVIGAZIONE ---
with st.sidebar:
    st.title("🛠️ Strumenti Dati")
    scelta = st.radio(
        "Cosa vuoi fare?",
        ("Unisci più File", "Analizza Singolo File (Pivot)")
    )
    st.write("---")
    st.info("Sviluppato da: **Elisabetta**\n\nContattami per personalizzazioni su misura.")

# --- FUNZIONE PER EXPORT ITA (Punto e virgola e Virgola decimale) ---
def convert_df(df):
    # utf-8-sig serve per far leggere bene gli accenti a Excel
    return df.to_csv(index=False, sep=';', decimal=',').encode('utf-8-sig')

# --- MODALITÀ 1: UNIFICAZIONE ---
if scelta == "Unisci più File":
    st.title("🔄 Unificatore di Dati")
    st.write("Carica i file, scegli la colonna ponte e crea il tuo database unico.")
    
    uploaded_files = st.file_uploader("Carica file Excel o CSV", accept_multiple_files=True, type=['xlsx', 'csv'], key="unificatore")
    
    if uploaded_files:
        dfs = {}
        for f in uploaded_files:
            if f.name.endswith('.xlsx'):
                dfs[f.name] = pd.read_excel(f)
            else:
                # Carica CSV provando a gestire i decimali europei
                dfs[f.name] = pd.read_csv(f, sep=None, engine='python', decimal=',')
        
        main_file = st.selectbox("Scegli il file BASE (Master):", list(dfs.keys()))
        final_df = dfs[main_file].copy()
        
        for name, df in dfs.items():
            if name != main_file:
                with st.expander(f"Unisci dati da: {name}", expanded=True):
                    c1, c2 = st.columns(2)
                    col_l = c1.selectbox(f"Ponte nel Master", final_df.columns, key=f"L_{name}")
                    col_r = c2.selectbox(f"Ponte in {name}", df.columns, key=f"R_{name}")
                    cols = st.multiselect(f"Colonne da aggiungere", [c for c in df.columns if c != col_r], key=f"C_{name}")
                    
                    if st.button(f"Applica Unione {name}"):
                        final_df = pd.merge(final_df, df[[col_r] + cols], left_on=col_l, right_on=col_r, how='left')
                        if col_l != col_r and col_r in final_df.columns:
                            final_df.drop(columns=[col_r], inplace=True)
                        st.success("Unito con successo!")

        st.markdown("---")
        st.subheader("Anteprima Risultato")
        # Mostra i numeri con la virgola nell'anteprima web
        st.dataframe(final_df.head(20).style.format(precision=2, decimal=',', thousands=''))
        
        st.download_button("📥 Scarica File Unito (Excel ITA)", convert_df(final_df), "file_unito_ita.csv")

# --- MODALITÀ 2: ANALISI (PIVOT) ---
else:
    st.title("📊 Analizzatore Rapido")
    st.write("Carica un file per generare tabelle riassuntive (Pivot).")
    
    single_file = st.file_uploader("Carica il file da analizzare", type=['xlsx', 'csv'], key="analizzatore")
    
    if single_file:
        # Leggiamo il file forzando la virgola come decimale
        if single_file.name.endswith('.xlsx'):
            df_analisi = pd.read_excel(single_file)
        else:
            df_analisi = pd.read_csv(single_file, sep=None, engine='python', decimal=',')
        
        st.write("### Anteprima Dati")
        st.dataframe(df_analisi.head(10).style.format(precision=2, decimal=',', thousands=''))
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            raggruppa = st.selectbox("Raggruppa per (Righe):", df_analisi.columns)
        with col2:
            # Identifichiamo le colonne numeriche
            numeric_cols = df_analisi.select_dtypes(include=['number']).columns.tolist()
            valore = st.selectbox("Cosa vuoi sommare? (Valori):", numeric_cols)
            
        if st.button("Genera Analisi"):
            # Calcolo Pivot
            pivot = df_analisi.groupby(raggruppa)[valore].sum().reset_index()
            
            st.write(f"#### Risultato: Somma di {valore} per {raggruppa}")
            # Visualizzazione con la virgola
            st.table(pivot.style.format({valore: '{:.2f}'.replace('.', ',')}))
            
            st.download_button("📥 Scarica Tabella Pivot (Excel ITA)", convert_df(pivot), "analisi_pivot.csv")

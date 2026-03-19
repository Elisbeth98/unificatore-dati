import streamlit as st
import pandas as pd
import io

# Configurazione pagina
st.set_page_config(page_title="Universal Data Merger ITA", layout="wide", page_icon="🔄")

st.title("🔄 Universal Data Merger (Versione Italia)")
st.write("Unisci i tuoi file Excel/CSV senza errori di formato (Virgola e Punto e Virgola).")

# Caricamento file
uploaded_files = st.file_uploader("Trascina qui i tuoi file (Excel o CSV)", accept_multiple_files=True, type=['xlsx', 'csv'])

if uploaded_files:
    dfs = {}
    for f in uploaded_files:
        try:
            if f.name.endswith('.xlsx'):
                # Per Excel leggiamo normalmente
                dfs[f.name] = pd.read_excel(f)
            else:
                # Per i CSV proviamo a capire se il separatore è , o ;
                content = f.getvalue().decode('utf-8-sig', errors='ignore')
                sep = ';' if ';' in content.split('\n')[0] else ','
                f.seek(0)
                dfs[f.name] = pd.read_csv(f, sep=sep, decimal=',')
        except Exception as e:
            st.error(f"Errore nel caricamento di {f.name}: {e}")
    
    if dfs:
        st.success(f"✅ {len(dfs)} file pronti per l'elaborazione.")

        # Scelta del file Master
        main_file_name = st.selectbox("1. Scegli il file BASE (Master):", list(dfs.keys()))
        final_df = dfs[main_file_name].copy()

        st.markdown("---")
        st.subheader("2. Configura le Unioni")

        # Logica di unione per gli altri file
        for name, df in dfs.items():
            if name != main_file_name:
                with st.expander(f"Unisci dati da: {name}", expanded=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        col_left = st.selectbox(f"Colonna 'ponte' nel Master", final_df.columns, key=f"L_{name}")
                    with c2:
                        col_right = st.selectbox(f"Colonna 'ponte' in {name}", df.columns, key=f"R_{name}")
                    
                    cols_to_pull = st.multiselect(f"Quali colonne vuoi AGGIUNGERE da {name}?", 
                                                 [c for c in df.columns if c != col_right], key=f"C_{name}")
                    
                    if st.button(f"Applica Unione: {name}", key=f"B_{name}"):
                        # Selezioniamo solo le colonne utili dal file secondario
                        new_data = df[[col_right] + cols_to_pull].copy()
                        
                        # Eseguiamo il merge (unione)
                        final_df = pd.merge(final_df, new_data, left_on=col_left, right_on=col_right, how='left')
                        
                        # Se le colonne ponte avevano nomi diversi, eliminiamo quella doppia
                        if col_left != col_right and col_right in final_df.columns:
                            final_df.drop(columns=[col_right], inplace=True)
                            
                        st.success(f"Dati di '{name}' integrati correttamente!")

        st.markdown("---")
        st.subheader("3. Anteprima e Download")
        st.dataframe(final_df.head(50))

        # --- ESPORTAZIONE OTTIMIZZATA PER EXCEL ITALIA ---
        # Creiamo un file CSV con separatore ; e decimale ,
        # utf-8-sig serve a far leggere correttamente gli accenti a Excel
        output_csv = final_df.to_csv(index=False, sep=';', decimal=',').encode('utf-8-sig')

        st.download_button(
            label="📥 Scarica Risultato per Excel (CSV ITA)",
            data=output_csv,
            file_name="risultato_unito_italiano.csv",
            mime="text/csv",
            help="Questo file si aprirà correttamente in Excel con colonne divise e virgole decimali."
        )

st.info("Consiglio: Se il file scaricato sembra ancora strano, prova ad aprirlo in Excel e usa 'Dati -> Testo in colonne', ma con questo formato dovrebbe essere automatico!")

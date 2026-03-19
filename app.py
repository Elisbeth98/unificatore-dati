import streamlit as st
import pandas as pd

st.set_page_config(page_title="Universal Data Merger", layout="wide")

st.title("🔄 Universal Data Merger")
st.write("L'innovazione a costo zero: unisci i tuoi file Excel senza fatica.")

# Caricamento file
uploaded_files = st.file_uploader("Trascina qui i tuoi file (Excel o CSV)", accept_multiple_files=True, type=['xlsx', 'csv'])

if uploaded_files:
    dfs = {}
    for f in uploaded_files:
        try:
            if f.name.endswith('.xlsx'):
                dfs[f.name] = pd.read_excel(f)
            else:
                dfs[f.name] = pd.read_csv(f)
        except Exception as e:
            st.error(f"Errore nel caricamento di {f.name}: {e}")
    
    if dfs:
        st.success(f"Caricati {len(dfs)} file con successo.")

        # Scelta del file Master
        main_file_name = st.selectbox("Scegli il file PRINCIPALE (Master):", list(dfs.keys()))
        final_df = dfs[main_file_name].copy()

        st.markdown("---")
        st.subheader("Configura le Unioni")

        # Logica di unione per gli altri file
        for name, df in dfs.items():
            if name != main_file_name:
                with st.expander(f"Unisci dati da: {name}"):
                    c1, c2 = st.columns(2)
                    with c1:
                        col_left = st.selectbox(f"Colonna ponte nel Master", final_df.columns, key=f"L_{name}")
                    with c2:
                        col_right = st.selectbox(f"Colonna ponte in {name}", df.columns, key=f"R_{name}")
                    
                    cols_to_pull = st.multiselect(f"Quali colonne vuoi copiare da {name}?", 
                                                 [c for c in df.columns if c != col_right], key=f"C_{name}")
                    
                    if st.button(f"Applica Unione {name}", key=f"B_{name}"):
                        new_data = df[[col_right] + cols_to_pull]
                        # Merge
                        final_df = pd.merge(final_df, new_data, left_on=col_left, right_on=col_right, how='left')
                        # Rimuovi colonna duplicata se ha nome diverso
                        if col_left != col_right and col_right in final_df.columns:
                            final_df.drop(columns=[col_right], inplace=True)
                        st.success(f"Fatto! Dati di {name} integrati.")

        st.markdown("---")
        st.subheader("Anteprima del Risultato Finale")
        st.dataframe(final_df)

        # Download
        csv = final_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Scarica il file unito (CSV)", csv, "risultato_unito.csv", "text/csv")

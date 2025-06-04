import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard de Inventario", layout="wide")
st.title("📦 Dashboard Limpio de Artículos")

uploaded_file = st.file_uploader("📁 Sube tu archivo Excel", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file, header=1)
else:
    try:
        df = pd.read_excel("Listado de piezas por vehiculos.xlsx", header=1)
        st.info(
            "Mostrando datos de 'Listado de piezas por vehiculos.xlsx' "
            "porque no se cargó ningún archivo"
        )
    except Exception as e:
        st.error(f"No se pudo cargar el archivo predeterminado: {e}")
        st.stop()

# Mostrar columnas originales
st.markdown("### 🔍 Columnas detectadas")
st.write(list(df.columns))

# Intentar encontrar columnas relevantes automáticamente
col_map = {}
for col in df.columns:
    name = str(col).lower()
    if "parte" in name or "j19" in name:
        col_map[col] = "Numero de Parte"
    elif "descripcion" in name or "tinte" in name:
        col_map[col] = "Descripcion"
    elif "unidad" in name or "322" in name:
        col_map[col] = "Unidades"
    elif "pintura" in name or "material" in name:
        col_map[col] = "Categoria"
    elif "clasificacion" in name:
        col_map[col] = "Clasificacion"

df = df.rename(columns=col_map)

if "Clasificación" in df.columns:
    df.drop(columns=["Clasificación"], inplace=True)

st.markdown("---")
st.subheader("📌 Indicadores Generales")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("🔢 Total de Artículos", len(df))
with col2:
    if "Unidades" in df.columns:
        unidades_total = pd.to_numeric(df["Unidades"], errors="coerce").sum()
        st.metric("📦 Total de Unidades", int(unidades_total))
with col3:
    if "Clasificacion" in df.columns:
        obsoletos = df[df["Clasificacion"].str.contains("obsoleto", case=False, na=False)]
        st.metric("🗑️ Artículos Obsoletos", len(obsoletos))

st.markdown("---")
st.subheader("🔍 Filtros")

col1, col2, col3 = st.columns(3)
with col1:
    filtro_categoria = st.multiselect(
        "Categoría",
        options=df["Categoria"].dropna().unique() if "Categoria" in df.columns else [],
        default=None,
    )
with col2:
    filtro_clasificacion = st.multiselect(
        "Clasificación",
        options=df["Clasificacion"].dropna().unique() if "Clasificacion" in df.columns else [],
        default=None,
    )
with col3:
    buscar_descripcion = st.text_input("Buscar por Descripción")

df_filtrado = df.copy()
if "Categoria" in df.columns and filtro_categoria:
    df_filtrado = df_filtrado[df_filtrado["Categoria"].isin(filtro_categoria)]
if "Clasificacion" in df.columns and filtro_clasificacion:
    df_filtrado = df_filtrado[df_filtrado["Clasificacion"].isin(filtro_clasificacion)]
if buscar_descripcion:
    df_filtrado = df_filtrado[df_filtrado["Descripcion"].str.contains(buscar_descripcion, case=False, na=False)]

st.markdown("---")
st.subheader("📊 Gráfico por Clasificación")
if "Clasificacion" in df_filtrado.columns:
    conteo = df_filtrado["Clasificacion"].value_counts().reset_index()
    conteo.columns = ["Clasificacion", "Cantidad"]
    fig = px.pie(
        conteo,
        names="Clasificacion",
        values="Cantidad",
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Plasma,
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("### 📈 Gráfico de barras por Categoría")
if "Categoria" in df_filtrado.columns:
    barras = df_filtrado["Categoria"].value_counts().reset_index()
    barras.columns = ["Categoria", "Cantidad"]
    fig_bar = px.bar(
        barras,
        x="Categoria",
        y="Cantidad",
        color="Categoria",
        color_discrete_sequence=px.colors.sequential.Tealgrn,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")
st.subheader("🧾 Tabla de Inventario Limpia")
st.dataframe(df_filtrado, use_container_width=True, height=500)

csv = df_filtrado.to_csv(index=False).encode("utf-8")
st.download_button(
    "📥 Descargar CSV filtrado", csv, file_name="inventario_filtrado.csv", mime="text/csv"
)

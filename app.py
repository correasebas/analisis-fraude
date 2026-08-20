import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Fraude Transaccional",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Dashboard de Monitoreo y Análisis de Fraude")
st.markdown("Analiza patrones transaccionales, detecta anomalias y genera reportes interactivos.")

# 1. Carga de Datos
st.sidebar.header("📂 Configuración y Filtros")
uploaded_file = st.sidebar.file_uploader("Cargar dataset CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    try:
        df = pd.read_csv("dataset_transacciones_fraude_600.csv")
    except FileNotFoundError:
        st.warning("⚠️ Sube un archivo CSV desde la barra lateral para comenzar.")
        st.stop()

# 2. Filtros Dinámicos
ciudades_opt = ["Todas"] + list(df["ciudad"].dropna().unique())
ciudad_sel = st.sidebar.selectbox("Ciudad del Cliente", ciudades_opt)

categorias_opt = ["Todas"] + list(df["categoria_comercio"].dropna().unique())
cat_sel = st.sidebar.selectbox("Categoría de Comercio", categorias_opt)

tipo_fraude_sel = st.sidebar.radio(
    "Filtrar Estado de Transacción",
    ["Todas", "Solo Fraude (1)", "Normales (0)"]
)

# Aplicar filtros
df_filtered = df.copy()

if ciudad_sel != "Todas":
    df_filtered = df_filtered[df_filtered["ciudad"] == ciudad_sel]

if cat_sel != "Todas":
    df_filtered = df_filtered[df_filtered["categoria_comercio"] == cat_sel]

if tipo_fraude_sel == "Solo Fraude (1)":
    df_filtered = df_filtered[df_filtered["fraude"] == 1]
elif tipo_fraude_sel == "Normales (0)":
    df_filtered = df_filtered[df_filtered["fraude"] == 0]

# 3. Métricas Principales (KPIs)
total_transacciones = len(df_filtered)
total_monto = df_filtered["valor_transaccion"].sum()
monto_promedio = df_filtered["valor_transaccion"].mean() if total_transacciones > 0 else 0
casos_fraude = (df_filtered["fraude"] == 1).sum()
tasa_fraude = (casos_fraude / total_transacciones * 100) if total_transacciones > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Transacciones Evaluadas", f"{total_transacciones:,}")
col2.metric("Monto Total Proc.", f"${total_monto:,.0f}")
col3.metric("Monto Promedio", f"${monto_promedio:,.0f}")
col4.metric("Tasa de Fraude", f"{tasa_fraude:.1f}%", delta=f"{casos_fraude} casos", delta_color="inverse")

st.markdown("---")

# 4. Gráficos Interactivos
st.subheader("📈 Análisis de Patrones y Comportamiento")

tab1, tab2, tab3 = st.tabs(["🚨 Fraude por Categoria y Ciudad", "💰 Distribución del Valor", "🔑 Autenticación y Hábitos"])

with tab1:
    col_a, col_b = st.columns(2)
    with col_a:
        fraude_cat = df_filtered.groupby(["categoria_comercio", "fraude"]).size().reset_index(name="conteo")
        fraude_cat["fraude_label"] = fraude_cat["fraude"].map({0: "Normal", 1: "Fraude"})
        fig1 = px.bar(
            fraude_cat, 
            x="categoria_comercio", 
            y="conteo", 
            color="fraude_label", 
            barmode="group",
            title="Transacciones por Categoría de Comercio",
            color_discrete_map={"Normal": "#2ECC71", "Fraude": "#E74C3C"}
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col_b:
        fraude_ciudad = df_filtered.groupby(["ciudad", "fraude"]).size().reset_index(name="conteo")
        fraude_ciudad["fraude_label"] = fraude_ciudad["fraude"].map({0: "Normal", 1: "Fraude"})
        fig2 = px.bar(
            fraude_ciudad, 
            x="ciudad", 
            y="conteo", 
            color="fraude_label", 
            barmode="stack",
            title="Distribución de Fraude por Ciudad",
            color_discrete_map={"Normal": "#3498DB", "Fraude": "#E74C3C"}
        )
        st.plotly_chart(fig2, use_container_width=True)

with tab2:
    fig3 = px.box(
        df_filtered, 
        x="fraude", 
        y="valor_transaccion", 
        color="fraude",
        labels={"fraude": "Es Fraude", "valor_transaccion": "Monto ($)"},
        title="Comparación del Valor de Transacción: Normal vs. Fraude",
        color_discrete_map={0: "#2ECC71", 1: "#E74C3C"}
    )
    st.plotly_chart(fig3, use_container_width=True)

with tab3:
    col_c, col_d = st.columns(2)
    with col_c:
        aut_fig = px.pie(
            df_filtered, 
            names="tipo_autenticacion", 
            title="Tipos de Autenticación Utilizados",
            hole=0.4
        )
        st.plotly_chart(aut_fig, use_container_width=True)
    
    with col_d:
        hab_data = df_filtered.groupby("fraude")[["ubicacion_habitual", "horario_habitual", "categoria_habitual"]].apply(
            lambda x: (x == "Sí").mean() * 100
        ).reset_index()
        hab_data["fraude_label"] = hab_data["fraude"].map({0: "Normal", 1: "Fraude"})
        
        hab_melted = pd.melt(
            hab_data, 
            id_vars=["fraude_label"], 
            value_vars=["ubicacion_habitual", "horario_habitual", "categoria_habitual"],
            var_name="Variable", 
            value_name="Porcentaje_Habitual"
        )
        fig4 = px.bar(
            hab_melted, 
            x="Variable", 
            y="Porcentaje_Habitual", 
            color="fraude_label", 
            barmode="group",
            title="% Cumplimiento de Hábitos Normales",
            color_discrete_map={"Normal": "#2ECC71", "Fraude": "#E74C3C"}
        )
        st.plotly_chart(fig4, use_container_width=True)

# 5. Exportación de Informe y Tabla de Datos
st.markdown("---")
st.subheader("📋 Detalle de Transacciones e Informe")

# Resumen ejecutivo en texto
total_monto_fraude = df_filtered[df_filtered["fraude"] == 1]["valor_transaccion"].sum()
st.info(
    f"**Resumen Ejecutivo del Filtro Actual:**\n"
    f"- Total transacciones analizadas: **{total_transacciones}**\n"
    f"- Total casos de fraude identificados: **{casos_fraude}**\n"
    f"- Pérdida / Riesgo por fraude detectado: **${total_monto_fraude:,.0f} COP**"
)

st.dataframe(df_filtered, use_container_width=True)

# Botón de descarga
csv_data = df_filtered.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Descargar Informe Filtrado en CSV",
    data=csv_data,
    file_name="informe_transacciones_filtrado.csv",
    mime="text/csv"
)

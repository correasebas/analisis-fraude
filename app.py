import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from groq import Groq

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Fraude Transaccional + Groq AI",
    page_icon="🛡️",
    layout="wide"
)

# Paleta de Colores Profesional / Corporativa
COLOR_NORMAL = "#1B365D"      # Azul Marino Financiero
COLOR_FRAUDE = "#D9381E"      # Rojo Carmesí / Alerta
COLOR_FONDO = "#F8F9FA"       # Gris Claro Limpio
COLOR_TEXTO = "#2C3E50"       # Gris Oscuro Profesional
COLOR_ACENTO = "#008080"      # Verde Azulado (Teal) para neutros

# Plantilla de diseño para Plotly
PLANTILLA_PLOTLY = dict(
    layout=go.Layout(
        font=dict(family="Arial, sans-serif", size=13, color=COLOR_TEXTO),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=50, b=40),
        xaxis=dict(showgrid=True, gridcolor="#E5E8E8", title_font=dict(size=12, color=COLOR_TEXTO)),
        yaxis=dict(showgrid=True, gridcolor="#E5E8E8", title_font=dict(size=12, color=COLOR_TEXTO)),
        legend=dict(title_font=dict(size=11, color=COLOR_TEXTO), font=dict(size=11))
    )
)

st.title("🛡️ Dashboard de Monitoreo de Fraude")

# 1. Carga de Datos y Configuración de Groq
st.sidebar.header("📂 Configuración y Filtros")

groq_api_key = st.sidebar.text_input("Groq API Key", type="password", help="Obtén tu API key en console.groq.com")

groq_model = st.sidebar.selectbox(
    "Modelo de Groq",
    [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        "gemma2-9b-it"
    ],
    index=0
)

uploaded_file = st.sidebar.file_uploader("Cargar dataset CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    try:
        df = pd.read_csv("dataset_transacciones_fraude_600.csv")
    except FileNotFoundError:
        st.warning("⚠️ Sube un archivo CSV desde la barra lateral para comenzar.")
        st.stop()

# Configuración de Reporte IA
st.sidebar.subheader("🤖 Configuración de Reporte IA")
num_insights = st.sidebar.slider("Número de Insights a generar", min_value=1, max_value=10, value=5)

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
total_monto = df_filtered["valor_transaccion"].sum() if total_transacciones > 0 else 0
monto_promedio = df_filtered["valor_transaccion"].mean() if total_transacciones > 0 else 0
casos_fraude = (df_filtered["fraude"] == 1).sum() if total_transacciones > 0 else 0
tasa_fraude = (casos_fraude / total_transacciones * 100) if total_transacciones > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Transacciones Evaluadas", f"{total_transacciones:,}")
col2.metric("Monto Total Proc.", f"${total_monto:,.0f}")
col3.metric("Monto Promedio", f"${monto_promedio:,.0f}")
col4.metric("Tasa de Fraude", f"{tasa_fraude:.1f}%", delta=f"{casos_fraude} casos", delta_color="inverse")

st.markdown("---")

# 4. Gráficos Interactivos con Estilo Profesional
st.subheader("📈 Análisis de Patrones y Comportamiento")

tab1, tab2, tab3 = st.tabs(["🚨 Fraude por Categoría y Ciudad", "💰 Distribución del Valor", "🔑 Autenticación y Hábitos"])

with tab1:
    col_a, col_b = st.columns(2)
    with col_a:
        fraude_cat = df_filtered.groupby(["categoria_comercio", "fraude"]).size().reset_index(name="conteo")
        fraude_cat["fraude_label"] = fraude_cat["fraude"].map({0: "Normal", 1: "Fraude"})
        
        fig1 = px.bar(
            fraude_cat, x="categoria_comercio", y="conteo", color="fraude_label", 
            barmode="group", title="Transacciones por Categoría de Comercio",
            color_discrete_map={"Normal": COLOR_NORMAL, "Fraude": COLOR_FRAUDE}
        )
        fig1.update_layout(PLANTILLA_PLOTLY["layout"])
        fig1.update_traces(marker_line_width=0, opacity=0.9)
        st.plotly_chart(fig1, use_container_width=True)

    with col_b:
        fraude_ciudad = df_filtered.groupby(["ciudad", "fraude"]).size().reset_index(name="conteo")
        fraude_ciudad["fraude_label"] = fraude_ciudad["fraude"].map({0: "Normal", 1: "Fraude"})
        
        fig2 = px.bar(
            fraude_ciudad, x="ciudad", y="conteo", color="fraude_label", 
            barmode="stack", title="Distribución de Fraude por Ciudad",
            color_discrete_map={"Normal": COLOR_NORMAL, "Fraude": COLOR_FRAUDE}
        )
        fig2.update_layout(PLANTILLA_PLOTLY["layout"])
        fig2.update_traces(marker_line_width=0, opacity=0.9)
        st.plotly_chart(fig2, use_container_width=True)

with tab2:
    fig3 = px.box(
        df_filtered, x="fraude", y="valor_transaccion", color="fraude",
        labels={"fraude": "Es Fraude", "valor_transaccion": "Monto ($)"},
        title="Comparación del Valor de Transacción: Normal vs. Fraude",
        color_discrete_map={0: COLOR_NORMAL, 1: COLOR_FRAUDE}
    )
    fig3.update_layout(PLANTILLA_PLOTLY["layout"])
    fig3.update_traces(marker_outline_width=1)
    st.plotly_chart(fig3, use_container_width=True)

with tab3:
    col_c, col_d = st.columns(2)
    with col_c:
        aut_fig = px.pie(
            df_filtered, names="tipo_autenticacion", 
            title="Tipos de Autenticación Utilizados", hole=0.5,
            color_discrete_sequence=[COLOR_NORMAL, COLOR_ACENTO, "#5D6D7E", "#A569BD"]
        )
        aut_fig.update_layout(PLANTILLA_PLOTLY["layout"])
        aut_fig.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#FFFFFF', width=2)))
        st.plotly_chart(aut_fig, use_container_width=True)
    
    with col_d:
        if not df_filtered.empty:
            cols_habitual = ["ubicacion_habitual", "horario_habitual", "categoria_habitual"]
            hab_data = (
                df_filtered.assign(**{c: df_filtered[c] == "Sí" for c in cols_habitual})
                .groupby("fraude")[cols_habitual]
                .mean()
                .mul(100)
                .reset_index()
            )
            hab_data["fraude_label"] = hab_data["fraude"].map({0: "Normal", 1: "Fraude"})
            
            hab_melted = pd.melt(
                hab_data, id_vars=["fraude_label"], 
                value_vars=cols_habitual,
                var_name="Variable", value_name="Porcentaje_Habitual"
            )
            fig4 = px.bar(
                hab_melted, x="Variable", y="Porcentaje_Habitual", color="fraude_label", 
                barmode="group", title="% Cumplimiento de Hábitos Normales",
                color_discrete_map={"Normal": COLOR_NORMAL, "Fraude": COLOR_FRAUDE}
            )
            fig4.update_layout(PLANTILLA_PLOTLY["layout"])
            fig4.update_traces(marker_line_width=0, opacity=0.9)
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("Sin datos para calcular hábitos habituales.")

# 5. Generación de Reporte con Groq AI
st.markdown("---")
st.subheader("🤖 Generación de Reporte Ejecutivo con Groq AI")

if st.button("🚀 Generar Reporte de Insights con Groq"):
    if not groq_api_key:
        st.error("⚠️ Por favor ingresa tu **Groq API Key** en la barra lateral.")
    elif df_filtered.empty:
        st.warning("⚠️ No hay datos para analizar con los filtros seleccionados.")
    else:
        with st.spinner("Analizando transacciones y consultando a Groq AI..."):
            try:
                top_categorias_fraude = df_filtered[df_filtered["fraude"] == 1]["categoria_comercio"].value_counts().to_dict()
                top_ciudades_fraude = df_filtered[df_filtered["fraude"] == 1]["ciudad"].value_counts().to_dict()
                autenticacion_fraude = df_filtered[df_filtered["fraude"] == 1]["tipo_autenticacion"].value_counts().to_dict()
                monto_fraude_promedio = df_filtered[df_filtered["fraude"] == 1]["valor_transaccion"].mean() if casos_fraude > 0 else 0
                
                contexto_prompt = f"""
                Actúa como un Analista Senior de Riesgo Financiero y Prevención de Fraude.
                Analiza las siguientes métricas del dataset filtrado:
                
                - Total Transacciones Evaluadas: {total_transacciones}
                - Transacciones Fraudulentas: {casos_fraude} ({tasa_fraude:.2f}%)
                - Monto Total en Riesgo/Fraude: ${df_filtered[df_filtered['fraude'] == 1]['valor_transaccion'].sum():,.0f} COP
                - Monto Promedio de Fraude: ${monto_fraude_promedio:,.0f} COP
                - Distribución de Fraude por Categoría: {top_categorias_fraude}
                - Distribución de Fraude por Ciudad: {top_ciudades_fraude}
                - Métodos de Autenticación en Fraudes: {autenticacion_fraude}
                
                Instrucciones:
                Genera exactamente **{num_insights} insights clave ejecutivos** numerados.
                Cada insight debe ser directo, accionable y basado exclusivamente en los datos provistos.
                Agrega al final una sección breve con **Recomendaciones de Mitigación**.
                """

                client = Groq(api_key=groq_api_key)
                response = client.chat.completions.create(
                    model=groq_model,
                    messages=[{"role": "user", "content": contexto_prompt}],
                    temperature=0.3
                )

                st.success("✅ Reporte generado exitosamente:")
                st.markdown(response.choices[0].message.content)

            except Exception as e:
                st.error(f"Error al conectar con Groq API: {e}")

# 6. Tabla de Datos y Descarga
st.markdown("---")
st.subheader("📋 Detalle de Transacciones")
st.dataframe(df_filtered, use_container_width=True)

csv_data = df_filtered.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Descargar CSV Filtrado",
    data=csv_data,
    file_name="informe_transacciones_filtrado.csv",
    mime="text/csv"
)

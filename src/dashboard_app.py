import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- FUNÇÕES DE PRÉ-PROCESSAMENTO E CÁLCULO ---

@st.cache_data
def load_and_prepare_data(uploaded_file):
    """
    Lê o arquivo CSV carregado, preenche nulos em métricas financeiras/de conversão
    e calcula o Custo Por Aquisição (CPA) por linha.
    """
    
    # Leitura do arquivo
    df = pd.read_csv(uploaded_file)
    
    # Preenchimento de nulos: 'Conversions' e 'Amount_spent' são definidos como 0
    # para permitir o cálculo agregado correto.
    df['Conversions'] = df['Conversions'].fillna(0)
    df['Amount_spent'] = df['Amount_spent'].fillna(0)
    
    # Cálculo do CPA (Custo Por Aquisição/Conversão).
    # O CPA é calculado apenas onde há conversões (> 0).
    # Se Conversions for 0, usamos NaN para evitar divisão por zero e não distorcer o CPA médio.
    df['CPA'] = np.where(
        df['Conversions'] > 0,
        df['Amount_spent'] / df['Conversions'],
        np.nan 
    )
    
    return df

@st.cache_data
def calculate_kpis_and_groups(df):
    """Calcula KPIs essenciais globais e gera tabelas de agregação para gráficos."""
    
    # 1. Agregações Globais
    total_spent = df['Amount_spent'].sum()
    total_conversions = df['Conversions'].sum()
    
    # CPA médio (ignora os valores 'NaN' ao calcular a média)
    average_cpa = df['CPA'].mean()
    
    kpis = {
        "Total Gasto": total_spent,
        "Total Conversões": total_conversions,
        "CPA Médio": average_cpa
    }
    
    # 2. Agrupamento para Gráfico Temporal (Gasto e Conversão por Ano/Mês)
    df_by_month = df.groupby('Ano_Mes').agg(
        Total_Gasto=('Amount_spent', 'sum'),
        Total_Conversões=('Conversions', 'sum')
    ).reset_index()
    
    return kpis, df_by_month

# --- FUNÇÃO PRINCIPAL DE CONSTRUÇÃO DO DASHBOARD ---

def create_dashboard(df_clean):
    st.header("📊 Dashboard de Insights de Performance")
    
    # 1. Filtragem para Análise Focada em Leads (Onde a coluna 'Objetivo' contém 'leads')
    df_leads = df_clean[df_clean['Objetivo'].astype(str).str.lower() == 'leads'].copy()
    
    # 2. Cálculo de KPIs Globais e Agrupamentos Temporais
    kpis, df_by_month = calculate_kpis_and_groups(df_clean)
    
    # --- Agrupamentos Específicos de Leads ---
    
    # Conversões (Leads) por Dia da Semana
    df_by_weekday = df_leads.groupby('Dia_da_Semana').agg(
        Total_Leads=('Conversions', 'sum')
    ).reset_index()
    
    # Leads e Gasto por Grupo de Anúncio (AdSet)
    df_by_adset = df_leads.groupby('AdSet_name').agg(
        Total_Leads=('Conversions', 'sum'),
        Total_Gasto=('Amount_spent', 'sum')
    ).reset_index()
    
    # Top 15 AdSets por Conversão para visualização
    df_by_adset_sorted = df_by_adset.sort_values(by='Total_Leads', ascending=False).head(15)
    
    # Leads por Tipo de Anúncio (Criativo)
    df_leads_by_type = df_leads.groupby('Tipo_de_Anúncio').agg(Total_Leads=('Conversions', 'sum')).reset_index()
    
    # --- Exibição de KPIs ---

    st.subheader("Key Performance Indicators (KPIs) Globais")
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    
    def format_brl(value):
        """Função utilitária para formatar valores monetários no padrão brasileiro (R$ X.XXX,XX)."""
        if pd.isna(value) or value is None:
            return "N/A"
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    kpi_col1.metric("💰 Total Gasto", format_brl(kpis['Total Gasto']))
    kpi_col2.metric("🎯 Total Conversões", f"{kpis['Total Conversões']:,.0f}".replace(",", "."))
    kpi_col3.metric("📉 CPA Médio", format_brl(kpis['CPA Médio']))

    st.markdown("---")

    # GRÁFICO 1: Gasto Total por Mês
    st.subheader("1. Análise de Investimento Temporal")
    fig_month_spent = px.bar(
        df_by_month, 
        x='Ano_Mes', 
        y='Total_Gasto', 
        title='Gasto Total por Mês (R$)',
        labels={'Total_Gasto': 'Gasto (R$)'}
    )
    fig_month_spent.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_month_spent, use_container_width=True)

    # GRÁFICO 2: Evolução de Conversões por Mês
    fig_month_conversions = px.line(
        df_by_month, 
        x='Ano_Mes', 
        y='Total_Conversões', 
        title='Evolução do Número de Conversões por Mês',
        markers=True # Adiciona marcadores para clareza
    )
    fig_month_conversions.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_month_conversions, use_container_width=True)
    
    st.markdown("---")
    
    # GRÁFICO 3: Leads por Dia da Semana (Filtro 'Leads')
    st.subheader("2. Performance por Dia da Semana (Foco em Leads)")
    
    dias_ordem = ['Segunda-Feira', 'Terça-Feira', 'Quarta-Feira', 'Quinta-Feira', 'Sexta-Feira', 'Sábado', 'Domingo']
    
    if not df_by_weekday.empty:
        # Ordena os dias da semana corretamente
        df_by_weekday['Dia_da_Semana'] = pd.Categorical(df_by_weekday['Dia_da_Semana'], categories=dias_ordem, ordered=True)
        df_by_weekday_sorted = df_by_weekday.sort_values('Dia_da_Semana').dropna(subset=['Dia_da_Semana'])
        
        fig_weekday_leads = px.bar(
            df_by_weekday_sorted, 
            x='Dia_da_Semana', 
            y='Total_Leads', 
            title='Número de Leads por Dia da Semana',
            color='Total_Leads'
        )
        st.plotly_chart(fig_weekday_leads, use_container_width=True)
    else:
        st.info("Não há dados de Leads para analisar por Dia da Semana.")
    
    st.markdown("---")
    
    # GRÁFICO 4: Leads por Tipo de Anúncio (Criativo)
    st.subheader("3. Análise por Tipo de Criativo (Foco em Leads)")
    
    fig_type_leads = px.bar(
        df_leads_by_type, 
        y='Tipo_de_Anúncio', 
        x='Total_Leads', 
        orientation='h',
        title='Número Total de Leads por Tipo de Anúncio',
        color='Total_Leads'
    )
    st.plotly_chart(fig_type_leads, use_container_width=True)

    # GRÁFICO 5: Top 15 AdSets por Leads
    st.subheader("4. Top 15 Grupos de Anúncio (AdSets) por Leads")
    
    fig_adset_leads = px.bar(
        df_by_adset_sorted, 
        x='Total_Leads', 
        y='AdSet_name', 
        orientation='h',
        title='Top 15 AdSets por Total de Leads',
        hover_data=['Total_Gasto', 'Total_Leads']
    )
    # Ordena o eixo Y pela contagem total de Leads (ascendente)
    fig_adset_leads.update_layout(yaxis={'categoryorder':'total ascending'}) 
    st.plotly_chart(fig_adset_leads, use_container_width=True)

    # GRÁFICO 6: Distribuição do CPA Geral
    st.subheader("5. Qualidade de Custo (Distribuição do CPA)")
    
    # Filtra apenas linhas com CPA válido (onde houve conversão)
    df_cpa_valid = df_clean[df_clean['CPA'].notna()]
    
    if not df_cpa_valid.empty:
        fig_cpa = px.histogram(
            df_cpa_valid,
            x='CPA',
            nbins=15,
            title='Distribuição do Custo Por Conversão (CPA)'
        )
        st.plotly_chart(fig_cpa, use_container_width=True)
    else:
        st.info("Não há dados de CPA válidos (sem conversões) para exibir o histograma.")

# --- FLUXO PRINCIPAL DO STREAMLIT ---

st.set_page_config(page_title="Dashboard de Insights", layout="wide")
st.title("📈 Dashboard de Insights de Performance de Anúncios")
st.markdown("Carregue o arquivo CSV que foi **validado** no App de Validação.")

uploaded_file_dashboard = st.file_uploader("**1. Escolha o CSV Validado**", type="csv")

if uploaded_file_dashboard is not None:
    try:
        # Carrega e prepara os dados, calculando o CPA por linha
        df_clean = load_and_prepare_data(uploaded_file_dashboard)
        
        st.success(f"Dados do arquivo '{uploaded_file_dashboard.name}' carregados para análise.")
        
        # Cria e exibe o dashboard
        create_dashboard(df_clean)

    except Exception as e:
        st.error(f"Erro ao processar os dados do Dashboard. Verifique se o arquivo está no formato esperado.")
        # Mantém a exceção para debug no console, mas evita o redundante st.exception(e) aqui.
        print(f"Erro detalhado: {e}")

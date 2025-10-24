import streamlit as st
import pandas as pd
from pydantic import ValidationError
import time

# Importa o modelo de validação Pydantic que define o esquema de dados esperado.
from validator import AdPerformanceRecord

def format_pydantic_error(error_detail: dict) -> str:
    """
    Formata um detalhe de erro do Pydantic (dicionário de erro) para uma mensagem amigável 
    e legível pelo usuário, em português.
    """
    # Tenta obter o nome do campo que causou o erro
    field = error_detail.get("loc", ["Campo Desconhecido"])[0]
    # Obtém a mensagem de erro original do Pydantic
    msg = error_detail.get("msg", "Erro de validação genérico.")
    
    # Lógica de formatação para erros comuns:
    if "field required" in msg:
        return f"O campo '{field}' está faltando ou vazio."
    if "float" in msg and ("not a valid float" in msg or "value is not a valid float" in msg):
        return f"O campo '{field}' deve ser um número decimal (ex: 100.50)."
    if "int" in msg and "not a valid integer" in msg:
        return f"O campo '{field}' deve ser um número inteiro (ex: 100)."
    
    # Mensagem padrão para outros erros não mapeados
    return f"Campo '{field}': {msg.capitalize()}."


def validate_data(df: pd.DataFrame):
    """
    Itera sobre o DataFrame, valida cada linha usando o modelo Pydantic 
    (AdPerformanceRecord) e gera um relatório detalhado de erros.

    Retorna:
    - valid_records (list): Lista de dicionários das linhas que passaram na validação.
    - error_report_list (list): Lista de dicionários com informações formatadas sobre os erros.
    """
    valid_records = []
    error_report_list = []
    
    # Itera sobre as linhas do DataFrame para validação individual
    for index, row in df.iterrows():
        try:
            # Converte a linha do pandas (Series) para um dicionário Python
            record_dict = row.to_dict()
            
            # Tenta validar o registro contra o modelo Pydantic
            validated_record = AdPerformanceRecord(**record_dict)
            
            # Se não houver exceção, o registro é válido
            valid_records.append(record_dict)
            
        except ValidationError as e:
            # Captura erros de validação Pydantic
            
            # Gera uma lista de mensagens de erro formatadas para a linha atual
            formatted_errors = [
                format_pydantic_error(error) 
                for error in e.errors()
            ]
            
            # Adiciona o registro de erro ao relatório
            error_report_list.append({
                # A linha CSV é o índice pandas + 2 (assumindo que o índice 0 é a linha 1 do cabeçalho)
                "Linha_CSV": index + 2, 
                "AdSet_Nome_Aprox": record_dict.get('AdSet_name', 'N/A'),
                "Primeiro_Erro_Detectado": formatted_errors[0],
                "Total_Erros_Nesta_Linha": len(formatted_errors)
            })
            
        except Exception as e:
            # Captura outros erros inesperados (ex: problemas de codificação na leitura da linha)
            error_report_list.append({
                "Linha_CSV": index + 2,
                "AdSet_Nome_Aprox": row.get('AdSet_name', 'N/A'),
                "Primeiro_Erro_Detectado": f"Erro Geral: {str(e)}",
                "Total_Erros_Nesta_Linha": 1
            })
            
    return valid_records, error_report_list

# --- Configuração e Layout do Streamlit ---
st.set_page_config(
    page_title="Validador de Performance de Anúncios",
    layout="wide"
)

st.title("✅ Validador de Dados de Performance de Anúncios")
st.markdown("Faça o upload do seu arquivo CSV para garantir que os dados seguem o **esquema definido** (`validator.py`).")

# Widget para upload de arquivo CSV
uploaded_file = st.file_uploader(
    "**1. Escolha o arquivo CSV** (e.g., data.csv)", 
    type="csv", 
    accept_multiple_files=False
)

if uploaded_file is not None:
    # 1. Leitura do arquivo CSV usando pandas
    try:
        # Tenta ler o CSV
        df = pd.read_csv(uploaded_file)
        
        st.subheader("Dados Carregados (Amostra)")
        st.write(f"Arquivo: **{uploaded_file.name}**")
        st.write(f"Total de Linhas Lidas: **{len(df)}**")
        # Exibe as primeiras 5 linhas para visualização
        st.dataframe(df.head(5), use_container_width=True)
        
        # Botão para iniciar o processo de validação
        if st.button("▶️ 2. Iniciar Validação e Relatório", type="primary"):
            st.info("Iniciando a validação linha a linha... Por favor, aguarde.")
            
            # 2. Execução da Validação
            start_time = time.time()
            valid_data, error_report = validate_data(df)
            end_time = time.time()
            
            total_records = len(df)
            valid_count = len(valid_data)
            error_count = len(error_report)
            
            st.subheader("Resumo da Validação")
            
            # Métricas de Validação exibidas em colunas
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total de Linhas", total_records)
            col2.metric("Válidas (OK)", valid_count)
            col3.metric("Com Erro", error_count)
            col4.metric("Tempo Total (s)", f"{end_time - start_time:.2f}")

            # 3. Exibição dos Erros (se houver)
            if error_count > 0:
                st.error(f"❌ **ATENÇÃO:** Foram encontrados **{error_count}** registros com falhas de validação.")
                
                st.markdown("### Relatório de Erros Amigável")
                st.warning("Use a tabela abaixo para identificar e corrigir rapidamente os dados incorretos no seu CSV original.")
                
                # Converte o relatório de erro para um DataFrame para exibição tabular
                df_errors = pd.DataFrame(error_report)
                st.dataframe(
                    df_errors,
                    use_container_width=True,
                    hide_index=True
                )
                
            else:
                st.success("✅ **SUCESSO!** Todos os registros passaram na validação. O esquema de dados está correto.")
                
            # 4. Exibição dos Dados Válidos (opcional, em um expander)
            with st.expander(f"Visualizar os {valid_count} Registros Válidos"):
                if valid_data:
                    df_valid = pd.DataFrame(valid_data)
                    st.dataframe(df_valid, use_container_width=True)
                else:
                    st.warning("Nenhum dado válido para exibir (todas as linhas tiveram erro).")

    except Exception as e:
        # Captura erros durante a leitura inicial do arquivo (ex: CSV mal formatado, codificação)
        st.error(f"Ocorreu um erro **inesperado** durante a leitura do CSV: {e}")
        st.exception(e)
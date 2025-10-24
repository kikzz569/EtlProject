import streamlit as st
import pandas as pd
from pydantic import ValidationError
import io
import time

# Importa o modelo de validação criado no arquivo 'validator.py'
from validator import AdPerformanceRecord

def format_pydantic_error(error_detail: dict) -> str:
    """
    Formata um detalhe de erro do Pydantic para uma mensagem amigável.
    """
    field = error_detail.get("loc", ["Campo Desconhecido"])[0]
    msg = error_detail.get("msg", "Erro de validação genérico.")
    
    # Tentativa de tornar a mensagem mais clara baseada no tipo de erro
    if "field required" in msg:
        return f"O campo '{field}' está faltando ou vazio."
    if "is not a valid float" in msg or "value is not a valid float" in msg:
        return f"O campo '{field}' deve ser um número (ex: 100.50)."
    if "int" in msg and "is not a valid integer" in msg:
         return f"O campo '{field}' deve ser um número inteiro (ex: 100)."
    
    # Mensagem padrão para outros erros
    return f"Campo '{field}': {msg.capitalize()}."


def validate_data(df: pd.DataFrame):
    """
    Função para iterar sobre o DataFrame, validar cada linha 
    e gerar um relatório de erros amigável.
    """
    valid_records = []
    error_report_list = []
    
    # Itera sobre as linhas do DataFrame como dicionários
    for index, row in df.iterrows():
        try:
            # Converte a série pandas (row) para um dicionário Python
            record_dict = row.to_dict()
            
            # Tenta validar o registro
            validated_record = AdPerformanceRecord(**record_dict)
            
            # Se for válido, armazena o registro
            valid_records.append(record_dict)
            
        except ValidationError as e:
            # Gera uma lista de erros formatados para esta linha
            formatted_errors = [
                format_pydantic_error(error) 
                for error in e.errors()
            ]
            
            error_report_list.append({
                "Linha_CSV": index + 2,  # Linha no arquivo original (index + 1 para 0-based, +1 para cabeçalho)
                "AdSet_Nome_Aprox": record_dict.get('AdSet_name', 'N/A'),
                "Primeiro_Erro_Detectado": formatted_errors[0],
                "Total_Erros_Nesta_Linha": len(formatted_errors)
            })
            
        except Exception as e:
            # Captura outros erros (ex: erro de arquivo/caminho)
            error_report_list.append({
                "Linha_CSV": index + 2,
                "AdSet_Nome_Aprox": record_dict.get('AdSet_name', 'N/A'),
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

# Widget para upload de arquivo
uploaded_file = st.file_uploader(
    "**1. Escolha o arquivo CSV** (e.g., data.csv)", 
    type="csv", 
    accept_multiple_files=False
)

if uploaded_file is not None:
    # 1. Leitura do arquivo CSV com pandas
    try:
        # Tentativa de leitura. É importante testar a codificação, mas deixamos o padrão primeiro.
        df = pd.read_csv(uploaded_file)
        
        st.subheader("Dados Carregados (Amostra)")
        st.write(f"Arquivo: **{uploaded_file.name}**")
        st.write(f"Total de Linhas Lidas: **{len(df)}**")
        st.dataframe(df.head(5), use_container_width=True)
        
        # Botão para iniciar a validação
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
            
            # Métricas de Validação
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total de Linhas", total_records)
            col2.metric("Válidas (OK)", valid_count)
            col3.metric("Com Erro", error_count)
            col4.metric("Tempo Total (s)", f"{end_time - start_time:.2f}")

            # 3. Exibição dos Erros de forma amigável
            if error_count > 0:
                st.error(f"❌ **ATENÇÃO:** Foram encontrados **{error_count}** registros com falhas de validação.")
                
                st.markdown("### Relatório de Erros Amigável")
                st.warning("Use a tabela abaixo para identificar e corrigir rapidamente os dados incorretos no seu CSV original.")
                
                # Transforma a lista de relatórios de erro em um DataFrame para exibição clara
                df_errors = pd.DataFrame(error_report)
                st.dataframe(
                    df_errors,
                    use_container_width=True,
                    hide_index=True
                )
                
            else:
                st.success("✅ **SUCESSO!** Todos os registros passaram na validação. O esquema de dados está correto.")
                
            # 4. Exibição dos Dados Válidos (opcional)
            with st.expander(f"Visualizar os {valid_count} Registros Válidos"):
                if valid_data:
                    df_valid = pd.DataFrame(valid_data)
                    st.dataframe(df_valid, use_container_width=True)
                else:
                    st.warning("Nenhum dado válido para exibir (todas as linhas tiveram erro).")

    except Exception as e:
        st.error(f"Ocorreu um erro **inesperado** durante a leitura do CSV: {e}")
        st.exception(e)
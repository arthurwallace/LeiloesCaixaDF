import io
import streamlit as st
import pandas as pd
import locale

from trycourier import Courier
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

UF = 'DF'
ARQUIVO_DADOS_RECENTES = f"Dados_com_data_{UF}.csv"

def get_property_type(description):
    return description.split(",")[0].strip()

def send_email(subject, body):
    try:
        # Configurar Courier
        client = Courier(auth_token='pk_prod_XNB7MJGSQX4EMBHXE0K17EZE8FCA')

        response = client.send_message(
            message={
                "to": [{"email": "arthur.wallace.silva@gmail.com"}, {"email": "givanildo.caldas@gmail.com"}],
                "content": {"title": subject, "body": body}
            }
        )

    except Exception as e:
        # Imprimir o erro em caso de exceção
        print(f"Erro ao enviar e-mail: {str(e)}")


def get_data_leilao(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Encontrar o elemento <i> com a classe 'fa-gavel'
        icon_element = soup.find('i', {'class': 'fa-gavel'})

        # Verificar se o elemento foi encontrado
        if icon_element:
            # Extrair o texto do elemento <span> pai
            parent_span = icon_element.find_parent('span')
            data_text = parent_span.get_text(strip=True)

            # Usar expressão regular para extrair data e horário
            match = re.search(r'(\d{2}/\d{2}/\d{4}) - (\d{2}h\d{2})', data_text)
            if match:
                data_leilao = match.group(1)
                horario_leilao = match.group(2)
            else:
                print("Padrão de data não encontrado.")
                data_leilao, horario_leilao = None, None
        else:
            print("Elemento não encontrado.")
            data_leilao, horario_leilao = None, None
        
        # Inicializar variáveis booleanas
        aceita_fgts = True
        aceita_financiamento = True
        aceita_parcelamento = True
        aceita_consorcio = True
        tem_acao_judicial = False
        acoes_judiciais = ''

        # Buscar todos os elementos <i> com a classe 'fa-info-circle'
        info_elements = soup.find('i', {'class': 'fa-info-circle'})
        parent_p = info_elements.find_parent('p')
        
        if parent_p:
            # Quebrar o texto do <p> em segmentos usando <br>
            segments = parent_p.decode_contents().split('<br>')
            for segment in segments:
                segment_text = BeautifulSoup(segment, 'html.parser').get_text().strip().lower()
                
                if 'não' in segment_text and 'fgts' in segment_text:
                    aceita_fgts = False
                if 'não' in segment_text and 'financiamento' in segment_text:
                    aceita_financiamento = False
                if 'não' in segment_text and 'parcelamento' in segment_text:
                    aceita_parcelamento = False
                if 'não' in segment_text and 'consórcio' in segment_text:
                    aceita_consorcio = False
                if 'ação judicial' in segment_text:
                    tem_acao_judicial = True
                    acoes_judiciais = segment_text
        
        print(data_leilao, horario_leilao, aceita_fgts, aceita_financiamento, aceita_parcelamento, aceita_consorcio, tem_acao_judicial, acoes_judiciais)
        return data_leilao, horario_leilao, aceita_fgts, aceita_financiamento, aceita_parcelamento, aceita_consorcio, tem_acao_judicial, acoes_judiciais
    except Exception as e:
        print(f"Erro ao obter data do leilão: {e}, URL: {url}")
        return None, None, False, False, False, False, False, ''


def verificar_novos_imoveis(df_atual):

    try:
        # Tentar carregar o arquivo de dados recentes
        df_anterior = pd.read_csv(ARQUIVO_DADOS_RECENTES)
        
    except (FileNotFoundError, pd.errors.EmptyDataError):
        df_anterior = pd.DataFrame()

    if not df_anterior.empty:
        df_anterior = format_data_frame(df_anterior)
        novos_imoveis = df_atual[~df_atual['N° do imóvel'].isin(df_anterior['N° do imóvel'])]
        # Identificar novos imóveis
    else:
         novos_imoveis = df_atual
   
    novos_imoveis = format_data_frame(novos_imoveis, novos_imoveis=True)
    imoveis_com_alteracao = pd.DataFrame(columns=df_atual.columns)
    
    if not df_anterior.empty:
        for index, row in df_atual.iterrows():
            n_imovel = row['N° do imóvel']
            preco_atual = row['Preço']
            modalidade_atual = row['Modalidade de venda']

            # Verificar se o número do imóvel existe no DataFrame anterior
            if n_imovel in df_anterior['N° do imóvel'].values:
                # Obter o preço do imóvel no DataFrame anterior
                preco_anterior = df_anterior.loc[df_anterior['N° do imóvel'] == n_imovel, 'Preço'].iloc[0]
                modalidade_anterior = df_anterior.loc[df_anterior['N° do imóvel'] == n_imovel, 'Modalidade de venda'].iloc[0]

                if preco_atual != preco_anterior or modalidade_atual != modalidade_anterior:
                    # Adicionar o imóvel ao DataFrame de imóveis com alteração
                    #df_anterior.loc[df_anterior['N° do imóvel'] == n_imovel, 'Preço'] = preco_atual
                    #df_anterior.loc[df_anterior['N° do imóvel'] == n_imovel, 'Modalidade de venda'] = modalidade_atual
                    imoveis_com_alteracao = pd.concat([imoveis_com_alteracao, row.to_frame().T], ignore_index=True)
                    df_anterior = df_anterior.drop((df_anterior.loc[df_anterior['N° do imóvel'] == n_imovel]).index)
        
        imoveis_com_alteracao = format_data_frame(imoveis_com_alteracao, novos_imoveis=True)  
        imoveis_removidos = df_anterior[~df_anterior['N° do imóvel'].isin(df_atual['N° do imóvel'])]
    # st.dataframe(imoveis_removidos)
    
    # print("\n\nREMOVIDOS\n\n")
    # print(imoveis_removidos)
    
    df_atualizado = pd.concat([df_anterior, novos_imoveis, imoveis_com_alteracao])

    print(novos_imoveis)
    #df_atualizado = pd.concat([df_atualizado, imoveis_removidos]).drop_duplicates(keep=False)
    if (novos_imoveis is not None and not novos_imoveis.empty) or (imoveis_com_alteracao is not None and imoveis_com_alteracao.empty):
        df_atualizado.to_csv(ARQUIVO_DADOS_RECENTES, index=False)
        return novos_imoveis
    
    df_atualizado.to_csv(ARQUIVO_DADOS_RECENTES, index=False)
        
        
    #     # print(len(df_atualizado))
        

    # df_atual = format_data_frame(df_atual, novos_imoveis=True)
    # df_atual.to_csv(ARQUIVO_DADOS_RECENTES, index=False)

    return pd.DataFrame()

def formatar_novos_imoveis(df_novos):
    formatted_string = ""
    for index, row in df_novos.iterrows():
        image_url = f"https://venda-imoveis.caixa.gov.br/fotos/F{row['N° do imóvel']}21.jpg"
        formatted_string += (
            #f'![Alt text]({image_url} "a title")'
            f"N° do Imóvel: {row['N° do imóvel']}\n"
            f"Cidade: {row['Cidade']}\n"
            f"Modalidade de Venda: {row['Modalidade de venda']}\n"
            f"Tipo de Imóvel: {row['Tipo de Imóvel']}\n"
            f"Descrição: {row['Descrição']}\n"
            f"Preço: {locale.currency(row['Preço'], grouping=True)}\n"
            f"Valor de Avaliação: {locale.currency(row['Valor de avaliação'], grouping=True)}\n"
            f"Desconto: {row['Desconto']}%\n"
            f"Endereço: {row['Endereço']}\n"
            f"Link de Acesso: {row['Link de acesso']}\n"
            f"Matrícula: https://venda-imoveis.caixa.gov.br/editais/matricula/DF/{row['N° do imóvel']}.pdf\n"
            "---------------------------------------\n"
        )
    return formatted_string

def format_data_frame(df_original, novos_imoveis = False):
    try:
        df = df_original.copy()
        df.columns = [col.strip() for col in df.columns]
        #print(df)
        df["N° do imóvel"] = df["N° do imóvel"].astype(str).str.zfill(13)
        
        
        df["Preço"] = df["Preço"].apply(lambda x: pd.to_numeric(x.replace(".", "").replace(",", "."), errors="coerce") if isinstance(x, str) else x)
        df["Valor de avaliação"] = df["Valor de avaliação"].apply(lambda x: pd.to_numeric(x.replace(".", "").replace(",", "."), errors="coerce") if isinstance(x, str) else x)

        df["Desconto"] = pd.to_numeric(
            df["Desconto"].astype(str).str.replace(",", "."), errors="coerce"
        )
        df["Tipo de Imóvel"] = df["Descrição"].apply(get_property_type)
        
        if novos_imoveis == True:
            print("NOVOS")
            with st.spinner('Buscando dados dos novos imóveis...'):
                print("Spiner")
                my_bar = st.progress(0, text=f"Buscando dados dos novos imóveis... 0/{len(df)}")
                df = df.reset_index(drop=True)
                for index, row in df.iterrows():
                    data_leilao, horario_leilao, aceita_fgts, aceita_financiamento, aceita_parcelamento, aceita_consorcio, tem_acao_judicial, acoes_judiciais = get_data_leilao(row['Link de acesso'])
                    
                    df.at[index, 'Data do Leilão'] = data_leilao
                    df.at[index, 'Horário do Leilão'] = horario_leilao
                    df.at[index, 'Aceita FGTS'] = aceita_fgts
                    df.at[index, 'Aceita Financiamento'] = aceita_financiamento
                    df.at[index, 'Aceita Parcelamento'] = aceita_parcelamento
                    df.at[index, 'Aceita Consorcio'] = aceita_consorcio
                    df.at[index, 'Tem Ação'] = tem_acao_judicial
                    df.at[index, 'Ações Judiciais'] = acoes_judiciais
                        
                        
                    progress_value = 0
                    my_bar.progress((index + 1)/len(df), text=f"Buscando dados dos novos imóveis... {index+1}/{len(df)}")
                
                my_bar.empty()

        return df
    
    except Exception as e:
        print("Erro: ", e)
        st.error(f"Ocorreu um erro: {e}")
        return None


def get_sidebar_filters(df):
    opcoes_ordenacao = [
        "Menor Preço",
        "Maior Preço",
        "Maior Desconto",
        "Menor Desconto",
        "Maior Avaliação",
        "Menor Avaliação",
        "Data mais próxima",
        "Data mais longe"
    ]
    ordenacao = st.sidebar.selectbox("Ordenar por", opcoes_ordenacao, 6)
    
    cidades_disponiveis = ["Todos"] + df["Cidade"].unique().tolist()
    cidade_filtro = st.sidebar.selectbox("Selecione a Cidade", cidades_disponiveis)

    modalidades_disponiveis = ["Todas"] + df["Modalidade de venda"].unique().tolist()
    modalidade_filtro = st.sidebar.selectbox(
        "Selecione a Modalidade de Venda", modalidades_disponiveis
    )

    tipos_disponiveis = ["Todos"] + df["Tipo de Imóvel"].unique().tolist()
    tipo_filtro = st.sidebar.selectbox("Selecione o Tipo de Imóvel", tipos_disponiveis)
    
    financimento_filtro = st.sidebar.selectbox("Aceita Financiamento", ["Todos", "Sim", "Não"])
    
    acao_filtro = st.sidebar.selectbox("Possui Ação Judicial", ["Todos", "Sim", "Não"])

    # Aplicando filtros ao DataFrame
    if cidade_filtro == "Todos":
        df_filtrado = df
    else:
        df_filtrado = df[df["Cidade"] == cidade_filtro]

    if modalidade_filtro != "Todas":
        df_filtrado = df_filtrado[
            df_filtrado["Modalidade de venda"] == modalidade_filtro
        ]

    if tipo_filtro != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Tipo de Imóvel"] == tipo_filtro]
        
    if financimento_filtro != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Aceita Financiamento"] == (financimento_filtro == "Sim")]
    
    if acao_filtro != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Tem Ação"] == (acao_filtro == "Sim")]

    # Aplicando ordenação ao DataFrame
    if ordenacao == "Maior Desconto":
        df_filtrado = df_filtrado.sort_values(by="Desconto", ascending=False)
    elif ordenacao == "Menor Desconto":
        df_filtrado = df_filtrado.sort_values(by="Desconto", ascending=True)
    elif ordenacao == "Maior Preço":
        df_filtrado = df_filtrado.sort_values(by="Preço", ascending=False)
    elif ordenacao == "Menor Preço":
        df_filtrado = df_filtrado.sort_values(by="Preço", ascending=True)
    elif ordenacao == "Maior Avaliação":
        df_filtrado = df_filtrado.sort_values(by="Valor de avaliação", ascending=False)
    elif ordenacao == "Menor Avaliação":
        df_filtrado = df_filtrado.sort_values(by="Valor de avaliação", ascending=True)
    elif ordenacao == "Data mais próxima":
        df_filtrado = df_filtrado.sort_values(by="Data do Leilão", ascending=True)
    elif ordenacao == "Data mais longe":
        df_filtrado = df_filtrado.sort_values(by="Data do Leilão", ascending=False)


    return df_filtrado

def imprimir_imoveis(df):
    for index, row in df.iterrows():
        imagem_url = (
            f"https://venda-imoveis.caixa.gov.br/fotos/F{row['N° do imóvel']}21.jpg"
        )
        modalidade_venda = row["Modalidade de venda"]
        cidade_bairro_uf = f"{row['Cidade']}, {row['Bairro']} - {row['UF']}"
        descricao = row["Descrição"]
        preco = locale.currency(row["Preço"], grouping=True).replace("$", "\$")
        avaliacao = locale.currency(row["Valor de avaliação"], grouping=True)
        desconto = row["Desconto"]
        endereco = row["Endereço"]
        link_acesso = row["Link de acesso"]
        matricula = f"https://venda-imoveis.caixa.gov.br/editais/matricula/{UF}/{row['N° do imóvel']}.pdf"
        data = row['Data do Leilão'] if 'Data do Leilão' in df.columns else ''
        data_formatada = row["Data do Leilão"].strftime("%d/%m/%Y") if "Data do Leilão" in df.columns and pd.notna(row["Data do Leilão"]) else ""
        horario = row['Horário do Leilão'] if "Horário do Leilão" in df.columns and pd.notna(row['Horário do Leilão']) else ""
        aceita_financiamento = f":green[**Sim**]" if row['Aceita Financiamento'] is True else f":red[**Não**]"
        aceita_fgts = f":green[**Sim**]" if row['Aceita FGTS'] is True else f":red[**Não**]"
        aceita_parcelamento = f":green[**Sim**]" if row['Aceita Parcelamento'] is True else f":red[**Não**]"
        aceita_consorcio = f":green[**Sim**]" if row['Aceita Consorcio'] is True else f":red[**Não**]"
        tem_acao = f":green[**Sim**]" if row['Tem Ação'] is True else f":red[**Não**]"
        lista_acoes = row['Ações Judiciais']
        col1, col2 = st.columns([1.5, 3])

        with col1:
            st.image(imagem_url)

        with col2:
            with st.expander(
                f"***{modalidade_venda}***\n\n**Data:** {data_formatada} - {horario}\n\n**Preço:** :green[**{preco}**] // **Avaliação:** {avaliacao}\n\n**Desconto:** {desconto}%\n\n{cidade_bairro_uf}\n\n**Financiamento:** {aceita_financiamento}\n\n**Ação Judicial:** {tem_acao}\n\n\n\n{descricao}"
            ):
                st.divider()
                st.write(f"**Modalidade de Venda:** {modalidade_venda}")
                st.write(f"**Preço Mínimo:** {preco}")
                st.write(f"**Avaliação:** {avaliacao}")
                st.write(f"**Desconto:** {desconto}%")
                st.write(f"**Endereço:** {endereco}")
                st.write(f"**Descrição:** {descricao}")
                st.write(f"**Link:** {link_acesso}")
                st.write(f"**Financiamento:** {aceita_financiamento}")
                st.write(f"**Ação Judicial:** {tem_acao}")
                st.write(f"{lista_acoes}")
                st.write(f"**FGTS:** {aceita_fgts}")
                st.write(f"**Parcelamento:** {aceita_parcelamento}")
                st.write(f"**Consórcio:** {aceita_consorcio}")
                
                
                # Exibir a data do leilão
                # if data_leilao:
                #     st.write(f"**Data do Leilão:** {data_leilao}")


                st.divider()
                st.write(f"Matrícula: ", matricula)
                st.image(imagem_url, caption="Imagem do Imóvel")
            
        st.divider()
            
    
    return

def format_email_novos_imoveis(novos_imoveis):
    alert_subject = 'Leilão Caixa DF - Novos Imóveis Adicionados!'
    alert_body = 'Foram adicionados novos imóveis. Verifique a lista para mais detalhes.'
    alert_body += '\n\nDetalhes dos Novos Imóveis:\n\n'
    alert_body += formatar_novos_imoveis(novos_imoveis)
    alert_body += '\n\nConfira em: https://leiloescaixadf.streamlit.app/\n\n'
    send_email(alert_subject, alert_body)



def main():
    
    st.set_page_config(
        page_title="Leilões Caixa - DF",
        page_icon="🏠"
    )
    
    st.title("Leilões de Imóveis Caixa - DF")
    
    locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
    
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    # Lendo o arquivo CSV diretamente da URL com a codificação 'latin1'
    url_csv = f"https://venda-imoveis.caixa.gov.br/listaweb/Lista_imoveis_{UF}.csv?245598167"
    # Defina os headers para simular um navegador
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    # Faça a solicitação GET com os headers
    response = requests.get(url_csv, headers=headers)

    # Verifique se a solicitação foi bem-sucedida
    if response.status_code == 200:
        # Carregue os dados CSV
        content = response.content.decode("latin1")
        df = pd.read_csv(io.StringIO(content), encoding="latin1", sep=";", skiprows=[0, 1])
        # st.dataframe(df)
        #print(df)
        df = format_data_frame(df)
    else:
        print("Falha ao obter o arquivo CSV")
    


    novos_imoveis = verificar_novos_imoveis(df)

    if not novos_imoveis.empty:
        # Enviar alerta por e-mail
        format_email_novos_imoveis(novos_imoveis)

        st.success(f"{len(novos_imoveis)} NOVO(S) IMÓVEL(IS) ADICIONADO(S)!")
        novos_imoveis["Data do Leilão"] = pd.to_datetime(novos_imoveis["Data do Leilão"], format="%d/%m/%Y", errors="coerce")
        imprimir_imoveis(novos_imoveis)
        st.divider()
    
    
    df_novo = pd.read_csv(ARQUIVO_DADOS_RECENTES)
    df_novo = format_data_frame(df_novo)
    
    df_novo["Data do Leilão"] = pd.to_datetime(df_novo["Data do Leilão"], format="%d/%m/%Y", errors="coerce")

    # Adicionando filtros ao menu lateral
    df_filtrado = get_sidebar_filters(df_novo)

    #st.dataframe(df_novo)
    st.write(f"Total de Imóveis: {len(df_filtrado)}")

    
    
    imprimir_imoveis(df_filtrado)

    st.divider()
    st.info("Desenvolvido por Arthur Wallace - 2024", icon="ℹ️")


if __name__ == "__main__":
    main()

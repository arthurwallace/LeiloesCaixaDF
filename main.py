import streamlit as st
import pandas as pd
import locale
from trycourier import Courier

ARQUIVO_DADOS_RECENTES = 'dados_recentes.csv'

def get_property_type(description):
    # Extract the property type from the description
    return description.split(",")[0].strip()


def send_email(subject, body):
    # Configurar Courier

    client = Courier(auth_token='pk_prod_XNB7MJGSQX4EMBHXE0K17EZE8FCA')

    response = client.send_message(
        message={
            "to": {"email": "arthur.wallace.silva@gmail.com"},
            "content": {"title": subject, "body": body}
            # ,
            # "data":{
            # "info": "Por favor, resete sua senha o quanto antes em:  " + reset_url + ""
            # }
        }
    )
    
    # st.success("E-mail enviado com sucesso!")
    
    # print(response)
    # # Verificar o status da resposta
    # if response["status"] == "delivered":
    #     st.success("E-mail enviado com sucesso!")
    # else:
    #     st.error(f"Falha ao enviar e-mail: {response['errors']}")

def verificar_novos_imoveis(df_atual):
    try:
        # Tentar carregar o arquivo de dados recentes
        df_anterior = pd.read_csv(ARQUIVO_DADOS_RECENTES)
        df_anterior["N° do imóvel"] = df_anterior["N° do imóvel"].astype(str).str.zfill(13)
        df_anterior["Preço"] = pd.to_numeric(
            df_anterior["Preço"].astype(str).str.replace(".", "").str.replace(",", "."),
            errors="coerce",
        )
        df_anterior["Valor de avaliação"] = pd.to_numeric(
            df_anterior["Valor de avaliação"].astype(str).str.replace(".", "").str.replace(",", "."),
            errors="coerce",
        )
        df_anterior["Desconto"] = pd.to_numeric(
            df_anterior["Desconto"].astype(str).str.replace(",", "."), errors="coerce"
        )

        df_anterior["Tipo de Imóvel"] = df_anterior["Descrição"].apply(get_property_type)
    
    except FileNotFoundError:
        # Se o arquivo não existir, assumir que não há dados anteriores
        df_anterior = pd.DataFrame()

    # Verificar se o DataFrame anterior está vazio
    if not df_anterior.empty:
        # Identificar novos imóveis
        novos_imoveis = df_atual[~df_atual['N° do imóvel'].isin(df_anterior['N° do imóvel'])]

        # print(f"DF Atual - {len(df_atual)}:")
        # print(df_atual[['N° do imóvel', 'Cidade', 'Modalidade de venda']].head())
        # print(f"DF Anterior - {len(df_anterior)}:")
        # print(df_anterior[['N° do imóvel', 'Cidade', 'Modalidade de venda']].head())
        # print(f"Novos Imóveis - {len(novos_imoveis)}:")
        # print(novos_imoveis[['N° do imóvel', 'Cidade', 'Modalidade de venda']].head())

        # Atualizar o arquivo de dados recentes apenas se houver novos imóveis
        if not novos_imoveis.empty:
            df_atual.to_csv(ARQUIVO_DADOS_RECENTES, index=False)

        return novos_imoveis

    # Salvar o DataFrame atual como o arquivo de dados recentes
    df_atual.to_csv(ARQUIVO_DADOS_RECENTES, index=False)

    return pd.DataFrame()


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
        matricula = f"https://venda-imoveis.caixa.gov.br/editais/matricula/DF/{row['N° do imóvel']}.pdf"

        st.image(imagem_url, width=200)
        with st.expander(
            f"{modalidade_venda}\n\n{cidade_bairro_uf}\n\n{descricao}\n\n**Preço:** {preco} // **Avaliação:** {avaliacao} // **Desconto:** {desconto}%"
        ):
            st.divider()
            st.write(f"**Modalidade de Venda:** {modalidade_venda}")
            st.write(f"**Preço Mínimo:** {preco}")
            st.write(f"**Avaliação:** {avaliacao}")
            st.write(f"**Desconto:** {desconto}%")
            st.write(f"**Endereço:** {endereco}")
            st.write(f"**Descrição:** {descricao}")
            st.write(f"**Link:** {link_acesso}")

            st.divider()
            st.write(f"Matrícula: ", matricula)
            st.image(imagem_url, caption="Imagem do Imóvel")
            
    
    return

def formatar_novos_imoveis(df_novos):
    # Crie uma string formatada com os detalhes dos novos imóveis
    formatted_string = ""
    for index, row in df_novos.iterrows():
        formatted_string += (
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


def main():
    st.title("Visualizador de Imóveis da Caixa")
    
    #send_email("Novos imóvel Caixa Adicionados!", "Teste email")

    # Lendo o arquivo CSV diretamente da URL com a codificação 'latin1'
    url_csv = "https://venda-imoveis.caixa.gov.br/listaweb/Lista_imoveis_DF.csv"
    df = pd.read_csv(url_csv, encoding="latin1", sep=";", skiprows=[0, 1])
    df.columns = [col.strip() for col in df.columns]

    df["N° do imóvel"] = df["N° do imóvel"].astype(str).str.zfill(13)
    df["Preço"] = pd.to_numeric(
        df["Preço"].astype(str).str.replace(".", "").str.replace(",", "."),
        errors="coerce",
    )
    df["Valor de avaliação"] = pd.to_numeric(
        df["Valor de avaliação"].astype(str).str.replace(".", "").str.replace(",", "."),
        errors="coerce",
    )
    df["Desconto"] = pd.to_numeric(
        df["Desconto"].astype(str).str.replace(",", "."), errors="coerce"
    )

    df["Tipo de Imóvel"] = df["Descrição"].apply(get_property_type)


    novos_imoveis = verificar_novos_imoveis(df)
    # print(novos_imoveis)
    if not novos_imoveis.empty:
        # Enviar alerta por e-mail
        alert_subject = 'Novos Imóveis Adicionados!'
        alert_body = 'Foram adicionados novos imóveis. Verifique a lista para mais detalhes.'
        # Adicione a string formatada ao corpo do e-mail
        alert_body += '\n\nDetalhes dos Novos Imóveis:\n\n'
        alert_body += formatar_novos_imoveis(novos_imoveis)
        #send_email(alert_subject, alert_body)
        print(alert_body)
        st.success(f"{len(novos_imoveis)} NOVO(S) IMÓVEL(IS) ADICIONADO(S)!")
        imprimir_imoveis(novos_imoveis)
        st.divider()
        
    # Adicionando filtros ao menu lateral
    cidades_disponiveis = ["Todos"] + df["Cidade"].unique().tolist()
    cidade_filtro = st.sidebar.selectbox("Selecione a Cidade", cidades_disponiveis)

    modalidades_disponiveis = ["Todas"] + df["Modalidade de venda"].unique().tolist()
    modalidade_filtro = st.sidebar.selectbox(
        "Selecione a Modalidade de Venda", modalidades_disponiveis
    )

    tipos_disponiveis = ["Todos"] + df["Tipo de Imóvel"].unique().tolist()
    tipo_filtro = st.sidebar.selectbox("Selecione o Tipo de Imóvel", tipos_disponiveis)

    # Adicionando opções de ordenação ao menu lateral
    opcoes_ordenacao = [
        "Menor Preço",
        "Maior Preço",
        "Maior Desconto",
        "Menor Desconto",
        "Maior Avaliação",
        "Menor Avaliação",
    ]
    ordenacao = st.sidebar.selectbox("Ordenar por", opcoes_ordenacao)

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

    st.info(f"Total de Imóveis: {len(df_filtrado)}")

    locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
    imprimir_imoveis(df_filtrado)

    st.divider()
    st.info("Desenvolvido por Arthur Wallace - 2024", icon="ℹ️")


if __name__ == "__main__":
    main()

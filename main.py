import streamlit as st
import pandas as pd
import locale


def get_property_type(description):
    # Extract the property type from the description
    return description.split(',')[0].strip()

def main():
    st.title('Visualizador de Imóveis da Caixa')
    
    # Lendo o arquivo CSV diretamente da URL com a codificação 'latin1'
    url_csv = 'https://venda-imoveis.caixa.gov.br/listaweb/Lista_imoveis_DF.csv'
    df = pd.read_csv(url_csv, encoding='latin1', sep=';', skiprows=[0, 1])
    df.columns = [col.strip() for col in df.columns]

    df['N° do imóvel'] = df['N° do imóvel'].astype(str).str.zfill(13)
    df['Preço'] = pd.to_numeric(df['Preço'].astype(str).str.replace('.', '').str.replace(',', '.'), errors='coerce')
    df['Valor de avaliação'] = pd.to_numeric(df['Valor de avaliação'].astype(str).str.replace('.', '').str.replace(',', '.'), errors='coerce')
    df['Desconto'] = pd.to_numeric(df['Desconto'].astype(str).str.replace(',', '.'), errors='coerce')

    df['Tipo de Imóvel'] = df['Descrição'].apply(get_property_type)
    
    # Adicionando filtros ao menu lateral
    cidades_disponiveis = ['Todos'] + df['Cidade'].unique().tolist()
    cidade_filtro = st.sidebar.selectbox('Selecione a Cidade', cidades_disponiveis)

    modalidades_disponiveis = ['Todas'] + df['Modalidade de venda'].unique().tolist()
    modalidade_filtro = st.sidebar.selectbox('Selecione a Modalidade de Venda', modalidades_disponiveis)

    tipos_disponiveis = ['Todos'] + df['Tipo de Imóvel'].unique().tolist()
    tipo_filtro = st.sidebar.selectbox('Selecione o Tipo de Imóvel', tipos_disponiveis)

    # Adicionando opções de ordenação ao menu lateral
    opcoes_ordenacao = ['Menor Preço', 'Maior Preço','Maior Desconto', 'Menor Desconto', 'Maior Avaliação', 'Menor Avaliação']
    ordenacao = st.sidebar.selectbox('Ordenar por', opcoes_ordenacao)

    # Aplicando filtros ao DataFrame
    if cidade_filtro == 'Todos':
        df_filtrado = df
    else:
        df_filtrado = df[df['Cidade'] == cidade_filtro]

    if modalidade_filtro != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['Modalidade de venda'] == modalidade_filtro]
        
    if tipo_filtro != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Tipo de Imóvel'] == tipo_filtro]

    # Aplicando ordenação ao DataFrame
    if ordenacao == 'Maior Desconto':
        df_filtrado = df_filtrado.sort_values(by='Desconto', ascending=False)
    elif ordenacao == 'Menor Desconto':
        df_filtrado = df_filtrado.sort_values(by='Desconto', ascending=True)
    elif ordenacao == 'Maior Preço':
        df_filtrado = df_filtrado.sort_values(by='Preço', ascending=False)
    elif ordenacao == 'Menor Preço':
        df_filtrado = df_filtrado.sort_values(by='Preço', ascending=True)
    elif ordenacao == 'Maior Avaliação':
        df_filtrado = df_filtrado.sort_values(by='Valor de avaliação', ascending=False)
    elif ordenacao == 'Menor Avaliação':
        df_filtrado = df_filtrado.sort_values(by='Valor de avaliação', ascending=True)

    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    for index, row in df_filtrado.iterrows():
        imagem_url = f"https://venda-imoveis.caixa.gov.br/fotos/F{row['N° do imóvel']}21.jpg"
        modalidade_venda = row['Modalidade de venda']
        cidade_bairro_uf = f"{row['Cidade']}, {row['Bairro']} - {row['UF']}"
        descricao = row['Descrição']
        preco = locale.currency(row['Preço'], grouping=True).replace("$", "\$")
        avaliacao = locale.currency(row['Valor de avaliação'], grouping=True)
        desconto = row['Desconto']
        endereco = row['Endereço']
        link_acesso = row['Link de acesso']
        matricula = f"https://venda-imoveis.caixa.gov.br/editais/matricula/DF/{row['N° do imóvel']}.pdf"

        st.image(imagem_url, width=200)
        with st.expander(f"{modalidade_venda}\n\n{cidade_bairro_uf}\n\n{descricao}\n\n**Preço:** {preco} // **Avaliação:** {avaliacao} // **Desconto:** {desconto}%"):
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
            st.image(imagem_url, caption='Imagem do Imóvel')
            
        
    
    
    st.divider()
    st.info('Desenvolvido por Arthur Wallace - 2024', icon="ℹ️")

if __name__ == "__main__":
    main()

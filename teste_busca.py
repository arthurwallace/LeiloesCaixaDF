import requests
from bs4 import BeautifulSoup
import re

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
                print(segment_text)
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
        
        return data_leilao, horario_leilao, aceita_fgts, aceita_financiamento, aceita_parcelamento, aceita_consorcio, tem_acao_judicial, acoes_judiciais
    except Exception as e:
        print(f"Erro ao obter data do leilão: {e}")
        return None, None, False, False, False, False, False, False, ''

# Exemplo de uso da função
url = "https://venda-imoveis.caixa.gov.br/sistema/detalhe-imovel.asp?hdnOrigem=index&hdnimovel=0000010143174"
data_leilao, horario_leilao, aceita_fgts, aceita_financiamento, aceita_parcelamento, aceita_consorcio, tem_acao_judicial, acoes_judiciais = get_data_leilao(url)
print(data_leilao, horario_leilao, aceita_fgts, aceita_financiamento, aceita_parcelamento, aceita_consorcio, tem_acao_judicial, acoes_judiciais)
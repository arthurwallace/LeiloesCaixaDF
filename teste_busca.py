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
        icone_datas = soup.find_all('i', {'class': 'fa-gavel'})
        
        texto_valores = soup.find('div', class_='content').get_text(strip=True)
        
        # Verificar se o elemento foi encontrado
        data_segundo_leilao = None
        horario_segundo_leilao = None
        valor_segundo_leilao = None
        if icone_datas:
            for dateTxt in icone_datas:
            # Extrair o texto do elemento <span> pai
                parent_span = dateTxt.find_parent('span')
                data_text = parent_span.get_text(strip=True)
                print(data_text, "\n")

                # Usar expressão regular para extrair data e horário
                match_data_horario = re.search(r'(\d{2}/\d{2}/\d{4}) - (\d{2}h\d{2})', data_text)
                if match_data_horario:
                    if '2º Leilão' in data_text:
                        print("2º Leilão---")
                        data_segundo_leilao = match_data_horario.group(1)
                        horario_segundo_leilao = match_data_horario.group(2)
                    else:
                        data_leilao = match_data_horario.group(1)
                        horario_leilao = match_data_horario.group(2)
                else:
                    print("Padrão de data não encontrado.")
                    data_leilao, horario_leilao = None, None
                
                
            match_valor_segundo_leilao = re.search(r'Valor mínimo de venda 2º Leilão: R\$\s*([\d,.]+)', texto_valores)
            if match_valor_segundo_leilao:
                valor_segundo_leilao_text = match_valor_segundo_leilao.group(1)
                valor_segundo_leilao = float(valor_segundo_leilao_text.replace('.', '').replace(',', '.'))
                print(valor_segundo_leilao)
        else:
            print("Elemento não encontrado.")
            data_leilao, horario_leilao = None, None
            
        print("1º Leilão: ", data_leilao, horario_leilao)
        print("2º Leilão: ", data_segundo_leilao, horario_segundo_leilao, valor_segundo_leilao)
        
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
                print("\n", segment_text)
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
        
        return data_leilao, horario_leilao, aceita_fgts, aceita_financiamento, aceita_parcelamento, aceita_consorcio, tem_acao_judicial, acoes_judiciais, data_segundo_leilao, horario_segundo_leilao, valor_segundo_leilao
    except Exception as e:
        print(f"Erro ao obter data do leilão: {e}")
        return None, None, False, False, False, False, False, False, ''

# Exemplo de uso da função
url = "https://venda-imoveis.caixa.gov.br/sistema/detalhe-imovel.asp?hdnOrigem=index&hdnimovel=8444416706895"
data_leilao, horario_leilao, aceita_fgts, aceita_financiamento, aceita_parcelamento, aceita_consorcio, tem_acao_judicial, acoes_judiciais = get_data_leilao(url)
print(data_leilao, horario_leilao, aceita_fgts, aceita_financiamento, aceita_parcelamento, aceita_consorcio, tem_acao_judicial, acoes_judiciais)
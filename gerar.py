# Instalações requeridas
# pip install prettytable

# Importações
from datetime import datetime
import json
import os
import random
import sys
from prettytable import PrettyTable


# Escolhas do usuário
while True:
    escolha = input('''O quê você quer gerar?

[1] Armadilhas
[2] Tesouros
[q] Quitar

Escolha -> ''')

    if escolha == '1':
        NOME_FONTE = 'armadilhas.json'
        break
    if escolha == '2':
        NOME_FONTE = 'tesouros.json'
        break
    if escolha == 'q':
        sys.exit()

quantia_gerada = int(input('Quantia? -> '))


# File function
def ler_fonte(nome):
    with open(('./dados/{}').format(nome), 'r', encoding='latin-1') as file:
        return json.loads(file.read())


# Read chosen feed
ARQUIVO_FONTE = ler_fonte(NOME_FONTE)


# Random dado roll based on autodetected number of faces
def rolar_dado(atributo):
    ultimo_valor = list(atributo.keys())[-1].split('-')
    valor_mais_alto = ultimo_valor[1] if len(ultimo_valor) > 1 else ultimo_valor[0]
    dado = int(valor_mais_alto) if valor_mais_alto.isnumeric() else 6

    return random.randint(1, dado)


# Detect if rolled dado is inside rollable range
def dado_equivalente(dado, alcance_de_rolagem):
    return alcance_de_rolagem and (
        dado is int(alcance_de_rolagem[0]) or (
            len(alcance_de_rolagem) > 1
            and int(alcance_de_rolagem[0]) <= dado <= int(alcance_de_rolagem[1])
        )
    )


# Fução principal
def construir():
    titulos = []
    celulas = []

    # Definir qual ação tomar no rolagem de dado
    def rolar_acao(atributo):
        if '.json' in atributo:
            atributo = ler_fonte(atributo)

        if isinstance(atributo, dict):
            resultado_da_rolagem = rolar_dado(atributo)

            for nome, valor in atributo.items():
                pegar_atributo(nome, valor, resultado_da_rolagem)
        elif isinstance(atributo, list):
            celulas.append('\n'.join(atributo))
        else:
            celulas.append(atributo)

    # Função recursiva
    def pegar_atributo(titulo, atributo, dado):
        possivel_rolar = '-' in titulo or titulo.isnumeric()

        if not possivel_rolar and titulo != 'Value':
            titulos.append(titulo)

        if not possivel_rolar or dado_equivalente(dado, titulo.split('-')):
            rolar_acao(atributo)

    # Começar recursão
    for titulo, atributo in ARQUIVO_FONTE.items():
        resultado_da_rolagem = rolar_dado(atributo)
        pegar_atributo(titulo, atributo, resultado_da_rolagem)

    return (titulos, celulas)


# Geração final da lista
def gerar():
    # Criar diretório "resultados" se não existe
    if not os.path.exists('resultados'):
        os.makedirs('resultados')

    # Criar arquivo
    file = open('./resultados/{}_{}.txt'.format(
        NOME_FONTE,
        datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    ), mode='a', encoding='latin-1')

    # Criar quantia requerida de entradas
    for indice in range(quantia_gerada):
        # Desconstrução de entrada
        (titulos, celulas) = construir()

        # Gerar tabela de entrada
        pretty_table = PrettyTable()
        pretty_table.field_names = titulos
        pretty_table.add_row(celulas)

        # Escrever tabela pra arquivo
        file.write(str(pretty_table) + '\n')

        # Incrementar loop
        indice += 1

    # Salvar no disco
    file.close()


# Run
gerar()

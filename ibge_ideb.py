import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import streamlit as st
import pandas as pd

# Função para carregar e processar os dados
@st.cache_data
def load_data():
    piramide_etaria = pd.read_csv('Censo 2022 - Pirâmide etária - Embu-Guaçu (SP).csv', sep=';')
    dados_alunos = pd.read_csv('TbAluno.csv', sep=',')
    evolucao_ideb = pd.read_excel('evolucao_ideb.xlsx')
    return piramide_etaria, dados_alunos, evolucao_ideb

def main():
    piramide_etaria, dados_alunos, evolucao_ideb = load_data()

## Limpeza dos dados

# Retirar colunas desnecessárias para análise
piramide_etaria.drop(['Município', 'Sigla UF', 'Código do Município', 'codMun'], axis=1, inplace=True)

# Criar coluna com a soma da população por grupo de idade
pop_list=['População feminina(pessoas)', 'População masculina(pessoas)']
piramide_etaria['População por idade']=piramide_etaria[pop_list].sum(axis=1)

# Calcular percentuais por faixa etária
pop_total = piramide_etaria['População por idade'].sum()
piramide_etaria['Percentual'] = (piramide_etaria['População por idade'] / pop_total * 100)

# Selecionar faixas etárias atendidas pela Passos Mágicos: 7 a 26 anos (PEDE, 2022)
piramide2 = piramide_etaria.set_index(['Grupo de idade']).T
idade_escolar = ['5 a 9 anos', '10 a 14 anos', '15 a 19 anos', '20 a 24 anos']
pop_escolar = piramide2[idade_escolar]

# Calcular o total da população em idade escolar
total_pop_escolar = pop_escolar.loc['População por idade'].sum()

# Ordenar a população em idade escolar em ordem ascendente
pop_escolar_ordenada = pop_escolar.sort_values(by='População por idade', axis=1)

# Selecionar colunas para cálculo da idade dos alunos
colunas_interesse = ['IdAluno', 'DataNascimento']
idade_alunos = dados_alunos[colunas_interesse]

# Retirar da tabela a linha com a migração incorreta
idade_alunos2 = idade_alunos.drop(793)

# Conversão da data de nascimento em data
idade_alunos2['DataNascimento'] = pd.to_datetime(idade_alunos2['DataNascimento'])

# Cálculo da idade
idade_alunos2['Idade']=2022-idade_alunos2['DataNascimento'].dt.year

# Agrupar alunos por faixa etária do IBGE
fx_etaria = [
    (idade_alunos2['Idade'] >= 5) & (idade_alunos2['Idade'] <= 9),
    (idade_alunos2['Idade'] >= 10) & (idade_alunos2['Idade'] <= 14),
    (idade_alunos2['Idade'] >= 15) & (idade_alunos2['Idade'] <= 19),
    (idade_alunos2['Idade'] >= 20) & (idade_alunos2['Idade'] <= 24),
    (idade_alunos2['Idade'] >= 25)
]

grupos = ['05 a 09 anos', '10 a 14 anos', '15 a 19 anos', '20 a 24 anos', '25 anos ou mais']
idade_alunos2['Grupo de idade'] = np.select(fx_etaria, grupos)
qtde_alunos_idade = idade_alunos2['Grupo de idade'].value_counts().sort_index()
# Renomear o grupo 5 a 9 anos

pop_escolar.rename(columns={'5 a 9 anos': '05 a 09 anos'}, inplace=True)
pop_escolar

pop_escolar2 = pop_escolar.transpose()
pop_escolar2

pop_escolar2['Alunos Passos Mágicos'] = qtde_alunos_idade
pop_escolar2

# Cálculo do percentual da população de Embu-Guaçu atendida pela ONG Passos Mágicos
pop_escolar2['População atendida'] = (pop_escolar2['Alunos Passos Mágicos'] / pop_escolar2['População por idade']) * 100
percentual_total = pop_escolar2['Alunos Passos Mágicos'].sum() / pop_escolar2['População por idade'].sum() * 100

# Convert 'dependencia_id' to string type
evolucao_ideb['dependencia_id'] = evolucao_ideb['dependencia_id'].astype(str)

# Use a dictionary for mapping replacement values
replace_dict = {'1': 'Federal', '2': 'Estadual', '3': 'Municipal', '4': 'Privada', '5': 'Pública'}
evolucao_ideb['dependencia_id'] = evolucao_ideb['dependencia_id'].replace(replace_dict)
evolucao_ideb.groupby(evolucao_ideb['ano'])['ciclo_id']


# Função para gerar gráficos
def plot_piramide_etaria(piramide_etaria):
    st.header("Pirâmide Etária de Embu-Guaçu")

    piramide_etaria.drop(['Município', 'Sigla UF', 'Código do Município', 'codMun'], axis=1, inplace=True)
    piramide_etaria['População por idade'] = piramide_etaria[['População feminina(pessoas)', 'População masculina(pessoas)']].sum(axis=1)
    piramide_etaria['Percentual'] = (piramide_etaria['População por idade'] / piramide_etaria['População por idade'].sum() * 100)

    idade_escolar = ['5 a 9 anos', '10 a 14 anos', '15 a 19 anos', '20 a 24 anos']
    pop_escolar = piramide_etaria[piramide_etaria['Grupo de idade'].isin(idade_escolar)].set_index('Grupo de idade').transpose()
    total_pop_escolar = pop_escolar.loc['População por idade'].sum()
    pop_escolar_ordenada = pop_escolar.sort_values(by='População por idade', axis=1)

    fig, axes = plt.subplots(1, 2, figsize=(20, 10))

    # Pirâmide etária de Embu-Guaçu
    axes[0].barh(piramide_etaria['Grupo de idade'], piramide_etaria['População por idade'], color='skyblue')
    axes[0].set_title('Pirâmide Etária de Embu-Guaçu', fontsize=16)
    axes[0].set_xlabel('População', fontsize=14)
    axes[0].set_ylabel('Grupo de Idade', fontsize=14)
    axes[0].tick_params(axis='both', labelsize=12)
    for i, v in enumerate(piramide_etaria['Percentual']):
        axes[0].text(piramide_etaria['População por idade'][i] / 2, i, f'{v:.1f}%', va='center', ha='center', color='darkblue', fontsize=12)

    # Pirâmide etária da população em idade escolar
    axes[1].barh(pop_escolar_ordenada.columns, pop_escolar_ordenada.loc['População por idade'], color='coral')
    axes[1].set_title('Pirâmide Etária da População em Idade Escolar de Embu-Guaçu', fontsize=16)
    axes[1].set_xlabel('População', fontsize=14)
    axes[1].set_ylabel('Grupo de Idade', fontsize=14)
    axes[1].tick_params(axis='both', labelsize=12)
    for i, v in enumerate(pop_escolar_ordenada.loc['População por idade']):
        percentual_escolar = v / total_pop_escolar * 100
        axes[1].text(v / 2, i, f'{percentual_escolar:.1f}%', va='center', ha='center', color='saddlebrown', fontsize=12)

    plt.tight_layout()
    st.pyplot(fig)

def plot_alunos(dados_alunos):
    st.header("Idade dos Alunos da Passos Mágicos")

    idade_alunos = dados_alunos[['IdAluno', 'DataNascimento']]
    idade_alunos['DataNascimento'] = pd.to_datetime(idade_alunos['DataNascimento'])
    idade_alunos['Idade'] = 2022 - idade_alunos['DataNascimento'].dt.year
    idade_alunos['Grupo de idade'] = pd.cut(idade_alunos['Idade'], bins=[4, 9, 14, 19, 24, np.inf], labels=['05 a 09 anos', '10 a 14 anos', '15 a 19 anos', '20 a 24 anos', '25 anos ou mais'])

    qtde_alunos_idade = idade_alunos['Grupo de idade'].value_counts().sort_index()

    cores_pastel = ['#FFB6C1', '#FFDAB9', '#98FB98', '#ADD8E6', '#E6E6FA']
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(qtde_alunos_idade.index, qtde_alunos_idade.values, color=cores_pastel)
    ax.set_ylabel('Quantidade de alunos')
    ax.set_xlabel('Grupo de idade')
    ax.set_title('Quantidade de alunos da Passos Mágicos por faixa etária')
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.5, yval, ha='center', va='bottom')

    st.pyplot(fig)

def plot_percentual(pop_escolar, qtde_alunos_idade):
    st.header("Percentual de População Atendida pela Passos Mágicos")

    pop_escolar.rename(columns={'5 a 9 anos': '05 a 09 anos'}, inplace=True)
    pop_escolar2 = pop_escolar.transpose()
    pop_escolar2['Alunos Passos Mágicos'] = qtde_alunos_idade
    pop_escolar2['População atendida'] = (pop_escolar2['Alunos Passos Mágicos'] / pop_escolar2['População por idade']) * 100

    percentual_total = pop_escolar2['Alunos Passos Mágicos'].sum() / pop_escolar2['População por idade'].sum() * 100
    st.write(f"Percentual total de alunos atendidos pela Passos Mágicos: {percentual_total:.1f}%")

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(pop_escolar2.index, pop_escolar2['População atendida'], color='lightgreen')
    ax.set_xlabel('Grupo de Idade')
    ax.set_ylabel('Percentual de População Atendida')
    ax.set_title('Percentual da População em Idade Escolar de Embu-Guaçu atendida pela Passos Mágicos')
    ax.set_ylim(0, 100)
    for i, v in enumerate(pop_escolar2['População atendida']):
        ax.text(i, v + 2, f'{v:.1f}%', ha='center', fontsize=10)

    st.pyplot(fig)

def plot_ideb(evolucao_ideb):
    st.header("IDEB de Embu-Guaçu")

    evolucao_ideb['dependencia_id'] = evolucao_ideb['dependencia_id'].astype(str)
    replace_dict = {'1': 'Federal', '2': 'Estadual', '3': 'Municipal', '4': 'Privada', '5': 'Pública'}
    evolucao_ideb['dependencia_id'] = evolucao_ideb['dependencia_id'].replace(replace_dict)

    grouped_data = evolucao_ideb.groupby(['ano', 'ciclo_id'])['ideb'].mean().unstack()
    grouped_data = grouped_data[['AI', 'AF', 'EM']]

    ax = grouped_data.plot(kind='bar', figsize=(12, 5), colormap='Pastel1')
    plt.title('IDEB por ciclo de ensino em Embu-Guaçu')
    plt.xlabel('Ano')
    plt.ylabel('IDEB Médio')
    plt.legend(title='Ciclo de Ensino', loc='upper center')
    plt.xticks(rotation=0)
    for container in ax.containers:
        ax.bar_label(container, fmt='%.2f', label_type='edge')

    st.pyplot()

def main():
    st.title("Análise de Dados de Educação em Embu-Guaçu")

    piramide_etaria, dados_alunos, evolucao_ideb = load_data()

    plot_piramide_etaria(piramide_etaria)
    plot_alunos(dados_alunos)

    idade_alunos = dados_alunos[['IdAluno', 'DataNascimento']]
    idade_alunos['DataNascimento'] = pd.to_datetime(idade_alunos['DataNascimento'])
    idade_alunos['Idade'] = 2022 - idade_alunos['DataNascimento'].dt.year
    idade_alunos['Grupo de idade'] = pd.cut(idade_alunos['Idade'], bins=[4, 9, 14, 19, 24, np.inf], labels=['05 a 09 anos', '10 a 14 anos', '15 a 19 anos', '20 a 24 anos', '25 anos ou mais'])
    qtde_alunos_idade = idade_alunos['Grupo de idade'].value_counts().sort_index()
    pop_escolar = piramide_etaria[piramide_etaria['Grupo de idade'].isin(['5 a 9 anos', '10 a 14 anos', '15 a 19 anos', '20 a 24 anos'])].set_index('Grupo de idade').transpose()
    pop_escolar.rename(columns={'5 a 9 anos': '05 a 09 anos'}, inplace=True)
    plot_percentual(pop_escolar, qtde_alunos_idade)
    plot_ideb(evolucao_ideb)

if __name__ == "__main__":
    main()

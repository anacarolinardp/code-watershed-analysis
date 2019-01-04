##Hidrotool=group
##Basic Analysis=name
##Drenagem=vector line
##Bacia=vector polygon
##Resultados=output file

from qgis.core import *
import math


'''Definindo funcoes'''

def relacao_bifurcacao(valores_hierarquia):
    posicao = 0
    rel_bifurcacao = []
    while posicao < len(valores_hierarquia) - 1:
        sucessor = posicao + 1
        calculo = valores_hierarquia[posicao] / valores_hierarquia[sucessor]
        rel_bifurcacao.append(calculo)
        posicao += 1

    rb = []
    valor_ordem = 1
    posicao_rb = 0
    while valor_ordem < len(valores_hierarquia):
        sucessor_ordem = valor_ordem + 1
        rb.append('- Relacao de ordem {} / {}: {}.'.format(valor_ordem, sucessor_ordem, rel_bifurcacao[posicao_rb]))
        valor_ordem += 1
        posicao_rb +=1
    
    return rb

def densidade_rios(valor_total_rios, valor_area_bacia):
    dr = valor_total_rios / valor_area_bacia
    return dr

def densidade_drenagem(valor_comprimento_canais, valor_area_bacia):
    dd = valor_comprimento_canais / valor_area_bacia
    return dd

def densidade_segmentos(valor_total_segmentos, valor_area_bacia): 
    ds = valor_total_segmentos / valor_area_bacia
    return ds

def coeficiente_manutencao(valor_densidade_drenagem):  
    cm = (1 / valor_densidade_drenagem) * 1000
    return cm

def ext_m_escoamento(valor_area_bacia, valor_comprimento_canais):
    em = valor_area_bacia / (4 * valor_comprimento_canais)
    return em

def indice_circularidade(valor_perimetro_bacia, valor_area_bacia):
    raio_circulo = valor_perimetro_bacia / (2 * math.pi)
    area_circulo = math.pi * (raio_circulo ** 2)
    ic = valor_area_bacia / area_circulo
    return ic

def coeficiente_compacidade(valor_perimetro_bacia, valor_area_bacia):
    kc = 0.28 * (valor_perimetro_bacia / math.sqrt(valor_area_bacia))
    return kc

def fator_forma(valor_area_bacia, valor_comprimento_bacia):
    kf = valor_area_bacia / (valor_comprimento_bacia ** 2)
    return kf

# Carregando as camadas da rede de drenagem e da bacia hidrografica
dlayer = QgsVectorLayer(Drenagem, "drenagem", "ogr")
blayer = QgsVectorLayer(Bacia, "bacia", "ogr")

'''Extraindo dados da rede de drenagem'''

# Acessando atributos da drenagem
dfeatures = dlayer.getFeatures()
# Listando os valores por coluna
listdfeatures = list(zip(*dfeatures))

# Valor de ordem minimo e maximo
maxordem = max(listdfeatures[0])
minordem = min(listdfeatures[0])

# Contando feicoes pela hierarquia fluvial
ordem = minordem
hierarquia = []
while (ordem <= maxordem):
    contagem = listdfeatures[0].count(ordem)
    hierarquia.append(contagem)
    ordem += 1

# Total de rios - quantidade de rios de primeira ordem
totalrios = hierarquia[0]

# Total de segmentos - soma dos rios de todas as ordens
totalsegmentos = math.fsum(hierarquia)

# Comprimento dos canais - soma de todos os elementos da lista com comprimento dos canais
comprimentocanais = math.fsum(listdfeatures[1])

# Comprimento medio dos canais - razao entre comprimento dos canais e total de segmentos
comprimentomcanais = comprimentocanais / totalsegmentos

# Criando lista com texto e contagem de canais de cada ordem
posicao_hf = 0
dados_hf = []
while posicao_hf < maxordem:
    order = posicao_hf + 1
    dados_hf.append('- Canais de ordem {}: {}.'.format(order, hierarquia[posicao_hf]))
    posicao_hf += 1


'''Extraindo dados da bacia hidrografica'''

areabh = blayer.getValues(blayer.fields()[0].name())[0]
perimetrobh = blayer.getValues(blayer.fields()[1].name())[0]
comprimentobh = blayer.getValues(blayer.fields()[2].name())[0]



'''Usando as funcoes'''

rb = relacao_bifurcacao(hierarquia)
dr = densidade_rios(totalrios, areabh)
dd = densidade_drenagem(comprimentocanais, areabh)
ds = densidade_segmentos(totalsegmentos, areabh) 
cm = coeficiente_manutencao(dd)
em = ext_m_escoamento(areabh, comprimentocanais)
ic = indice_circularidade(perimetrobh, areabh)
kc = coeficiente_compacidade(perimetrobh, areabh)
kf = fator_forma(areabh, comprimentobh)


'''Exportando resultados'''

resultado = open(Resultados, 'wt')
texto = []
texto.append('Quantidade de rios: {:.0f}\n'.format(totalrios)) 
texto.append('Quantidade de segmentos: {:.0f}\n'.format(totalsegmentos)) 
texto.append('Comprimento total dos canais: {:.2f}\n'.format(comprimentocanais))
texto.append('Comprimento medio dos canais: {:.2f}\n'.format(comprimentomcanais))
texto.append('Hierarquia fluvial:\n')
for z in range(len(dados_hf)):
    texto.append('{} \n'.format(dados_hf[z]))
for z in range(len(rb)):
    texto.append('{} \n'.format(rb[z]))
texto.append('Densidade de rios: {:.2f}\n'.format(dr))
texto.append('Densidade de drenagem: {:.2f}\n'.format(dd))
texto.append('Densidade de segmentos: {:.2f}\n'.format(ds))
texto.append('Coeficiente de manutenÃÂÃÂ§ÃÂÃÂ£o: {:.2f}\n'.format(cm))
texto.append('ExtensÃÂÃÂ£o media do escoamento superficial: {:.2f}\n'.format(em))
texto.append('IÃÂndice de circularidade: {:.2f}\n'.format(ic))
texto.append('Coeficiente de compacidade: {:.2f}\n'.format(kc))
texto.append('Fator de forma: {:.2f}\n'.format(kf))
resultado.writelines(texto)
resultado.close()


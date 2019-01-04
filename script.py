##Hidrotool=group
##Basic Analysis=name
##Drenagem=vector line
##Bacia=vector polygon
##Resultados=output file

from qgis.core import *
import math


'''Functions'''

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
        rb.append('- Order relation {} / {}: {}.'.format(valor_ordem, sucessor_ordem, rel_bifurcacao[posicao_rb]))
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

# Loading dreinage and watershed layers
dlayer = QgsVectorLayer(Drenagem, "drenagem", "ogr")
blayer = QgsVectorLayer(Bacia, "bacia", "ogr")

'''Extracting dreinage data'''

# Dreinage attributes
dfeatures = dlayer.getFeatures()
# Listing values per column
listdfeatures = list(zip(*dfeatures))

# Max and min order values
maxordem = max(listdfeatures[0])
minordem = min(listdfeatures[0])

# Counting features of channel hierarchy
ordem = minordem
hierarquia = []
while (ordem <= maxordem):
    contagem = listdfeatures[0].count(ordem)
    hierarquia.append(contagem)
    ordem += 1

# Total of rivers - quantity of first order rivers
totalrios = hierarquia[0]

# Total segments - sum of rivers of all orders
totalsegmentos = math.fsum(hierarquia)

# Channels Length - The sum of all the elements in the list that has length values ​​of channels ('Length' field)
comprimentocanais = math.fsum(listdfeatures[1])

# Average length of channels - ratio between channel length and total segments
comprimentomcanais = comprimentocanais / totalsegmentos

# Creating list with text and channel count of each order
posicao_hf = 0
dados_hf = []
while posicao_hf < maxordem:
    order = posicao_hf + 1
    dados_hf.append('- Channel order {}: {}.'.format(order, hierarquia[posicao_hf]))
    posicao_hf += 1


'''Extracting watershed data'''

areabh = blayer.getValues(blayer.fields()[0].name())[0]
perimetrobh = blayer.getValues(blayer.fields()[1].name())[0]
comprimentobh = blayer.getValues(blayer.fields()[2].name())[0]


'''Using functions'''

rb = relacao_bifurcacao(hierarquia)
dr = densidade_rios(totalrios, areabh)
dd = densidade_drenagem(comprimentocanais, areabh)
ds = densidade_segmentos(totalsegmentos, areabh) 
cm = coeficiente_manutencao(dd)
em = ext_m_escoamento(areabh, comprimentocanais)
ic = indice_circularidade(perimetrobh, areabh)
kc = coeficiente_compacidade(perimetrobh, areabh)
kf = fator_forma(areabh, comprimentobh)


'''Output results'''

resultado = open(Resultados, 'wt')
texto = []
texto.append('Number of rivers: {:.0f}\n'.format(totalrios)) 
texto.append('Number of segments: {:.0f}\n'.format(totalsegmentos)) 
texto.append('Channels length: {:.2f}\n'.format(comprimentocanais))
texto.append('Average channels length: {:.2f}\n'.format(comprimentomcanais))
texto.append('Channel hierarchy:\n')
for z in range(len(dados_hf)):
    texto.append('{} \n'.format(dados_hf[z]))
for z in range(len(rb)):
    texto.append('{} \n'.format(rb[z]))
texto.append('Density of rivers: {:.2f}\n'.format(dr))
texto.append('Density of dreinage: {:.2f}\n'.format(dd))
texto.append('Density of segments: {:.2f}\n'.format(ds))
texto.append('Coefficient of maintenance: {:.2f}\n'.format(cm))
texto.append('Mean extension of surface runoff: {:.2f}\n'.format(em))
texto.append('Circularity index: {:.2f}\n'.format(ic))
texto.append('Coefficient of capacity: {:.2f}\n'.format(kc))
texto.append('Shape factor: {:.2f}\n'.format(kf))
resultado.writelines(texto)
resultado.close()


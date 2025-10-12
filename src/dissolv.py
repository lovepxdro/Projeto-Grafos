
arq = open("../data/bairros_recife - bairros_recife.csv", "r", encoding="utf-8")

listBairros = arq.readlines()
arq.seek(0)

matrizBRcf = [] #Para organizar as microregiões
listaOrganizada = [] #Para deixar a lista pronta para entrar na matriz uma vez que os criterios de microregiões estejam explicados

for i in range (len(listBairros)):
    if (i == 0):
        continue
    else:
        lista3 = []

        if(listBairros[i].find("\n") > 0):
            listBairros[i] = listBairros[i][0:listBairros[i].find("\n")]

        listBairros[i] = listBairros[i].strip(",")
        lista3 = listBairros[i].split(",")

        for j in range(len(lista3)):
            if (len(lista3[j]) == 0):
                continue
            else:
                listaOrganizada.append(lista3[j])

    lista3.clear()

for i in range(len(listaOrganizada)):
    for j in range(len(listaOrganizada)-1, i, -1):
        if (listaOrganizada[i] == listaOrganizada[j]):
            listaOrganizada.pop(j)
   
listBairros[0] = listBairros[0][0:listBairros[0].find("\n")]

matrizBRcf = listBairros[0].split(",")

print("-=-"*30)
print(matrizBRcf)
print()
listaOrganizada.sort()
print(listaOrganizada)
print("-=-"*30)

arq.close()

# PARTE DE DEIXAR OS BAIRROS EM SUAS RESPECTIVAS COLUNAS ANTES DE PASSAR PARA O NOVO ARQUIVO CONTENDO TODAS AS INFORMAÇÕES
# TEVE DE SER INTERROMPIDO DEVIDO A AUSÊNCIA DE INFORMAÇÕES MAIS DETALHADAS

# for i in range(len(listaOrganizada)):
#     if (listaOrganizada[i] == "Recife" or listaOrganizada[i] == "Santo Amaro"):
#         matrizBRcf.insert(1, listaOrganizada[i])

#     elif(listaOrganizada[i] == "Boa Viagem" or listaOrganizada[i]  == "Cabanga" or listaOrganizada[i]  == "Ilha do Leite"
#           or listaOrganizada[i]  == "Paissandu" or listaOrganizada[i] == "Santo Antônio" or listaOrganizada[i]  == "São José"
#           or listaOrganizada[i]  == "Soledad"):
#         matrizBRcf.insert(matrizBRcf.index("1.2") + 1, listaOrganizada[i])
    
#     elif (listaOrganizada[i] == "Coelhos" or listaOrganizada[i]  == "Ilha Joana Bezerra"):
#         matrizBRcf.insert(matrizBRcf.index("1.3") + 1, listaOrganizada[i])

#     elif (listaOrganizada[i] == "Arruda" or listaOrganizada[i]  == "Campina do Barreto" or listaOrganizada[i]  == "Campo Grande"
#           or listaOrganizada[i]  == "Encruzilhada" or listaOrganizada[i]  == "Hipódromo" or listaOrganizada[i]  == "Peixinhos"
#           or listaOrganizada[i]  == "Ponto de Parada" or listaOrganizada[i]  == "Rosarinho" or listaOrganizada[i]  == "Torreão"):
#         matrizBRcf.insert(matrizBRcf.index("2.1") + 1, listaOrganizada[i])

#     elif (listaOrganizada[i] == "Água Fria" or listaOrganizada[i]  == "Alto Santa Teresinha" or listaOrganizada[i] == "Bomba do Hemetério" 
#           or listaOrganizada[i]  == "Cajueiro" or listaOrganizada[i]  == "Fundão" or listaOrganizada[i]  == "Porto da Madeira"
#           or listaOrganizada[i]  == "Beberibe" or listaOrganizada[i]  == "Dois Unidos" or listaOrganizada[i]  == "Linha do Tiro"):
#         matrizBRcf.insert(matrizBRcf.index("2.2") + 1, listaOrganizada[i])

#     # elif (listaOrganizada[i] == "Beberibe" or listaOrganizada == "Dois Unidos" or listaOrganizada == "Linha do Tiro"):
#     #     matrizBRcf.insert(matrizBRcf.index("2.3") + 1, listaOrganizada[i])

#     elif (listaOrganizada[i] == "Aflitos" or listaOrganizada[i] == "Alto do Mandu" or listaOrganizada[i]  == "Apipucos"
#           or listaOrganizada[i]  == "Casa Amarela" or listaOrganizada[i]  == "Casa Forte" or listaOrganizada[i]  == "Derby"
#           or listaOrganizada[i]  == "Dois Irmãos" or listaOrganizada[i]  == "Espinheiro" or listaOrganizada[i]  == "Graças"
#           or listaOrganizada[i]  == "Jaqueira" or listaOrganizada[i]  == "Monteiro" or listaOrganizada[i]  == "Parnamirim"
#           or listaOrganizada[i]  == "Poço" or listaOrganizada[i]  == "Santana" or listaOrganizada[i]  == "Sítio dos Pintos"
#           or listaOrganizada[i] == "Tamarineira"):
#         matrizBRcf.insert(matrizBRcf.index("3.1") + 1, listaOrganizada[i])
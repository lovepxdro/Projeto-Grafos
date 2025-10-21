from pathlib import Path

# Resolve paths relative to this script so the script works no matter the CWD
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"
OUT_DIR = BASE_DIR.parent / "out"
OUT_DIR.mkdir(parents=True, exist_ok=True)

INPUT_FILE = DATA_DIR / "bairros_recife.csv"
if not INPUT_FILE.exists():
    raise FileNotFoundError(f"Arquivo de entrada não encontrado: {INPUT_FILE}")

arq = INPUT_FILE.open("r", encoding="utf-8")

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

print("-=-"*60)
print(matrizBRcf)
print()
listaOrganizada.sort(reverse=True)
print(listaOrganizada)
print("-=-"*60)

arq.close()

# PARTE DE DEIXAR OS BAIRROS EM SUAS RESPECTIVAS COLUNAS ANTES DE PASSAR PARA O NOVO ARQUIVO CONTENDO TODAS AS INFORMAÇÕES
# TEVE DE SER INTERROMPIDO DEVIDO A AUSÊNCIA DE INFORMAÇÕES MAIS DETALHADAS

for i in range(len(listaOrganizada)):
    if (listaOrganizada[i] == "Recife" or listaOrganizada[i] == "Santo Amaro"):
        matrizBRcf.insert(1, listaOrganizada[i] + " 1.1")

    elif(listaOrganizada[i] == "Boa Vista" or listaOrganizada[i]  == "Cabanga" or listaOrganizada[i]  == "Ilha do Leite"
          or listaOrganizada[i]  == "Paissandu" or listaOrganizada[i] == "Santo Antônio" or listaOrganizada[i]  == "São José"
          or listaOrganizada[i]  == "Soledade"):
        matrizBRcf.insert(matrizBRcf.index("1.2") + 1, listaOrganizada[i] + " 1.2")
    
    elif (listaOrganizada[i] == "Coelhos" or listaOrganizada[i]  == "Ilha Joana Bezerra"):
        matrizBRcf.insert(matrizBRcf.index("1.3") + 1, listaOrganizada[i] + " 1.3")

    elif (listaOrganizada[i] == "Arruda" or listaOrganizada[i]  == "Campina do Barreto" or listaOrganizada[i]  == "Campo Grande"
          or listaOrganizada[i]  == "Encruzilhada" or listaOrganizada[i]  == "Hipódromo" or listaOrganizada[i]  == "Peixinhos"
          or listaOrganizada[i]  == "Ponto de Parada" or listaOrganizada[i]  == "Rosarinho" or listaOrganizada[i]  == "Torreão"):
        matrizBRcf.insert(matrizBRcf.index("2.1") + 1, listaOrganizada[i] + " 2.1")

    elif (listaOrganizada[i] == "Água Fria" or listaOrganizada[i]  == "Alto Santa Teresinha" or listaOrganizada[i] == "Bomba do Hemetério" 
          or listaOrganizada[i]  == "Cajueiro" or listaOrganizada[i]  == "Fundão" or listaOrganizada[i]  == "Porto da Madeira"
          or listaOrganizada[i]  == "Beberibe" or listaOrganizada[i]  == "Dois Unidos" or listaOrganizada[i]  == "Linha do Tiro"):
        matrizBRcf.insert(matrizBRcf.index("2.2") + 1, listaOrganizada[i] + " 2.2")

    # elif (listaOrganizada[i] == "Beberibe" or listaOrganizada == "Dois Unidos" or listaOrganizada == "Linha do Tiro"):
    #     matrizBRcf.insert(matrizBRcf.index("2.3") + 1, listaOrganizada[i])

    elif (listaOrganizada[i] == "Aflitos" or listaOrganizada[i] == "Alto do Mandu" or listaOrganizada[i]  == "Apipucos"
          or listaOrganizada[i]  == "Casa Amarela" or listaOrganizada[i]  == "Casa Forte" or listaOrganizada[i]  == "Derby"
          or listaOrganizada[i]  == "Dois Irmãos" or listaOrganizada[i]  == "Espinheiro" or listaOrganizada[i]  == "Graças"
          or listaOrganizada[i]  == "Jaqueira" or listaOrganizada[i]  == "Monteiro" or listaOrganizada[i]  == "Parnamirim"
          or listaOrganizada[i]  == "Poço" or listaOrganizada[i]  == "Santana" or listaOrganizada[i]  == "Sítio dos Pintos"
          or listaOrganizada[i] == "Tamarineira"):
        matrizBRcf.insert(matrizBRcf.index("3.1") + 1, listaOrganizada[i] + " 3.1")

    elif (listaOrganizada[i] == "Alto José Bonifácio" or listaOrganizada[i]  == "Alto José do Pinho" or listaOrganizada[i] == "Mangabeira"
        or listaOrganizada[i]  == "Morro da Conceição" or listaOrganizada[i]  == "Vasco da Gama"):
        matrizBRcf.insert(matrizBRcf.index("3.2") + 1, listaOrganizada[i] + " 3.2")

    elif (listaOrganizada[i] == "Brejo da Guabiraba" or listaOrganizada[i]  == "Brejo de Beberibe" or listaOrganizada[i]  == "Córrego do Jenipapo"
          or listaOrganizada[i]  == "Guabiraba" or listaOrganizada[i]  == "Macaxeira" or listaOrganizada[i]  == "Nova Descoberta"
          or listaOrganizada[i]  == "Passarinho" or listaOrganizada[i]  == "Pau-Ferro"):
        matrizBRcf.insert(matrizBRcf.index("3.3") + 1, listaOrganizada[i] + " 3.3")
    
    # elif (listaOrganizada[i] == "Coelhos" or listaOrganizada[i]  == "Ilha Joana Bezerra"):
    #     matrizBRcf.insert(matrizBRcf.index("1.3") + 1, listaOrganizada[i])

    elif (listaOrganizada[i] == "Cordeiro" or listaOrganizada[i]  == "Ilha do Retiro" or listaOrganizada[i]  == "Iputinga"
          or listaOrganizada[i]  == "Madalena" or listaOrganizada[i]  == "Prado" or listaOrganizada[i]  == "Torre"
          or listaOrganizada[i]  == "Zumbi"):
        matrizBRcf.insert(matrizBRcf.index("4.1") + 1, listaOrganizada[i] + " 4.1")

    elif (listaOrganizada[i] == "Engenho do Meio" or listaOrganizada[i]  == "Torrões"):
        matrizBRcf.insert(matrizBRcf.index("4.2") + 1, listaOrganizada[i] + " 4.2")

    elif (listaOrganizada[i] == "Caxangá" or listaOrganizada[i]  == "Cidade Universitária" or listaOrganizada[i]  == "Várzea"):
        matrizBRcf.insert(matrizBRcf.index("4.3") + 1, listaOrganizada[i] + " 4.3")

    elif (listaOrganizada[i] == "Afogados" or listaOrganizada[i]  == "Bongi" or listaOrganizada[i]  == "Mangueira"
          or listaOrganizada[i]  == "Mustardinha" or listaOrganizada[i]  == "San Martin"):
        matrizBRcf.insert(matrizBRcf.index("5.1") + 1, listaOrganizada[i] + " 5.1")

    elif (listaOrganizada[i] == "Areias" or listaOrganizada[i]  == "Caçote" or listaOrganizada[i]  == "Estância"
          or listaOrganizada[i]  == "Jiquiá"):
        matrizBRcf.insert(matrizBRcf.index("5.2") + 1, listaOrganizada[i] + " 5.2")

    elif (listaOrganizada[i] == "Barro" or listaOrganizada[i]  == "Coqueiral" or listaOrganizada[i]  == "Curado"
          or listaOrganizada[i]  == "Jardim São Paulo" or listaOrganizada[i]  == "Sancho" or listaOrganizada[i]  == "Tejipió"
          or listaOrganizada[i]  == "Totó"):
        matrizBRcf.insert(matrizBRcf.index("5.3") + 1, listaOrganizada[i] + " 5.3")

    elif (listaOrganizada[i] == "Boa Viagem" or listaOrganizada[i] == "Brasília Teimosa" or listaOrganizada[i]  == "Imbiribeira" 
          or listaOrganizada[i]  == "Ipsep" or listaOrganizada[i]  == "Pina"):
        matrizBRcf.insert(matrizBRcf.index("6.1") + 1, listaOrganizada[i] + " 6.1")

    elif (listaOrganizada[i] == "Ibura" or listaOrganizada[i]  == "Jordão"):
        matrizBRcf.insert(matrizBRcf.index("6.2") + 1, listaOrganizada[i] + " 6.2")
    
    elif (listaOrganizada[i] == "Cohab"):
        matrizBRcf.insert(matrizBRcf.index("6.3") + 1, listaOrganizada[i] + " 6.3")

print(matrizBRcf)

print("-=-" * 60)

for i in range(len(matrizBRcf) - 1, -1, -1):
    if (matrizBRcf[i][0].isdigit()):
        matrizBRcf.pop(i)

print(matrizBRcf)

OUT_FILE = OUT_DIR / "bairros_unique.csv"
with OUT_FILE.open("w", encoding="utf-8") as arq:
    for i in range(len(matrizBRcf)):
        arq.write(matrizBRcf[i] + "\n")

# todos os passos de como a lista foi preparada e como cada informação saiu do arquivo inicial, foi tratada para entrar no arquivo final
# está printado no terminal, já o arquivo criado será gerado na pasta "out". Rode o codigo para ver o arquivo processado (ele vai criar um arquivo 
# novo na pasta mencionada com todos os nomes tratados e ordenados juntamente com suas microregiões) O arquivo pode ser reescrito infinitamente sem 
# riscos de travar o codigo, ter informações perdidas ou escrever informações adicionais.
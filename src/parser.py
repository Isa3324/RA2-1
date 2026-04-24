token_EPar = "EPAR" # "("
token_DPar = "DPAR" # ")"
token_Num = "NUM" #  numeros reais
token_OP = "OP"  # "+", "-", "*", "/", "//", "%" e "^"
token_Mem = "MEM" # MEM
token_Res = "RES" # RES
token_Invalido = "INVALIDO" # nao é aceito
token_Start = "START"
token_End = "END"

def estadoOperador(linha,posicao):
    if linha[posicao] == '/':
        if posicao + 1 < len(linha) and linha[posicao + 1] == '/':
            return posicao + 2, (token_OP, '//', posicao)
        return posicao + 1, (token_OP, '/', posicao)
    return posicao + 1, (token_OP, linha[posicao], posicao)

def estadoNumero(linha,posicao):
    inicio = posicao
    ponto = False
    
    while posicao < len(linha):
        if linha[posicao].isdigit():
            posicao += 1

        elif linha[posicao] == '.':
            if ponto:
                while posicao < len(linha) and (linha[posicao].isdigit() or linha[posicao] == '.'):
                    posicao += 1
                return posicao, (token_Invalido, linha[inicio:posicao], inicio)

            ponto = True
            posicao += 1

            if posicao >= len(linha) or not linha[posicao].isdigit():
                return posicao, (token_Invalido, linha[inicio:posicao], inicio)

        else:
            break

    numero = linha[inicio:posicao]
    return posicao, (token_Num, numero, inicio)

def estadoParenteses(linha,posicao):
    proxi_posicao = posicao + 1
    if linha[posicao] == '(':
        return proxi_posicao, (token_EPar, '(', posicao)
    elif linha[posicao] == ')':
        return proxi_posicao, (token_DPar, ')', posicao)

    return proxi_posicao, (token_Invalido, linha[posicao], posicao)

def estadoIdentificador(linha,posicao):
    inicio = posicao

    while posicao < len(linha) and linha[posicao].isalpha() and linha[posicao].isupper():
        posicao += 1

    letras = linha[inicio:posicao]

    if letras == "RES":
        return posicao, (token_Res, letras, inicio)
    elif letras == "START":
        return posicao, (token_Start, letras, inicio)
    elif letras == "END":
        return posicao, (token_End, letras, inicio)

    return posicao, (token_Mem, letras, inicio)



def parserExpressao(linha, tokens):
    #Percorre a linha e coloca em tokens
    posicao = 0
    
    while posicao < len(linha):
        variavel = linha[posicao]

        if variavel == "(" or variavel == ")":
            posicao, token = estadoParenteses(linha, posicao)
            tokens.append(token)
        elif variavel.isdigit(): 
            # se é um numero
            posicao, token = estadoNumero(linha,posicao)
            tokens.append(token)
        elif variavel in ["+", "-", "*", "/", "%", "^"]:
            posicao, token = estadoOperador(linha,posicao)
            tokens.append(token)
        elif variavel.isupper() and variavel.isalpha():
            # Se e uma letra maiuscula
            posicao, token = estadoIdentificador(linha,posicao)
            tokens.append(token)
        elif variavel == " ":
            posicao += 1
        else:
            tokens.append((token_Invalido,variavel,posicao))
            posicao += 1
            
    return tokens
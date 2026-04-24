from lexer import (
    token_EPar, token_DPar, token_Num, token_OP,
    token_Mem, token_Res, token_Invalido
)


def inicializar_contexto():
    return {
        "indice_linha": 0,
        "contador_constantes": 0,
        "constantes": [],       # [(label, valor), ...]
        "memorias": set(),      # nomes de memoria usados
    }


def nova_constante(valor, contexto):
    label = f"const_{contexto['contador_constantes']}"
    contexto["contador_constantes"] += 1
    contexto["constantes"].append((label, valor))
    return label


def adicionar_cabecalho(codigoAssembly):
    codigoAssembly += ".syntax unified\n"
    codigoAssembly += ".global _start\n\n"
    codigoAssembly += ".text\n"
    codigoAssembly += "_start:\n"
    codigoAssembly += "    ldr r10, =pilha          @ topo da pilha RPN\n"
    codigoAssembly += "    ldr r11, =resultados     @ ponteiro para vetor de resultados\n"
    codigoAssembly += "    ldr r8,  =resultados     @ base fixa do vetor resultados\n"
    codigoAssembly += "\n"
    return codigoAssembly


def adicionar_rodape(codigoAssembly, contexto):
    codigoAssembly += "fim:\n"
    codigoAssembly += "    b fim\n\n"
    codigoAssembly += ".data\n"
    codigoAssembly += "    .align 8\n"

    for label, valor in contexto["constantes"]:
        codigoAssembly += f"{label}: .double {valor}\n"

    for nome_mem in sorted(contexto["memorias"]):
        codigoAssembly += f"{nome_mem}: .space 8\n"

    codigoAssembly += "pilha:      .space 2048\n"
    codigoAssembly += "resultados: .space 800\n"
    return codigoAssembly


def gerar_push_numero(lexema, contexto):
    label = nova_constante(lexema, contexto)
    trecho = ""
    trecho += f"    @ push {lexema}\n"
    trecho += f"    ldr r0, ={label}\n"
    trecho += f"    vldr d0, [r0]\n"
    trecho += f"    vstr d0, [r10]\n"
    trecho += f"    add r10, r10, #8\n"
    return trecho


def gerar_operador(operador):
    trecho = ""
    trecho += f"    @ operador {operador}\n"
    trecho += "    sub r10, r10, #8\n"
    trecho += "    vldr d1, [r10]\n"
    trecho += "    sub r10, r10, #8\n"
    trecho += "    vldr d0, [r10]\n"

    if operador == "+":
        trecho += "    vadd.f64 d2, d0, d1\n"
    elif operador == "-":
        trecho += "    vsub.f64 d2, d0, d1\n"
    elif operador == "*":
        trecho += "    vmul.f64 d2, d0, d1\n"
    elif operador == "/":
        trecho += "    vdiv.f64 d2, d0, d1\n"
    elif operador == "//":
        trecho += "    @ TODO: divisao inteira em 64 bits\n"
        trecho += "    @ converter para inteiro e dividir separadamente\n"
    elif operador == "%":
        trecho += "    @ TODO: resto da divisao em 64 bits\n"
    elif operador == "^":
        trecho += "    @ TODO: potenciacao em 64 bits\n"

    trecho += "    vstr d2, [r10]\n"
    trecho += "    add r10, r10, #8\n"
    return trecho


def gerar_store_mem(nome_mem, contexto):
    contexto["memorias"].add(nome_mem)
    trecho = ""
    trecho += f"    @ store em memoria {nome_mem}\n"
    trecho += f"    ldr r9, ={nome_mem}\n"
    trecho += "    sub r10, r10, #8\n"
    trecho += "    vldr d0, [r10]\n"
    trecho += "    vstr d0, [r9]\n"
    trecho += "    @ recoloca na pilha para manter o resultado disponivel\n"
    trecho += "    vstr d0, [r10]\n"
    trecho += "    add r10, r10, #8\n"
    return trecho


def gerar_load_mem(nome_mem, contexto):
    contexto["memorias"].add(nome_mem)
    trecho = ""
    trecho += f"    @ load de memoria {nome_mem}\n"
    trecho += f"    ldr r9, ={nome_mem}\n"
    trecho += "    vldr d0, [r9]\n"
    trecho += "    vstr d0, [r10]\n"
    trecho += "    add r10, r10, #8\n"
    return trecho


def gerar_res():
    trecho = ""
    trecho += "    @ RES: topo da pilha contem N\n"
    trecho += "    @ deve buscar o resultado de N linhas anteriores\n"
    trecho += "    sub r10, r10, #8\n"
    trecho += "    vldr d0, [r10]\n"
    trecho += "    @ TODO: converter d0 para inteiro N\n"
    trecho += "    @ TODO: calcular endereco resultados_base + (linha_atual - N - 1) * 8\n"
    trecho += "    @ TODO: carregar esse double e empilhar\n"
    return trecho


def salvar_resultado_da_linha(indice_linha):
    trecho = ""
    trecho += f"    @ salva resultado final da linha {indice_linha}\n"
    trecho += "    sub r10, r10, #8\n"
    trecho += "    vldr d0, [r10]\n"
    trecho += "    vstr d0, [r11]\n"
    trecho += "    add r11, r11, #8\n"
    return trecho


def extrair_tokens_uteis(tokens):
    uteis = []
    for tipo, lexema, pos in tokens:
        if tipo not in (token_EPar, token_DPar):
            uteis.append((tipo, lexema, pos))
    return uteis


def gerarAssembly(tokens, codigoAssembly):
    """
    Gera assembly para UMA linha e concatena em codigoAssembly.
    Sem classe.
    Sem calcular a expressao em Python.
    """

    contexto["indice_linha"] += 1
    indice = contexto["indice_linha"]

    uteis = extrair_tokens_uteis(tokens)

    codigoAssembly += f"    @ ==========================================\n"
    codigoAssembly += f"    @ Linha {indice}\n"
    codigoAssembly += f"    @ ==========================================\n"

    # Caso especial: (MEM)  -> carregar da memoria
    if len(uteis) == 1 and uteis[0][0] == token_Mem:
        nome_mem = uteis[0][1]
        codigoAssembly += gerar_load_mem(nome_mem, contexto)
        codigoAssembly += salvar_resultado_da_linha(indice)
        codigoAssembly += "\n"
        return codigoAssembly

    # Caso especial: (V MEM) -> guardar valor em memoria
    if len(uteis) == 2 and uteis[0][0] == token_Num and uteis[1][0] == token_Mem:
        valor = uteis[0][1]
        nome_mem = uteis[1][1]
        codigoAssembly += gerar_push_numero(valor, contexto)
        codigoAssembly += gerar_store_mem(nome_mem, contexto)
        codigoAssembly += salvar_resultado_da_linha(indice)
        codigoAssembly += "\n"
        return codigoAssembly

    # Caso especial: (N RES)
    if len(uteis) == 2 and uteis[0][0] == token_Num and uteis[1][0] == token_Res:
        valor = uteis[0][1]
        codigoAssembly += gerar_push_numero(valor, contexto)
        codigoAssembly += gerar_res()
        codigoAssembly += salvar_resultado_da_linha(indice)
        codigoAssembly += "\n"
        return codigoAssembly

    # Caso geral: expressao RPN
    for tipo, lexema, pos in uteis:
        if tipo == token_Num:
            codigoAssembly += gerar_push_numero(lexema, contexto)

        elif tipo == token_OP:
            codigoAssembly += gerar_operador(lexema)

        elif tipo == token_Invalido:
            codigoAssembly += f"    @ token invalido: {lexema} na posicao {pos}\n"

        elif tipo == token_Mem:
            codigoAssembly += f"    @ memoria '{lexema}' fora de caso especial\n"

        elif tipo == token_Res:
            codigoAssembly += "    @ RES fora de caso especial\n"

    codigoAssembly += salvar_resultado_da_linha(indice)
    codigoAssembly += "\n"
    return codigoAssembly
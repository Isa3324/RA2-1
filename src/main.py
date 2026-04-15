import sys
from file_reader import ler_arquivo
from parser import parseExpressao
#from executor import executarExpressao
from assembly_generator import (
    inicializar_estado, 
    gerarAssembly, 
    montar_codigo_final
)




def main():
    # ver se tem um arquivo depois do nome do programa
    # ou
    # se o arquivo termina com .txt
    if len(sys.argv) != 2 or not sys.argv[1].endswith(".txt"):
        print("Para rodar deve ter um arquivo.txt, exemplo:: python src/main.py <arquivo.txt>")
        return

    nome_arquivo = sys.argv[1]
    linhas = ler_arquivo(nome_arquivo)

    if not linhas:
        print("nao tem linhas dentro do arquivo ", nome_arquivo)
        return

    #print("Arquivo lido com sucesso!")
    
    codigoAssembly = inicializar_estado()
    
    
    for linha in linhas:
        tokens = []
        tokens = parseExpressao(linha, tokens)
        #resultados_novos, memoria, resultados = executarExpressao(tokens, memoria, resultados)
        #print(tokens)
        codigoAssembly = gerarAssembly(tokens, codigoAssembly)
    
    codigoAssembly = montar_codigo_final(codigoAssembly)        
    print(codigoAssembly)
    
    #with open("output/assembly_ultima_execucao.s", "w", encoding="utf-8") as f:
    #    f.write(codigoAssembly)

if __name__ == "__main__":
    main()
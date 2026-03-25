import sys
from file_reader import ler_arquivo
from parser import parseExpressao

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

    print("Arquivo lido com sucesso!")
    print("Linhas encontradas:")
    for linha in linhas:
        print(linha)
        #parseExpressao(linha, tokens)
        

if __name__ == "__main__":
    main()
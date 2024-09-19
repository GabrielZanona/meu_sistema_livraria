import os
import sqlite3
import csv
from pathlib import Path
from datetime import datetime
import shutil

# Diretórios
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
BACKUP_DIR = BASE_DIR / 'backups'
EXPORT_DIR = BASE_DIR / 'exports'

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)

db_path = DATA_DIR / 'livraria.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS livros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    autor TEXT NOT NULL,
    ano_publicacao INTEGER NOT NULL,
    preco REAL NOT NULL
)
''')
conn.commit()

def fazer_backup():
    nome_backup = f'backup_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.db'
    caminho_backup = BACKUP_DIR / nome_backup
    shutil.copy(db_path, caminho_backup)
    limpar_backups()

def limpar_backups():
    backups = sorted(BACKUP_DIR.glob('backup_*.db'), key=os.path.getmtime)
    while len(backups) > 5:
        backups[0].unlink()
        backups.pop(0)

def add_livro():
    titulo = input("Título: ")
    autor = input("Autor: ")
    try:
        ano = int(input("Ano: "))
        preco = float(input("Preço: "))
    except ValueError:
        print("Ano ou preço inválido.")
        return
    fazer_backup()
    cur.execute('INSERT INTO livros (titulo, autor, ano_publicacao, preco) VALUES (?, ?, ?, ?)', (titulo, autor, ano, preco))
    conn.commit()
    print("Livro adicionado!")

def listar_livros():
    cur.execute('SELECT * FROM livros')
    livros = cur.fetchall()
    if livros:
        for livro in livros:
            print(f'ID: {livro[0]}, Título: {livro[1]}, Autor: {livro[2]}, Ano: {livro[3]}, Preço: {livro[4]}')
    else:
        print("Nenhum livro encontrado.")

def atualizar_preco():
    try:
        livro_id = int(input("ID do livro: "))
        novo_preco = float(input("Novo preço: "))
    except ValueError:
        print("ID ou preço inválido.")
        return
    fazer_backup()
    cur.execute('UPDATE livros SET preco = ? WHERE id = ?', (novo_preco, livro_id))
    conn.commit()
    if cur.rowcount:
        print("Preço atualizado!")
    else:
        print("Livro não encontrado.")

def remover_livro():
    try:
        livro_id = int(input("ID do livro: "))
    except ValueError:
        print("ID inválido.")
        return
    fazer_backup()
    cur.execute('DELETE FROM livros WHERE id = ?', (livro_id,))
    conn.commit()
    if cur.rowcount:
        print("Livro removido!")
    else:
        print("Livro não encontrado.")

def buscar_por_autor():
    autor = input("Autor: ")
    cur.execute('SELECT * FROM livros WHERE autor LIKE ?', (f'%{autor}%',))
    livros = cur.fetchall()
    if livros:
        for livro in livros:
            print(f'ID: {livro[0]}, Título: {livro[1]}, Autor: {livro[2]}, Ano: {livro[3]}, Preço: {livro[4]}')
    else:
        print("Nenhum livro encontrado para este autor.")

def exportar_csv():
    cur.execute('SELECT * FROM livros')
    livros = cur.fetchall()
    if livros:
        caminho_csv = EXPORT_DIR / 'livros.csv'
        with open(caminho_csv, 'w', newline='', encoding='utf-8') as arquivo_csv:
            escritor = csv.writer(arquivo_csv)
            escritor.writerow(['id', 'titulo', 'autor', 'ano_publicacao', 'preco'])
            escritor.writerows(livros)
        print(f"Dados exportados para {caminho_csv}")
    else:
        print("Nenhum livro para exportar.")

def importar_csv():
    caminho_csv = input("Caminho do arquivo CSV: ")
    if not os.path.isfile(caminho_csv):
        print("Arquivo não foi encontrado.")
        return
    fazer_backup()
    with open(caminho_csv, 'r', encoding='utf-8') as arquivo_csv:
        leitor = csv.reader(arquivo_csv)
        next(leitor)
        livros_importados = 0
        for linha in leitor:
            if len(linha) != 5:
                continue
            try:
                cur.execute('INSERT INTO livros (id, titulo, autor, ano_publicacao, preco) VALUES (?, ?, ?, ?, ?)',
                            (int(linha[0]), linha[1], linha[2], int(linha[3]), float(linha[4])))
                livros_importados += 1
            except sqlite3.IntegrityError:
                continue
    conn.commit()
    print(f"{livros_importados} livros foram importados.")

def menu():
    while True:
        print("""
1. Adicionar livro
2. Listar livros
3. Atualizar preço
4. Remover livro
5. Buscar por autor
6. Exportar Livros FORMATO CSV
7. Importar Livros FORMATO CSV
8. Fazer backup
9. Sair
""")
        opcao = input("Escolha uma opção: ")
        if opcao == '1':
            add_livro()
        elif opcao == '2':
            listar_livros()
        elif opcao == '3':
            atualizar_preco()
        elif opcao == '4':
            remover_livro()
        elif opcao == '5':
            buscar_por_autor()
        elif opcao == '6':
            exportar_csv()
        elif opcao == '7':
            importar_csv()
        elif opcao == '8':
            fazer_backup()
            print("Backup realizado com sucesso!")
        elif opcao == '9':
            print("Saindo do app...")
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    menu()
    conn.close()

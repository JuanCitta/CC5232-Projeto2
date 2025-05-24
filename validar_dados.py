import psycopg2
from datetime import date

def validar_dados():
    try:
        conn = psycopg2.connect(
            host="-",
            database="-",
            user="-",
            password="-"
        )
        cursor = conn.cursor()

        tabelas = [
            "usuario", "historico", "amizades", "clubes", "clube_usuario"
        ]

        dados = {}
        
        for tabela in tabelas:
            cursor.execute(f"SELECT * FROM {tabela}")
            dados[tabela] = cursor.fetchall()
                
        menor_data = date.today()
        for linha in dados["usuario"]:
            usuario_data = []
            usuario_data.append((linha[0], linha[3]))
            if linha[3] < menor_data:
                menor_data = linha[3]
            
        erros = []
        
        for linha in dados["historico"]:
            elos = {}
            elos.update({linha[2] : linha[4]})
            elos.update({linha[3]: linha[5]})
            if linha[1] == linha[2]:
                erros.append(f"Jogador jogou contra si mesmo ID1 {linha[1]} ID2 {linha[2]}")       
            
            if linha[8] == linha[9] and linha[8] != "Empate":
                erros.append(f"Resultado inadmissivel {linha[8]} e {linha[9]}")
        
            if linha[8] == "Empate" and linha [9] != "Empate" or linha[8] != "Empate" and linha[9] == "Empate":
                erros.append(f"Resultado inadmissivel {linha[8]} e {linha[9]}")
            
            if linha[8] == "Vitória" and linha[4] < elos[linha[2]]:
                erros.append(f"Usuario {linha[2]} perdeu elo com vitoria na partida {linha[0]}")
            if linha[9] == "Vitória" and linha[5] < elos[linha[3]]:
                erros.append(f"Usuario {linha[3]} perdeu elo com vitoria na partida {linha[0]}")
            for usuario in usuario_data:
                if linha[1] == usuario[0] and linha[10] > usuario[1]:
                    erros.append(f"Data da partida inadmissivel. Partida: {linha[10]} Data_Criacao: {usuario[1]} ID do usuario: {usuario[0]} ID Partida: {linha[0]}")
                
        
        for linha in dados["amizades"]:
            for usuario in usuario_data:
                if usuario[0] == linha[0] or usuario[0] == linha[1] and linha[2] < usuario[1]:
                    erros.append(f"Data na amizade entre ID1: {linha[0]} e ID2: {linha[1]} errada. {linha[2]}")     
               
        for linha in dados["clubes"]:
            if linha[2] < menor_data:
                erros.append(f"Data de criacao invalida ID do clube {linha[0]} Data: {linha[2]}")               
        
        for linha in dados["clube_usuario"]:
            for usuario in usuario_data:
                if linha[1] == usuario[0] and linha[2] < usuario[1]:
                    erros.append(f"Data de join: {linha[1]} invalido para o usuario de ID {usuario[0]} no clube de ID {linha[0]}")
        if len(erros) > 0:
            print("Erros de consistencia encontrados:")
            for erro in erros:
                print(" -", erro)
        else:
            print("Todas as tabelas estao consistentes.")

    except Exception as e:
        print(f"Erro: {e}")
        
    finally:
        if 'conn' in locals():
            conn.close()
validar_dados()

import psycopg2
from tabulate import tabulate
import traceback

# Conexao com o banco de dados
def conectar():
    return psycopg2.connect(
            host="db.kyxedeqogvcoshwlxdie.supabase.co",
            database="postgres",
            user="postgres",
            password="aMUSGl7r02YQ6eKF"
        )

# Descricoes e comandos SQL
queries = {
    1: (
        "Mostre o historico de partidas de um jogador em ordem.",
        """
        SELECT 
            id_partida,
            CASE 
                WHEN id_jogador1 = 2 THEN id_jogador2 
                ELSE id_jogador1 
            END AS adversario,
            CASE 
                WHEN id_jogador1 = 2 THEN elo_jogador1 
                ELSE elo_jogador2 
            END AS meu_elo,
            CASE 
                WHEN id_jogador1 = 2 THEN elo_jogador2 
                ELSE elo_jogador1 
            END AS elo_adversario,
            CASE 
                WHEN id_jogador1 = 2 THEN precisao1 
                ELSE precisao2 
            END AS minha_precisao,
            CASE 
                WHEN id_jogador1 = 2 THEN resultado1 
                ELSE resultado2 
            END AS meu_resultado,
            movimentos,
            data,
            tipo
        FROM historico
        WHERE id_jogador1 = 2 OR id_jogador2 = 2
        ORDER BY id_partida;
        """
    ),
    2: (
        "Contagem de vitorias por cor",
        """
        SELECT 
            CASE 
                WHEN (h.id_jogador1 = brancas AND h.resultado1 = 'Vitória') OR
                    (h.id_jogador2 = brancas AND h.resultado2 = 'Vitória')
                THEN 'Brancas'
                WHEN (h.id_jogador1 = pretas AND h.resultado1 = 'Vitória') OR
                    (h.id_jogador2 = pretas AND h.resultado2 = 'Vitória')
                THEN 'Pretas'
                ELSE 'Empate'
            END AS cor_vencedora,
            COUNT(*) AS total_vitorias
        FROM 
            historico h
        GROUP BY 
            cor_vencedora
        ORDER BY 
            total_vitorias DESC;
        """
    ),
    3: (
        "Mostra os 3 jogadores com mais partidas", 
        """
        SELECT u.id, u.nome_usuario,
        COUNT(*) as total_jogos
        FROM usuario u
        JOIN historico h on u.id = h.id_jogador1 or u.id = h.id_jogador2
        GROUP BY u.id, u.nome_usuario
        ORDER BY total_jogos DESC
        LIMIT 3;
        """
    ),
    4: (
        "Pega os 3 clubes com maior media de elo",
        """
        SELECT 
            c.id_clube,
            c.nome_clube,
            COUNT(cu.id_usuario) AS total_membros,
            ROUND(AVG(u.elo)::numeric, 2) AS media_elo
        FROM 
            clubes c
        LEFT JOIN 
            clube_usuario cu ON c.id_clube = cu.id_clube
        LEFT JOIN 
            usuario u ON cu.id_usuario = u.id
        GROUP BY 
            c.id_clube, c.nome_clube
        ORDER BY 
            total_membros DESC
        LIMIT 3;
        """
        
    ),
    5: (
        "Pega os administradores dos clubes em ordem alfabetica",
        
        """
        SELECT 
            c.id_clube,
            c.nome_clube,
            u.id AS id_admin,
            u.nome_usuario,
            u.elo,
            cu.data_join AS data_ingresso,
            cu.cargo
        FROM 
            clubes c
        JOIN 
            clube_usuario cu ON c.id_clube = cu.id_clube
        JOIN 
            usuario u ON cu.id_usuario = u.id
        WHERE 
            cu.cargo = 'Administrador'  -- ou outro valor que represente admin
        ORDER BY 
            u.nome_usuario ASC;
        """
    ),
    6: (
        "Media de Elo de todos os jogadores",
        """
        SELECT 
            ROUND(AVG(elo)::numeric, 2) AS media_elo
        FROM 
            usuario
        """
    ),
    7: ("Pega as 3 contas mais velhas",
        """
        SELECT 
            data_criacao,
            nome_usuario,
            id
        FROM 
            usuario
        GROUP BY
            nome_usuario,id
        ORDER BY
            data_criacao ASC
        LIMIT 3;

        """
    ),
    8: ("Pega os 5 usuarios com maior elo",
        """
        SELECT 
            id,
            nome_usuario,
            elo
        FROM 
            usuario
        WHERE 
            elo IS NOT NULL
        ORDER BY 
            elo DESC
        LIMIT 5;
        """
    ),
    9: ("Contagem de cada tipo de Partida",
        """
        SELECT 
            tipo,
            COUNT(*) AS total_partidas
        FROM 
            historico
        WHERE 
            tipo IN ('Bullet', 'Rápida', 'Por correspondência', 'Xadrez960', 'Padrão')
        GROUP BY 
            tipo
        ORDER BY 
            total_partidas DESC;
        """
    ),
    10: ("Pega o id dos 5 jogadores com mais vitorias",
         """
        SELECT 
            id_jogador1,
            COUNT(*) AS vitorias
        FROM 
            historico
        WHERE 
            resultado1 = 'Vitória'
        GROUP BY 
            id_jogador1
        ORDER BY 
            vitorias DESC
        LIMIT 5;
         """
    )
}

# Funcao para executar e imprimir os resultados
def executar_query(numero):
    try:
        conn = conectar()
        cursor = conn.cursor()
        descricao, comando = queries[numero]
        print(f"\n {descricao}\n")
        cursor.execute(comando)
        resultados = cursor.fetchall()
        colunas = [desc[0] for desc in cursor.description]
        print(tabulate(resultados, headers=colunas, tablefmt='fancy_grid'))
        
    except Exception as e:
        print(f"Erro ao executar a query {numero}: {e}")
        traceback.print_exc()
    finally:
        if 'conn' in locals():
            conn.close()

# Menu 
def menu():
    while True:
        print("\n Menu de Consultas SQL")
        for num, (desc, _) in queries.items():
                print(f"{num}. {desc}")
        try:
            escolha = int(input("\nDigite o número da query que deseja executar (ou 0 para sair): "))
            if escolha == 0:
                print("Saindo do programa.")
                break
            if escolha in queries:
                executar_query(escolha)
        except ValueError:
            print("Por favor, digite um número válido.")

if __name__ == "__main__":
    menu()

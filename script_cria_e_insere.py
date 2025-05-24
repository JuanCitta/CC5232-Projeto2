import random
from faker import Faker
import psycopg2
from datetime import datetime, date, timedelta
from operator import itemgetter

fake = Faker('pt_BR')

ELO_RANGE = 200
NUM_USUARIOS = 200
NUM_CLUBES = 20
MAX_AMIGOS = 50
TIPOS_DE_PARTIDA = ["Bullet", "Rápida","Padrão","Xadrez960","Por correspondência"]
CARGOS = ["Administrador", "Membro", "Membro", "Membro", "Membro", "Membro", "Membro", "Membro", "Membro", "Membro"]
DATA_INICIO = date(2025,1,1)
DATA_FIM = datetime.now().date()
duration = DATA_FIM - DATA_INICIO
NUM_DIAS = duration.days
DATA_PRIMEIRO_USUARIO = DATA_FIM
# Funcoes auxiliares
def gerar_usuario():
    global DATA_PRIMEIRO_USUARIO
    usuarios = []
    for i in range(1,NUM_USUARIOS+1):
        elo = 1000
        nome_usuario = fake.user_name()
        id = i
        data_criado = fake.date_between(DATA_INICIO,DATA_FIM)
        usuarios.append([id,nome_usuario,elo,data_criado])
        if data_criado < DATA_PRIMEIRO_USUARIO:
            DATA_PRIMEIRO_USUARIO = data_criado
    return usuarios
    
def gerar_historico(usuarios):
    historico = []
    id_partida = 1
    #Itera pelos dias entre a criacao do banco e a data atual, para facilitar a continuidade dos elos
    for d in range (1,NUM_DIAS+1):
        candidatos = []
        delta = timedelta(d)     
        offset = DATA_INICIO + delta 
        #apenas adiciona os usuarios com data de criacao posterior a partida
        for u in usuarios:
            if u[3]> offset:
                candidatos.append(u)
        candidatos.sort(key=lambda x:x[2])
        for p in range(abs(round((random.normalvariate(3,4)))) * NUM_USUARIOS): 
            if len(candidatos)< 2:
                break
            
            jogador1 = random.choice(candidatos)
            oponentes_validos = []
            for jogador in candidatos:
                if jogador1[0] != jogador[0] and abs(jogador[2] - jogador1[2]) < ELO_RANGE:
                    oponentes_validos.append((jogador))
            if not oponentes_validos:
                continue
            jogador2 = random.choice(oponentes_validos)
            res_esperado_p1 = 1/(1+10**((jogador2[2]-jogador1[2])/400))
            res_esperado_p2 = 1/(1+10**((jogador1[2]-jogador2[2])/400))
            id_1 = jogador1[0]
            id_2 = jogador2[0]
            brancas = random.choice([id_1,id_2])
            pretas = id_2 if id_1 == brancas else id_1
            res = random.randint(0,100)
            if res <= 90 :
                if random.randint(0,100) <= 53:
                    ganhador = brancas
                else:
                    ganhador = pretas
                if ganhador == jogador1:
                    res_p1, res_p1_str = 1, "Vitória"
                    res_p2, res_p2_str = 0, "Derrota"  
                else:
                    res_p1, res_p1_str = 0, "Derrota"
                    res_p2, res_p2_str = 1, "Vitória"
            else:
                res_p1, res_p1_str = 0.5, "Empate"
                res_p2, res_p2_str = 0.5, "Empate"
                
            novo_elo1 = round(jogador1[2] + 15 * (res_p1 - res_esperado_p1))
            novo_elo2 = round(jogador2[2] + 15 * (res_p2 - res_esperado_p2))
            movimentos = round(random.normalvariate(35,5))
            precisao_p1 = round(random.normalvariate(55,5))
            precisao_p2 = round(random.normalvariate(55,5))
            tipo = random.choice(TIPOS_DE_PARTIDA)
            
            jogador1[2] = novo_elo1
            jogador2[2] = novo_elo2
            
            for u in usuarios:
                if u[0] == jogador1[0]:
                    u[2] = novo_elo1
                elif u[0] == jogador2[0]:
                    u[2] = novo_elo2
            
            if jogador1[0] > jogador2[0]:
                jogador1, jogador2 = jogador2, jogador1  
                res_p1_str, res_p2_str = res_p2_str, res_p1_str  
                precisao_p1, precisao_p2 = precisao_p2, precisao_p1  
                novo_elo1, novo_elo2 = novo_elo2, novo_elo1  
                brancas, pretas = pretas, brancas
            
            historico.append((
                id_partida,                     
                id_1, id_2,                     #IDs
                jogador1[2], jogador2[2],       #Elos
                precisao_p1, precisao_p2,       
                movimentos,                
                res_p1_str, res_p2_str,        
                offset,              
                tipo,
                brancas,
                pretas                      
            ))
            
            id_partida += 1
    return historico
            


def gerar_clubes():
    clubes = []
    for clube in range(1,NUM_CLUBES + 1):
        id_clube = clube
        nome_clube = fake.name()
        data_criacao = fake.date_between(DATA_PRIMEIRO_USUARIO,DATA_FIM)
        clubes.append((id_clube,nome_clube,data_criacao))
    return clubes
        
def gerar_clube_usuario(usuarios,clubes):
    global DATA_PRIMEIRO_USUARIO
    clube_usuario = []
    for c in clubes:
        users = usuarios.copy()
        id_clube = c[0]
        candidatos = []
        data_criacao = c[2]
        for us in usuarios:
            if us[3]< data_criacao:
                candidatos.append((us[0]))
        if candidatos:
            index = random.randint(0,len(candidatos))
            fundador = candidatos.pop(index)
        else:
            continue
        clube_usuario.append((c[0],fundador,c[2],"Fundador"))
        for u in range(1,round(abs(random.normalvariate(NUM_USUARIOS/5,NUM_USUARIOS/15)))):
            data_join = fake.date_between_dates(c[2],DATA_FIM)
            cargo = random.choice(CARGOS)
            usuario = random.choice(users)
            users.pop(users.index(usuario))
            id_usuario = usuario[0]
            if id_usuario == fundador:
                continue
            clube_usuario.append((id_clube,id_usuario,data_join,cargo))
    return clube_usuario

def gerar_amizades(usuarios):
    amizades = set()
    pares_amizade = set()  
    users = usuarios.copy()

    for u in users:
        candidatos = []
        data_criacao = u[3]
        id_usuario = u[0]

        for us in usuarios:
            if us[3] <= data_criacao and us[0] != id_usuario:
                candidatos.append(us)

        if not candidatos:
            continue

        num_amigos = random.randint(0, MAX_AMIGOS)
        random.shuffle(candidatos)

        for a in range(min(num_amigos, len(candidatos))):
            amigo = candidatos[a]
            id_amigo = amigo[0]
            par = (min(id_usuario, id_amigo), max(id_usuario, id_amigo))

            if par in pares_amizade:
                continue  

            data = fake.date_between_dates(date_start=data_criacao, date_end=DATA_FIM)
            amizades.add((*par, data))
            pares_amizade.add(par)

    return amizades



def gerar_dados():
    usuarios = gerar_usuario()
    clubes = gerar_clubes()
    historico = gerar_historico(usuarios)
    clube_usuario = gerar_clube_usuario(usuarios,clubes)
    amizades = gerar_amizades(usuarios)
    
    dados = {
        "usuarios" : usuarios,
        "clubes" : clubes,
        "historico" : historico,
        "clube_usuario" : clube_usuario,
        "amizades" : amizades
    }
    return dados
    
    
def inserir_no_banco(dados):
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
        for tabela in tabelas:
            cursor.execute(f"DROP TABLE IF EXISTS {tabela} CASCADE;")
        
        comandos_sql = [
            """
            CREATE TABLE usuario (
                id BIGINT NOT NULL PRIMARY KEY,
                nome_usuario VARCHAR NOT NULL,
                elo BIGINT NULL,
                data_criacao DATE
            );
            """,
            """
            CREATE TABLE historico (
                id_partida BIGINT PRIMARY KEY,
                id_jogador1 BIGINT NOT NULL,
                id_jogador2 BIGINT NOT NULL,
                elo_jogador1 BIGINT,
                elo_jogador2 BIGINT,
                precisao1 FLOAT,
                precisao2 FLOAT,
                movimentos INTEGER,
                resultado1 VARCHAR,
                resultado2 VARCHAR,
                data DATE,
                tipo VARCHAR,
                brancas BIGINT,
                pretas BIGINT,
                FOREIGN KEY (id_jogador1) REFERENCES usuario(id),
                FOREIGN KEY (id_jogador2) REFERENCES usuario(id)
            );
            """,
            """
            create table amizades (
            id_1 bigint generated by default as identity not null,
            id_2 bigint not null,
            data date null default now(),
            constraint amizades_pkey primary key (id_1, id_2),
            constraint amizades_id_1_fkey foreign KEY (id_1) references usuario (id),
            constraint amizades_id_2_fkey foreign KEY (id_2) references usuario (id)
            );
            """,
            """
            create table clubes (
            id_clube bigint generated by default as identity not null,
            nome_clube character varying not null,
            data_criacao date null,
            constraint clubes_pkey primary key (id_clube)
            );
            """,
             """
            create table clube_usuario (
            id_clube bigint generated by default as identity not null,
            id_usuario bigint not null,
            data_join date null,
            cargo character varying null,
            constraint clube_usuario_pkey primary key (id_clube, id_usuario),
            constraint clube_usuario_id_clube_fkey foreign KEY (id_clube) references clubes (id_clube),
            constraint clube_usuario_id_usuario_fkey foreign KEY (id_usuario) references usuario (id)
            );
            """
            
        ]    
        
        for comando in comandos_sql:
            cursor.execute(comando)
        
        cursor.executemany("INSERT INTO usuario (id, nome_usuario, elo, data_criacao) VALUES (%s, %s, %s, %s)", dados['usuarios'])
        cursor.executemany("INSERT INTO clubes (id_clube, nome_clube, data_criacao) VALUES (%s, %s, %s)", dados['clubes'])
        print("Usuarios e clubes inseridos.")
        
        cursor.executemany("INSERT INTO clube_usuario (id_clube, id_usuario, data_join, cargo) VALUES (%s, %s, %s, %s)", dados['clube_usuario'])
        cursor.executemany("INSERT INTO amizades (id_1, id_2, data) VALUES (%s, %s, %s)", dados['amizades'])
        print("Relacoes clube-usuario e amizades inseridas.")
        
        cursor.executemany("""
                    INSERT INTO historico 
                    (id_partida, id_jogador1, id_jogador2, elo_jogador1, elo_jogador2, 
                    precisao1, precisao2, movimentos, resultado1, resultado2, data, tipo, brancas, pretas) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, dados['historico'])
        print("Historico de partidas inserido.")
        
        print("Todos os dados foram inseridos com sucesso!")
            
        conn.commit()
    except Exception as e:
        print(f"Erro: {e}")
        return False

    finally:
        if 'conn' in locals():
            conn.close()

dados = gerar_dados()
inserir_no_banco(dados)

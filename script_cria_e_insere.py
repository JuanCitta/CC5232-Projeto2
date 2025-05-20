import random
from faker import Faker
import psycopg2
import datetime
from datetime import timedelta
from operator import itemgetter

fake = Faker('pt_BR')

DIAS_31 = [1,3,5,7,8,10,12]
ELO_RANGE = 200
NUM_USUARIOS = 10
NUM_CLUBES = 5
MAX_AMIGOS = 15
TIPOS_DE_PARTIDA = ["Bullet", "Rápida","Padrão","Xadrez960","Por correspondência"]
CARGOS = ["Administrador", "Membro", "Membro", "Membro", "Membro", "Membro", "Membro", "Membro", "Membro", "Membro"]
DATA_INICIO = datetime.date(2025,1,1)
DATA_FIM = datetime.datetime.now().date()
duration = DATA_FIM - DATA_INICIO
NUM_DIAS = duration.days
# Funcoes auxiliares
def usuario():
    usuarios = []
    for i in range(1,NUM_USUARIOS+1):
        elo = 1000
        nome_usuario = fake.user_name()
        id = i
        data_criado = fake.date_between(DATA_INICIO,DATA_FIM)
        usuarios.append([id,nome_usuario,elo,data_criado])
    
    return usuarios
    
def historico(usuarios):
    #mes = 1
    historico = []
    id_partida = 1
    elo = []
    elo_usuario = {}
    #Itera pelos dias entre a criacao do banco e a data atual, para facilitar a continuidade dos elos
    for d in range (1,NUM_DIAS+1):
        delta = timedelta(d)     
        offset = DATA_INICIO + delta 
        #apenas adiciona os usuarios com data de criacao posterior a partida
        for u in usuarios:
            if u[3]> offset:
                elo.append([u[2],u[0]])
        elo.sort()
        for p in range(abs(round((random.normalvariate(3,4)))) * NUM_USUARIOS): 
            p1 = random.randint(1,len(elo) - 1)
            p2 = p1-1 if elo[p1-1][0] - elo[p1][0] < ELO_RANGE else p1+1
            id_p1 = elo[p1][1]
            id_p2 = elo[p2][1]
            res_esperado_p1 = 1/(1+10**((elo[p2][0]-elo[p1][0])/400))
            res_esperado_p2 = 1/(1+10**((elo[p1][0]-elo[p2][0])/400))
            res = random.randint(0,1)
            if res == 0 :
                ganhador = random.choice((p1,p2))
                if ganhador == p1:
                    res_p1 = 1
                    res_p1_string = "Vitória"
                    res_p2 = 0  
                    res_p2_string = "Derrota"
                else:
                    res_p1 = 0
                    res_p1_string = "Derrota"
                    res_p2 = 1
                    res_p2_string = "Vitória"
            else:
                res_p1 = 0.5
                res_p1_string = "Empate"
                res_p2 = 0.5
                res_p2_string = "Empate"
            
            novo_elo_p1 = round(elo[p1][0] + 15 * (res_p1 - res_esperado_p1),1)
            novo_elo_p2 = round(elo[p2][0] + 15 * (res_p2 - res_esperado_p2),1)
            movimentos = round(random.normalvariate(35,5))
            precisao_p1 = round(random.normalvariate(55,5))
            precisao_p2 = round(random.normalvariate(55,5))
            data = offset
            tipo = random.choice(TIPOS_DE_PARTIDA)
            
            historico.append((id_p1,id_p2,id_partida,novo_elo_p1,precisao_p1,movimentos,res_p1_string, data, tipo))
            historico.append((id_p2,id_p1,id_partida,novo_elo_p2,precisao_p2,movimentos,res_p2_string, data, tipo))
            elo[p1][0] = novo_elo_p1
            elo[p2][0] = novo_elo_p2
            
            elo_usuario.update({id_p1 : novo_elo_p1})
            elo_usuario.update({id_p2 : novo_elo_p2})
            id_partida += 1
        #if d == 28 and mes == 2:
        #    mes = 3
        #elif d == 31 and mes in DIAS_31:
        #    mes+= 1
        #elif d == 30:
        #    mes+= 1

    for id,elo in elo_usuario.items():
        for u in usuarios:
            if id == u[0]:
                u[2] = elo
    return historico
            


def clubes():
    clubes = []
    for clube in range(1,NUM_CLUBES + 1):
        id_clube = clube
        nome_clube = fake.village()
        data_criacao = fake.date_between(DATA_INICIO,DATA_FIM)
        clubes.append((id_clube,nome_clube,data_criacao))
        
def clube_usuario(usuarios,clubes):
    clube_usuario = []
    for c in clubes:
        users = usuarios.copy()
        id_clube = c[0]
        fundador = random.choice(users)
        users.pop(fundador)
        while(c[2] > fundador):
            fundador = random.choice(usuarios)
        clube_usuario.append((c[0],fundador,c[2],"Fundador"))
        for u in range(1,abs(random.normalvariate(NUM_USUARIOS/5,NUM_USUARIOS/15))):
            data_join = fake.date_between_dates(c[2])
            cargo = random.choice(CARGOS)
            usuario = random.choice(users)
            users.pop(usuario)
            id_usuario = usuario[0]
            clube_usuario.append((id_clube,id_usuario,data_join,cargo))
    return clube_usuario

def amizades(usuarios):
    amizades = []
    users = usuarios.copy()
    for u in users:

        for a in range(0,random.randint(0,MAX_AMIGOS)):
            data1 = u[3]
    return amizades
def inserir_no_banco():
    try:
        conn = psycopg2.connect(
            host="db.kyxedeqogvcoshwlxdie.supabase.co",
            database="postgres",
            user="postgres",
            password="aMUSGl7r02YQ6eKF"
        )
        cursor = conn.cursor()
        tabelas = [
            "usuario", "partidas", "historico", "amizades", "clubes", "clube_usuario"
        ]
        for tabela in tabelas:
            cursor.execute(f"DROP TABLE IF EXISTS {tabela} CASCADE;")
        
        comandos_sql = [
            """
            CREATE TABLE usuario (
                id BIGINT NOT NULL PRIMARY KEY,
                nome_usuario VARCHAR NOT NULL,
                elo BIGINT NULL
            );
            """,
            """
            create table historico (
            id_usuario bigint generated by default as identity not null,
            id_partida bigint not null,
            id_oponente bigint,
            precisao real null,
            movimentos bigint null,
            resultado boolean null,
            data DATE,
            constraint historico_pkey primary key (id_usuario, id_partida, id_oponente),
            constraint historico_id_partida_fkey foreign KEY (id_partida) references partidas (id_partida),
            constraint historico_id_usuario_fkey foreign KEY (id_usuario) references usuario (id),
            constraint historico_id_oponente_fkey foreign KEY (id_oponente) references usuario (id)
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
        conn.commit()
    except Exception as e:
        print(f"Erro: {e}")
        return False

    finally:
        if 'conn' in locals():
            conn.close()

a = usuario()
print(a)
p = historico(a)

#for h in p:
#    if h[0] == 1:
#        print(h)
#for us in a:
#    if us[0] == 1:
#        print(us)
#

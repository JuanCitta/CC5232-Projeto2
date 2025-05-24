# Banco de Dados para Aplicativo de Xadrez

Projeto para a matéria CC5232-Banco de Dados

Feito por: 

-Juan Manuel Citta 24.123.022-6

-Sebastian Citta 24.123.068-9

-Luis Fernando Souza Goncalves 24.123.052-3

## Descrição:
O banco de dados foi projetado para simular um database de um aplicativo de Xadrez.

Dados fictícios são gerados através de um arquivo python chamado "script_cria_e_insere.py" que gera o id do usúario, lista de amizades, histórico de partidas e clubes.

Esses dados podem ser validados utilizando o arquivo "validar_dados.py", que confere a consistência. A validação é majoritariamente para a data de criação, mas também faz algumas validações no histórico do usúario.

Com o arquivo queries.py o usuário pode escolher entre 10 queries para que o resultado seja imprimido na tela do terminal.

## Como executar:
### Criar e inserir dados:
Ao executar o arquivo script_cria_e_insere.py ele retorna esta mensagem:
![image](https://github.com/user-attachments/assets/ae707da5-7d87-476b-a583-522177646531)

### Queries:
Ao executar o arquivo queries.py um menu iterativo permitirá o usuário acessar as queries desejadas:

### Validar dados:
Ao executar o arquivo validar_dados.py o programa printara a seguinte mensagem ao validar corretamente os dados:
![image](https://github.com/user-attachments/assets/f2773834-a224-4b4b-8bf7-1740e30665c1)


## Diagrama:

![image](https://github.com/user-attachments/assets/1059f588-c3e0-4742-8073-830d38f4e629)


##MER: 

![image](https://github.com/user-attachments/assets/0b46f06d-a11b-4eed-8f90-97f9f8ee29cc)

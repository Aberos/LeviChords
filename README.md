# LeviChords

Site para cadastrar cifras e montar o repertório de cada culto, com um modo de leitura pensado para o celular e o tablet: letra grande, fundo escuro e acordes destacados em laranja.

O nome vem dos levitas, os músicos do templo (1 Crônicas 15:16).

## Funcionalidades

### Músicas

- Cadastro colando a cifra em texto puro, com os acordes na linha acima da letra.
- Reconhecimento automático das linhas de acordes, das seções (`[Refrão]`, `[Intro]`), das tablaturas e da letra.
- Pré-visualização da cifra colorida antes de salvar.
- Busca por título ou artista.
- Transposição de tom de meio em meio tom, com a grafia de sustenidos ou bemóis de acordo com o tom de destino.

### Repertórios

- Um repertório por data, com descrição, ordem das músicas e o tom de cada uma.
- Índice no topo do repertório para ir direto a qualquer música.
- A página inicial abre o próximo repertório agendado.

### Modo de leitura

| Botão | O que faz |
| --- | --- |
| A− / A+ | Diminui ou aumenta a letra. As linhas nunca são cortadas: se não couberem, a letra se ajusta à largura da tela. |
| Tom − / Tom + | Transpõe a música meio tom para baixo ou para cima. |
| Páginas | Vira a página com um toque: à esquerda volta, no resto da tela avança. Também aceita pedal ou teclado Bluetooth (PageDown, PageUp, setas e Espaço). |
| Mais → Tela cheia | Esconde as barras do navegador e do sistema, quando o navegador permite. |
| Mais → Ajustar à tela | Escolhe o maior tamanho de letra em que a cifra inteira cabe na tela. |
| Mais → Colunas | Divide a cifra em 1, 2 ou 3 colunas no tablet, sem separar o acorde da letra. Com o modo Páginas, as colunas viram como as páginas de um livro. |
| Mais → Sem tabs | Esconde as tablaturas. Aparece só nas músicas que têm tablatura. |
| Mais → Rolar | Rolagem automática em três velocidades. |
| Mais → Tema | Alterna entre o tema escuro e o claro. |

As preferências ficam salvas no aparelho, e a tela permanece ligada durante a leitura nos navegadores que oferecem esse recurso.

As páginas funcionam em navegadores antigos, como o do Android 4.4. Os recursos essenciais, como a leitura e a transposição, funcionam até sem JavaScript.

### Acesso

- Todas as páginas exigem login.
- A opção "Lembrar de mim" mantém o acesso por 30 dias. Sem ela, a sessão termina quando o navegador é fechado.
- Os usuários são criados com `createsuperuser` ou pelo `/admin/`.

## Formato da cifra

```text
[Intro] G  D  Em  C  (2x)

[Primeira Parte]
G              D/F#
Grande é o Senhor
         Em        C
E mui digno de louvor
```

Também são reconhecidos:

- acordes com extensões e baixo, como `G7M`, `Em7(9)`, `A7/4` e `F#m7(b5)/E`;
- acordes entre parênteses, como `( G  D  Em )`;
- rótulos com dois-pontos, como `Intro: G  D`;
- tablaturas, como `E|---7-8---|`.

O tom original é informado no cadastro (`G`, `F#`, `Bb`, `Am`).

## Requisitos

- Docker e Docker Compose
- VS Code com a extensão Python Debugger, para depuração

## Configuração

Crie o arquivo de configuração na raiz do projeto:

```sh
cp .env.example .env
```

Defina a chave da aplicação e as credenciais do PostgreSQL antes de iniciar os serviços.

| Variável | Descrição |
| --- | --- |
| `DJANGO_SECRET_KEY` | Chave da aplicação |
| `DJANGO_ALLOWED_HOSTS` | Hosts permitidos, separados por vírgula |
| `POSTGRES_DB` | Nome do banco |
| `POSTGRES_USER` | Usuário do banco |
| `POSTGRES_PASSWORD` | Senha do banco |
| `APP_PORT` | Porta HTTP, inicialmente `8000` |
| `DEBUG_PORT` | Porta do debugger, inicialmente `5678` |
| `BIND_HOST` | Interface de publicação das portas, inicialmente `127.0.0.1` |
| `APP_PREFIX` | Prefixo de URL quando a aplicação estiver atrás de um proxy |

O Compose conecta a aplicação ao PostgreSQL em `db:5432`. Sem `POSTGRES_DB` definida, o Django usa SQLite no arquivo `db.sqlite3`.

## Execução

```sh
docker compose up --build -d
```

As migrações são aplicadas na inicialização. Com as portas do `.env.example`, os endereços são:

- Site: http://localhost:8000/
- Administração: http://localhost:8000/admin/

Para criar o usuário que cadastra as cifras:

```sh
docker compose exec app python manage.py createsuperuser
```

Para acompanhar os logs e encerrar os serviços:

```sh
docker compose logs -f app
docker compose down
```

Os dados permanecem no volume `postgres_data`.

### Acesso pelo celular ou tablet na rede local

Para abrir o site em outro aparelho na mesma rede Wi-Fi, suba um servidor que publica apenas a porta do site no IP do computador (troque `192.168.0.10` pelo IP da sua máquina):

```sh
docker compose run -d --name levichords-rede \
  -p 192.168.0.10:8000:8000 \
  -e DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,192.168.0.10 \
  app python manage.py runserver 0.0.0.0:8000
```

No aparelho, acesse `http://192.168.0.10:8000`. Para encerrar:

```sh
docker compose rm -sf levichords-rede
```

Não use `BIND_HOST=0.0.0.0` para isso, porque essa configuração também publica a porta do debugger na rede.

## Testes

```sh
docker compose run --rm app pytest
```

## Depuração

Com os serviços em execução, selecione **Django: Docker (attach)** no painel **Executar e Depurar** do VS Code e pressione **F5**.

Como o servidor roda com `--noreload`, reinicie a aplicação após alterações no código Python:

```sh
docker compose restart app
```

## Publicação no Render

O `Dockerfile` da raiz gera a imagem de produção: instala só as dependências da aplicação, reúne os arquivos estáticos e sobe o site com o gunicorn. O `Dockerfile.dev` é o usado pelo Docker Compose no desenvolvimento.

Ao iniciar, o contêiner de produção executa `deploy/start.sh`, que aplica as migrações, cria o primeiro usuário quando as variáveis `DJANGO_SUPERUSER_*` estão definidas e inicia o gunicorn na porta informada em `PORT`.

1. No Render, crie um banco em **New → Postgres** e copie a **Internal Database URL**.
2. Crie o site em **New → Web Service**, escolha o repositório do GitHub e o ambiente **Docker**.
3. Em **Environment**, defina as variáveis abaixo e conclua a criação.

| Variável | Valor |
| --- | --- |
| `DJANGO_SECRET_KEY` | Uma chave longa e aleatória |
| `DATABASE_URL` | A Internal Database URL do banco |
| `DJANGO_HTTPS` | `1`, para os cookies de sessão trafegarem só por HTTPS |
| `DJANGO_SUPERUSER_USERNAME` | Usuário que cadastra as cifras |
| `DJANGO_SUPERUSER_EMAIL` | E-mail desse usuário |
| `DJANGO_SUPERUSER_PASSWORD` | Senha desse usuário |
| `DJANGO_ALLOWED_HOSTS` | Opcional: domínios próprios, separados por vírgula |

O endereço `.onrender.com` do serviço é liberado automaticamente. A cada `git push` na branch principal, o Render gera uma nova versão do site.

Depois do primeiro acesso, as variáveis `DJANGO_SUPERUSER_*` podem ser removidas. Enquanto existirem, cada inicialização apenas informa no log que o usuário já existe.

Para testar a imagem de produção localmente:

```sh
docker build -t levichords .
```

## Padrões de código

- PEP 8, formatado pelo Black com 79 colunas.
- PEP 257, com docstrings em módulos, classes e funções, verificadas pelo Ruff.
- PEP 484, com anotações de tipo verificadas pelo Mypy em modo estrito com `django-stubs`.
- JavaScript em ES5 e CSS sem variáveis.

## Pre-commit

Os hooks executam Black, Ruff e Mypy, com as configurações do `pyproject.toml`.

```sh
docker compose run --rm --no-deps app pre-commit run --all-files
```

A primeira execução baixa os repositórios e instala as dependências dos hooks.

Para executar os hooks automaticamente no `git commit` feito no host, instale o pre-commit no ambiente Python local:

```sh
python -m pip install ".[dev]"
pre-commit install
```

## Estrutura

```text
apps/
  core/       layout base, login, barra e scripts do modo de leitura, CSS
  songs/      músicas, reconhecimento e transposição de acordes (chords.py)
  setlists/   repertórios e ordem das músicas
config/       configurações do Django
deploy/       script de inicialização da imagem de produção
```

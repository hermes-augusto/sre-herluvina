# Story: Implementação do Hardening de Segurança com Foco em Portabilidade - Northwind Traders

**ID**: STORY-03  
**Status**: Completed  
**Autor**: SRE / Security Engineer  

Esta story gerencia a implementação das defesas de segurança detalhadas em [documents/06_security_test_plan.md](file:///workspaces/sre-herluvina/documents/06_security_test_plan.md), redesenhadas sob a premissa de **portabilidade absoluta** e facilidade de instalação (DevEx). As melhorias de segurança (login, HTTPS, retry de concorrência e não-root) serão configuradas para serem automáticas ou parametrizáveis via variáveis de ambiente no `.env`, garantindo que qualquer desenvolvedor consiga clonar e rodar o projeto localmente com configuração zero (*plug-and-play*).

---

## 1. Critérios de Aceitação

*   **AC-01**: Autenticação local para o dashboard Streamlit implementada por meio de variáveis de ambiente do `.env` (`DASHBOARD_USER`/`DASHBOARD_PASSWORD`), sem dependência de IDPs ou bancos externos de credenciais.
*   **AC-02**: Geração dinâmica de certificados SSL autoassinados em tempo de inicialização (via script Python embarcado no container), tornando o HTTPS opcional e configurável via variável de ambiente (`STREAMLIT_ENABLE_SSL=true/false`).
*   **AC-03**: Mecanismo de Retry e Backoff implementado na conexão do DuckDB (`app/main.py`) para tratar falhas de lock de escrita do dbt de forma transparente para o analista, solucionando **RNF-05** sem quebrar a execução local.
*   **AC-04**: Containers Docker endurecidos para executar sob usuário comum (`appuser`), garantindo que permissões de escrita nos volumes locais mapeados (`./data`) sejam compatíveis dinamicamente entre Linux, macOS e Windows (WSL).
*   **AC-05**: Scripts utilitários de varredura (Bandit, Trivy, Gitleaks) empacotados em containers Docker executados sob demanda pelo script CLI `bin/run-security-scans.sh`, dispensando instalações manuais na máquina física do desenvolvedor.

---

## 2. Checklist de Progresso

- [x] **Etapa 1: Segurança de Acesso e Gestão de Segredos**
  - [x] Adicionar variáveis `DASHBOARD_USER` e `DASHBOARD_PASSWORD` no `.env.example`
  - [x] Implementar interface de login básica e segura em `app/main.py` consumindo estas variáveis de ambiente
  - [x] Remover fallbacks de credenciais do MinIO do código em `app/ingest.py` e forçar interrupção com erro caso ausentes
  - [x] Instalar o hook de pré-commit do Gitleaks de forma opcional via script de inicialização local
- [x] **Etapa 2: HTTPS Automático Opcional e Hardening de Permissões**
  - [x] Adicionar variável `STREAMLIT_ENABLE_SSL=false` no `.env.example`
  - [x] Criar script de inicialização Python (`app/entrypoint.py`) que gera chaves OpenSSL autoassinadas caso `STREAMLIT_ENABLE_SSL=true` e os arquivos não existam
  - [x] Atualizar `docker-compose.yml` para expor o Streamlit em HTTPS condicional e rodar sob o ID do usuário do host de forma dinâmica (`user: "${UID}:${GID}"`)
  - [x] Testar montagem de volume `./data` em modo leitura/escrita sob a nova regra de permissões em diferentes sistemas
- [x] **Etapa 3: Resiliência de Banco e Automação de Scans CLI**
  - [x] Implementar lógica de Retry (3 tentativas com sleep de 0.5s) para capturar exceções de lock do DuckDB em `app/main.py`
  - [x] Criar script CLI `bin/run-security-scans.sh` que executa Bandit (SAST), Trivy (SCA) e Gitleaks (Secrets) via Docker local sob demanda
  - [x] Validar a execução ponta a ponta dos testes de segurança (`TC-SEC-01` a `TC-SEC-05`)
  - [x] Atualizar os status na Matriz de Rastreabilidade (RTM)

---

## 3. Lista de Arquivos Planejada (File List)

- [x] `app/entrypoint.py` -> Script em Python para checagem e geração dinâmica de SSL e boot da aplicação.
- [x] `bin/run-security-scans.sh` -> Script de disparo dos scans de segurança rodando Bandit, Trivy e Gitleaks.
- [x] `app/main.py` -> Editado para incluir tratamento de login local e retries de conexão do DuckDB.
- [x] `Dockerfile` -> Atualizado para configurar o usuário dinâmico e dependências de criptografia do Python.
- [x] `docker-compose.yml` -> Editado para dar suporte ao mapeamento dinâmico de IDs de usuário do host.
- [x] `bin/setup-pre-commit.sh` -> Script para instalação e setup opcional do hook de pré-commit do Gitleaks.
- [x] `gitleaks.toml` -> Configuração de caminhos do allowlist para evitar falsos positivos no Gitleaks.
- [x] `.gitleaksignore` -> Assinaturas de impressões digitais de falsos-positivos permitidos no repositório.

---

## 4. Riscos e Ambiguidades

### Riscos Técnicos de Implementação (3)
1.  **Divergência de Variáveis UID/GID em Ambientes Windows**: A variável de ambiente `${UID}` e `${GID}` é populada nativamente em shells Unix (Linux/macOS), mas não existe no Prompt de Comando ou PowerShell do Windows. Desenvolvedores Windows rodando o docker-compose diretamente sem passar as variáveis podem enfrentar erros de parser de string vazia no Docker.
2.  **Incompatibilidade de Navegador com HTTPS Autoassinado local**: O k6 ou o navegador podem rejeitar por completo o tráfego do Streamlit caso o SSL autoassinado seja ativado, exigindo que o desenvolvedor aceite exceções de segurança locais manualmente, o que prejudica a experiência DevEx.
3.  **Falso Senso de Segurança na Autenticação Local por .env**: Usuários experientes podem acessar o container do Streamlit ou ler o arquivo `.env` local na máquina para obter a senha em texto plano. Esta autenticação local protege apenas contra acessos não autorizados de terceiros na mesma rede física de escritório, e não contra ataques com privilégios locais de hardware.

### Ambiguidades Pendentes (2)
1.  **Compatibilidade do Script de Certificados sem OpenSSL no Host**: Se o container Python-slim do Docker não possuir o binário do OpenSSL ou a biblioteca de criptografia instalada, a geração dinâmica de chaves falhará no boot, impossibilitando a inicialização da aplicação sob HTTPS.
2.  **Mecanismo de Escapamento do Retry em Caso de Falha de Escrita**: Caso o pipeline diário do dbt trave no dbt run (deixando o lock de escrita aberto infinitamente no DuckDB), os retries de conexão do Streamlit se esgotarão em 1.5 segundos, gerando erros recorrentes na tela. Resta ambíguo se devemos aumentar o número de tentativas e o atraso (delay) caso o processo de ETL concorrente esteja ativo.

---
*Fim do Documento da Story.*

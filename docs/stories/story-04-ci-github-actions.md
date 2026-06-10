# Story: Automação de Integração Contínua (CI) via GitHub Actions - Northwind Traders

**ID**: STORY-04  
**Status**: Completed  
**Autor**: DevOps / SRE Engineer  

Esta story gerencia a especificação, criação e teste do workflow de Integração Contínua (CI) utilizando a ferramenta **GitHub Actions**. O objetivo é criar uma esteira automatizada que execute varreduras estáticas de segurança (SAST/SCA/Secret scan) e testes dinâmicos de integração (inicialização de containers, ingestão de dados e execução de testes dbt) a cada Push ou Pull Request na branch `main` e `feature/*`, garantindo que alterações de código não quebrem a execução local nem exponham segredos ou vulnerabilidades.

---

## 1. Critérios de Aceitação

*   **AC-01**: Arquivo de workflow de CI do GitHub Actions configurado e salvo em `.github/workflows/ci.yml`.
*   **AC-02**: Execução de varreduras estáticas automatizada a cada push:
    *   **Gitleaks** para busca de segredos em commits.
    *   **Bandit** para análise estática de segurança do código Python.
    *   **Trivy** para identificação de CVEs nas dependências listadas no `requirements.txt`.
*   **AC-03**: Execução de testes dinâmicos de integração em runners do GitHub:
    *   Criação das imagens Docker locais e inicialização dos containers (`minio`, `python-pipeline` e `streamlit`).
    *   Validação do status de integridade do MinIO via health check.
    *   Execução ponta a ponta do pipeline local (`bin/run-pipeline.sh`) contendo as etapas de ingestão, transformação dbt, testes dbt e auditoria de reconciliação.
*   **AC-04**: O workflow do GitHub Actions deve falhar e bloquear o merge de Pull Requests se qualquer etapa estática ou dinâmica falhar (código de saída diferente de `0`).

---

## 2. Checklist de Progresso

- [x] **Etapa 1: Estruturação e Triggers do Workflow**
  - [x] Criar o diretório `.github/workflows/`
  - [x] Criar o arquivo de especificação `.github/workflows/ci.yml`
  - [x] Configurar os gatilhos (triggers) do workflow para eventos de `push` e `pull_request` nas branches `main` e `feature/*`
- [x] **Etapa 2: Implementação dos Jobs Estáticos (Segurança e Qualidade)**
  - [x] Configurar o job de Secret Scanning utilizando a Action oficial do Gitleaks
  - [x] Configurar o job de SAST configurando a execução do Bandit sobre a pasta `app/`
  - [x] Configurar o job de SCA integrando o Trivy para escanear a imagem do pipeline e o arquivo `requirements.txt`
  - [x] Adicionar checagem de estilo de código (linter como `flake8` ou `black --check`) para manter a formatação do Python
- [x] **Etapa 3: Implementação do Job Dinâmico (Integração e Teste Ponta a Ponta)**
  - [x] Configurar o runner do GitHub Actions (Ubuntu-latest) para suportar execução do Docker e Docker Compose
  - [x] Criar o job de build das imagens do Docker e subir os containers locais
  - [x] Inserir rotina de espera até que o container do MinIO atinja o status de `healthy`
  - [x] Configurar a execução do script `bin/run-pipeline.sh` dentro do runner de CI
  - [x] Coletar os relatórios de erros lógicos e log quantitativo gerado pelo pipeline do dbt
- [x] **Etapa 4: Validação do Fluxo Completo de CI**
  - [x] Simular um push de código contendo erro intencional no dbt para verificar se o CI falha e bloqueia a integração
  - [x] Simular um push de código correto e verificar se a esteira completa é executada com sucesso
  - [x] Atualizar o status dos testes e validações na Matriz de Rastreabilidade (RTM)

---

## 3. Lista de Arquivos Planejada (File List)

- [x] `.github/workflows/ci.yml` -> Configuração e descrição dos jobs e etapas da esteira de CI do GitHub Actions.
- [x] `docs/stories/story-04-ci-github-actions.md` -> Este documento de história de progresso de CI.
- [x] `bin/ci-integration-test.sh` -> Script opcional facilitador para testar a inicialização do compose e healthcheck no runner de CI.

---

## 4. Riscos e Ambiguidades

### Riscos Técnicos de Implementação (3)
1.  **Exaustão de Recursos no Runner de CI do GitHub**: A execução de testes de integração dinâmicos exige build de múltiplas imagens Docker locais e a execução concorrente de MinIO, dbt e DuckDB. Em runners gratuitos padrão do GitHub Actions (que possuem apenas 2 vCPUs e 7GB de RAM), o build concorrente pode falhar por falta de memória ou CPU, resultando em falhas falsas de build (*flaky builds*).
2.  **Vazamento de Segredos do MinIO nos Logs Públicos do GitHub Actions**: Se o pipeline falhar na inicialização e o comando `docker compose logs` for executado para depuração no runner de CI, a chave privada e a senha do MinIO (injetadas via variáveis de ambiente no container) podem ser impressas em texto claro nos logs públicos do GitHub.
3.  **Divergência de Ambiente entre o Runner e o Host Local**: O runner do GitHub Actions roda sobre uma máquina virtual limpa com Ubuntu Server. Se o pipeline local depender de configurações específicas do sistema operacional do host de desenvolvimento local (como caminhos de pasta absolutos, chaves SSH do host ou mapeamentos de rede física), os testes falharão na esteira de CI mesmo funcionando perfeitamente na máquina de trabalho.

### Ambiguidades Pendentes (2)
1.  **Políticas de Cache de Imagens Docker e dbt no CI**: Não há definição se o workflow deve utilizar cache para camadas do Docker e pacotes pip para acelerar as execuções (que podem demorar mais de 5 minutos por execução sem cache). O dbt também gera metadados temporários que, se cacheados, podem mascarar falhas lógicas entre diferentes execuções.
2.  **Necessidade de Testes Dinâmicos Concorrentes (Performance) no CI**: Permanece ambíguo se a esteira de CI deve rodar os testes de carga com o `k6` a cada push ou se estes devem ficar restritos a execuções sob demanda no ambiente local, visto que rodar testes de performance longos (como o de Soak com duração de 4 horas) é inviável financeiramente e tecnicamente em runners padrão de integração contínua.

---
*Fim do Documento da Story.*

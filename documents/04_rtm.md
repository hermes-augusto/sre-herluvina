# Matriz de Rastreabilidade de Requisitos (RTM) - Northwind Traders

Este documento apresenta a Matriz de Rastreabilidade de Requisitos (RTM) para a plataforma analítica local da Northwind Traders. O objetivo da RTM é garantir que cada Requisito Funcional (RF) e Requisito Não Funcional (RNF) esteja mapeado para um componente correspondente da arquitetura especificada em [documents/03_architecture.md](file:///workspaces/sre-herluvina/documents/03_architecture.md) e possua um Caso de Teste (TC) associado para validação de qualidade.

---

## 1. Matriz de Rastreabilidade (RTM)

A tabela abaixo vincula os requisitos aos componentes RM-ODP e aos casos de teste propostos. Qualquer requisito sem componente ou sem caso de teste associado é classificado com o status **Aberto**.

| Req | Tipo | Origem (Stakeholder / Documento) | Componente (RM-ODP) | Teste/Evidência (TC-NN) | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **RF-01** | Funcional | Engenharia de Dados / [01_functional_requirements.md](file:///workspaces/sre-herluvina/documents/01_functional_requirements.md) | `Minio Object Storage` / `dbt-duckdb Adapter` | `TC-01` | **Coberto** |
| **RF-02** | Funcional | Analistas de BI, Liderança Executiva / [01_functional_requirements.md](file:///workspaces/sre-herluvina/documents/01_functional_requirements.md) | `dbt CLI Engine` (Marts Layer) | `TC-02` | **Coberto** |
| **RF-03** | Funcional | Engenharia de Dados / [01_functional_requirements.md](file:///workspaces/sre-herluvina/documents/01_functional_requirements.md) | `dbt CLI Engine` (Intermediate Layer) | `TC-03` | **Coberto** |
| **RF-04** | Funcional | Operações e Logística, Analistas de BI / [01_functional_requirements.md](file:///workspaces/sre-herluvina/documents/01_functional_requirements.md) | `dbt CLI Engine` (Intermediate Layer) | `TC-04` | **Coberto** |
| **RF-05** | Funcional | Operações e Logística, Liderança Executiva / [01_functional_requirements.md](file:///workspaces/sre-herluvina/documents/01_functional_requirements.md) | `dbt CLI Engine` / `Streamlit Web UI` | `TC-05` | **Coberto** |
| **RF-06** | Funcional | Operações e Logística, Liderança Executiva / [01_functional_requirements.md](file:///workspaces/sre-herluvina/documents/01_functional_requirements.md) | `dbt CLI Engine` / `Streamlit Web UI` | `TC-06` | **Coberto** |
| **RF-07** | Funcional | Liderança Executiva, Operações e Logística / [01_functional_requirements.md](file:///workspaces/sre-herluvina/documents/01_functional_requirements.md) | `dbt CLI Engine` (Marts Layer) | `TC-07` | **Coberto** |
| **RF-08** | Funcional | Engenharia de Dados, SRE / [01_functional_requirements.md](file:///workspaces/sre-herluvina/documents/01_functional_requirements.md) | `dbt CLI Engine` / `Pipeline Shell Trigger` | `TC-08` | **Coberto** |
| **RF-09** | Funcional | Engenharia de Dados, SRE / [01_functional_requirements.md](file:///workspaces/sre-herluvina/documents/01_functional_requirements.md) | `Pipeline Shell Trigger` / `Minio Object Storage` | `TC-09` | **Coberto** |
| **RNF-01** | Não Funcional | Engenharia de Dados, SRE / [02_non_functional_requirements.md](file:///workspaces/sre-herluvina/documents/02_non_functional_requirements.md) | `dbt CLI Engine` (`dbt test` constraints) | `TC-10` | **Coberto** |
| **RNF-02** | Não Funcional | Engenharia de Dados, SRE / [02_non_functional_requirements.md](file:///workspaces/sre-herluvina/documents/02_non_functional_requirements.md) | `Pipeline Shell Trigger` / `Minio Object Storage` | `TC-11` | **Coberto** |
| **RNF-03** | Não Funcional | Liderança Executiva, Engenharia / [02_non_functional_requirements.md](file:///workspaces/sre-herluvina/documents/02_non_functional_requirements.md) | `Pipeline Shell Trigger` (Timestamps check) | `TC-12` / `TC-26` | **Coberto** |
| **RNF-04** | Não Funcional | SRE, Engenharia / [02_non_functional_requirements.md](file:///workspaces/sre-herluvina/documents/02_non_functional_requirements.md) | `Pipeline Shell Trigger` (Log volume) | `TC-13` | **Coberto** |
| **RNF-05** | Não Funcional | Analistas de BI / [02_non_functional_requirements.md](file:///workspaces/sre-herluvina/documents/02_non_functional_requirements.md) | `northwind.duckdb File` (Read-only flag) | `TC-14` / `TC-24` | **Coberto** |
| **RNF-06** | Não Funcional | Engenharia de Dados / [02_non_functional_requirements.md](file:///workspaces/sre-herluvina/documents/02_non_functional_requirements.md) | `Minio Object Storage` / `dbt-duckdb Adapter` | `TC-15` | **Coberto** |
| **RNF-07** | Não Funcional | Analistas de BI / [02_non_functional_requirements.md](file:///workspaces/sre-herluvina/documents/02_non_functional_requirements.md) | `northwind.duckdb File` (Index/Query optimization) | `TC-16` / `TC-24` / `TC-25` / `TC-27` | **Coberto** |
| **RNF-08** | Não Funcional | Engenharia, SRE / [02_non_functional_requirements.md](file:///workspaces/sre-herluvina/documents/02_non_functional_requirements.md) | `dbt CLI Engine` (Materialization strategies) | `TC-17` | **Coberto** |
| **RNF-09** | Não Funcional | SRE / [02_non_functional_requirements.md](file:///workspaces/sre-herluvina/documents/02_non_functional_requirements.md) | *Nenhum componente nativo* (Ver Seção 3) | `TC-18` / `TC-25` / `TC-26` / `TC-27` / `TC-SEC-03` | **Coberto** |
| **RNF-10** | Não Funcional | SRE / [02_non_functional_requirements.md](file:///workspaces/sre-herluvina/documents/02_non_functional_requirements.md) | `Docker Compose` / `.gitignore` | `TC-19` / `TC-SEC-01` / `TC-SEC-04` | **Coberto** |
| **RNF-11** | Não Funcional | Engenharia de Dados / [02_non_functional_requirements.md](file:///workspaces/sre-herluvina/documents/02_non_functional_requirements.md) | `app/audit.py` / `audit_log` DuckDB | `TC-20` / `TC-SEC-05` | **Coberto** |
| **RNF-12** | Não Funcional | SRE, Engenharia de Dados / [02_non_functional_requirements.md](file:///workspaces/sre-herluvina/documents/02_non_functional_requirements.md) | `Pipeline Shell Trigger` (Alerting routine) | `TC-21` | **Coberto** |
| **RNF-13** | Não Funcional | Engenharia de Dados / [02_non_functional_requirements.md](file:///workspaces/sre-herluvina/documents/02_non_functional_requirements.md) | `dbt CLI Engine` (dbt-expectations) | `TC-22` | **Coberto** |
| **RNF-14** | Não Funcional | SRE, Engenharia de Dados / [02_non_functional_requirements.md](file:///workspaces/sre-herluvina/documents/02_non_functional_requirements.md) | `Docker Compose` (Setup verification) | `TC-23` / `TC-SEC-02` | **Coberto** |

---

## 2. Detalhamento dos Casos de Teste Propostos (TC-NN)

Esta seção especifica a lógica de teste ou verificação de evidência para cada caso proposto:

*   **TC-01 (RF-01)**: Executar o upload dos CSVs brutos no bucket do Minio local e disparar a carga inicial no DuckDB via API do S3 (httpfs), verificando se todos os cabeçalhos de colunas foram mapeados com sucesso sem falhas de conversão de esquema.
*   **TC-02 (RF-02)**: Consultar os valores consolidados por categoria na tabela `fct_order_items` e verificar matematicamente contra uma planilha de controle se o lucro líquido calculado bate exatamente com: `receita_bruta - frete_rateado - desconto`.
*   **TC-03 (RF-03)**: Validar se a soma do frete proporcional de todos os itens de um pedido na fato é igual ao frete total do cabeçalho daquele pedido. Testar pedidos com 1 item, múltiplos itens de valores distintos e pedidos de valor bruto zero.
*   **TC-04 (RF-04)**: Inserir pedidos de teste com datas conhecidas e validar se o tempo de envio em dias (`shipped_date - order_date`) e atraso (`shipped_date - required_date`) é calculado corretamente, gerando valores positivos para atrasos e negativos ou nulos para entregas adiantadas.
*   **TC-05 (RF-05)**: Verificar se as agregações geográficas de entrega atrasada agrupadas por cliente e região contam corretamente os atrasos sem duplicar linhas de transações ou rotas.
*   **TC-06 (RF-06)**: Validar se a junção com a dimensão de transportadoras calcula corretamente as médias de prazo e soma de fretes pagos agrupados por fornecedor.
*   **TC-07 (RF-07)**: Verificar se o volume de pedidos processados é corretamente associado ao funcionário responsável por meio da chave estrangeira correspondente.
*   **TC-08 (RF-08)**: Simular a entrada de um registro de pedido inválido (onde `shipped_date < order_date`) e confirmar se o pipeline detecta e marca este registro como inconsistente, gravando o alerta correspondente na tabela de qualidade de dados.
*   **TC-09 (RF-09)**: Comparar o número de linhas do arquivo CSV bruto carregado no bucket do Minio com a contagem total de registros persistidos na camada de staging do DuckDB.
*   **TC-10 (RNF-01)**: Rodar o comando `dbt test` para validar as constraints de integridade referencial (relacionamento entre chaves estrangeiras na fato de detalhes de pedidos e as dimensões correspondentes).
*   **TC-11 (RNF-02)**: Executar teste automatizado comparando as contagens de linhas de arquivos no bucket do Minio contra o destino analítico. O teste deve falhar (exibir código de saída 1) se houver qualquer divergência na contagem.
*   **TC-12 (RNF-03)**: Verificar se o tempo total decorrido registrado pelos timestamps de início e fim no log do pipeline é menor ou igual a 45 minutos.
*   **TC-13 (RNF-04)**: Inspecionar o volume de logs montado localmente no host e validar se 100% das falhas ocorridas nas transformações e cargas de dados do dbt e do Minio estão devidamente capturadas.
*   **TC-14 (RNF-05)**: Executar uma simulação de concorrência onde consultas frequentes de leitura no Streamlit são feitas enquanto um script de carga do dbt grava no banco local. Garantir que as leituras não entrem em timeout.
*   **TC-15 (RNF-06)**: Carregar no Minio um arquivo CSV contendo caracteres acentuados especiais em formato UTF-8 e confirmar se os caracteres são decodificados e exibidos corretamente no banco analítico sem quebras.
*   **TC-16 (RNF-07)**: Executar um conjunto de 10 consultas SQL analíticas de agregação complexas no DuckDB e verificar se o tempo médio de resposta no percentil 95 (P95) é menor ou igual a 5 segundos.
*   **TC-17 (RNF-08)**: Rodar o pipeline diário duas vezes consecutivas para o mesmo conjunto de dados brutos carregados no Minio e garantir que não haja duplicação de registros na camada final (garantia de idempotência).
*   **TC-18 (RNF-09)**: Verificar a consistência e o Uptime do arquivo local de banco analítico. Como o DuckDB é embutido e não roda como um serviço de banco de dados ativo (daemon), o teste deve monitorar a acessibilidade contínua ao arquivo pela aplicação do Streamlit.
*   **TC-19 (RNF-10)**: Rodar uma ferramenta local de varredura estática de segurança no código-fonte do projeto (como o gitleaks) para garantir que nenhuma chave de API ou credencial secreta local (incluindo as access keys do Minio) foi gravada.
*   **TC-20 (RNF-11)**: Validar a gravação de logs de auditoria no repositório. Como o DuckDB não possui suporte nativo a triggers de auditoria automáticos de gravação por ser um banco embarcado, este teste deve validar a existência de tabelas ou arquivos de log gerados programaticamente durante a escrita.
*   **TC-21 (RNF-12)**: Simular uma falha de banco de dados (ex: arquivo de banco corrompido) e garantir que o script de trigger do pipeline capture a falha e escreva um alerta estruturado na auditoria do sistema em até 5 minutos.
*   **TC-22 (RNF-13)**: Validar se a suíte de testes de dados do dbt e do dbt-expectations cobre pelo menos 90% das colunas finais das tabelas expostas.
*   **TC-23 (RNF-14)**: Rodar o comando `docker compose up --build` em uma máquina nova/limpa e medir se o tempo total até a inicialização bem-sucedida do Minio e do Streamlit é menor ou igual a 15 minutos.
*   **TC-24 (RNF-05 / RNF-07)**: Executar teste de carga simulando 20 usuários virtuais concorrentes no Streamlit realizando consultas analíticas, paralelamente à gravação concorrente de 50.000 registros pelo pipeline.
*   **TC-25 (RNF-09 / RNF-07)**: Executar teste de soak (estabilidade prolongada) sob carga contínua de 10 usuários por 4 horas para identificar eventuais vazamentos de memória e degradação progressiva de latência.
*   **TC-26 (RNF-09 / RNF-03)**: Executar teste de spike (pico repentino) elevando instantaneamente a carga para 100 usuários virtuais e injetando simultaneamente 250.000 registros analíticos no pipeline para verificar a resiliência a picos.
*   **TC-27 (RNF-07 / RNF-09)**: Executar teste de estresse em escada de 10 até 300 usuários concorrentes sob volumetria de 1.000.000 de registros para identificar o ponto exato de quebra e saturação de recursos locais.
*   **TC-SEC-01 (RNF-10)**: Rodar o analisador estático Bandit sobre o diretório do código-fonte Python (`app/`) para detectar injeções de comandos, SQL dynamic execution e brechas SAST comuns.
*   **TC-SEC-02 (RNF-14)**: Executar varredura de composição SCA com Trivy no `requirements.txt` e nas imagens Docker do projeto para detectar dependências desatualizadas com CVEs críticas.
*   **TC-SEC-03 (RNF-09)**: Realizar testes dinâmicos de vulnerabilidade DAST no Streamlit exposto usando a CLI do OWASP ZAP para detectar XSS, injeção de parâmetros e configurações incorretas de HTTP.
*   **TC-SEC-04 (RNF-10)**: Configurar hooks pré-commit e varreduras com Gitleaks para detectar vazamento de chaves privadas do S3 ou credenciais no histórico do Git.
*   **TC-SEC-05 (RNF-11)**: Executar varredura de postura de configuração com Prowler simulado sobre a API S3 compatível do container MinIO local para validar encriptação, permissões de buckets e controle de acesso.

---

## 3. Análise de Gaps e Requisitos "Abertos"

Identificamos inicialmente duas brechas analíticas (gaps) na infraestrutura local projetada na arquitetura. Atualmente, apenas um requisito de auditoria de banco permanece classificado com o status **Aberto**:

### Gap 1: RNF-09 (Disponibilidade e Uptime do Repositório Analítico Local) - Mitigado e Coberto
*   **Motivo**: O DuckDB é um banco de dados embarcado e sem servidor (serverless/embedded). Ele funciona lendo e gravando direto em um arquivo local (`northwind.duckdb`). Isso significa que não há um "processo/serviço" de banco de dados que fica rodando continuamente em segundo plano para aceitar conexões TCP. O Uptime de 99.0% especificado em RNF-09 não pode ser testado por monitoramento de porta tradicional (ex: ping na porta 5432).
*   **Mitigação Adotada**: Coberto e mitigado por meio do plano de testes de carga em [documents/05_performance_test_plan.md](file:///workspaces/sre-herluvina/documents/05_performance_test_plan.md) (`TC-25`, `TC-26`, `TC-27`), que validam a disponibilidade do ecossistema local e a integridade de acesso ao arquivo DuckDB sob estresse contínuo pela aplicação do Streamlit.

### Gap 2: RNF-11 (Rastreabilidade de Alterações de Dados - Logs DML) - Mitigado e Coberto
*   **Motivo**: Como o DuckDB é um motor SQL embarcado em arquivos, ele não possui recursos nativos corporativos de triggers DML (tabelas de histórico de auditoria preenchidas automaticamente por gatilhos do banco ao inserir/deletar/atualizar linhas) e logs nativos avançados como o WAL (Write-Ahead Logging) do PostgreSQL. 
*   **Mitigação Adotada**: Coberto e mitigado por meio do script de auditoria quantitativa no nível da aplicação (`app/audit.py`), que persiste registros e status detalhados de reconciliação de volumes na tabela de logs de auditoria (`audit_log`) do DuckDB a cada execução do pipeline.

---

## 4. Riscos e Ambiguidades de Rastreabilidade

### Riscos (3)
1.  **Falsos Positivos nos Testes de Concorrência (RNF-05)**: O teste `TC-14` pode passar em ambientes de desenvolvimento locais com poucos dados e usuários simulados, mas falhar em produção local se múltiplos analistas de BI tentarem ler o painel do Streamlit enquanto uma carga de dados massiva do dbt está em execução.
2.  **Acúmulo de Débito Técnico nos Gaps de Auditoria**: Ignorar a falta de triggers nativos no DuckDB (RNF-11) e confiar apenas nos logs do dbt pode fazer com que alterações manuais diretas no arquivo `northwind.duckdb` (feitas fora do dbt) ocorram sem qualquer rastro de auditoria.
3.  **Falta de Validação Real de Ingestão no TC-09**: Comparar apenas contagens de linhas de arquivos CSV (RF-09 / RNF-02) no Minio não garante que as linhas foram importadas corretamente em suas respectivas colunas (pode ocorrer truncamento silencioso de dados ou carregamento de colunas nulas).

### Ambiguidades (2)
1.  **Origem do Requisito de Produtividade dos Funcionários (RF-07)**: Não há clareza em [01_functional_requirements.md](file:///workspaces/sre-herluvina/documents/01_functional_requirements.md) sobre qual diretoria operacional utilizará a métrica de produtividade ou como o tempo médio de processamento será correlacionado com o volume real de trabalho do funcionário sem violar regras locais de privacidade de dados.
2.  **Validação de Rastreamento de Erros Silenciosos (RNF-04)**: Há ambiguidade em como diferenciar falhas não estruturais (como dados incorretos que não disparam falha na query SQL) de falhas de execução que interrompem o pipeline, garantindo que mesmo as inconsistências lógicas silenciosas fiquem devidamente logadas.

---
*Fim do Documento RTM.*
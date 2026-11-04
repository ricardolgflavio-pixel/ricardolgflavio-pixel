# LinkedIn Kit — Posicionamento para Estágio em Segurança, Direito Digital e IA

**Autor:** Ricardo Luiz G. Flávio · **Perfil:** <https://www.linkedin.com/in/ricardo-flavio/>

> Perfil-alvo: recrutadores de AppSec, DevSecOps, GRC/Privacidade, Direito Digital e Engenharia de IA.
> Limites do LinkedIn respeitados: headline ≤ 220 caracteres · "Sobre" ≤ 2.600 · descrição de experiência ≤ 2.000 · posts ≤ 3.000.
> Dados biográficos fornecidos pelo titular. Localização pública: **Lorena, São Paulo, Brasil**. Nunca incluir endereço residencial ou documentos pessoais.

## Índice

1. [Headlines (3 opções)](#1-headlines-3-opções)
2. [Seção "Sobre"](#2-seção-sobre-about)
3. [Experiência / Projetos (STAR)](#3-experiência--projetos-método-star)
4. [Competências (Skills)](#4-competências-skills)
5. [Posts prontos](#5-posts-técnicos-prontos)
6. [Checklist de perfil](#6-checklist-de-perfil)
7. [Perfil em inglês](#7-perfil-em-inglês-idioma-secundário-foco-em-vagas-nos-eua)
8. [Oito experiências profissionais](#8-trajetória-profissional--31-anos-desde-1995--career-history)
9. [Formação acadêmica](#9-formação-acadêmica--education)
10. [Licenças e certificados](#10-licenças-e-certificados--licenses-and-certifications)

---

## 1. Headlines (3 opções)

**Opção A — Híbrida: Direito Digital + AppSec** *(recomendada para vagas que pedem os dois perfis)*

```text
31 anos em Hardware, Redes & ECU/EPROM | DevSecOps, AppSec, IA & LGPD | Direito (7º sem.) + Seg. Informação (3º sem.) + Mecatrônica | Buscando estágio
```

**Opção B — Foco técnico: DevSecOps / Engenharia de IA**

```text
Segurança da Informação (UCB) | DevSecOps & AI Engineering: Python, LangGraph, RAG com pgvector, SAST (AST, Bandit, Semgrep) e OAuth2 | Buscando estágio
```

**Opção C — Foco jurídico: GRC / LGPD**

```text
Direito (FACIC) + Segurança da Informação (UCB) | GRC, LGPD, Propriedade Intelectual e Governança de IA | Compliance as Code | Buscando estágio
```

---

## 2. Seção "Sobre" (About)

```text
Tenho 31 anos de base prática, desde 1995, em Hardware, Redes, Eletrônica Embarcada Automotiva (ECU/EPROM/ADAS) e Telemetria Satelital. Vivo em Lorena, São Paulo, Brasil.

Na Mecânica Rally, lidero a transformação digital e a implantação da vertical de seguros e rastreamento para linha leve, pesada, motos e máquinas, impulsionando a empresa em +60%. Sou credenciado Ituran desde 2018, com atuação técnica em raio de 300 km, diagnóstico de telemetria satelital/RF e segurança de IoT/M2M.

Minha trajetória inclui reprogramação de ECU diretamente em EPROM, mapas de injeção e avanço, conversão de combustível, GNV, câmbios, Air-Bag, ABS e ADAS; também implantação de laboratórios de hardware, redes, servidores, provimento de internet e docência técnica.

FORMAÇÃO
• Direito — FACIC, 7º semestre (2023–2028).
• CST em Segurança da Informação — UCB, 3º semestre (2025–2028).
• Técnico em Mecatrônica — UNI VITÓRIA TEC, concluinte 2026.
• 7 certificados oficiais, 294 horas: Hackers do Bem (básico e nivelamento), redes neurais, Direito Autoral e Crimes Cibernéticos, Direito Espacial, Windows Server e Inglês 2.

Sou autor do AutoTech AI OS & Zezé da Regulagem: ecossistema automotivo com Python, agentes LangGraph, RAG em PostgreSQL/pgvector, OAuth2/Vault e DevSecOps. No showcase público, demonstro o gate jurídico Pydantic, auditor AST, Bandit, Semgrep e validação de saída OWASP LLM05. O produto completo é privado e está em teste em oficina real.

Transformo requisitos de LGPD e propriedade intelectual em controles executáveis: origem auditada, dados factuais, bloqueio de fontes proprietárias fechadas e minimização de dados pessoais.

Busco estágio em Segurança da Informação (AppSec, DevSecOps, Cibersegurança Automotiva, GRC), Direito Digital (LGPD, Governança de IA) ou Engenharia de IA. Também estou disponível para projetos e consultoria técnica.

Portfólio: github.com/ricardolgflavio-pixel/ricardolgflavio-pixel
```

---

## 3. Experiência / Projetos (Método STAR)

**Título:** Fundador e Engenheiro de Segurança & IA — AutoTech AI OS & Zezé da Regulagem
**Tipo:** Projeto autoral · **Competências a vincular:** Python, LangGraph, RAG, pgvector, DevSecOps, SAST, OAuth2, LGPD, Governança de IA

**Descrição (cole no campo de descrição):**

```text
SaaS B2B/B2C em monorepo para o mercado automotivo: agentes de IA, planos de manutenção preventiva, SOS Guincho e Barganha do Zezé (marketplace P2P).

SITUAÇÃO
▪ IA de diagnóstico automotivo exige dados técnicos, e extrair bases proprietárias fechadas (Doutor-IE, Simplo) arrisca violar as Leis 9.610/98 e 9.609/98. A telemetria própria traz dados pessoais sujeitos à LGPD.

TAREFA
▪ Projetar um sistema multi-agente com RAG seguro e juridicamente defensável desde a origem, com evidências auditáveis.

AÇÃO
▪ Orquestrei 3 agentes em LangGraph: Diagnóstico Mecânico, Visão Computacional e Comercial/Orçamentação.
▪ Modelei o RAG em PostgreSQL + pgvector com filtro de conformidade de PI: origem lícita, dado factual e nenhum scraping.
▪ Implementei Compliance as Code com Pydantic v2: validação de origem, licença, copyright e PII (LGPD) antes de gravar no índice.
▪ Apliquei OAuth2 com escopos mínimos, segredos no Vault, Pydantic e Mypy strict.
▪ Construí o "Guardião", auditor SAST próprio baseado em AST (eval/exec, segredos hardcoded, SQL concatenado, endpoints sem validação), integrado a Bandit, Semgrep e pip-audit.
▪ Redigi um ADR com matriz de risco (OWASP Top 10 for LLM, LGPD, Lei 9.610/98).

RESULTADO TÉCNICO
▪ Quality gate de CI que bloqueia merge com falhas de severidade alta (tipagem estrita, SAST em 3 camadas, SCA).
▪ Achados com CWE e OWASP para injeção, segredos expostos e execução dinâmica.

RESULTADO JURÍDICO
▪ Política de PI aplicada por código: fontes proibidas são rejeitadas na ingestão, com trilha de auditoria (audit_id e SHA-256).
▪ Privacy by Design: telemetria só entra com base legal, anonimização e segregação por tenant.

Stack: Python, LangGraph, FastAPI, PostgreSQL, pgvector, Pydantic, Mypy, Bandit, Semgrep, GitHub Actions, OAuth2, Vault.
```

**Formação (campos de educação):**

- *Universidade Católica de Brasília (UCB)* — Curso Superior de Tecnologia (Tecnólogo) em Segurança da Informação · 3º semestre · 2025–2028. Atividades: AppSec, DevSecOps, criptografia, GRC.
- *FACIC — Cruzeiro (SP)* — Bacharelado em Direito · 7º semestre · 2023–2028. Atividades: Direito Digital, LGPD, Propriedade Intelectual.

---

## 4. Competências (Skills)

> O LinkedIn aceita até 50. **Fixe as 3 primeiras** (Application Security, DevSecOps, LGPD): são as mais buscadas pelos recrutadores-alvo.

**Segurança e DevSecOps (18)**
Application Security (AppSec) · DevSecOps · SAST (Static Application Security Testing) · Segurança da Informação · OWASP Top 10 · OWASP Top 10 for LLM Applications · Secure SDLC · Análise Estática de Código · Threat Modeling · OAuth 2.0 · Gestão de Segredos · HashiCorp Vault · Bandit · Semgrep · CI/CD · GitHub Actions · Análise de Vulnerabilidades · ISO/IEC 27001

**IA e Engenharia de Software (14)**
Python · LangGraph · Sistemas Multi-Agente · Retrieval-Augmented Generation (RAG) · Inteligência Artificial Generativa · Large Language Models (LLM) · PostgreSQL · pgvector · Pydantic · Mypy · FastAPI · Visão Computacional · Arquitetura de Software · Monorepo

**Jurídico, GRC e Privacidade (18)**
LGPD (Lei Geral de Proteção de Dados) · Direito Digital · Governança de IA · Propriedade Intelectual · Direitos Autorais · Lei do Software · Privacy by Design · Governança, Risco e Conformidade (GRC) · Compliance · Gestão de Riscos · Proteção de Dados · Auditoria · Legal Design · Contratos · Pesquisa Jurídica · Redação Jurídica · Termos de Uso e Política de Privacidade · Compliance as Code

---

## 5. Posts técnicos prontos

> Dica: publique entre terça e quinta, responda aos comentários na primeira hora e coloque o link do GitHub **no primeiro comentário** (o LinkedIn tende a reduzir o alcance de posts com link externo no corpo).

### Post 1 — Apresentação profissional e busca por estágio

```text
DA EPROM AO LANGGRAPH: 31 ANOS DE PRÁTICA APLICADOS À CIBERSEGURANÇA E GOVERNANÇA DE IA

Comecei em 1995, com diagnóstico de injeção eletrônica. Passei por hardware, redes, servidores, docência e reprogramação de ECU diretamente em EPROM: mapas de injeção, avanço e conversão de combustível.

Desde 2018, atuo como credenciado Ituran em telemetria satelital/RF e lidero a transformação digital da Mecânica Rally. A implantação da vertical de seguros e rastreamento contribuiu para +60% de crescimento da empresa.

Essa base prática sustenta o AutoTech AI OS & Zezé da Regulagem, ecossistema em teste em oficina real:
1. Hardware, ECU/EPROM & Telemetria Satelital.
2. Multiagentes LangGraph + RAG em PostgreSQL/pgvector.
3. Compliance as Code: origem auditada, LGPD e propriedade intelectual.
4. Pipeline DevSecOps SAST: Guardião AST, Bandit e Semgrep.

Hoje curso Direito (7º semestre, FACIC) e Segurança da Informação (3º semestre, UCB), além do Técnico em Mecatrônica (UNI VITÓRIA TEC, concluinte 2026). Concluí 7 certificados oficiais, somando 294 horas, em cibersegurança, IA, Direito, infraestrutura e inglês.

Busco estágio em AppSec, DevSecOps, Cibersegurança Automotiva, GRC, Direito Digital ou Engenharia de IA. Também estou disponível para projetos e consultoria técnica em Lorena, São Paulo, Brasil.

A vitrine pública reúne código executável, controles de segurança e governança com evidências. Link no primeiro comentário.

#Ciberseguranca #DevSecOps #AppSec #DireitoDigital #LGPD #GovernancaDeIA #LangGraph #Estagio
```

### Post 2 — Como construir RAG corporativo sem violar Direitos Autorais e PI

```text
Seu RAG está respondendo com conteúdo que a sua empresa tem o direito de usar?

Em IA corporativa, o risco jurídico começa na ingestão. Depois que um conteúdo ilícito vira vetor, ele contamina o índice, as respostas e as evidências de auditoria.

No AutoTech AI OS (diagnóstico automotivo com agentes LangGraph), decidi impedir a entrada em vez de remediar depois. As regras:

1️⃣ Fato não é obra.
A Lei 9.610/98 protege a criação intelectual e, no art. 8º, exclui da proteção ideias, métodos e informações de uso comum. "Bobina com 0,5 Ω", "P0301 = falha de combustão no cilindro 1" e "torque de 38 Nm" são fatos técnicos. Texto editorial, diagramas autorais e a curadoria de uma base são outra história.

2️⃣ Origem lícita ou nada.
O dado só entra se vier de: catálogo aberto de fabricante, padrão SAE/ISO ou telemetria própria (Ordens de Serviço e scanner OBD2).

3️⃣ Scraping de base proprietária é proibido por arquitetura.
Bases fechadas, como Doutor-IE e Simplo, estão em lista de bloqueio. A coleta por web scraping é rejeitada pelo schema. É uma questão de Lei 9.609/98, Lei 9.610/98 e termos de uso.

4️⃣ Privacy by Design.
Telemetria exige base legal LGPD, anonimização e segregação por tenant, e passa por varredura de CPF, telefone, e-mail e placa.

5️⃣ Compliance as Code.
Tudo isso virou um contrato de dados em Pydantic v2: cada fragmento carrega fonte, licença, método de coleta, audit_id e hash SHA-256. Se algo não prova a origem, não entra no pgvector.

Limites honestos: regex de PII e de copyright geram falsos positivos e negativos. Por isso há anonimização na origem, revisão humana e auditoria amostral. E catálogo "aberto" também tem termos de uso, então o domínio só entra na allow-list depois de revisão jurídica.

O que mais mudou meu jeito de pensar: política em PDF não impede ninguém de errar, mas um validador em CI impede.

O código e o ADR (matriz de risco, OWASP Top 10 for LLM e LGPD) estão no meu GitHub, link no primeiro comentário.

#RAG #PropriedadeIntelectual #DireitosAutorais #LGPD #GovernancaDeIA #ComplianceAsCode #Pydantic #pgvector

(Conteúdo educacional; não constitui aconselhamento jurídico.)
```

### Post 3 — Esteira DevSecOps em Python para proteger agentes de IA

```text
Um agente de IA é código que recebe texto não confiável e pode agir no mundo. Se o LLM gera um comando, uma consulta SQL ou um JSON, tudo isso é entrada não confiável. É o que o OWASP Top 10 for LLM chama de Improper Output Handling (LLM05).

A esteira DevSecOps que montei para o AutoTech AI OS, em 5 camadas:

1️⃣ Pydantic v2 na fronteira
Todo dado que entra no agente ou sai dele passa por um modelo com extra="forbid", limites de tamanho e Enum. Entrada fora do contrato é rejeitada antes de qualquer lógica.

2️⃣ Mypy --strict
Tipagem estrita pega uma classe inteira de bugs antes do runtime e documenta o contrato de cada função.

3️⃣ Guardião: auditor próprio com AST
Usei ast.NodeVisitor para percorrer a árvore sintática e aplicar regras de domínio:
• eval/exec/__import__ (CWE-95)
• credencial hardcoded (CWE-798)
• SQL por f-string ou concatenação, inclusive via variável (CWE-89)
• endpoint sem tipo ou com dict/Any, ou seja, sem validação (CWE-20)
Cada achado sai com CWE, OWASP e correção sugerida. O quality gate falha o build por severidade.

Por que AST e não só regex? A AST entende estrutura: distingue um eval() real de uma string que contém "eval" e rastreia SQL montado em uma variável e passado depois para execute().

4️⃣ Bandit + Semgrep
Bandit cobre padrões conhecidos do ecossistema Python. Semgrep roda regras OWASP e as minhas regras de governança de IA, inclusive uma que bloqueia referências a bases proprietárias fechadas (Compliance as Code).

5️⃣ pip-audit
Dependências com versões fixadas e checadas contra vulnerabilidades conhecidas, para cobrir a cadeia de suprimentos (LLM03).

O Guardião também tem autoteste: um módulo vulnerável embutido garante que o detector continua enxergando cada regra. Teste do próprio teste.

Limitações: análise estática não substitui DAST, pentest nem revisão humana, e o rastreio de SQL é intraprocedural. Segurança é defesa em camadas.

O código, o workflow de GitHub Actions e o ADR estão no meu GitHub, link no primeiro comentário.

#DevSecOps #AppSec #Python #SAST #OWASP #LLMSecurity #Semgrep #Bandit #Pydantic #LangGraph
```

---

## 6. Checklist de perfil

- [ ] Foto profissional, banner com o diagrama da arquitetura ou do pipeline, URL personalizada (já definida: `linkedin.com/in/ricardo-flavio`).
- [ ] Headline escolhida (A, B ou C) e "Sobre" colados.
- [ ] Projeto cadastrado em **Experiência** (ou **Projetos**) com o link do GitHub.
- [ ] Repositório fixado no perfil do GitHub com README exibido e descrição curta.
- [ ] Competências adicionadas e as 3 principais fixadas.
- [ ] Modo "Open to Work" configurado para estágio (visível só para recrutadores, se preferir).
- [ ] Publicar 1 post por semana, na ordem: Post 1 → Post 2 → Post 3.
- [ ] Idiomas: Português (nativo) e Inglês (informe seu nível real).

---

## 7. Perfil em inglês (idioma secundário, foco em vagas nos EUA)

> Texto para o idioma secundário English do perfil; a aplicação deve ser verificada na sessão autenticada.

**Headline (EN)**

```text
31 Years in Hardware, Networks & ECU/EPROM | DevSecOps, AppSec, AI & LGPD | Law (7th sem.), Information Security (3rd sem.) & Mechatronics | Seeking Internship
```

**About (EN)**

```text
I bring 31 years of practical experience since 1995 in hardware, networks, automotive embedded electronics (ECU/EPROM/ADAS) and satellite telemetry. Based in Lorena, São Paulo, Brazil.

At Mecânica Rally, I lead digital transformation and the launch of insurance and vehicle-tracking services for cars, heavy vehicles, motorcycles and machinery, driving growth of over 60%. An accredited Ituran technical specialist since 2018, I work within a 300 km radius on satellite/RF telemetry, diagnostics and IoT/M2M security.

My background includes ECU reprogramming directly in EPROM memory, injection and ignition maps, fuel conversion, CNG systems, transmissions, Air-Bag, ABS and ADAS; hardware laboratory deployment, networks, internet servers and technical teaching.

EDUCATION
• Law, LL.B. — FACIC, 7th semester (2023–2028).
• Information Security, Technologist degree — UCB, 3rd semester (2025–2028).
• Technical Diploma in Mechatronics — UNI VITÓRIA TEC, completing in 2026.
• 7 official certificates totaling 294 hours: Hackers do Bem (basic and foundation), neural networks, copyright and cybercrime, space law, Windows Server and English 2.

I created AutoTech AI OS & Zezé da Regulagem: an automotive ecosystem using Python, LangGraph agents, PostgreSQL/pgvector RAG, OAuth2/Vault and DevSecOps. The public showcase demonstrates a Pydantic legal ingestion gate, an AST auditor, Bandit, Semgrep and OWASP LLM05 output validation. The full product is private and under testing in a real repair shop.

I translate LGPD and intellectual-property requirements into executable controls: audited provenance, factual data, blocked closed proprietary sources and personal-data minimization.

Seeking internships in Information Security (AppSec, DevSecOps, Automotive Cybersecurity, GRC), Digital Law (LGPD, AI Governance) or AI Engineering. Also available for technical projects and consulting.

Portfolio: github.com/ricardolgflavio-pixel/ricardolgflavio-pixel
```

**Project (EN)**

```text
B2B/B2C SaaS monorepo for the automotive aftermarket: AI agents, preventive-maintenance plans, SOS tow/emergency and a P2P marketplace.

SITUATION
▪ AI diagnosis for cars needs technical data, and scraping closed proprietary databases risks violating Brazilian copyright and software laws (9.610/98, 9.609/98). First-party telemetry also contains personal data under LGPD.

TASK
▪ Design a multi-agent RAG system that is secure and legally defensible by design, with auditable evidence.

ACTION
▪ Orchestrated 3 LangGraph agents: Mechanical Diagnosis, Computer Vision and Commercial Quoting.
▪ Modeled the RAG on PostgreSQL + pgvector with an IP-compliance filter: lawful source, factual data only, no scraping.
▪ Implemented Compliance as Code with Pydantic v2: validation of source, license, copyright markers and PII before anything is written to the index.
▪ Applied OAuth2 with least-privilege scopes, Vault-managed secrets, Pydantic and strict Mypy.
▪ Built "Guardião", an in-house AST-based SAST auditor (eval/exec, hardcoded secrets, string-built SQL, unvalidated endpoints), integrated with Bandit, Semgrep and pip-audit.
▪ Wrote an ADR with a risk matrix (OWASP Top 10 for LLM, LGPD, Copyright Law).

TECHNICAL RESULT
▪ CI quality gate that blocks merges on high-severity findings (strict typing, three SAST layers, SCA).
▪ Findings mapped to CWE and OWASP for injection, exposed secrets and dynamic execution.

LEGAL RESULT
▪ IP policy enforced as code: prohibited sources are rejected at ingestion, with an audit trail (audit_id and SHA-256).
▪ Privacy by Design: telemetry is admitted only with a lawful basis, anonymization and tenant segregation.

Stack: Python, LangGraph, FastAPI, PostgreSQL, pgvector, Pydantic, Mypy, Bandit, Semgrep, GitHub Actions, OAuth2, Vault.
```

## 8. Trajetória profissional — 31 anos desde 1995 / Career history

### 2018 – Presente / Present | Mecânica Rally

**PT-BR — Gestor Sênior, Responsável Técnico & Arquiteto de Transformação Digital (AutoTech AI OS)** · Lorena, São Paulo, Brasil

Liderança técnica e governança; transformação digital e implantação da vertical de seguros e rastreadores (linha leve, pesada, motos e máquinas), impulsionando a empresa em +60%. Arquitetura do AutoTech AI OS & Zezé da Regulagem (Python, LangGraph, pgvector, DevSecOps, LGPD/IP Compliance).

**EN-US — Senior Manager, Technical Lead & Digital Transformation Architect (AutoTech AI OS)** · Lorena, São Paulo, Brazil

Technical leadership and governance; digital transformation and launch of insurance and tracking services for cars, heavy vehicles, motorcycles and machinery, driving over 60% growth. Architecture of AutoTech AI OS & Zezé da Regulagem (Python, LangGraph, pgvector, DevSecOps, LGPD/IP Compliance).

### 2018 – Presente / Present | Credenciado Ituran Rastreadores

**PT-BR — Especialista Técnico em Telemetria Satelital, Rastreamento & Cibersegurança Automotiva** · Lorena, São Paulo, Brasil

Instalação, manutenção e diagnóstico de telemetria satelital/RF em frotas pesadas, máquinas, veículos leves e motos, atendendo multinacionais, montadoras e seguradoras, com foco em segurança física/lógica de IoT/M2M e cibersegurança automotiva. Atuação em raio de 300 km de Lorena, SP.

**EN-US — Technical Specialist in Satellite Telemetry, Tracking & Automotive Cybersecurity** · Lorena, São Paulo, Brazil

Installation, maintenance and diagnostics of satellite/RF telemetry for heavy fleets, machinery, cars and motorcycles, serving multinationals, automakers and insurers. Focus on IoT/M2M physical and logical security and automotive cybersecurity, within a 300 km radius of Lorena, SP.

### 2003 – 2017 | Mecânica Rally 2

**PT-BR — Fundador, Gestor & Especialista em Eletrônica Embarcada (ECU / EPROM / ADAS)** · Lorena, São Paulo, Brasil

Reprogramação de módulos de injeção eletrônica (ECU) diretamente na memória EPROM (mapas de injeção, avanço de ignição, conversão de combustível na ECU), GNV (3ª, 5ª e 6ª geração com injeção direta), câmbio automático/automatizado, Air-Bag, ABS e sistemas ADAS, além da gestão integral do negócio e TI.

**EN-US — Founder, Manager & Embedded Electronics Specialist (ECU / EPROM / ADAS)** · Lorena, São Paulo, Brazil

ECU reprogramming directly in EPROM memory (injection maps, ignition timing and ECU fuel conversion); 3rd, 5th and 6th generation CNG with direct injection, automatic/automated transmissions, Air-Bag, ABS and ADAS. Full business and IT management.

### 2003 – 2003 | Onlinet Provedor de Internet

**PT-BR — Técnico de Infraestrutura de Redes, Servidores & Provimento de Acesso (UOL / Speedy Telefônica)** · Lorena, São Paulo, Brasil

Administração de servidores de internet, configuração de redes, implantação de acesso Speedy (Telefônica) e suporte técnico.

**EN-US — Network Infrastructure, Servers & Internet Access Technician (UOL / Speedy Telefônica)** · Lorena, São Paulo, Brazil

Internet server administration, network configuration, Speedy (Telefônica) access deployment and technical support.

### 2000 – 2002 | MBD Informática

**PT-BR — Executivo de Implantação de Laboratório de Hardware, Redes & Desenvolvimento** · Lorena, São Paulo, Brasil

Implantação da oficina de hardware (desktops, notebooks, impressoras), redes, programação, vendas técnicas e suporte. Site: loja.mbd.com.br.

**EN-US — Hardware Laboratory, Networks & Development Deployment Executive** · Lorena, São Paulo, Brazil

Deployed the hardware workshop (desktops, notebooks, printers), networks, programming, technical sales and support. Website: loja.mbd.com.br.

### 1998 – 2000 | Informat Escola de Computação

**PT-BR — Professor de Hardware, Infraestrutura & Pesquisador de Material Didático** · Lorena, São Paulo, Brasil

Docência em hardware e redes, pesquisa tecnológica e desenvolvimento de material didático.

**EN-US — Hardware & Infrastructure Instructor and Teaching Materials Researcher** · Lorena, São Paulo, Brazil

Hardware and networking instruction, technology research and development of teaching materials.

### 1997 – 2000 | Caas Computadores

**PT-BR — Técnico de Hardware, Redes & Suporte de TI** · Lorena, São Paulo, Brasil

Manutenção de computadores, notebooks e impressoras, cabeamento e configuração de redes e internet.

**EN-US — Hardware, Networks & IT Support Technician** · Lorena, São Paulo, Brazil

Computer, notebook and printer maintenance, cabling, network and internet configuration.

### 1995 – 1996 | Mecânica Rally

**PT-BR — Técnico em Mecatrônica & Diagnóstico de Injeção Eletrônica** · Lorena, São Paulo, Brasil

Atuação no início da injeção eletrônica no Brasil, diagnóstico de sensores, atuadores e mecatrônica automotiva.

**EN-US — Mechatronics & Electronic Fuel Injection Diagnostics Technician** · Lorena, São Paulo, Brazil

Worked during the early adoption of electronic fuel injection in Brazil, diagnosing sensors, actuators and automotive mechatronics.

## 9. Formação acadêmica / Education

| Instituição / Institution | PT-BR | EN-US | Período / Period |
|---|---|---|---|
| FACIC — Faculdade de Ciências Humanas de Cruzeiro | Bacharelado em Direito, 7º semestre | Law (LL.B.), 7th semester | 2023–2028 |
| UCB — Universidade Católica de Brasília | CST em Segurança da Informação, 3º semestre | Technologist degree in Information Security, 3rd semester | 2025–2028 |
| UNI VITÓRIA TEC | Curso Técnico em Mecatrônica, concluinte | Technical Diploma in Mechatronics, completing in 2026 | 2026–2026 |

## 10. Licenças e certificados / Licenses and certifications

**7 certificados oficiais / 7 official certificates — 294 horas / hours.** Títulos oficiais preservados em português; tradução em inglês para leitura.

### Programa Hackers do Bem — Formação em Cibersegurança: Curso Básico (64h)

EN-US: Hackers do Bem — Cybersecurity Training: Basic Course.

Emissor / Issuer: **SENAI São Paulo / RNP / Softex (MCTI)** · Emissão / Issued: **Março / March de 2026**.

### Programa Hackers do Bem — Formação em Cibersegurança: Nivelamento (80h)

EN-US: Hackers do Bem — Cybersecurity Training: Foundation.

Emissor / Issuer: **SENAI São Paulo / RNP / Softex (MCTI)** · Emissão / Issued: **Março / March de 2026**.

### Inteligência Artificial I — Conhecendo as Redes Neurais Artificiais (40h)

EN-US: Artificial Intelligence I — Introduction to Artificial Neural Networks.

Emissor / Issuer: **Instituto Federal do Triângulo Mineiro (IFTM)** · Emissão / Issued: **Agosto / August de 2026**.

Aproveitamento / Score: **92,50%**.

Credencial / Credential ID: `69a9cc0e-65e7-4f5e-81d8-09e6035856ef`.

### Direito Autoral, Crimes Cibernéticos e Tributos Aplicados a Eventos (20h)

EN-US: Copyright, Cybercrime and Taxes Applied to Events.

Emissor / Issuer: **Instituto Federal do Rio Grande do Sul (IFRS)** · Emissão / Issued: **Abril / April de 2026**.

Aproveitamento / Score: **84,17%**.

Credencial / Credential ID: `8a86dfe9-8e5a-49a8-814b-c7c1bf3743c3`.

### Curso Básico de Direito Espacial — 1ª Turma/2026 (20h)

EN-US: Basic Space Law Course — 1st Class/2026.

Emissor / Issuer: **Agência Espacial Brasileira (AEB / MCTI)** · Emissão / Issued: **Março / March de 2026**.

### Windows Server 2016: Instalação e Administração (40h)

EN-US: Windows Server 2016: Installation and Administration.

Emissor / Issuer: **Instituto Federal do Rio Grande do Sul (IFRS)** · Emissão / Issued: **Maio / May de 2026**.

Aproveitamento / Score: **89,38%**.

Credencial / Credential ID: `0db92a03-21f7-4d6d-8d1c-e7839e596883`.

### Inglês 2 (30h)

EN-US: English 2.

Emissor / Issuer: **Instituto Federal do Rio Grande do Sul (IFRS)** · Emissão / Issued: **Julho / July de 2026**.

Aproveitamento / Score: **86,82%**.

Credencial / Credential ID: `250475bb-2785-4d07-9087-e78063a96e8e`.

## 11. Automação e conferência

O script lê os textos deste kit e os registros estruturados em `scripts/linkedin_profile_data.json`. Usa a sessão persistente `/tmp/linkedin_profile_session`; não lê senhas ou exporta cookies. O modo batch exige sessão autenticada e retorna erro se qualquer ação falhar.

```bash
/tmp/li_venv/bin/python -B scripts/linkedin_auto_config.py --batch --headless --only S,M,J,T,V,U
/tmp/li_venv/bin/python -B scripts/linkedin_auto_config.py --batch --headless --only X,A
/tmp/li_venv/bin/python -B scripts/linkedin_auto_config.py --render-card
```

`S`: localização; `M`/`J`: Sobre PT-BR/EN-US; `T`: experiências; `V`: Mecatrônica; `U`: certificados. Os cadastros consultam o perfil antes de adicionar para evitar duplicatas. `X` remove meses automáticos das experiências, pois o titular forneceu somente anos; `A` restaura e confere a headline após alterações de cargos pelo LinkedIn.

A ação **W publica** o Post 1 com o card de `assets/linkedin_post_card.html`, aguarda o preview e comenta o link do GitHub na URL da nova publicação. O recibo em `/tmp/linkedin_post_receipt.json` permite retomar o comentário sem republicar. A ação C mantém o comportamento de rascunho. `--no-save` preenche os formulários sem enviar.

[Publicação com card e vitrine técnica](https://www.linkedin.com/feed/update/urn:li:activity:7523601679770869761/).

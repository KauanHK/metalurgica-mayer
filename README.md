<div align="center">

<br>

<!-- Banner animado com nome -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=200&section=header&text=Metalúrgica%20Mayer&fontSize=48&fontColor=ffffff&fontAlignY=35&desc=Sistema%20Web%20de%20Gestão%20de%20Estruturas%20Metálicas&descAlignY=58&descSize=18&animation=twinkling" width="100%"/>

<br>

<!-- Badges de tecnologias com ícones reais -->
<p>
  <img src="https://skillicons.dev/icons?i=html,css,js,react,python,flask,postgres&theme=dark&perline=7" />
</p>

<br>

<p>
  <img src="https://img.shields.io/badge/Status-Em%20Desenvolvimento-orange?style=for-the-badge&logo=github"/>
  <img src="https://img.shields.io/badge/Projeto-PAC%20Engenharia%20de%20Software-blue?style=for-the-badge&logo=bookstack&logoColor=white"/>
  <img src="https://img.shields.io/badge/Versão-1.0.0-green?style=for-the-badge"/>
</p>

<br>

</div>

---

## 📌 Sobre o Projeto

A **Metalúrgica Mayer** é uma aplicação web desenvolvida para auxiliar empresas do ramo de estruturas metálicas no gerenciamento de clientes, solicitações, orçamentos e controle de materiais.

O projeto foi desenvolvido durante o **Projeto de Aprendizagem Colaborativa Extensionista (PAC)**, aplicando conceitos de Engenharia de Software desde o levantamento de requisitos até o planejamento da implementação.

Além da área institucional voltada aos clientes, o sistema conta com uma área administrativa **(ERP)**, destinada ao gerenciamento interno da empresa.

---

## 🎯 Objetivos

<div align="center">

| ✅ Objetivo | 📋 Descrição |
|---|---|
| Atendimento ao Cliente | Facilitar e agilizar o contato com clientes |
| Centralização | Unificar solicitações de serviços em um só lugar |
| Orçamentos | Organizar e controlar todos os orçamentos gerados |
| Estoque | Monitorar o controle de materiais em tempo real |
| Gestão Interna | Melhorar o gerenciamento interno da empresa |
| Eficiência | Tornar os processos mais rápidos e organizados |

</div>

---

## 🖥️ Arquitetura do Sistema

```
╔══════════════════════════════════════════════════════════╗
║                        CLIENTE                           ║
║                   Site Institucional                     ║
╚══════════════════╦═══════════════════╦═══════════════════╝
                   ║                   ║
           ┌───────▼──────┐   ┌────────▼──────┐
           │ Solicitar    │   │    Contato    │
           │  Serviço     │   │   /Suporte   │
           └───────┬──────┘   └───────────────┘
                   │
                   ▼
╔══════════════════════════════════════════════════════════╗
║               ÁREA ADMINISTRATIVA (ERP)                  ║
╠══════════╦══════════╦══════════╦══════════╦══════════════╣
║Dashboard ║ Clientes ║ Solicit. ║Orçamentos║  Materiais  ║
╠══════════╩══════════╩══════════╩══════════╩══════════════╣
║          Patrimônios         │         Perfil            ║
╚══════════════════════════════════════════════════════════╝
```

---

## 🚀 Funcionalidades

### 🌐 Área Institucional

- 🏠 Página Inicial
- ⚙️ Serviços oferecidos
- 🏗️ Portfólio de Projetos
- 📞 Contato
- 📝 Solicitação de orçamento online
- 🏢 Informações da empresa

### 🏢 Área Administrativa (ERP)

- 🔐 Login seguro
- 📊 Dashboard interativo
- 👥 Cadastro e gestão de Clientes
- 📋 Gestão de Solicitações
- 💰 Criação de Orçamentos
- 📦 Controle de Materiais
- 🗃️ Controle de Estoque
- 🔧 Lista de Patrimônios
- 👤 Perfil do Usuário

---

## 🛠 Stack Tecnológica

<div align="center">

### Front-end
<img src="https://skillicons.dev/icons?i=html,css,js,react,tailwind&theme=dark" />

| Tecnologia | Uso |
|---|---|
| HTML5 | Estrutura semântica das páginas |
| CSS3 | Estilização e responsividade |
| JavaScript | Interatividade e lógica no cliente |
| React | Interface dinâmica e componentizada |
| Tailwind CSS | Utilitários de estilo rápido |

### Back-end
<img src="https://skillicons.dev/icons?i=python,flask&theme=dark" />

| Tecnologia | Uso |
|---|---|
| Python | Linguagem principal do servidor |
| Flask | Framework web e API REST |

### Banco de Dados
<img src="https://skillicons.dev/icons?i=postgres&theme=dark" />

| Tecnologia | Uso |
|---|---|
| PostgreSQL | Banco de dados relacional robusto |

### Ferramentas
<img src="https://skillicons.dev/icons?i=vscode,git,github&theme=dark" />

| Ferramenta | Uso |
|---|---|
| Visual Studio Code | IDE principal |
| Git | Versionamento de código |
| GitHub | Repositório remoto |
| Draw.io | Diagramas e fluxos |
| Stitch AI | Prototipação com IA |

</div>

---

## 📂 Estrutura do Projeto

```text
PROJECT_PAC_REPOSITORY/
│
├── 📁 backend/
│   ├── 📁 api/
│   ├── 📁 controllers/
│   ├── 📁 models/
│   ├── 📁 routes/
│   ├── 📁 database/
│   └── 🐍 app.py
│
├── 📁 frontend/
│   ├── 📁 public/
│   ├── 📁 src/
│   │   ├── 📁 assets/
│   │   │   ├── 📁 css/
│   │   │   └── 📁 images/
│   │   │
│   │   ├── 📁 components/
│   │   │   ├── 📁 Navbar/
│   │   │   ├── 📁 Footer/
│   │   │   ├── 📁 Sidebar/
│   │   │   └── 📁 Cards/
│   │   │
│   │   ├── 📁 pages/
│   │   │   ├── 📁 institucional/
│   │   │   └── 📁 erp/
│   │   │
│   │   ├── 📁 hooks/
│   │   ├── 📁 services/
│   │   ├── 📁 routes/
│   │   └── ⚛️  App.jsx
│   │
│   └── 📄 package.json
│
├── 📄 README.md
└── 🚫 .gitignore
```

---

## 📋 Documentação Produzida

Durante o projeto foram desenvolvidos os seguintes artefatos de Engenharia de Software:

<div align="center">

| # | Documento |
|---|---|
| 01 | Documento de Iniciação |
| 02 | Stakeholders |
| 03 | Escopo do Projeto |
| 04 | Objetivos |
| 05 | Requisitos Funcionais e Não-Funcionais |
| 06 | Casos de Uso |
| 07 | Modelagem de Dados |
| 08 | Arquitetura do Sistema |
| 09 | Stack Tecnológica |
| 10 | Planejamento e Cronograma |
| 11 | Plano de Testes |
| 12 | Casos de Teste |
| 13 | Matriz de Rastreabilidade |

</div>

---

## 📸 Protótipos

Os wireframes do sistema foram desenvolvidos utilizando inteligência artificial e posteriormente organizados para implementação em React, CSS e JavaScript.

> 🔗 *Imagens dos protótipos serão adicionadas em breve.*

---

## 👨‍💻 Equipe

<div align="center">

<table>
  <tr>
    <td align="center">
      <b>Gustavo Eisermann Voltolini</b>
    </td>
    <td align="center">
      <b>Igor de Andrade</b>
    </td>
    <td align="center">
      <b>Kauan Henrique Kaestner</b>
    </td>
  </tr>
  <tr>
    <td align="center">
      <b>Ruan Yago Klen Richter</b>
    </td>
    <td align="center">
      <b>Vitor Aurélio Cordeiro da Rocha Mayer</b>
    </td>
    <td></td>
  </tr>
</table>

</div>

---

## 📌 Status do Projeto

```diff
+ Planejamento concluído
+ Modelagem concluída
+ Arquitetura definida
+ Wireframes desenvolvidos
+ Estrutura do projeto criada

! Desenvolvimento em andamento
```

---

## 📄 Licença

Projeto acadêmico desenvolvido exclusivamente para fins educacionais no âmbito do **PAC — Projeto de Aprendizagem Colaborativa Extensionista**.

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=100&section=footer&animation=twinkling" width="100%"/>

**Engenharia de Software • Projeto PAC**

⭐ Desenvolvido pela equipe **Metalúrgica Mayer**

</div>


</div>

Sprint 1 — Fundação técnica
Período: 20/08 a 02/09/2026
Objetivo: Sair do papel: ambiente, banco de dados e aplicação mínima rodando na máquina de todos os integrantes.
Principais entregas:
Repositório estruturado em frontend, backend e docs, com fluxo de branches e revisão por pull request.
Projeto Flask criado, PostgreSQL configurado e migrations do modelo de dados aplicadas.
CRUD-piloto ligando tela, API e banco para validar a stack de ponta a ponta.
Layout base em Tailwind: menu lateral, barra superior e componentes reaproveitáveis.
Backlog completo no quadro do projeto e revalidação dos requisitos e protótipos.
Critério de saída: Todos conseguem executar a aplicação e o banco localmente, e o CRUD-piloto grava e lê do PostgreSQL.
Sprint 2 — Autenticação e casca do sistema interno
Período: 03/09 a 16/09/2026
Objetivo: Permitir o acesso ao sistema e a navegação por toda a estrutura do sistema interno.
Principais entregas:
Cadastro de usuários com senha criptografada, login, logout e controle de sessão.
Proteção das rotas administrativas e permissões por perfil de usuário.
Tela de login e shell do sistema interno com navegação para todos os módulos.
Módulo de gestão de perfil: dados pessoais, troca de senha e logout.
Casos de teste de autenticação e de controle de acesso.
Critério de saída: O usuário autenticado acessa o sistema interno, navega pelos módulos e altera a própria senha; acesso sem sessão é bloqueado.
Feriado de 07/09 (segunda-feira) reduz a capacidade da sprint.
Sprint 3 — Clientes e site institucional (parte 1)
Período: 17/09 a 30/09/2026
Objetivo: Entregar o primeiro módulo de negócio completo e colocar a empresa on-line.
Principais entregas:
CRUD de clientes com busca, paginação e validações: nome, telefone, e-mail, endereço e observações.
Estrutura do histórico de solicitações na ficha do cliente.
Páginas públicas “Início” e “Sobre nós”, responsivas, com conteúdo fornecido pela empresa.
Casos de teste do módulo de clientes executados e registrados.
Critério de saída: Cadastro de clientes utilizável em condições reais e duas páginas do site publicadas.
Primeira validação com a Metalúrgica Mayer, até 30/09.
Sprint 4 — Solicitações e site institucional (parte 2)
Período: 01/10 a 14/10/2026
Objetivo: Fechar o ciclo cliente → solicitação, incluindo a entrada de pedidos pelo site.
Principais entregas:
Cadastro, consulta e edição de solicitações vinculadas ao cliente, com atualização de status.
Filtros por cliente, status e período, e histórico exibido na ficha do cliente.
Páginas de serviços e portfólio, solicitação de serviços e contato.
Integração do formulário público: a solicitação enviada pelo site entra no sistema interno e vincula o cliente.
Atualização da matriz de rastreabilidade.
Critério de saída: Uma solicitação enviada pelo site aparece no sistema interno corretamente vinculada, e o site institucional fica completo.
Feriado de 12/10 (segunda-feira) reduz a capacidade da sprint.
Sprint 5 — Orçamentos e almoxarifado
Período: 15/10 a 28/10/2026
Objetivo: Cobrir a parte comercial e o controle de materiais da metalúrgica.
Principais entregas:
Orçamentos vinculados à solicitação, com itens, quantidades, valores e cálculo do total.
Situação do orçamento (pendente, aprovado ou recusado), observações e listagem com filtros.
Cadastro de materiais e registro de entradas e saídas de estoque.
Saldo disponível calculado e consulta das movimentações.
Casos de teste de orçamentos e de movimentação de estoque.
Critério de saída: É possível percorrer solicitação, orçamento e aprovação, e as movimentações refletem no saldo de materiais.
Segunda validação com a Metalúrgica Mayer, até 28/10, já com dados reais.
Sprint 6 — Patrimônio, dashboard e responsividade
Período: 29/10 a 11/11/2026
Objetivo: Concluir o escopo funcional e uniformizar a experiência de uso.
Principais entregas:
Módulo de patrimônio: cadastro, consulta, estado de conservação, localização e situação do bem.
Dashboard com indicadores de clientes, solicitações, orçamentos, materiais e patrimônio, além de atalhos.
Revisão de responsividade em todas as telas do site e do sistema interno.
Padronização visual, estados de carregamento e mensagens de erro.
Ajustes acumulados a partir das duas validações com a empresa.
Critério de saída: Todos os módulos previstos implementados, com o dashboard exibindo números reais do banco.
Feriado de 02/11 (segunda-feira) reduz a capacidade da sprint.
Sprint 7 — Testes, publicação e entrega final
Período: 12/11 a 26/11/2026 (15 dias)
Objetivo: Estabilizar o sistema em produção e concluir o material acadêmico.
Principais entregas:
Execução completa do plano de testes e fechamento da matriz de rastreabilidade.
Correção dos defeitos encontrados, por ordem de severidade.
Publicação da aplicação e do banco em ambiente acessível à empresa, com carga de dados iniciais.
Homologação final com a Metalúrgica Mayer até 18/11 e ajustes decorrentes.
Manual de uso, documentação técnica final e relatório do PAC VI.
Apresentação atualizada com capturas reais do sistema e ensaiada.
Critério de saída: Sistema em produção, homologado pela empresa, com relatório final e apresentação prontos.

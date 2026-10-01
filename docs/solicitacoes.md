# Solicitações de serviço

Parte da Sprint 4 (Solicitações e site institucional): fecha o ciclo cliente →
solicitação, tanto pelo ERP quanto pela entrada pública do formulário do site.
Critério de saída: uma solicitação enviada pelo site aparece no sistema interno
corretamente vinculada ao cliente.

Código em `backend/app/modules/service_requests/` (arquitetura hexagonal, como os
demais módulos). As telas do ERP e a página do formulário do site ainda não
existem no repositório; a seção "O que o front precisa consumir" lista o contrato.

## Modelo

Uma solicitação pertence sempre a **um cliente** (`client_id`, FK com `RESTRICT`:
cliente com histórico não pode ser excluído, apenas desativado) e nunca muda de
dono. Campos: `title` (3–150), `description` (opcional), `status`, `origin`,
`requested_at` (data do pedido), `due_date` (prazo, opcional), `created_at`,
`updated_at`. A resposta traz também `client_name`.

## Status e regras

| Status        | Significado                                       |
|---------------|---------------------------------------------------|
| `open`        | Aberta: registrada, ainda não avaliada            |
| `in_analysis` | Em análise: orçando/avaliando viabilidade         |
| `in_progress` | Em execução: serviço sendo produzido              |
| `completed`   | Concluída (terminal)                              |
| `cancelled`   | Cancelada (terminal)                              |

- Toda solicitação nasce `open`.
- Entre `open`, `in_analysis` e `in_progress` a troca é livre (a equipe avança e
  volta quando o escopo muda).
- `completed` e `cancelled` são terminais: tentar mudar o status devolve **409**.
  Para um novo pedido, cadastra-se uma nova solicitação.
- Não há `DELETE`: o que não vai adiante é cancelado e continua no histórico.
- `due_date` não pode ser anterior a `requested_at` (422).

## Fluxo interno (autenticado)

Todas as rotas exigem `Authorization: Bearer <access_token>`.

| Método | Rota                                  | Descrição                                   |
|--------|---------------------------------------|---------------------------------------------|
| GET    | `/api/service-requests`               | Lista paginada, da mais recente             |
| POST   | `/api/service-requests`               | Cadastra (cliente ativo obrigatório)        |
| GET    | `/api/service-requests/{id}`          | Consulta                                    |
| PATCH  | `/api/service-requests/{id}`          | Edita campos enviados; é aqui que o status muda |
| GET    | `/api/clients/{id}/service-requests`  | Histórico na ficha do cliente (404 se o cliente não existe) |

Filtros (query) da listagem e do histórico: `status`, `origin`
(`internal` | `website`), `date_from`, `date_to` (sobre `requested_at`,
inclusivos; período invertido dá 422) e `search` (trecho do título). A listagem
geral ainda aceita `client_id`. Paginação padrão do projeto (`page`,
`page_size`; resposta `{data, total, page, page_size, total_pages}`).

No cadastro interno, o cliente precisa existir e estar **ativo** (422 caso
contrário): abrir pedido novo para quem saiu da operação costuma ser engano. A
solicitação interna nasce com `origin = internal`.

## Entrada pública (formulário do site)

`POST /api/public/service-requests` — **sem autenticação** (tag "Site público").

Requisição:

```json
{
  "name": "Maria Souza",
  "email": "maria@exemplo.com.br",
  "phone": "47999990000",
  "document": "529.982.247-25",
  "title": "Portão de garagem",
  "description": "Preciso de um portão deslizante de 4 metros.",
  "website": ""
}
```

- `name` (2–150), `title` (3–150) e `description` (5–5000) são obrigatórios;
  textos são aparados (`strip`).
- `email` e `phone` (até 20) são opcionais individualmente, mas **pelo menos um
  dos dois é obrigatório** (senão 422): sem contato a equipe não consegue responder.
- `document` (CPF/CNPJ) é opcional; aceita máscara, é validado pelos dígitos
  verificadores e gravado só com dígitos. Mesma normalização do cadastro de
  clientes. String vazia vira ausente (vale também para `email` e `phone`).
- `website` é o **honeypot** (veja abaixo): deve ficar vazio.

Resposta `201`:

```json
{ "id": "0192...-uuid", "status": "open" }
```

Erros de validação seguem o formato padrão da API
(`{code: "validation_error", message, details: [{field, message, type}]}`, 422).
Não há outros erros de negócio previstos para este endpoint.

### O que acontece no servidor

Numa única transação (`PublicServiceRequestSubmitter`):

1. Procura o cliente pelo **documento** (se informado) e, na falta de um cliente
   com ele, pelo **e-mail**, sem diferenciar maiúsculas de minúsculas. Se há
   vários clientes com o mesmo e-mail, vale o ativo mais antigo (e, sem ativo, o
   inativo mais antigo).
2. Se o documento informado não existe, mas o e-mail pertence a um cliente que
   **tem outro documento**, é outra pessoa/empresa usando o mesmo contato: cadastra
   um cliente novo em vez de misturar. (E-mail de cliente sem documento é
   aproveitado.)
3. Se não encontrou, **cadastra um cliente novo**: ativo, com os dados do
   formulário e `notes = "Cadastrado pelo site"`.
4. Grava a solicitação vinculada a esse cliente: `status = open`,
   `origin = website`, `requested_at` = hoje (fuso de Brasília), sem prazo.

Se dois envios simultâneos trazem o mesmo documento novo, o segundo esbarra na
unicidade do documento; o use case refaz a transação uma vez e reaproveita o
cliente criado pelo primeiro.

### Decisões de segurança e privacidade

- **Cliente inativo recebe a solicitação, mas não é reativado.** O histórico não
  pode se perder nem se fragmentar em fichas duplicadas; a triagem é da equipe
  (filtro `origin=website`). A regra "cliente ativo" do cadastro interno não se
  aplica à entrada pública.
- **Dados do formulário nunca sobrescrevem um cliente existente.** Quem envia não
  está autenticado; se bastasse saber um e-mail para trocar nome ou telefone,
  qualquer um poderia adulterar o cadastro. Consequência: se o solicitante informa
  um telefone diferente do cadastrado, o novo telefone **não** é guardado — a
  equipe vê o cadastro antigo. Se isso virar problema, a evolução natural é
  registrar o contato informado dentro da própria solicitação.
- **A resposta não vaza dados do cliente** (só `id` da solicitação e `status`) e é
  idêntica para cliente novo e existente: o endpoint não pode servir para
  descobrir se um e-mail ou documento está cadastrado.
- **Honeypot (`website`)**: campo escondido no formulário (CSS, `tabindex=-1`,
  `autocomplete=off`). Se vier preenchido, a API responde `201` com um id
  aleatório e `status: "open"`, **sem gravar nada**, para o robô não aprender que
  foi detectado.
- **Limites**: `description` em 5000 caracteres, demais campos com os limites do
  cadastro de clientes.
- **Ainda não há limitação de taxa (rate limit)** no backend. Recomendado aplicar
  no nginx (`limit_req` na rota `/api/public/service-requests`) antes de
  publicar; captcha só se o honeypot se mostrar insuficiente.
- O CORS segue o `CORS_ORIGINS` já existente; em produção o site e a API ficam na
  mesma origem pelo nginx.

## Triagem pela equipe

Solicitações vindas do site chegam sem ninguém do lado de dentro conferindo. Para
triar: `GET /api/service-requests?origin=website&status=open`. O cliente criado
pelo site é identificável por `notes = "Cadastrado pelo site"`.

## O que o front precisa consumir

**Site (público)** — formulário de solicitação de serviços (Figura 4):

- Enviar `POST /api/public/service-requests` com os campos acima, incluindo o
  honeypot `website` (input escondido, vazio).
- Validar no cliente: contato (e-mail ou telefone), tamanhos e CPF/CNPJ; o
  servidor revalida e devolve 422 com `details[].field` para marcar o campo.
  Erros de contato aparecem com `field` vazio (erro do corpo inteiro).
- Em `201`, mostrar confirmação genérica (não há dados de cliente na resposta).

**ERP (autenticado)**:

- Listagem de solicitações: `GET /api/service-requests` com filtros `client_id`,
  `status`, `origin`, `date_from`/`date_to`, `search`; exibir `origin` (badge
  "Site" para triagem).
- Ficha do cliente: `GET /api/clients/{id}/service-requests` (mesmos filtros,
  menos `client_id`).
- Detalhe e edição: `GET`/`PATCH /api/service-requests/{id}`; tratar 409 ao tentar
  mudar o status de uma solicitação concluída/cancelada.
- Cadastro: `POST /api/service-requests` com `client_id`, `title` e opcionais
  `description`, `requested_at`, `due_date`; 422 se o cliente está inativo.

## Rastreabilidade

O repositório ainda não tem a matriz de rastreabilidade (o README e o cronograma
só a citam como entregável); não foi criada aqui. Quando existir, os requisitos
atendidos por este módulo são: gestão de solicitações (cadastro, consulta,
edição, status), filtros por cliente/status/período, histórico na ficha do cliente
e integração do formulário público.

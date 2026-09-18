# Autenticação e proteção de rotas

Parte da Sprint 2 (Autenticação e casca do ERP): login, proteção de rotas e
gestão do próprio perfil, no backend. O front-end (tela de login, shell do ERP,
tela de perfil) ainda não existe no repositório e fica para uma próxima parte.

## Fluxo

1. `POST /api/auth/login` recebe `email` e `password`, confere a senha
   (bcrypt) contra o hash gravado em `users.password_hash` e devolve um par de
   tokens JWT — `access_token` (curto, `ACCESS_TOKEN_EXPIRES_MIN` minutos) e
   `refresh_token` (longo, `REFRESH_TOKEN_EXPIRES_DAYS` dias) — mais os dados
   do usuário autenticado.
2. Toda rota protegida exige o cabeçalho `Authorization: Bearer <access_token>`.
   `get_current_subject` (`app/core/security`) decodifica o token e extrai o
   `sub` (id do usuário); `get_current_actor` (`app/modules/users`) carrega
   esse usuário e confere que ele existe e está ativo antes de liberar a rota
   — é por isso que o core nunca faz essa checagem sozinho: ele não conhece o
   módulo `users`.
3. `POST /api/auth/refresh` troca um `refresh_token` válido por um novo
   `access_token`, sem exigir login de novo. Não emite um refresh token novo
   junto: sem uma lista de revogação, "rotacionar" não invalidaria o antigo, e
   só complicaria o front à toa.
4. Logout é responsabilidade do front-end: descartar os tokens guardados.
   **Não há endpoint de logout nem revogação de refresh token nesta etapa** —
   os tokens são stateless e expiram sozinhos. Se isso virar um problema (por
   exemplo, um usuário desativado precisa perder acesso imediatamente, e não
   só quando o token expirar), a solução é uma lista de revogação — fora do
   escopo desta parte.

## Rotas protegidas

- `/api/clients/*` exige um token de acesso válido (`get_current_actor`
  aplicado no `APIRouter` do módulo).
- `/api/users/me*` exige o mesmo, e sempre atua sobre o dono do token — não
  existe ainda edição de outro usuário por um administrador.

## Gestão de perfil

- `GET /api/users/me` devolve os dados do usuário autenticado.
- `PATCH /api/users/me` altera nome e/ou telefone; campo ausente no corpo não
  é tocado. E-mail, perfil (`role`) e status (`is_active`) não são editáveis
  por aqui.
- `POST /api/users/me/password` troca a senha, exigindo a senha atual.

## Fora do escopo desta parte

- Cadastro de novos usuários por um administrador (`POST /users`). A tabela e
  o seed do admin inicial (`scripts/seed/initial_user.py`) já existem, mas
  ainda não há endpoint de criação.
- Autorização por perfil (`admin` vs. `operator`): `UserActor.is_admin` já
  existe, mas nenhuma rota o usa ainda — todo usuário autenticado tem o mesmo
  acesso.
- Qualquer tela do front-end (login, shell do ERP, perfil) — o Next.js
  referenciado no `docker-compose.yml` ainda não existe no repositório.

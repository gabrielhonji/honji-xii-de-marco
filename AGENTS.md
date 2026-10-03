# Orientações do projeto

Leia `DESIGN.md` antes de alterar o visual. A marca principal é HONJI; os nomes seguem `HONJI — nome do projeto`. Preserve composição editorial, grade discreta, paleta institucional, temas claro/escuro e acessibilidade em dispositivos móveis. Autoria: `gabriel.honji`.

Mantenha o crédito do autor confirmado no footer. Documentação pública deve tratar do produto, suas funcionalidades, instalação e autoria.

Nunca versionar respostas de formulários, certificados de participantes, arquivos temporários, credenciais ou lotes exportados. Use dados fictícios em exemplos públicos. A pasta `documentos-certificados/` é material local de referência e deve continuar fora do repositório.

Nomes, RAs e documentos reais nunca podem aparecer em testes, fixtures, exemplos, capturas ou histórico público. Todos os testes devem usar dados inventados. Antes de publicar, executar `python tools/check_public_data.py --staged`; revisar também imagens e arquivos binários. Manter templates que contenham nomes ou assinaturas somente em `documentos-certificados/`. Não ler respostas reais para alimentar testes automatizados.

Não altere a carga horária ou confirme períodos de participação sem uma regra explícita ou revisão da secretaria. Preserve a validação e geração em memória.

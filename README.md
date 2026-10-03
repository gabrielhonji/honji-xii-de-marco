# HONJI — XII de Março

Secretaria digital da Atlética XII de Março, da UTFPR Campus Apucarana. Uma aplicação para transformar respostas de formulário em certificados por pessoa, atividade e semestre.

Desenvolvido por **[gabriel.honji](https://github.com/gabrielhonji)** · [Instagram](https://www.instagram.com/gabriel.honji/)

![HONJI — XII de Março](assets/social-card.png)

## Funcionalidades

- Importação de CSV e XLSX no formato original do formulário.
- Expansão de intervalos explícitos em semestres, incluindo início e fim.
- Revisão de nome, RA, atividade, função, período e carga horária.
- Identificação de respostas ambíguas e remoção de duplicatas idênticas.
- Aprovação individual ou em lote dos registros sem pendência.
- Prévia de certificados com o fundo institucional original.
- Exportação de PDFs em ZIP, por nome ou RA, com relatório de conferência.
- Temas claro e escuro com preferência lembrada no navegador.
- Interface para desktop, iPhone e iPad; registros em cartões no celular.
- Marca vetorial, favicon, ícones de tela inicial e manifesto.

## Instalação

Requer **Python 3.10 ou superior**. No Windows:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python server.py
```

No macOS ou Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python server.py
```

Acesse **http://127.0.0.1:8000**. Para outra porta, use `python server.py --port 8080` com o Python do ambiente virtual.

## Uso

1. Exporte as respostas do Google Forms em CSV ou XLSX e importe o arquivo.
2. Confira as participações reconhecidas e revise as pendências. Use um semestre único ou os campos **De** e **Até** para expandir um período.
3. Confirme a carga horária e aprove os registros que deseja emitir.
4. Confira a prévia e escolha a data e o padrão dos nomes.
5. Baixe o ZIP. Se o download automático não começar, use **Baixar ZIP gerado**.

### Organização do lote

```text
XII-certificados-2026-10-03.zip
├── participante-exemplo/
│   ├── participante-exemplo - xii - 2026.1.pdf
│   └── participante-exemplo - pantercats - 2026.2.pdf
└── relatorio.csv
```

O relatório inclui nome, RA, atividade, descrição, semestre, horas, arquivo e texto de origem. Participações distintas que produziriam o mesmo nome recebem sufixos, preservando todos os arquivos.

## Regras de emissão

| Entrada | Comportamento |
| --- | --- |
| `2020/1 até 2023/2` | Um registro por semestre, incluindo os limites |
| `2023.1` ou `2023/01` | Semestre único |
| `2023/1 e 2024/2` | Apenas os semestres informados |
| Ano sem semestre | Revisão obrigatória |
| Participação “desde” uma data | Revisão dos limites |
| Duas datas sem conexão | Revisão do intervalo |
| Eventos e ações sociais | Confirmação de atividade, semestre e horas |

Cargas sugeridas pelos modelos: **100 horas por semestre** para atividades contínuas e **48 horas para EP**. JIA, outros eventos e ações sociais começam com zero e exigem confirmação. A secretaria confere os dados e a validade da emissão.

O RA vem da planilha. A distribuição usa um modelo neutro, sem nomes fixos ou assinaturas. Um fundo institucional autorizado pode ser colocado localmente em `documentos-certificados/certificate-background.jpg`; esse arquivo não é servido pela aplicação nem publicado no repositório.

## Identidade HONJI

O **Giro original** é a assinatura compartilhada: quatro pétalas redondas em rotação, com centro aberto. Os projetos seguem **HONJI — nome do projeto**. Neste produto, a base editorial combina papel, bordô e carvão, grade discreta e tipografia serifada de destaque.

O mesmo símbolo aparece no header, no hero, no favicon, nos ícones de tela inicial e na imagem de compartilhamento. Ele é aplicado diretamente, sem depender de uma escolha armazenada no navegador. A página **/identidade** apresenta a marca aprovada e permite baixar o SVG.

[DESIGN.md](DESIGN.md) registra as regras de uso, cores, autoria e adaptações para dispositivos móveis.

## Estrutura

```text
assets/                     Marca, ícones e fundo institucional
web/                        Interface, estilos, temas e manifesto
tools/build_brand_assets.py  Exportação dos ícones e imagem de compartilhamento
tests/                      Testes das regras e geração
server.py                   API local e processamento em memória
requirements.txt            Dependências da aplicação
requirements-dev.txt        Dependências de desenvolvimento
DESIGN.md                   Identidade visual reutilizável
```

## Privacidade e execução

O servidor escuta somente em `127.0.0.1`. Arquivos e certificados são processados em memória, sem salvar dados pessoais no servidor ou nos logs. Recarregar a página encerra o lote. Guarde o ZIP antes de fechar.

Uploads têm limite de 10 MB; planilhas descompactadas, 40 MB. O serviço valida origem, host, campos e horas. Serve apenas arquivos públicos previstos e neutraliza fórmulas no relatório CSV.

Respostas reais, certificados de participantes, lotes, temporários e credenciais ficam fora do controle de versão. O repositório distribui código, identidade da ferramenta e fundo institucional. Para hospedagem pública, implemente autenticação, HTTPS, limites de uso e retenção de dados. Esta versão é destinada ao uso local.

Antes de hospedar, configure o domínio absoluto de `og:image` no HTML para permitir o carregamento externo da imagem de compartilhamento.

## Desenvolvimento e testes

```powershell
.venv\Scripts\python -m pip install -r requirements-dev.txt
.venv\Scripts\python -m unittest discover -s tests -v
```

São 23 testes de períodos, ambiguidades, duplicatas, aprovação, validações HTTP, privacidade dos arquivos, conteúdo dos PDFs e nomes sem sobrescrita. Incluem um lote de 75 certificados e a equivalência CSV/XLSX com dados fictícios. Todos os testes usam dados fictícios.

Para experimentar, importe [a planilha fictícia](outputs/honji-qa-20261003/participacoes-ficticias.xlsx) ou [o CSV correspondente](tests/fixtures/participacoes-ficticias.csv). São 14 respostas: 31 participações propostas, 12 pendências, 19 registros sem pendência e 5 duplicatas removidas. Todos os dados dessa amostra são fictícios. A aba **Guia** explica os casos e resultados esperados.

[QA.md](QA.md) registra o escopo da verificação e as limitações dos testes em dispositivos.

Para exportar os ícones novamente:

```powershell
.venv\Scripts\python tools/build_brand_assets.py
```

## Autor

**gabriel.honji** · [GitHub](https://github.com/gabrielhonji) · [Instagram](https://www.instagram.com/gabriel.honji/)

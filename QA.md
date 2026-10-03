# Verificação · 3 de outubro de 2026

## Resultados

30 testes automatizados passaram. Foram verificados CSV UTF-8 e Windows-1252, separadores alternativos, equivalência com XLSX, intervalos e semestres isolados, duplicatas e nomes conflitantes para um mesmo RA, zeros à esquerda, entradas inválidas, aprovação explícita, caracteres especiais e neutralização de fórmulas no relatório.

O lote de 75 PDFs passou na verificação da integridade do ZIP e da correspondência entre os arquivos e o relatório. Os PDFs das dez atividades foram conferidos por texto, semestre, horas, data, identidade e tamanho de página. Duas amostras foram renderizadas e inspecionadas visualmente.

As rotas HTTP foram verificadas quanto a importação, prévia, exportação, erros de validação, arquivos privados, origem e host. A execução permanece local.

## Interface

Verificados no navegador: importação CSV e XLSX, busca sem exigir acentos, estado vazio, aprovação dos 19 registros sem pendência, expansão manual de um período, erro de intervalo dentro do diálogo, inclusão manual, exclusão com desfazer, prévia e limpeza do PDF ao fechar, geração de 21 certificados e invalidação do link de download após mudar o padrão de nomes. Não foram observados erros de console nessa sequência.

O seletor de arquivo funciona por clique e teclado. Header e hero usam o Giro original; favicon e ícones de tela inicial reproduzem sua geometria. A XII usa uma pantera vetorial monocromática. Lua e sol são preenchidos. O footer é sólido e mantém o crédito de gabriel.honji.

## Responsividade e limites

Foram aplicadas larguras de viewport de 320, 390, 393, 768, 820 e 1440 px. O zoom existente do navegador altera a largura CSS efetiva; em todas as medições, a largura de rolagem do documento ficou igual à largura útil. A tabela passa a cartões em telas pequenas. O viewport normal foi restaurado.

Fundo, grade, safe areas, scrollbar e regras de overscroll foram ajustados. Esta verificação usa o navegador local; não equivale a uma execução em Safari de iPhone ou iPad físicos. O comportamento de elasticidade da rolagem nesses dispositivos ainda precisa dessa conferência.

## Reproduzir

```powershell
python -m unittest discover -s tests -v
```

Importe `outputs/honji-qa-20261003/participacoes-ficticias.xlsx` para repetir a revisão manual. A amostra contém somente dados fictícios; resultados esperados estão na aba Guia.

A padronização de modalidades foi testada na importação, edição e geração. PDF e relatório usam Futebol 7 para aliases reconhecidos. Modalidades combinadas e horas conflitantes ficam pendentes; semestres e horas explícitos em eventos são preservados para conferência. A geração bloqueia participações repetidas. Também foram conferidos botões agrupados, scrollbar da tabela e botão de tema com largura fixa de 100 px.

A cópia isolada dos arquivos públicos passou nos 30 testes sem acesso a documentos privados, usando o modelo neutro. O verificador de publicação e o hook de commit passaram sem bloqueios. Os hooks locais de commit e push estão configurados; o push verifica também os commits anteriores alcançáveis.

## Migração da interface

React 19, TypeScript, Tailwind CSS 4 e Vite 8 passaram na verificação de tipos e no build de produção. Os estilos editoriais e a marca foram preservados; tabela, editor, diálogos, botões e tema são componentes. A distribuição inclui o build, servido pelo Python sem depender de Node durante a execução.

Na interface React foram conferidos: importação da amostra fictícia (31 participações, 12 pendências), aprovação de 19 registros, busca por João sem acento, erro de intervalo invertido, expansão em dois semestres, exclusão com desfazer, prévia e padronização. A geração apresentou o link do ZIP de 20 aprovados. O navegador integrado não expôs um evento de download para esse link blob; a validação do conteúdo do ZIP é coberta pelos testes HTTP. Não declarar o salvamento automático como verificado neste ambiente.

A tabela usa a rolagem vertical da página e mantém apenas rolagem horizontal interna quando necessária. Ações discretas ganham superfície no hover/foco; campos e seletores compartilham os estados visuais. O botão de tema mantém as dimensões e usa vetores preenchidos, alinhados.

Após a migração, também foram verificados 390, 393, 768 e 820 pixels CSS efetivos: a largura de rolagem do documento ficou igual à largura útil em todos os casos. O viewport normal foi restaurado. Uma participação manual fictícia com `atleta de Fut7` foi salva como `Futebol 7`. O proxy de desenvolvimento do Vite retornou 200 na API sem alterar as restrições de origem do backend.

Tooltips compartilhados descrevem importação, tema, ajuda, ações de revisão e emissão. Aparecem no hover ou foco de teclado, respeitam os limites da tela e não alteram o layout. Cancelar mostra Esc; salvar aceita Ctrl/⌘ + Enter. A lua mantém uma inclinação suave, centralizada no mesmo espaço de 20 px. Campos da finalização destacam apenas a borda no hover. O download alternativo aparece como link discreto “ZIP pronto · Baixar novamente”.

Os três seletores usam opções próprias com o tema HONJI. Foram conferidos escolha por clique, setas/Home/Enter, Esc fechando somente o menu dentro do editor, filtro de 12 pendências e padrão de arquivos por RA. A largura de rolagem do menu coincide com sua largura útil. O tooltip Cancelar/Esc e o salvamento por Ctrl+Enter foram verificados no navegador. A lua usa rotação de −35°.

Campos de texto e seletores compartilham altura de 44 px, padding e fonte de 13 px no desktop e 16 px no celular. RA e atividade foram medidos com a mesma altura em ambas as larguras; nomes, descrição, semestre e horas também têm a mesma geometria. O viewport normal foi restaurado.

## Medição de geração

Em uma execução neste computador, com identidades exclusivamente fictícias, template neutro e geração sequencial em memória: 100 PDFs com ZIP em 0,214 s (0,161 MB); 1.000 em 2,134 s (1,610 MB). A contagem dos PDFs no ZIP foi conferida. A medição não inclui rede, template com imagem, concorrência ou persistência; não é um teste de 100.000 certificados nem uma comparação com C. O limite continua em 1.000 por emissão.

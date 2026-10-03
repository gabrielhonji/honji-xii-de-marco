# Verificação · 3 de outubro de 2026

## Resultados

23 testes automatizados passaram. Foram verificados CSV UTF-8 e Windows-1252, separadores alternativos, equivalência com XLSX, intervalos e semestres isolados, duplicatas e nomes conflitantes para um mesmo RA, zeros à esquerda, entradas inválidas, aprovação explícita, caracteres especiais e neutralização de fórmulas no relatório.

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

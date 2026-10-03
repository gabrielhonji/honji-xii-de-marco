# Identidade visual · HONJI

A marca aprovada é **HONJI**, com o símbolo **Giro original**. Os projetos seguem **HONJI — nome do projeto**; este produto é **HONJI — XII de Março**. Autoria permanente: **gabriel.honji**, com GitHub `https://github.com/gabrielhonji` e Instagram `https://www.instagram.com/gabriel.honji/`.

## Símbolo aprovado

Quatro pétalas redondas em rotação, com centro aberto. O arquivo canônico é `assets/honji-symbol.svg`. Preserve exatamente seus contornos, proporções e composição. Não adicionar letras, recortes, olhos, ornamentos ou conexões ao símbolo. Não substituí-lo por um monograma H ou por uma variação experimental.

Aplique o mesmo Giro no header, no hero, no favicon, nos ícones de tela inicial e na imagem de compartilhamento. O símbolo é vetorial, monocromático e transparente; herda a cor de seu contexto. Os ícones para tela inicial e favicon usam uma superfície bordô com o Giro em creme para garantir contraste. Os ícones rasterizados reproduzem as mesmas curvas do SVG.

A marca permanece como padrão do produto, independentemente de armazenamento local. `/identidade` é um guia da marca aprovada, com download do símbolo, sem seletor de alternativas.

O favicon usa uma base circular bordô com cantos externos transparentes, nas versões SVG e ICO. O Giro continua com a geometria original. Ícones de tela inicial mantêm a superfície completa para receber a máscara do sistema operacional.

## Base editorial compartilhada

Papel/creme, grade leve, títulos grandes, destaques em serifa, tipografia de apoio sem serifa, espaço generoso e numeração discreta. HONJI aparece sem subtítulo genérico no lettering. Cada projeto pode adaptar paleta e conteúdo, preservando Giro, padrão de nomes e crédito do autor.

## Paleta da XII

| Token | Claro | Escuro |
| --- | --- | --- |
| Fundo | `#F8F4ED` | `#171315` |
| Superfície | `#FFFBF6` | `#211B1E` |
| Destaque | `#EEE4D8` | `#30242A` |
| Texto | `#421C27` | `#F6EEE5` |
| Texto secundário | `#79636A` | `#C8B5BA` |
| Bordô | `#761B35` | `#E39AAD` |
| Dourado | `#A07725` | `#DAB465` |

A identidade da XII deriva das referências em bordô, preto e dourado. O documento emitido preserva o fundo institucional original. A marca do produto não modifica o certificado.

## Interação e layout

- Header com marca e identificação do projeto agrupadas à esquerda; tema e estado local à direita. Não colocar um link isolado de ajuda no centro.
- Ajuda próxima das instruções de importação. Ações com ícones vetoriais de 20 px e traços consistentes; evitar setas diagonais decorativas. Lua e sol são vetores preenchidos.
- Autoria sempre visível no footer, com link confirmado do autor.
- Footer sólido, como o header, sem link solto para a identidade. A pantera monocromática de `assets/xii-icon.svg` identifica a XII no header e no footer; o Giro identifica HONJI.
- Tema inicial acompanha o dispositivo; a escolha manual fica no navegador.
- Tooltips discretos no hover e foco de teclado descrevem a ação; só exibem atalhos implementados. A lua preenchida tem inclinação suave, mantendo a centralização e o tamanho do botão.
- Controles de toque com pelo menos 44 px. Campos com fonte de 16 px em celular.
- Registros em cartões em celular. Preservar rolagem vertical do conteúdo, sem overflow horizontal.
- Validar 390/393 px para iPhones, 768/820 px para iPads e desktop quando as alterações afetarem o layout. Restaurar o viewport normal depois dos testes.
- Fundo e grade pertencem ao elemento raiz e preenchem as bordas. Scrollbar acompanha o tema. Respeitar safe areas, zoom e movimento reduzido.

## Manutenção

As explorações ficam locais até a identidade estar definida. Publicar alterações consolidadas e necessárias, sem subir cada proposta intermediária. Repetir testes de tema e responsividade apenas quando mudanças ou falhas justificarem.

`tools/build_brand_assets.py` exporta favicon, ícones de tela inicial e cartão de compartilhamento a partir da geometria aprovada. As explorações antigas ficam em `tmp/brand-explorations/`, fora do repositório.

---
name: apresentacao-pdf-bonita
description: Monta uma apresentação comercial bonita em PDF (e PPTX), no padrão preto e branco de consultoria (capa com foto, número gigante recortado na foto, faixa de logos de clientes, listas com ícone, cronograma mês a mês, caixas de preço e o "Obrigado." no fim), com a marca e as informações de quem usa. Entrevista a pessoa, uma pergunta por vez, para preencher as lacunas (marca, números, clientes, dores, oferta, preço, cronograma, fotos) e gera o PDF pelo Chrome. Serve para proposta, plano de ação, apresentação da empresa, oferta de IA para serviços, workshop ou mentoria. Use quando alguém disser "apresentação bonita", "PDF bonito", "proposta em PDF", "deck da proposta", "PPT bonito", "material para o cliente", "plano de ação" ou "apresentação da minha empresa".
---

# Apresentação em PDF bonita

Esta skill gera uma apresentação 1920x1080 em preto e branco, com tipografia forte (Schibsted
Grotesk), fotos em preto e branco e muito espaço vazio. O desenho já está pronto. O seu trabalho é
**entrevistar a pessoa** para preencher o conteúdo e depois rodar o montador.

Você não escreve CSS nem inventa página nova. Você escolhe as páginas do catálogo abaixo, preenche
um `conteudo.json` e roda `scripts/montar.py`.

## Como conduzir

1. **Uma pergunta por vez**, curta. Sempre que der, ofereça opções de múltipla escolha, com a
   recomendada primeiro. Espere a resposta antes da próxima.
2. Pergunte só o que muda o material. O que tiver um padrão bom, decida e conte o que decidiu.
3. **Nunca invente número, cliente, depoimento ou preço.** Sem a informação, deixe a lacuna
   visível (`Empresa 1`, `+00`) e diga à pessoa o que falta.
4. Se a pessoa já mandou um texto, uma proposta antiga ou um site, leia antes e só pergunte o que
   faltou.

## A entrevista, na ordem

1. **Que material é?**
   1. Proposta para um cliente (recomendado)
   2. Plano de ação com IA para um cliente
   3. Apresentação da minha empresa, sem cliente
   4. Oferta de workshop ou mentoria
2. **Quem apresenta:** nome da empresa ou marca, uma frase do que faz, o site, e o arquivo da logo
   (PNG com fundo transparente é o melhor). Sem logo, o montador faz uma logo provisória: um
   monograma com as iniciais num quadrado e o nome ao lado (`"Sua Marca"` vira `SM`; para outras
   letras, preencha `iniciais` na `marca`). Diga à pessoa que é provisória.
3. **Quem fala:** nome, cargo e uma foto de rosto (opcional). Aparece na faixa de baixo das
   páginas de preço.
4. **Para quem é:** nome do cliente e a data. Pule se for a apresentação da empresa.
5. **Os números da empresa:** três números com rótulo (ex.: `+50 projetos`, `+2 mil pessoas
   treinadas`, `3 estados`) e **um número de destaque**, o maior orgulho, que vira a página do número
   gigante.
6. **Os clientes:** arquivos das logos (até 12) ou só os nomes. Sem permissão para mostrar,
   use as logos genéricas `Empresa 1` a `Empresa 12` (é o padrão: `"logos": 12`).
7. **O que pesa hoje no cliente:** de 4 a 6 dores, cada uma com um título curto e uma frase.
8. **A virada:** a frase grande que apresenta a solução (ex.: "Conselheiro de confiança em
   tecnologia.") e os temas que você conduz (até 12).
9. **Como funciona:** o método (os critérios da prioridade), os passos mês a mês ou o dia do
   workshop.
10. **A oferta:** o serviço, o preço, a duração, o início e uma bonificação, se houver. Ao cliente
    vão o preço total e os benefícios, nunca o custo interno.
11. **As fotos:** pergunte se a pessoa tem fotos dela, da equipe ou do cliente. Sem fotos, use as
    três que vêm com a skill (`assets/fotos/`). Também dá para baixar fotos gratuitas do Unsplash
    pelo tema, mas só com o ok da pessoa. Toda foto vira preto e branco sozinha.
12. **O versículo:** a última página traz um texto bíblico. Pergunte qual versículo a pessoa quer,
    com uma sugestão que combine com o material, a recomendada primeiro. Por exemplo:
    1. Colossenses 3:23: "Tudo quanto fizerdes, fazei-o de todo o coração, como ao Senhor, e não aos
       homens." (recomendado para proposta e serviço)
    2. Provérbios 27:23: "Procura conhecer o estado das tuas ovelhas; põe o teu coração sobre os teus
       rebanhos." (para quem cuida de patrimônio, finanças ou gestão)
    3. Provérbios 16:3: "Confia ao Senhor as tuas obras, e teus pensamentos serão estabelecidos."
    4. Outro que a pessoa escolher, ou nenhum.

    Confira o texto numa Bíblia antes de pôr (a Almeida Corrigida Fiel está em bibliaonline.com.br)
    e ponha o livro, o capítulo, o versículo e a tradução em `autor`.
13. **O fecho:** o próximo passo (ex.: "Assinatura digital hoje; primeiro encontro na semana de 1º de
    dezembro.").

## O catálogo de páginas

Cada página é um item de `paginas` no `conteudo.json`, com um `tipo`. O exemplo completo, com
todos os tipos, está em `exemplos/plano-de-acao-com-ia.json`. Comece copiando ele.

| tipo | o que é | campos |
|---|---|---|
| `capa` | foto de fundo, letra gigante vazada, título | `kicker`, `titulo`, `subtitulo`, `rodape_direita`, `foto`, `letra` |
| `numeros` | a marca grande e três números | `numeros` [`valor`, `rotulo`], `slogan`, `foto` |
| `destaque` | um número gigante com a foto dentro e a faixa de logos | `numero`, `rotulo`, `foto`, `logos` (número ou lista de nomes/arquivos) |
| `frase` | uma frase grande no branco (ou no preto com `"escuro": true`) | `titulo`, `texto` |
| `lista` | título, subtítulo e lista com ícones que desce até ocupar a página, com foto em diagonal | `lado` (`dir`/`esq`; vazio alterna sozinho), `kicker`, `titulo`, `texto` (o subtítulo), `itens` [`icone`, `titulo`, `texto`], `fim`, `foto` |
| `temas` | grade de temas com ícone e foto ao lado | `titulo`, `texto`, `rotulo_temas`, `temas` [`icone`, `nome`], `foto` |
| `ordem` | o método: gráfico de barras e quatro critérios | `kicker`, `titulo`, `texto`, `legenda`, `criterios` [`icone`, `nome`, `texto`], `barras`, `foto` |
| `mosaico` | blocos escuros com ícone sobre a foto | `titulo`, `texto`, `blocos` [`icone`, `nome`], `faixa`, `foto` |
| `numerada` | 01, 02, 03 no fundo escuro | `kicker`, `titulo`, `texto`, `itens` [`titulo`, `texto`], `foto` |
| `grade` | cronograma: linhas e células | `kicker`, `titulo`, `linhas` [`fase`, `sub`, `celulas` [`tipo`, `tag`, `titulo`, `texto`]], `nota`, `legenda` |
| `proposta` | caixas de preço sobre a foto | `titulo`, `texto`, `caixas` [`destaque`, `rotulo`, `nome`, `valor`, `unidade_valor`, `unidade`, `detalhe`, `riscado`, `largura`], `faixa`, `foto` |
| `obrigado` | o fecho em preto, com o versículo | `citacao` (o versículo), `autor` (livro, capítulo:versículo e tradução), `proximo_passo` |

- **Quebra de linha** no título: `\n`.
- **Lado da foto** na `lista`: sem `lado`, a primeira lista tem a foto à direita e cada lista seguinte
  troca de lado. Os itens se espalham na altura da página; de 4 a 6 itens fica melhor.
- **Tipos de célula** na `grade`: `forte` (preta), `claro` (cinza) e `borda` (branca com contorno).
- **Faixa** (`faixa`) nas páginas `mosaico` e `proposta`: a pessoa de `pessoa` mais até 3 itens
  [`icone`, `titulo`, `texto`].
- **Ícones** disponíveis: estrada, pasta, balao, ia, microfone, relogio, grafico, ferramenta, equipe,
  porcentagem, ampulheta, musica, cadeado, chave, casa, documento, repete, celular, calendario, email,
  olho, onda, ingresso, predio, moeda, contrato, balanca, redes, anuncio, caminhao, alvo, check,
  carrinho, coracao, escudo, foguete, pessoa, lupa, engrenagem.
- **Fotos**: caminho do arquivo (relativo ao `conteudo.json`), ou o nome de uma das fotos de
  `assets/fotos/`. Sem foto, a página usa uma textura escura. `foto_posicao` (ex.: `"30% 50%"`)
  ajusta o recorte.

Uma ordem que funciona para proposta: capa, numeros, destaque, frase (a dor em uma frase), lista
(o que pesa hoje), frase (a virada), temas, ordem, mosaico, numerada, grade, proposta, proposta
final e obrigado. Para apresentação da empresa, tire as páginas de preço.

## Como gerar

1. Crie uma pasta para o material, fora da pasta da skill, e copie para ela o exemplo como
   `conteudo.json`, mais as fotos e a logo da pessoa.
2. Preencha o `conteudo.json` com as respostas da entrevista.
3. Rode (a pasta da skill é a "Base directory" que aparece quando ela carrega):

   ```bash
   python3 "<pasta da skill>/scripts/montar.py" conteudo.json
   ```

   Com `--pptx`, sai também um PowerPoint (uma imagem por slide, para apresentar; não é editável).
4. Precisa do Google Chrome. Para a folha de conferência e o PPTX: `poppler` (`brew install poppler`)
   e `pip install pillow python-pptx`.

## Antes de entregar

1. Abra `_build/folha.png` (as miniaturas de todas as páginas) e confira **cada página**: texto que
   vaza da caixa, título que encosta na foto, item cortado embaixo, logo invisível no fundo.
2. Se algo vazou, encurte o texto. Lista com mais de 6 itens e título com mais de 3 linhas quase
   sempre vazam.
3. Mostre o PDF à pessoa e pergunte, com opções, o que mudar. Ajuste o `conteudo.json` e rode de novo.
4. Na conversa, diga o que ficou como lacuna (logos genéricas, número de exemplo) para a pessoa
   trocar antes de mandar ao cliente.

## Como escrever o texto

- Frase curta. Uma ideia por linha.
- Título diz a conclusão, não o assunto: "O que pesa hoje", não "Dores".
- Fale com o cliente por "você".
- Nada de "não é X, é Y", nem trio de adjetivos, nem frase de efeito no fim de cada bloco.
- Número com unidade: `R$ 5 mil por mês`, `6 meses`, `+50 projetos`.

## Quem fez

Feito por Guilherme Reis. Ensino empresários e profissionais a trabalhar com IA no dia a dia.
Instagram: [@guilhermereis.ai](https://www.instagram.com/guilhermereis.ai/).

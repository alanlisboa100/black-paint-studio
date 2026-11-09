# Black Paint Studio 2.3.0 — Termux

Editor local com camadas, pincéis, estudos procedurais e integração opcional com BlackCore. Esta revisão corrige o fluxo de pintura e prepara a instalação no Android. Não contém um modelo de imagem treinável: o motor local desenha por regras; a interpretação aberta de referências depende do BlackCore e do provider configurado nele.

## Guias incluídos para o BlackCore

- `AGENTS.md`: instruções de trabalho da IA neste projeto.
- `GUIA_INSTALACAO_IA.md`: extração, instalação, diagnóstico, teste no aparelho e texto pronto para entregar ao BlackCore.
- `GUIA_CONSTRUCAO_VISUAL.md`: receita do desenho, funções, coordenadas, máscaras, curvas, luz, olhos, checkpoints e ciclo de comparação.
- `GUIA_ALTERACOES_BLACKCORE.md`: controles de olhos/boca/expressão/cabelo/tecido, limites, exemplos JSON e revisão antes/depois.

Na versão 2.3.0, **Misuki natural** oferece seis expressões e veludo/cetim no editor. A CLI aceita `--expression` e `--settings`: abertura/largura/inclinação dos olhos, íris, pupila, olhar, sobrancelhas, curva/abertura/largura da boca, lábios, brilho/ondulação fina do cabelo e contraste das dobras. Há novas texturas de tecido, dobras, ilhoses e acabamento do anel. A composição continua frontal.

```bash
python render_misuki_portrait.py --settings presets/misuki_suave.json --output gallery/misuki_suave.png
python render_misuki_portrait.py --expression happy --settings presets/satin.json --output gallery/misuki_alegre.png
python gerar_estudos_expressao.py --output-dir gallery/estudos_expressao
```

Na versão 2.3.0, a franja tem uma base contínua com aberturas curvas, a iluminação acompanha cada mecha, os olhos recebem sombra das pálpebras e reflexos menores, e o contorno do queixo foi revisado. Os guias documentam o código para uma IA poder reproduzir e modificar o procedimento; ler esses arquivos não realiza treinamento automático.

Para repetir o resultado com relatório e comparação com 2.1.0:

```bash
python reproduzir_misuki.py --width 900 --quality standard --seed 7331 --output-dir gallery/reproducao_misuki
```

## Instalar

Extraia o ZIP e, dentro da pasta `black-paint-studio`, execute:

```bash
bash install_termux.sh
cd ~/black-paint-studio-2.3.0
bash start_termux.sh
```

O instalador usa os pacotes nativos `nodejs-lts`, `python` e `python-pillow`. Copia o projeto para a pasta privada do Termux se você o extraiu em Downloads. Não substitui uma pasta existente: use outro destino com `PAINT_INSTALL_DIR` quando necessário.

Abra `http://127.0.0.1:3333` no navegador do mesmo celular. Sem acesso ao armazenamento, imagens vão para `gallery/` dentro do projeto. Para salvar em Downloads:

```bash
termux-setup-storage
```

Aceite a permissão do Android e volte ao estúdio. Não é obrigatório instalar Termux:API para pintar ou exportar; a indexação da galeria usa `termux-media-scan` apenas se disponível.

## Diagnosticar e parar

```bash
python paint_cli.py --doctor
python paint_cli.py --stop
PORT=3334 python paint_cli.py --open
```

Erros do servidor ficam em `server.log`. Instalações existentes iniciadas por outro caminho ou bloqueadas pelo `/proc` do Android podem precisar ser encerradas pela sessão original. Para manter o Termux em segundo plano, ajuste a otimização de bateria do aplicativo no Android; o sistema ainda pode encerrar processos.

## Pintar e guardar o trabalho

- Camadas independentes, visibilidade, opacidade, modos de mistura, clipping e alpha lock.
- Pincéis de óleo, aquarela, guache, lápis, carvão, tinta, aerógrafo e outros materiais simulados.
- Balde corrigido para as coordenadas da camada, inclusive em telas com DPR alto; preenchimentos de cores próximas não entram em ciclos.
- Gestos de zoom com dois dedos encerram o traço corrente. Pressão depende do hardware e navegador.
- **Salvar PNG** exporta a resolução lógica do documento e informa o destino. O servidor evita sobrescrever arquivos; se indisponível, o navegador faz o download.
- **Salvar Projeto** guarda `.bpaint` com camadas e propriedades. **Projeto** abre esses arquivos.
- **Recuperar** restaura o último trabalho salvo automaticamente neste navegador, endereço e porta. A recuperação ocorre cerca de 900 ms após uma ação; fechar abruptamente antes disso pode perder a última ação. Ao reabrir, a tela vazia não apaga a recuperação anterior. Mudanças de endereço/porta e limpeza de dados do navegador afetam esse recurso. Salve `.bpaint` para cópias duráveis.
- Limite de 12 camadas e documentos com maior lado de até 1440 px. O histórico guarda até 12 ações, com orçamento estimado de 24 MiB de dados únicos; preserva ao menos duas posições, que podem exceder esse orçamento. Não é um teto absoluto de RAM.

A interface usa recursos locais e funciona sem baixar fontes. Geradores locais e academia não precisam de internet. O servidor precisa continuar rodando para abrir/recarregar o editor: não é uma PWA instalada com service worker.

## Misuki e construção por etapas

Em **Retrato local**, escolha **Misuki natural** e toque em **Gerar personagem local**. O novo motor desenha uma composição frontal com mechas curvas, fios orientados, sombras suaves limitadas às máscaras do rosto, íris detalhada, cílios, pescoço e roupa. Os olhos leem a cor de `misuki.json`. O modo **Leve** gera 720 × 960 sem supersampling; **Detalhada** gera 900 × 1200, pintando internamente em resolução dupla e reduzindo ao final. Use Leve primeiro no celular.

O botão separado da Misuki pede um plano visual ao BlackCore quando disponível. Se essa geração falhar ou estiver desativada, usa esse novo retrato local. A composição frontal é construída por regras e não transforma automaticamente qualquer referência, pose ou movimento. A imagem enviada orientou o trabalho visual; o renderizador não copia seus pixels. A aparência ainda não alcança todos os detalhes da referência.

```bash
python paint_cli.py --ink-portrait --style misuki
python paint_cli.py --ink-portrait --style misuki --quality economy
python render_misuki_portrait.py --output gallery/misuki.png --checkpoint-dir gallery/etapas_misuki
python render_misuki_portrait.py --background night --seed 42 --output gallery/misuki_noite.png
python render_misuki_portrait.py --engine vector --output gallery/misuki_vetorial.png
python render_neural_plan.py --plan neural_plan_S2.json --output gallery/plano.png --checkpoint-dir gallery/etapas_plano
```

O motor natural salva cinco etapas reais: silhueta, volume do rosto, olhos/expressão, cabelo/roupa e acabamento. `exemplos_misuki_natural/` inclui o resultado, etapas e relatório técnico. A seed varia fios e pequenas marcas, mantendo a mesma anatomia; ela não cria novas poses. Fundo branco suave é o padrão deste estudo e `--background night` oferece fundo escuro.

O motor vetorial anterior continua acessível com `--engine vector`, baseado em `neural_plan_S2.json`. Seus checkpoints mostram pontos da sequência de elementos do plano. O rasterizador mantém curvas e arcos, respeita opacidade zero e limita dimensões. Pintadas são alocadas por região, evitando criar uma camada do tamanho inteiro para cada marca. Paths com múltiplos subcaminhos não implementam todas as regras de buracos/winding do SVG; o resultado Python pode diferir do navegador. Nenhum dos motores fornece uma pontuação automática de fidelidade artística.

Outros estudos:

```bash
python paint_cli.py --ink-portrait --style natural
python paint_cli.py --ink-portrait --style ink
python render_study_examples.py --study city --output-dir gallery/estudos
python render_academy_results.py --output-dir gallery/academia
```

## Referência com BlackCore

Abra uma imagem com **Abrir**. Ela vira um documento editável e uma referência reduzida para análise. A referência permanece separada da nova pintura gerada. **Mostrar referência** permite sobrepor sua visualização.

Configure o executável no PATH, ou use:

```bash
BLACKCORE_BIN=/caminho/do/blackcore python paint_cli.py --open
```

O campo **Modelo Google** pode ficar vazio: o BlackCore escolhe seu padrão. Você pode informar um identificador aceito por sua instalação; o Paint não impõe uma lista de versões. Também pode definir `BLACKCORE_MODEL` no ambiente do servidor. O servidor já aberto deve ser reiniciado para receber novas variáveis.

O Paint usa a interface de comando `blackcore --print ... --provider google --image ... --no-session`. Essa interface, modelos, autenticação e quotas dependem da versão instalada do BlackCore. Não foram testados contra o BlackCore real deste usuário. Os testes usam um executável simulado. Sem um plano válido, a análise mostra um erro e preserva a pintura. A geração Misuki tem fallback local.

## Configuração opcional

- `PAINT_OUTPUT_DIR`: destino dos PNGs do servidor e das ferramentas que usam o adaptador de saída. Nas ferramentas com `--output`, esse argumento tem prioridade.
- `PYTHON`: executável Python usado pelo servidor; padrão `python3`.
- `HOST`: padrão `127.0.0.1`. `0.0.0.0` libera a rede local; esse modo não contém login.
- `MISUKI_FORCE_LOCAL=1`: ignora a geração externa da Misuki.

`enhance_eyes_neural.py` precisa de NumPy, que é opcional:

```bash
pkg install python-numpy
# ou instale junto com o projeto:
bash install_termux.sh --extras
```

Os scripts PIN32 são colorizadores específicos para aquela composição, com máscaras por regras. Não oferecem seleção semântica genérica de cabelo/roupa:

```bash
python paint_pin32_perfection.py --input desenho.png --output gallery/colorido.png --max-edge 1200
```

`ai_masterpieces_generator.py` e `generate_personagem_ia.py` dependem de um serviço remoto Pollinations. Foram preservados como ferramentas opcionais; a disponibilidade externa não foi validada e não faz parte do editor local.

## Verificação

```bash
npm test
python paint_cli.py --doctor
```

Veja `ANALISE_E_MELHORIAS.md` para mudanças, resultados e limitações. Em Linux, instale Pillow com `python3 -m pip install -r requirements.txt`; o editor não precisa de pacotes npm externos.

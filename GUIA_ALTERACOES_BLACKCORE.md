# Alterar olhos, boca, expressão, cabelo e roupa — 2.3.0

Leia primeiro AGENTS.md e GUIA_CONSTRUCAO_VISUAL.md. Este guia ensina a usar os
controles reais do motor natural. Os exemplos são frontais; não são um sistema
de rig para qualquer pose nem treinamento automático de um modelo.

## Procedimento para cada pedido

1. Traduza o pedido em uma mudança concreta. Exemplo: “olhos mais delicados”
   pode significar menor abertura, não pintar a íris inteira de preto.
2. Copie um JSON de `presets/` para outra pasta. Preserve o original e o PNG
   anterior. Mude poucos controles por vez e mantenha seed, tamanho e fundo.
3. Renderize com `--settings`, confira rosto ampliado e retrato completo.
   Confira que a personagem mantém olhos vermelhos, cabelo preto e chifres.
4. Se a mudança exigir uma forma que o controle não oferece, altere o código
   responsável e rode os testes antes de renderizar novamente.
5. Entregue o antes/depois e diga exatamente o que mudou. Não chame uma
   execução sem erro de aprovação artística. Espere a avaliação do usuário
   quando for uma preferência de aparência.

## Expressões disponíveis

| CLI/JSON | Aparência construída |
|---|---|
| `neutral` | Neutra |
| `soft` | Sorriso discreto e pálpebras relaxadas |
| `happy` | Sorriso mais curvo, boca pouco aberta e olhos mais fechados |
| `sad` | Cantos da boca baixos e parte interna das sobrancelhas elevada |
| `angry` | Pálpebras estreitas e sobrancelhas inclinadas para dentro |
| `surprised` | Maior abertura dos olhos, íris menor e boca aberta |

```bash
python render_misuki_portrait.py --expression happy --settings presets/velvet.json --output gallery/misuki_alegre.png --checkpoint-dir gallery/etapas_alegre
python render_misuki_portrait.py --expression sad --settings presets/satin.json --output gallery/misuki_triste.png
python gerar_estudos_expressao.py --output-dir gallery/estudos_expressao
```

O último comando gera os seis retratos e um painel de recortes do rosto. Na
interface, escolha **Misuki natural**, expressão, tecido e gere o personagem.
Esses controles da interface se aplicam ao estilo Misuki natural; os outros
estudos mantêm suas próprias composições.

## Controles em JSON

Todos os números são finitos. Valores fora dos limites, chaves desconhecidas,
booleanos no lugar de números e tecidos inexistentes são rejeitados.

| Chave | Limite / valor padrão | Efeito |
|---|---|---|
| `expression` | `neutral` e opções acima | Escolhe um conjunto de controles |
| `eye_open` | 0.5–1.4 / 1 | Altura das pálpebras |
| `eye_width` | 0.8–1.15 / 1 | Largura ao redor do centro do olho |
| `eye_tilt` | -0.6–0.6 / 0 | Inclinação espelhada dos olhos |
| `iris_size` | 0.75–1.15 / 1 | Raio da íris em relação ao original |
| `pupil_size` | 0.18–0.36 / 0.25 | Raio escuro proporcional à íris |
| `gaze_x` | -1–1 / 0 | Desloca ambas as íris, até 8 unidades da base |
| `gaze_y` | -1–1 / 0 | Desloca ambas as íris, até 5 unidades da base |
| `brow_tilt` | -1–1 / 0 | Positivo baixa a parte interna; negativo eleva |
| `mouth_width` | 0.7–1.4 / 1 | Largura da boca ao redor do centro |
| `mouth_curve` | -1–1 / 0 | Positivo sorri; negativo baixa os cantos |
| `mouth_open` | 0–1 / 0 | Abertura e cavidade da boca |
| `lip_fullness` | 0.6–1.4 / 1 | Volume dos lábios |
| `hair_shine` | 0.3–1.3 / 1 | Intensidade do brilho das mechas |
| `hair_wave` | 0–2 / 1 | Ondulação fina dos fios, sem mudar a massa do cabelo |
| `cloth_material` | `velvet` / `satin` | Veludo difuso ou cetim com brilho estreito |
| `cloth_fold` | 0.4–1.5 / 1 | Contraste das dobras existentes |

A ordem é: padrões → expressão escolhida → números explícitos do JSON. O
argumento CLI `--expression` escolhe a expressão mesmo se o JSON tiver outra;
os números do JSON ainda substituem os valores desse conjunto. Para testar
expressões sem substituições do rosto, use `presets/velvet.json` ou
`presets/satin.json`. `presets/misuki_suave.json` contém ajustes completos.

Exemplo de arquivo `meus_ajustes.json`:

```json
{
  "expression": "soft",
  "eye_open": 0.85,
  "eye_width": 1.02,
  "gaze_x": 0.3,
  "gaze_y": 0,
  "mouth_width": 1.08,
  "mouth_curve": 0.55,
  "lip_fullness": 1.1,
  "hair_shine": 1.12,
  "hair_wave": 1.25,
  "cloth_material": "velvet",
  "cloth_fold": 1.1
}
```

```bash
python reproduzir_misuki.py --settings meus_ajustes.json --width 720 --quality economy --seed 7331 --output-dir gallery/minha_variacao
```

O relatório registra os controles efetivamente aplicados. Escolha nova pasta
para cada variação se quiser preservar tudo. Esses comandos substituem seus
arquivos de demonstração nomeados na pasta de saída.

## Quando alterar o código

**Olhos:** `paint_eye` transforma os pontos das duas pálpebras juntos. A máscara,
a sombra, a linha da pálpebra e os cílios usam as mesmas curvas transformadas.
A íris é recortada por essa máscara. Não mova só a pupila deixando reflexos,
sombra ou íris no ponto antigo. Use `paint_iris` para textura e profundidade.
Para olhos fechados de verdade, implemente a linha de fechamento e omita a
esclera; `eye_open=0.5` ainda representa um olho aberto.

**Boca:** `paint_lips` compartilha cantos e centro entre lábio superior, linha
central, lábio inferior e cavidade. Para sorrir, eleve os cantos e mantenha
transições curvas. Mais abertura exige uma cavidade, não uma linha preta mais
grossa. As sombras são limitadas ao rosto. O sorriso atual é estilizado, sem
dentição completa, língua detalhada ou deformação ampla das bochechas.

**Expressão:** `portrait_controls.PRESETS` combina pálpebras, sobrancelhas e
boca. Atualize também as listas CLI/servidor/interface e exemplos se adicionar
uma nova expressão. Não prometa que apenas trocar o texto de um prompt altera
o motor local. Para mexer no nariz, formato da cabeça e bochechas, modifique
`paint_face` e reveja o encontro com franja, orelha e pescoço.

**Cabelo:** `hair_wave` varia os fios; para novas mechas, comprimento ou franja,
altere as duas bordas Bézier em `paint_hair`. Faça primeiro a massa e a
sobreposição, depois luz e fios. Preserve raízes coerentes e escureça contatos.
Brilho excessivo clareia o cabelo preto e dá aparência metálica.

**Roupa:** `paint_clothing` separa máscara do torso e da gola. Dobras seguem
costuras e pontos de tensão. Veludo recebe luz ampla e textura discreta; cetim
tem reflexos mais estreitos. Ilhoses e anel recebem borda escura e pequeno
reflexo. Para outra roupa, crie a nova silhueta e máscaras; mudar apenas
`cloth_material` não troca o modelo do traje.

## Verificação

```bash
npm test
python paint_cli.py --doctor
```

Confira cinco checkpoints, ambos os olhos alinhados, boca integrada ao rosto,
brilho coerente entre olhos/cabelo/metal e textura sem vazamento na pele.
Testes validam controles e confinamento de alterações; a qualidade visual é
conferida abrindo os PNGs. Os exemplos são construídos por Pillow, sem um
gerador externo de imagens.

## Pedido pronto para o BlackCore

> Leia AGENTS.md, GUIA_CONSTRUCAO_VISUAL.md e GUIA_ALTERACOES_BLACKCORE.md.
> Use os controles JSON existentes para alterar olhos, boca e expressão antes
> de editar a geometria. Preserve a identidade da Misuki e o resultado anterior.
> Renderize com a mesma seed, salve cinco etapas e compare o rosto e o retrato
> completo. Para cabelo e roupa, respeite máscaras, curvas, costuras e luz.
> Quando mudar o código, rode os testes e mostre os PNGs realmente gerados.
> Informe quais controles aplicou e quais limites permanecem.

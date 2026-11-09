# Como reproduzir e melhorar a construção da Misuki

Este guia documenta a receita implementada em `natural_portrait_engine.py`.
Para os controles de expressão e ajustes JSON introduzidos em 2.3.0, consulte
`GUIA_ALTERACOES_BLACKCORE.md`. A construção atual usa esses controles para
transformar pálpebras, sombra e cílios no mesmo sistema.
Ler o guia fornece contexto a uma IA assistente; isso não treina seus pesos.
O código constrói um retrato frontal próprio. Não usa pixels da referência,
não identifica anatomia automaticamente e não anima a personagem.

## Arquivos e responsabilidades

| Arquivo/função | Responsabilidade |
|---|---|
| `misuki.json` | Ficha da identidade; `palette.vermelhoIris` controla a íris no motor natural |
| `render_misuki_portrait.py` | Entrada CLI, tamanho, qualidade, seed, fundo e escolha natural/vetorial |
| `Painter` | Escala, máscaras, curvas, gradientes, sombras, mechas e checkpoints |
| `paint_base` | Silhueta, cabelo de fundo, ombros, pescoço e sombra sob a mandíbula |
| `paint_face` | Máscara do rosto, volume, blush, nariz, mandíbula e orelha |
| `paint_eye`, `paint_iris` | Pálpebras, esclera, íris, pupila, reflexos, cílios e sobrancelhas |
| `paint_lips` | Formas discretas da boca e sombras recortadas pela máscara do rosto |
| `paint_clothing` | Gargantilha, textura, costuras e amarração |
| `paint_hair`, `Painter.lock` | Franja, mechas curvas, volume e fios orientados |
| `paint_horns` | Dois chifres curvos com linhas discretas de textura |
| `server.js`, `app.js` | Geração local e carregamento no editor |

A ficha contém mais descrições do que o motor interpreta. Cabelo, roupa e
chifres naturais ainda são definidos pelas formas do código; modificar só o
texto da ficha não redesenha essas formas.

## Receita de execução

Use esta mesma seed para comparar alterações sem confundir novos fios com
melhoria de anatomia:

```bash
python render_misuki_portrait.py --width 900 --quality standard --seed 7331 --background paper --output gallery/misuki.png --checkpoint-dir gallery/etapas_misuki
```

Para o A25, comece com `--width 720 --quality economy`. Standard pinta em 2× e
reduz com Lanczos; economy pinta no tamanho final. O maior tamanho aceito é
1080 de largura. Mais pixels não corrigem proporções.

Para gerar também o relatório técnico e uma comparação com a demonstração
2.1.0 incluída no pacote:

```bash
python reproduzir_misuki.py --width 900 --quality standard --seed 7331 --output-dir gallery/reproducao_misuki
```

Esse comando substitui os arquivos de demonstração nomeados na pasta de saída;
escolha outra pasta para preservar uma reprodução anterior. A comparação só
é diretamente equivalente com o mesmo tamanho, seed e fundo do exemplo 2.1.0.

As coordenadas de desenho usam a base **900 × 1200**. `Painter.point` aplica
a escala; não misture coordenadas da base com pixels já escalados.

## Ordem de construção e revisão

1. **Base e silhueta:** delimite a massa do cabelo, ombros e pescoço. Reserve
   a área do rosto. Verifique se a cabeça está apoiada no pescoço.
2. **Rosto e volume:** construa primeiro a máscara. Aplique tons amplos e
   sombras suaves dentro dela; depois nariz, blush e contorno discreto.
   Verifique o encontro da mandíbula com o pescoço e a continuidade do queixo.
3. **Olhos e expressão:** forme as duas amêndoas, pinte a esclera e recorte
   a íris. Acrescente pupila, sombra da pálpebra, reflexos pequenos e cílios.
   Confira alinhamento e direção do olhar sem exigir simetria perfeita.
4. **Mechas e roupa:** pinte roupa e uma base contínua da franja. Sobreponha
   mechas grandes com curvas coerentes. Faça volume e só depois fios finos.
   Confira raízes, pontas, sobreposição e aberturas curvas da franja.
5. **Acabamento:** pinte os chifres e pequenas marcas. Abra o retrato completo
   no tamanho normal e ampliado. Confira identidade, contornos, sombras e luz.

O código grava `01_base_e_silhueta.png`, `02_rosto_e_volume.png`,
`03_olhos_e_expressao.png`, `04_mechas_e_roupa.png` e `05_acabamento.png`.
São partes realmente construídas, não cinco filtros aplicados ao mesmo PNG.

## Sombras sem alterar cabelo ou fundo

`Painter.soft` cria um patch na área necessária, desfoca seu alpha e multiplica
esse alpha pela máscara da parte pintada. Passe `clip=face` para pele,
`clip=neck` para pescoço ou a máscara da mecha para cabelo. Não aplique uma
elipse desfocada global para tentar corrigir uma região sem a máscara.

Gradientes amplos dão o volume geral. Sombras estreitas indicam contato e
oclusão: pálpebra sobre olho, cabelo sobre testa, queixo sobre pescoço.
Reduza contraste onde a luz é difusa. Não contorne o nariz inteiro com linha
escura. Evite borrar a imagem inteira, pois isso apaga os detalhes já corretos.

## Cabelo por curvas

Cada `Painter.lock(left, right, ...)` recebe duas curvas cúbicas. Cada curva
tem quatro pontos: começo, controle 1, controle 2 e fim. As duas bordas formam
uma fita; os fios interpolam essas bordas ao longo do parâmetro `t`.

O volume também é calculado nas coordenadas da fita. Faixas largas de luz
acompanham a curvatura; linhas menores dão textura. As bordas ficam mais
escuras e o brilho é moderado. Os patches são recortados pela máscara.

Ao mudar uma mecha, confira que as bordas não cruzam entre si. Controle a
largura no comprimento e convergência nas pontas. Várias raízes incoerentes ou
milhares de linhas retas produzem aparência de peruca. Corrija a massa e as
mechas antes de acrescentar mais fios. A camada contínua da franja impede
aberturas retangulares no limite superior da máscara do rosto.

## Olhos com profundidade

A íris usa distância radial e ângulo em um patch pequeno. A borda externa e
a pupila escurecem; variações radiais dão textura; a parte inferior recebe
mais luz. A pálpebra projeta sombra por cima e oculta parte da íris.

Reflexos devem acompanhar a mesma luz nos dois olhos. Evite círculos brancos
grandes, pupilas deslocadas e esclera branco puro. Cílios acompanham as curvas
das pálpebras; não os desenhe como raios uniformes em torno da íris.

## Ciclo de melhoria verificável

1. Guarde o PNG anterior e registre seed, qualidade, largura e fundo.
2. Escolha um problema concreto: franja reta, sombra vazando, olhar rígido ou
   mandíbula duplicada. Altere uma família de elementos por vez.
3. Rode `npm test` após alterações relevantes e renderize as cinco etapas.
4. Compare antes/depois com os mesmos parâmetros. Examine também recortes
   de olhos e cabelo; confira se a correção não criou outro problema.
5. Registre o que mudou e os limites que continuam. Entregue o PNG para a
   pessoa avaliar; a avaliação artística não é substituída por testes.

`exemplos_misuki_v21/` preserva o resultado anterior. `exemplos_misuki_natural/`
contém o atual, etapas, comparação e relatório de execução.

Os testes cobrem dimensões, validação, determinismo, confinamento de sombra,
cor da íris, checkpoints e servidor. Não medem beleza, semelhança com a
referência ou desempenho Android. `semantic_fidelity_score` permanece nulo.

## Evoluções que exigem nova implementação

Para inclinação da cabeça e novas expressões, introduza pontos anatômicos
compartilhados e transforme olhos, nariz, boca e franja no mesmo sistema.
Girar peças isoladas faz o rosto perder coerência. Para outras poses e corpos,
implemente construção de anatomia e sobreposição correspondente.

Para interpretar referências, a integração de visão precisa produzir um plano
validado que o Paint execute. Imagem enviada a uma IA não garante um plano
correto. Para movimento, acrescente rig, quadros coerentes e exportação: os
checkpoints atuais não são uma animação da personagem.

Não instale um modelo pesado no telefone como requisito destes estudos. A
receita atual usa Pillow e regras explícitas; modelos externos são outro fluxo
e dependem de configuração e do pedido do usuário.

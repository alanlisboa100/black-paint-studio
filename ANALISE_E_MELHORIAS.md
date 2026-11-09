# Análise e alterações — 2.3.0

## Alterações controladas e ensino ao BlackCore — 2.3.0

- Seis expressões com pálpebras, sobrancelhas e boca combinadas. As máscaras e sombras dos olhos seguem as curvas transformadas, e os reflexos acompanham a íris ao mudar o olhar.
- Controles JSON para abertura/largura/inclinação de olhos, tamanho de íris/pupila, olhar, sobrancelha, largura/curva/abertura da boca e volume dos lábios. Limites e entradas finitas validados antes de pintar.
- Cabelo com ondulação fina adicional e brilho ajustável; massa e corte ainda são definidos por curvas no código.
- Roupa com dobras ligadas a costuras, veludo/cetim, textura discreta, ilhoses e acabamento do anel. Trocar material não troca a silhueta do traje.
- Expressão e tecido disponíveis no editor; CLI aceita `--expression` e `--settings`. Relatórios registram todos os controles aplicados.
- `GUIA_ALTERACOES_BLACKCORE.md` ensina a tradução de pedidos em parâmetros, precedência, revisão visual, alterações de geometria e limitações. Presets e gerador de painel de expressões incluídos.

**37 testes aprovados: 20 JavaScript + 17 Python.** Incluem rejeição de parâmetros inválidos, seis resultados diferentes com mudanças confinadas ao rosto, limites de íris em olhos transformados, material sem repintar rosto e geração HTTP de expressão/tecido. Modos de renderização e exemplos foram gerados no Linux; isso não valida Android ou interface interativa em navegador real. Testes não fornecem nota artística. A composição permanece frontal, sem interpretação livre local ou treinamento automático.

## Refinamento e reprodução — 2.2.0

- Base contínua da franja com aberturas curvas, eliminando as aberturas retas da versão anterior.
- Volume das mechas calculado nas coordenadas de duas curvas, com bandas de luz acompanhando o cabelo. O patch de iluminação ocupa só a caixa da mecha.
- Íris com contraste radial revisado, bordas/pupila mais profundas, sombra sob a pálpebra superior, esclera com gradiente e reflexos menores.
- Mandíbula/queixo com contorno revisado e sombras sutis; sombras da boca confinadas à máscara do rosto.
- `AGENTS.md` e dois guias descrevem instalação, construção, revisão e limites. Não contêm pesos nem treinamento automático.
- `reproduzir_misuki.py` gera PNG, cinco etapas, relatório técnico e comparação com o exemplo 2.1.0 preservado/reproduzido a partir do código daquela versão.

Verificação: 20 testes JavaScript e 13 Python aprovados, incluindo a geração HTTP em 720 × 960. Sintaxe JS/Python/shell verificada, modos leve e detalhado renderizados. O novo retrato foi aberto para inspeção visual. As medições desta revisão estão em `exemplos_misuki_natural/relatorio.json`; são do processo Python nesta máquina Linux, sem medição no A25. O navegador e o BlackCore reais continuam sem teste neste ambiente.

O estudo segue frontal, com anatomia escrita no código. Não há geração automática de qualquer pose, reconhecimento semântico local, movimento da personagem nem nota de fidelidade. A comparação visual mostra a revisão concreta e não garante superioridade estética universal.

## Novo motor natural — 2.1.0

- Composição frontal redesenhada em Pillow: mechas entre curvas Bézier, 1.750 fios orientados, brilho seguindo o cabelo e fios soltos.
- Rosto com sombras desfocadas recortadas por máscara, blush discreto, volume no nariz e pescoço; olhos com textura radial de íris, pupila, pálpebras e cílios.
- Roupa com gola texturizada, costuras e amarração; chifres curvos mantidos como identidade da personagem.
- Geração direta no editor em modo leve (720 × 960) ou detalhado (900 × 1200 com supersampling de 2×). Pillow é suficiente; sem nova dependência nem download de modelo.
- Cinco checkpoints correspondem às partes efetivamente construídas. O motor vetorial anterior permanece disponível em `--engine vector`.
- Seed controla pequenas variações de fios; não altera a pose. A imagem de referência não entra como pixels no algoritmo. A anatomia é uma composição frontal escrita manualmente, sem reconhecimento semântico ou animação.

Validação da versão 2.1.0: **20 testes JavaScript + 13 Python = 33 aprovados**. Novos testes verificam confinamento das sombras, determinismo, variação da seed, dimensões, etapas distintas, cor da íris, entradas inválidas e PNG leve servido pelo HTTP. Sintaxe JavaScript, compilação Python e sintaxe shell verificadas. CLI leve e fundo noturno também renderizados. O resultado detalhado foi inspecionado visualmente.

Medição nesta máquina Linux: renderizar e salvar o retrato detalhado com cinco checkpoints levou **2,475 segundos**, com pico de RSS de **52,5 MiB** nesse processo Python. Isso não mede o desempenho do Samsung A25, a memória total do editor/navegador nem o comportamento no Android. O relatório acompanha `exemplos_misuki_natural/`.

## Revisão anterior — 2.0.0

## Problemas encontrados e corrigidos

| Área | Problema do pacote recebido | Alteração |
|---|---|---|
| Referência | `referenceDataUrl` nunca era preenchida; botão de visão ficava desabilitado | Imagem aberta passa a registrar a referência reduzida e a atualizar o botão |
| Misuki externa | UI ignorava respostas no modo `plan`; prompt não exigia o formato esperado | Esquema JSON explícito e aplicação do plano SVG |
| Misuki local | Desenho geométrico simples com chifres retos | Retrato baseado no plano do pacote, olhos ligados à ficha visual e dois chifres curvos |
| Balde | Usava DPR e dimensões do display na camada lógica | Coordenadas e resolução da camada |
| Balde | Recolorir dentro da tolerância permitia revisitar pixels | Mapa de pixels visitados |
| Pincéis decorativos | Matrix, partículas e spray pintavam no display e eram apagados pela composição | Direcionamento para a camada ativa |
| Alpha lock | Pincel forçava `source-over`, ignorando a trava | Preserva `source-atop`; borracha não remove alpha travado |
| Toque | Eventos de outro dedo podiam continuar o traço; zoom deixava traço sem histórico | Identifica o ponteiro de desenho e encerra o traço ao iniciar zoom |
| Histórico | Restauração alterava a lista de camadas antes de carregar imagens; IDs podiam repetir | Carrega camadas antes de aplicar, descarta restaurações antigas e recalcula IDs |
| Histórico/RAM | Snapshots repetidos e somente limite de contagem | Compartilha strings iguais, orçamento estimado e limite de camadas |
| Projetos | Só existia PNG achatado | `.bpaint` editável e recuperação via IndexedDB |
| PNG | Salvamento duplo, falhas silenciosas, sobrescrita | Salva pelo servidor; download como fallback; informa destino e evita colisão |
| Transparência | Compositor pintava fundo preto mesmo em documento transparente | Mantém o alpha das camadas e usa transparência ao abrir imagem |
| GPU | Aplicava a composição inteira sobre a camada ativa; escala usava dimensões erradas | Acabamento da camada ativa na sua resolução lógica |
| GPU | Shader GLSL antigo tentava WebGL2; recursos permaneciam alocados | Passe WebGL1 e liberação de recursos após copiar o resultado |
| Rasterizador | Perdia amostras de arco; reflexão de curvas usava controle antigo; largura de linha sem escala | Preserva pontos, reinicia reflexão e escala largura |
| Rasterizador/RAM | Nova imagem grande por forma; resolução sem limites | Patches por região e limite de 2 MP |
| Instalação | Sem instalador, versão incoerente e ausência de diagnóstico | Scripts Termux, versão 2.0.0, `--doctor`, `--stop` e log |
| Python | Ferramentas com destino Android fixo e NumPy não documentado | Adaptador de saída, parâmetros PIN32 e dependência opcional |
| BlackCore | Lista fixa de identificadores de modelos | Usa padrão do BlackCore ou identificador fornecido |
| Servidor | Rotas locais podiam ser acionadas por páginas externas; renderizadores podiam concorrer | Verificação de origem/Host e apenas um subprocesso local de pintura por vez |
| Interface | Fonte externa com handler incompatível com CSP; botão BN sem implementação | Fontes do sistema, controles com rolagem; remove botão inativo |

## Verificação executada

- 19 testes JavaScript e 9 testes Python passaram: 28 no total.
- Verificação sintática de todos os arquivos JavaScript e compilação de todos os arquivos Python.
- Os sete estilos expostos pela CLI foram renderizados e seus PNGs foram abertos e verificados.
- Plano S2: 113 elementos pintados, zero pulados na execução de teste.
- Retrato Misuki novo e cinco checkpoints foram gerados. Os resultados finais do plano S2 e da Misuki foram inspecionados visualmente.
- Testes reais do servidor HTTP em loopback para status, arquivos, geração, origem, gravação, colisão de nomes e uploads inválidos. BlackCore foi simulado.

## O que ainda depende do aparelho

Os testes rodaram em Linux com Node/Python/Pillow, sem Android ou Termux real. O navegador automatizado não pôde ser instalado: o download do Chromium veio inválido. Assim, não houve verificação visual/interativa da página num navegador real. Os gestos, layout móvel, GPU, permissões Android, abertura do navegador e comportamento em segundo plano exigem teste no celular.

Também não foi possível testar o executável real do BlackCore, modelos Google, chaves/quotas ou serviço externo Pollinations. O pacote não tem treinamento autônomo, compreensão visual local, seleção semântica genérica, liquify ou fidelidade artística garantida. O estudo frontal da Misuki melhora a base procedural, mas não substitui um modelo visual. Não há fundamento para prometer “100% perfeito” ou desempenho idêntico em todos os aparelhos.

## Teste curto no Termux

1. Rode `python paint_cli.py --doctor` e abra o editor.
2. Pinte, use balde com uma cor próxima e confira desfazer/refazer.
3. Adicione uma camada; teste alpha lock e acabamento GPU.
4. Abra uma imagem; confira a referência e sua sobreposição.
5. Gere Misuki local e salve PNG: confira o destino mostrado.
6. Salve `.bpaint`, abra-o e confira camadas/propriedades.
7. Faça uma alteração, espere pelo menos dois segundos, reabra no mesmo endereço e toque em Recuperar.
8. Configure BlackCore, reinicie o servidor e teste uma referência pequena.

# Instruções para a IA que instala ou modifica este pacote

Este é o Black Paint Studio 2.3.0. Leia `GUIA_INSTALACAO_IA.md` para instalar e
`GUIA_CONSTRUCAO_VISUAL.md` para reproduzir ou melhorar o retrato. Essas são
instruções operacionais e documentação do código; não são pesos de um modelo.

Para alterações de aparência, leia `GUIA_ALTERACOES_BLACKCORE.md`. Use os
controles JSON e expressões existentes, registre parâmetros e compare PNGs
com a mesma seed antes de modificar formas manualmente.

## Regras do projeto

- Preserve projetos `.bpaint`, desenhos, referências e a instalação anterior.
  O instalador usa uma pasta própria por versão e recusa destino já existente.
- Não instale modelos pesados, não configure chaves e não publique nada como
  parte da instalação local. BlackCore é uma integração opcional.
- O motor local é procedural e frontal. Não anuncie reconhecimento de qualquer
  referência, aprendizado automático, novas poses ou animação sem implementar
  e verificar essas capacidades.
- Priorize proporções, sobreposição e luz antes de aumentar a quantidade de
  fios. Mantenha sombras confinadas à máscara da parte pintada.
- Preserve cinco checkpoints reais e a cor de íris da ficha `misuki.json`.
  Não atribua nota de fidelidade com base apenas em contraste ou simetria.
- Depois de mudar código, rode os testes pertinentes e gere a imagem.
  Inspecione visualmente os resultados; testes de código não julgam beleza.
- Registre exatamente o ambiente testado. Testar Linux não comprova execução
  Android, gestos, WebGL ou funcionamento do BlackCore real.
- Para nova versão, mantenha coerentes `package.json`, `server.js`,
  `paint_cli.py`, o indicador em `index.html`, `install_termux.sh` e README.

O pedido do usuário define o escopo. Estes guias ajudam a executar esse pedido;
não autorizam ações externas por conta própria.

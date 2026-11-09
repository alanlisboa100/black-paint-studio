# Instalação reproduzível no Termux — 2.3.0

Este guia é para a pessoa ou IA que recebeu o ZIP. Execute no Termux do
celular, com o arquivo `paint_studio.zip` na pasta Download. Não use os caminhos
`/workspace/...` da máquina onde o pacote foi desenvolvido.

## 1. Preparar o acesso ao arquivo

```bash
termux-setup-storage
```

Aceite a permissão no Android. Depois:

```bash
pkg install -y unzip
paint_unpack="$(mktemp -d "$HOME/paint-install.XXXXXX")"
unzip "$HOME/storage/downloads/paint_studio.zip" -d "$paint_unpack"
cd "$paint_unpack/black-paint-studio"
```

Se o arquivo tiver outro nome, use o nome real. Pare e resolva qualquer erro
de extração antes de instalar. Não apague versões anteriores para abrir espaço
sem solicitação do usuário.

## 2. Instalar

```bash
bash install_termux.sh
cd "$HOME/black-paint-studio-2.3.0"
```

O script atualiza o índice do pkg, instala `nodejs-lts`, `python` e
`python-pillow`, copia o pacote para a pasta privada do Termux e executa o
diagnóstico. Não requer `npm install`, NumPy, chave Google nem modelo local.

Se o destino já existe, o instalador recusa substituí-lo. Use a instalação
existente se for esta mesma versão ou escolha outra pasta explicitamente:

```bash
PAINT_INSTALL_DIR="$HOME/black-paint-studio-2.3.0-copia" bash install_termux.sh
```

Isso deve ser executado da pasta extraída que contém o script. Depois entre na
pasta escolhida. Não trate uma falha de pkg como instalação concluída. Corrija
o repositório/conectividade do Termux conforme o erro apresentado; não troque
automaticamente dependências nativas por compilações pip demoradas.

## 3. Verificar a geração local antes do navegador

```bash
python paint_cli.py --doctor
python render_misuki_portrait.py --width 720 --quality economy --output gallery/misuki_teste.png --checkpoint-dir gallery/etapas_teste
```

O diagnóstico deve indicar `png: true`. BlackCore ausente é permitido.
Abra o PNG e confira cabelo preto, olhos vermelhos, dois chifres e rosto sem
vazamentos de sombra. Confira os cinco PNGs na pasta de etapas. Não reporte
sucesso visual sem abrir a imagem.

Para verificar as funções cobertas pelos testes:

```bash
npm test
```

## 4. Abrir o editor

```bash
bash start_termux.sh
```

Abra `http://127.0.0.1:3333` no navegador do mesmo aparelho. Mantenha o Termux
rodando. Escolha **Misuki natural**, **Leve** e **Gerar personagem local**.
O modo detalhado exige mais memória e CPU.

O botão separado da Misuki tenta BlackCore e tem fallback local. Para testar
somente esse fallback, inicie o servidor com:

```bash
MISUKI_FORCE_LOCAL=1 python paint_cli.py --open
```

Se já houver um servidor iniciado pelo CLI deste projeto, pare-o primeiro com
`python paint_cli.py --stop`. Não encerre processos de outros aplicativos.
Para uma porta alternativa: `PORT=3334 python paint_cli.py --open` e abra
`http://127.0.0.1:3334`. Consulte `server.log` quando houver falha.

## 5. Confirmar a instalação no aparelho

Teste pintar, desfazer/refazer, gerar Misuki, salvar PNG e salvar/abrir `.bpaint`.
Confira o destino mostrado ao salvar. Um teste Linux não cobre permissões,
gestos, GPU, segundo plano e layout desse Android. Relate os resultados reais
do aparelho e qualquer erro, sem afirmar que tudo funciona por suposição.

## Texto para entregar ao BlackCore

> Instale o Paint Studio deste ZIP seguindo AGENTS.md e GUIA_INSTALACAO_IA.md.
> Preserve minha instalação anterior e meus desenhos. Use as dependências
> nativas do Termux. Faça o diagnóstico, renderize a Misuki em modo leve com
> cinco checkpoints e confira o PNG. Abra o editor e teste geração e salvamento.
> Leia GUIA_CONSTRUCAO_VISUAL.md antes de alterar o motor. Informe falhas reais
> e não prometa aprendizado automático nem fidelidade medida sem evidência.

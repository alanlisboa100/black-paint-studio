#!/usr/bin/env python3
"""
paint_cli.py - Utilitário de Linha de Comando do Black Paint Studio
Permite iniciar o estúdio, abrir no celular e gerar artes rápidas.
"""
import argparse, json, os, shutil, signal, subprocess, sys, time
from urllib.error import URLError
from urllib.request import urlopen
from pathlib import Path
from termux_compat import scan_media, output_dir

ROOT = Path(__file__).resolve().parent
APP_VERSION = '2.3.0'

def read_server_status(url):
    try:
        with urlopen(url + "/api/status", timeout=1) as response:
            return json.loads(response.read().decode('utf-8'))
    except (URLError, TimeoutError, OSError, ValueError):
        return None

def stop_own_server():
    """Stop only a Node process launched from this exact project directory."""
    target = str(ROOT / 'server.js')
    stopped = False
    try:
        for entry in Path('/proc').iterdir():
            if not entry.name.isdigit() or int(entry.name) == os.getpid():
                continue
            try:
                args = [part.decode('utf-8', 'ignore') for part in (entry / 'cmdline').read_bytes().split(b'\0') if part]
                if args and Path(args[0]).name in ('node','nodejs') and target in args[1:]:
                    os.kill(int(entry.name), signal.SIGTERM)
                    stopped = True
            except (OSError, ValueError):
                continue
    except OSError:
        return False
    return stopped

def start_server_and_open():
    """Inicia o servidor e abre no navegador do Android."""
    print("\033[1;36m🎨 Iniciando Black Paint Studio...\033[0m")
    
    # Reuse an existing instance; detached output avoids a full pipe stalling Node.
    host = os.environ.get('HOST', '127.0.0.1')
    if host in ('0.0.0.0', '::'):
        host = '127.0.0.1'
    port = os.environ.get('PORT', '3333')
    url = f"http://{host}:{port}"
    status = read_server_status(url)
    old_instance = status and status.get('name') == 'Black Paint Studio' and status.get('version') != APP_VERSION
    if old_instance:
        print("\033[1;33m🔄 Atualização detectada; reiniciando apenas o servidor deste projeto...\033[0m")
        if not stop_own_server():
            print(f"Há uma versão antiga ocupando a porta {port}, mas não encontrei o processo deste projeto para reiniciar. Feche a sessão antiga do Paint e tente de novo.", file=sys.stderr)
            return 1
        for _ in range(30):
            if read_server_status(url) is None: break
            time.sleep(.2)
        status=None
    if status and status.get('name') != 'Black Paint Studio':
        print(f'A porta {port} está ocupada por outro aplicativo. Use PORT=3334.', file=sys.stderr)
        return 1
    if status:
        print("\033[1;32m✅ O servidor já está ativo.\033[0m")
    else:
        node = shutil.which("node")
        if not node:
            print("Node.js não foi encontrado. Instale Node.js e tente novamente.", file=sys.stderr)
            return 1
        try:
            with (ROOT / 'server.log').open('a', encoding='utf-8') as log:
                process = subprocess.Popen([node, str(ROOT / "server.js")], stdin=subprocess.DEVNULL,
                                           stdout=log, stderr=log, cwd=ROOT, start_new_session=True)
        except OSError as exc:
            print(f"Não consegui iniciar o servidor: {exc}", file=sys.stderr)
            return 1
        for _ in range(30):
            try:
                ready = read_server_status(url)
                if ready and ready.get('name') == 'Black Paint Studio' and ready.get('version') == APP_VERSION: break
                if process.poll() is not None: break
                time.sleep(.2)
            except (URLError, TimeoutError, OSError): time.sleep(.2)
        else:
            ready = None
        if not ready or ready.get('name') != 'Black Paint Studio' or ready.get('version') != APP_VERSION:
            print(f"O servidor não respondeu em {url}. Confira {ROOT / 'server.log'}.", file=sys.stderr)
            return 1
    print(f"\033[1;32m🚀 Abrindo estúdio no navegador: {url}\033[0m")
    opener = shutil.which("termux-open-url")
    if opener:
        subprocess.run([opener, url], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        print("Abra esse endereço no navegador do aparelho.")
    return 0

def draw_terminal_canvas(width=40, height=20):
    """Gera uma prévia de arte ASCII no terminal."""
    print("\n\033[1;35m╔" + "═" * (width * 2) + "╗\033[0m")
    print(f"\033[1;35m║  \033[1;37mTERMINAL CYBER CANVAS PREVIEW\033[1;35m" + " " * (width * 2 - 32) + "║\033[0m")
    print("\033[1;35m╠" + "═" * (width * 2) + "╣\033[0m")
    for y in range(height):
        sys.stdout.write("\033[1;35m║\033[0m")
        for x in range(width):
            dist = ((x - width/2)**2 + (y - height/2)**2)**0.5
            if dist < height * 0.35:
                r = int(255 * (1 - dist/(height*0.35)))
                g = int(255 * (dist/(height*0.35)))
                sys.stdout.write(f"\033[48;2;{r};{g};255m  \033[0m")
            else:
                sys.stdout.write("  ")
        sys.stdout.write("\033[1;35m║\033[0m\n")
    print("\033[1;35m╚" + "═" * (width * 2) + "╝\033[0m\n")

def generate_portrait(output=None, style='natural', quality='standard', checkpoint_dir=None, expression=None, settings=None):
    """Generate a local CPU portrait study without a remote model."""
    style = 'color' if style == 'oil' else style
    if style not in ('ink', 'color', 'natural', 'stroke', 'misuki', 'ibis', 'cel'):
        print('Use --style stroke, misuki, ink, ibis, color ou natural.', file=sys.stderr)
        return 1
    if style == 'misuki':
        from render_misuki_portrait import render
        default_name = 'misuki_portrait.png'
        label = 'Misuki natural com ficha visual, sombras e mechas curvas'
        from portrait_controls import load_settings
        image = render(width=720 if quality=='economy' else 900, quality=quality, checkpoint_dir=checkpoint_dir, expression=expression, options=load_settings(settings))
    elif style == 'stroke':
        from render_stroke_portrait import render
        default_name = 'personagem_stroke.png'
        label = 'ilustração em fiapos'
        image = render('natural')
    elif style in ('ibis', 'cel'):
        from render_ibis_anime import render
        default_name = 'personagem_ibis_anime.png'
        label = 'anime cel-shading estilo Ibis Paint X'
        image = render(style)
    elif style == 'natural':
        from render_natural_character import render
        default_name = 'personagem_natural.png'
        label = 'natural (luz de janela, massas de óleo)'
        image = render()
    elif style == 'ink':
        from render_ink_character import generate
        default_name = 'personagem_ink.png'
        label = 'line art monocromática'
        image = generate('ink')
    else:
        from render_painted_character import render
        default_name = 'personagem_pintado.png'
        label = 'gótico pintado por massas'
        image = render()
    if output:
        out_file = Path(output).expanduser()
        if not out_file.is_absolute(): out_file = ROOT / out_file
    else:
        out_dir = output_dir()
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / default_name
    out_file.parent.mkdir(parents=True, exist_ok=True)
    image.save(out_file, 'PNG', optimize=True)
    scan_media(out_file)
    print(f'Estudo de personagem {label} (CPU, sem modelo de IA) salvo em: {out_file}')
    return 0

def doctor():
    checks = {'python': sys.version.split()[0], 'node': shutil.which('node'),
              'blackcore_optional': shutil.which(os.environ.get('BLACKCORE_BIN', 'blackcore')),
              'termux_open_url_optional': shutil.which('termux-open-url')}
    try:
        from PIL import Image, __version__
        checks['pillow'] = __version__
        probe = Image.new('RGB', (8, 8), 'red')
        import io
        data = io.BytesIO(); probe.save(data, 'PNG'); data.seek(0)
        Image.open(data).verify()
        checks['png'] = True
    except ImportError:
        checks['pillow'] = None
    try:
        checks['output'] = str(output_dir())
    except OSError as exc:
        checks['output'] = str(exc)
    print(json.dumps(checks, ensure_ascii=False, indent=2))
    return 0 if checks.get('node') and checks.get('pillow') and checks.get('png') else 1


def main():
    parser = argparse.ArgumentParser(prog="paint", description="Black Paint Studio CLI")
    parser.add_argument("--doctor", action="store_true", help="Verifica dependências e pasta de saída")
    parser.add_argument("--stop", action="store_true", help="Para somente o servidor deste projeto")
    parser.add_argument("--open", "-o", action="store_true", help="Inicia e abre no navegador do celular")
    parser.add_argument("--preview", "-p", action="store_true", help="Gera arte rápida no terminal")
    parser.add_argument("--ink-portrait", action="store_true", help="Gera estudo de personagem localmente, sem modelo de IA")
    parser.add_argument("--style", choices=('stroke','misuki','natural','color','ink','ibis','cel'), default='misuki', help="Acabamento do retrato local")
    parser.add_argument("--quality", choices=("economy","standard"), default="standard", help="Qualidade do retrato Misuki")
    parser.add_argument("--checkpoint-dir", help="Pasta para as cinco etapas da Misuki")
    parser.add_argument("--expression", choices=('neutral','soft','happy','sad','angry','surprised'))
    parser.add_argument("--settings", help="JSON de ajustes da Misuki natural")
    parser.add_argument("--output", help="Caminho PNG de saída para --ink-portrait ou --gpu-finish")
    parser.add_argument("--gpu-finish", help="Aplica o passe leve (grão+nitidez) num PNG/JPG e salva")
    args = parser.parse_args()

    if args.doctor:
        return doctor()
    if args.stop:
        print('Servidor encerrado.' if stop_own_server() else 'Nenhum servidor deste projeto encontrado.')
        return 0
    if args.gpu_finish:
        from apply_gpu_finish import apply_finish
        from PIL import Image
        src = Path(args.gpu_finish).expanduser()
        dest = Path(args.output).expanduser() if args.output else src.with_name(src.stem + '_gpu.png')
        dest.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(src) as source:
            apply_finish(source).save(dest, 'PNG', optimize=True)
        scan_media(dest)
        print(f'Acabamento GPU-leve salvo em: {dest}')
        return 0
    if args.ink_portrait:
        if args.style != 'misuki' and (args.expression or args.settings):
            parser.error('--expression e --settings exigem --style misuki')
        return generate_portrait(args.output, args.style, args.quality, args.checkpoint_dir,args.expression,args.settings)
    if args.preview:
        draw_terminal_canvas()
    else:
        return_code = start_server_and_open()
        if return_code:
            raise SystemExit(return_code)

if __name__ == "__main__":
    raise SystemExit(main())

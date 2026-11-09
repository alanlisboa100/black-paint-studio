#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
if ! command -v pkg >/dev/null 2>&1; then
    echo 'Use este instalador dentro do Termux. Em Linux: pip install -r requirements.txt; npm start.' >&2
    exit 1
fi
paint_source_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
paint_install_dir="${PAINT_INSTALL_DIR:-$HOME/black-paint-studio-2.3.0}"
pkg update -y
pkg install -y nodejs-lts python python-pillow
if [[ "${1:-}" == '--extras' ]]; then pkg install -y python-numpy; fi
if [[ "$paint_source_dir" != "$paint_install_dir" ]]; then
    if [[ -e "$paint_install_dir" ]]; then
        echo "Destino já existe: $paint_install_dir. Use a instalação atual ou defina PAINT_INSTALL_DIR com outra pasta." >&2
        exit 1
    fi
    mkdir -p "$paint_install_dir"
    cp -R "$paint_source_dir"/. "$paint_install_dir/"
fi
cd "$paint_install_dir"
python paint_cli.py --doctor
printf '\nInstalado em %s\n' "$paint_install_dir"
printf 'Para abrir: cd "%s" && bash start_termux.sh\n' "$paint_install_dir"
echo 'Para salvar na pasta Download, execute termux-setup-storage e aceite a permissão. Sem ela, os PNGs ficam em gallery/.'

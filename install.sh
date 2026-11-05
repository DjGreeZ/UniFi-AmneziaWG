#!/bin/sh
set -eu
# Shared POSIX-shell presentation. Keep diagnostics separate from progress output.
ui_init() {
    umask 077
    exec 3>&1
    AWG_UI_LOG=$(mktemp "/tmp/awg-$1.XXXXXX")
    AWG_UI_ERR=$(mktemp "/tmp/awg-$1-stderr.XXXXXX")
    AWG_UI_STEP='Подготовка'
    AWG_UI_HANDOFF=0
    AWG_UI_TEMP=''
    AWG_UI_TTY=0
    AWG_UI_RESET='' AWG_UI_BOLD='' AWG_UI_BLUE='' AWG_UI_GREEN='' AWG_UI_RED='' AWG_UI_DIM=''
    if [ -t 3 ] && [ "${TERM:-dumb}" != dumb ]; then
        AWG_UI_TTY=1
        if [ "${NO_COLOR+x}" != x ]; then
            AWG_UI_RESET=$(printf '\033[0m')
            AWG_UI_BOLD=$(printf '\033[1m')
            AWG_UI_BLUE=$(printf '\033[36m')
            AWG_UI_GREEN=$(printf '\033[32m')
            AWG_UI_RED=$(printf '\033[31m')
            AWG_UI_DIM=$(printf '\033[2m')
        fi
    fi
    trap 'ui_exit "$?"' 0
    trap 'exit 130' INT
    trap 'exit 143' TERM
    trap 'exit 129' HUP
    if [ "${AWG_CONSOLE_BANNER:-0}" != 1 ]; then
        printf '\n  %s%sAmneziaWG Client для UniFi · v%s%s\n' "$AWG_UI_BOLD" "$AWG_UI_BLUE" "$2" "$AWG_UI_RESET" >&3
        printf '  %sDeveloped by Roman Tselischev / https://vk.com/greez%s\n\n' "$AWG_UI_DIM" "$AWG_UI_RESET" >&3
        AWG_CONSOLE_BANNER=1
        export AWG_CONSOLE_BANNER
    fi
}

ui_clear() {
    if [ "$AWG_UI_TTY" = 1 ]; then printf '\r\033[2K' >&3; fi
}

ui_exit() {
    ui_code=$1
    trap - 0
    if [ "$ui_code" -ne 0 ] && [ "$AWG_UI_HANDOFF" = 0 ]; then
        ui_error_source=$AWG_UI_LOG
        if [ -s "$AWG_UI_ERR" ]; then
            cat "$AWG_UI_ERR" >>"$AWG_UI_LOG"
            ui_error_source=$AWG_UI_ERR
        fi
        ui_clear
        printf '  %s✕%s %s\n' "$AWG_UI_RED" "$AWG_UI_RESET" "$AWG_UI_STEP" >&3
        if [ "$ui_code" = 130 ] || [ "$ui_code" = 143 ] || [ "$ui_code" = 129 ]; then
            printf '    Операция прервана.\n' >&3
        else
            ui_reason=$(awk 'NF {line=$0} END {print line}' "$ui_error_source")
            [ -z "$ui_reason" ] || printf '    %s\n' "$ui_reason" >&3
        fi
        printf '    Журнал: %s\n\n' "$AWG_UI_LOG" >&3
    fi
    rm -f -- "$AWG_UI_ERR"
    if [ -n "$AWG_UI_TEMP" ]; then rm -rf -- "$AWG_UI_TEMP"; fi
    exit "$ui_code"
}

# Call directly under set -e, never as an if/|| condition: failed commands in
# shell-function stages must terminate the operation before any success message.
ui_capture() {
    "$@" >>"$AWG_UI_LOG" 2>"$AWG_UI_ERR"
    cat "$AWG_UI_ERR" >>"$AWG_UI_LOG"
    : >"$AWG_UI_ERR"
}

ui_run() {
    AWG_UI_STEP=$1
    shift
    if [ "$AWG_UI_TTY" = 1 ]; then
        printf '  %s›%s %s…' "$AWG_UI_BLUE" "$AWG_UI_RESET" "$AWG_UI_STEP" >&3
    fi
    ui_capture "$@"
    ui_clear
    printf '  %s✓%s %s\n' "$AWG_UI_GREEN" "$AWG_UI_RESET" "$AWG_UI_STEP" >&3
}

ui_success() {
    printf '\n  %s%s%s%s\n' "$AWG_UI_BOLD" "$AWG_UI_GREEN" "$1" "$AWG_UI_RESET" >&3
}

ui_note() {
    printf '  %s\n' "$1" >&3
}

ui_init install 0.3.1
BASE=https://raw.githubusercontent.com/DjGreeZ/UniFi-AmneziaWG/v0.3.1
FILE=AmneziaWG-UniFi-v0.3.1.run
AWG_UI_TEMP=$(mktemp -d /tmp/awg-download.XXXXXX)
cd "$AWG_UI_TEMP"
download_package() {
 curl -fsSL --connect-timeout 15 --max-time 300 "$BASE/$FILE" -o "$FILE"
 curl -fsSL --connect-timeout 15 --max-time 60 "$BASE/AmneziaWG-UniFi-v0.3.1.sha256" -o checksums
 sha256sum -c checksums
}
ui_run 'Загрузка пакета' download_package
AWG_UI_HANDOFF=1
sh "$FILE"

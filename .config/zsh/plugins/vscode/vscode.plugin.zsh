if [[ $('uname') == 'Linux' ]]; then
    local _vscode_linux_paths > /dev/null 2>&1
    _vscode_linux_paths=(
        "$HOME/bin/code-insiders"
        "$HOME/bin/code"
        "/usr/local/bin/code-insiders"
        "/usr/local/bin/code"
        "/opt/vscode/code-insiders"
        "/opt/vscode/code"
        "/usr/bin/code-insiders"
        "/usr/bin/code"
    )
    for _vscode_path in $_vscode_linux_paths; do
        if [[ -a $_vscode_path ]]; then
            vs_run() { $_vscode_path $@ >/dev/null 2>&1 &| }
            vs_run_sudo() {sudo $_vscode_path $@ >/dev/null 2>&1}
            alias svs=vs_run_sudo
            alias vs=vs_run
            break
        fi
    done

elif  [[ "$OSTYPE" = darwin* ]]; then
    local _vscode_darwin_paths > /dev/null 2>&1
    _vscode_darwin_paths=(
        "$HOME/Applications/Visual Studio Code - Insiders.app/Contents/Resources/app/bin/code"
        "$HOME/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"
        "/usr/local/bin/code"
        "/Applications/Visual Studio Code - Insiders.app/Contents/Resources/app/bin/code"
        "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"
    )
    for _vscode_path in $_vscode_darwin_paths; do
        if [[ -a $_vscode_path ]]; then
            vs_run () { "$_vscode_path" $* }
            vs_run_sudo () {sudo "$_vscode_path" $* }
            alias svs=vs_run_sudo
            alias vs=vs_run
            break
        fi
    done

elif [[ "$OSTYPE" = 'cygwin' ]]; then
    local _vscode_cygwin_paths > /dev/null 2>&1
    _vscode_cygwin_paths=(
        "$(cygpath $ProgramW6432/Microsoft\ VS\ Code\ Insiders)/bin/code-insiders.cmd"
        "$(cygpath $ProgramW6432/Microsoft\ VS\ Code)/bin/code.cmd"
        "$(cygpath $ProgramW6432/Visual\ Studio\ Code)/code.exe"
    )
    for _vscode_path in $_vscode_cygwin_paths; do
        if [[ -a $_vscode_path ]]; then
            vs_run () { "$_vscode_path" $* }
            alias vs=vs_run
            break
        fi
    done

fi

alias vst='vs .'
alias vsa='vs -a'
alias vsta='vst -a'
alias svsa='svs -a'
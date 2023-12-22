# Path to your oh-my-zsh installation.
export ZSH="$HOME/.oh-my-zsh"

# Which plugins would you like to load?
# Standard plugins can be found in $ZSH/plugins/
# Custom plugins may be added to $ZSH_CUSTOM/plugins/
# Example format: plugins=(rails git textmate ruby lighthouse)
# Add wisely, as too many plugins slow down shell startup.
plugins=(
git
zsh-autosuggestions
zsh-syntax-highlighting
sudo
z
git-open
dash
vi-mode
vscode
sublime
fzf
)

source $ZSH/oh-my-zsh.sh
source ~/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
source ~/.bashrc

alias mysql=/usr/local/mysql/bin/mysql
alias ls='lsd'
alias vim='nvim'
alias ra='ranger'
alias raj='ranger --choosedir=$HOME/.rangerdir; LASTDIR=`cat $HOME/.rangerdir`; cd "$LASTDIR"'
alias lt="ls --tree"
alias reload="source ~/.zshrc"
alias cl="clear"

# ranger 配置
export RANGER_LOAD_DEFAULT_RC=FALSE
# 使用,补全历史记录
bindkey ',' autosuggest-accept

bindkey '^h'  backward-char         #control+h：向左移动一个单词
bindkey '^l'  forward-char          #control+l：向右移动一个单词
bindkey '^k'  up-line-or-history    #control+k：向上翻看历史记录
bindkey '^j'  down-line-or-history  #control+j：向下翻看历史记录

# vi-mode 使用nvim作为默认打开工具
EDITOR=nvim 
export EDITOR

export FZF_DEFAULT_OPTS=" \
--height 80% \
--reverse \
--border \
--color=bg+:#363a4f,bg:#24273a,spinner:#f4dbd6,hl:#ed8796 \
--color=fg:#cad3f5,header:#ed8796,info:#c6a0f6,pointer:#f4dbd6 \
--color=marker:#f4dbd6,fg+:#cad3f5,prompt:#c6a0f6,hl+:#ed8796"

# starship theme
eval "$(starship init zsh)"

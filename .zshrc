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
git-open
vi-mode
fzf
)

source $ZSH/oh-my-zsh.sh
source ~/.bashrc

alias ls='lsd'
alias vim='nvim'
alias ra='ranger'
alias raj='ranger --choosedir=$HOME/.rangerdir; LASTDIR=`cat $HOME/.rangerdir`; cd "$LASTDIR"'
alias lt="ls --tree"
alias reload="source ~/.zshrc"
alias cl="clear"
alias lg="lazygit"

# ranger icon config
export RANGER_LOAD_DEFAULT_RC=FALSE
# use ',' to accept autosuggestion
bindkey ',' autosuggest-accept

# use nvim as default editor
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

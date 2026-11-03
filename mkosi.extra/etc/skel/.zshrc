# ~/.zshrc — Netmask OS

# history
HISTFILE=~/.zsh_history
HISTSIZE=10000
SAVEHIST=10000
setopt share_history hist_ignore_dups hist_reduce_blanks
setopt autocd correct

# completion
autoload -Uz compinit && compinit -d ~/.zcompdump

# prompt:  netmask ❯
PROMPT='%F{cyan}netmask%f %(?.%F{cyan}.%F{red})❯%f '
RPROMPT='%F{8}%~%f'

# aliases
alias ls='ls --color=auto'
alias ll='ls -lahF'
alias grep='grep --color=auto'
alias df='df -h'
alias free='free -h'

# editor
export EDITOR=nano
export VISUAL=nano

umask 022

# ~/.zprofile — Netmask OS
# Auto-start the desktop session on tty1 (the autologin console).
if [ -z "$DISPLAY" ] && [ -z "$WAYLAND_DISPLAY" ] && [ -z "$SSH_CONNECTION" ] \
   && [ "${XDG_VTNR:-0}" = "1" ]; then
    exec startx -- -keeptty > "$HOME/.startx.log" 2>&1
fi

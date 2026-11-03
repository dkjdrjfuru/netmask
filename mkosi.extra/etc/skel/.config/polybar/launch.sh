#!/usr/bin/env bash
# Netmask OS — (re)start polybar. Called by i3 via `exec_always`,
# so kill any previous instance first (i3 restarts re-run this).
killall -q polybar
while pgrep -u "$USER" -x polybar >/dev/null 2>&1; do
    sleep 0.2
done

polybar --reload netmask \
    -c "$HOME/.config/polybar/config.ini" \
    >/tmp/polybar-netmask.log 2>&1 &
disown

echo "polybar started (log: /tmp/polybar-netmask.log)"

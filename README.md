# Netmask OS — minimal ISO

**Netmask OS** is a minimal, live-bootable Debian 12 (bookworm) desktop in a single ISO,
built with **one command** (`mkosi build`). It ships exactly what it says on the tin:

| # | Feature | Implementation |
|---|---------|----------------|
| 1 | Wallpaper | `netmask_logo.png` (1920×1080, brand colors) via `feh`, set at i3 startup |
| 2 | Bottom taskbar | `polybar`: logo, workspaces, CPU/MEM, network up/down, clock, `discord.gg/netmask` |
| 3 | Window manager | `i3-wm` 4.22 — i3-gaps features are **merged upstream** since 4.22 (gaps, smart borders) |
| 4 | Terminal | `kitty` + **FiraCode Nerd Font** + netmask color scheme |
| 5 | Auto-login | `getty@tty1` auto-logins `netmask` (no password) → `startx` → i3 |
| 6 | Bootable | Hybrid ISO: **BIOS + UEFI** (El Torito via `grub-mkrescue`), tested target: VirtualBox |

Brand: bg `#0D0D1A` · accent `#00D9FF` · accent2 `#E94560` · Discord `discord.gg/netmask`

---

## Requirements

* Build host: **Ubuntu 22.04+ / Debian 12+** (x86_64), ~10 GB free disk, internet access.
* **mkosi ≥ 24** (tested with mkosi 27.1). Ubuntu 22.04's `apt install mkosi` ships an
  ancient 13.x — install a current mkosi via **pipx** instead (below).
  On Ubuntu 24.10+ / Debian 13, `apt install mkosi` is new enough.
* ISO tools on the host: `squashfs-tools xorriso grub-pc-bin grub-efi-amd64-bin mtools`.
* When building Debian images **from Ubuntu**, also install `debian-archive-keyring`
  (mkosi verifies the Debian mirror signature with the host keyrings).

## Quick start

```bash
# 1) mkosi (Ubuntu 22.04/24.04 — via pipx; skip on Debian 13 / Ubuntu 24.10+ which have new enough apt versions)
sudo apt update
sudo apt install -y pipx
pipx install mkosi
export PATH="$HOME/.local/bin:$PATH"

# 2) host tools for the ISO stage
sudo apt install -y squashfs-tools xorriso grub-pc-bin grub-efi-amd64-bin mtools debian-archive-keyring

# 3) build (single command, reproducible)
mkosi build          # on Ubuntu 24.04+ use:  sudo mkosi build
```

> **Why `sudo` on 24.04?** Ubuntu 24.04 restricts unprivileged user namespaces via AppArmor
> (`apparmor_restrict_unprivileged_userns=1`), which mkosi normally uses to build rootless.
> On Ubuntu 22.04, 24.10+ and Debian 12/13, plain `mkosi build` works without root.

**Output:**

```
output/netmask-os-minimal.iso      ← the bootable ISO (BIOS + UEFI)
output/netmask-os-rootfs/          ← unpacked rootfs (kept for `mkosi shell` debugging)
```

Rebuilds are incremental (package cache in `mkosi.cache/`). Clean everything: `mkosi clean`.

---

## Boot it in VirtualBox (UEFI + BIOS)

1. **Machine → New** → Type *Linux*, Version *Debian (64-bit)*.
2. Memory **≥ 2048 MB** (the live overlay runs in RAM), 2 CPUs recommended.
3. Hard disk: **Do not add a virtual hard disk** (it's a live system).
4. Settings → Storage: attach `netmask-os-minimal.iso` to the **optical drive**.
5. Firmware:
   * **BIOS boot** → leave *System → Motherboard → Extended Features → Enable EFI* **off**.
   * **UEFI boot** → tick *Enable EFI*. Keep *Enable Secure Boot* **unchecked**
     (VirtualBox's default; the ISO's grub is unsigned).
6. Video memory ≥ 32 MB. Network: NAT (default) — Netmask OS gets DHCP automatically.
7. Start. The GRUB menu shows for 3 s, then boots to the desktop automatically.

You land on i3 with the netmask wallpaper and the bottom polybar — logged in as
`netmask`, no password ever asked.

### Key bindings (Super = Windows/Cmd key)

| Keys | Action |
|------|--------|
| `Super` + `Enter` | kitty terminal |
| `Super` + `1…9,0` | switch workspace (polybar mirrors it) |
| `Super` + `Shift` + `1…0` | move window to workspace |
| `Super` + `H/J/K/L` or arrows | focus (vim keys) |
| `Super` + `Shift` + `H/J/K/L` | move window |
| `Super` + `F` | fullscreen |
| `Super` + `V` / `B` | split vertical / horizontal |
| `Super` + `E` / `S` / `W` | layout: toggle / stacking / tabbed |
| `Super` + `Shift` + `Space` | floating toggle |
| `Super` + `R` | resize mode (h/j/k/l, Esc to exit) |
| `Super` + `Shift` + `Q` | close window |
| `Super` + `Shift` + `C` / `R` | reload config / restart i3 |
| `Super` + `Shift` + `E` | exit session (confirm dialog) |

---

## How the build works

```
mkosi build
 ├─ 1. [Distribution] Debian 12 rootfs via apt (Packages= below), Architecture x86-64
 ├─ 2. mkosi.extra/            → overlay copied onto the rootfs
 │      etc/skel/…             i3 / polybar / kitty / zsh / xinitrc configs (→ /home/netmask)
 │      etc/systemd/…/autologin.conf   getty@tty1 --autologin netmask
 │      etc/sudoers.d/netmask  passwordless sudo
 │      usr/share/backgrounds/netmask/netmask_logo.png
 │      usr/share/fonts/truetype/netmask/FiraCodeNerdFont-*.ttf
 ├─ 3. mkosi.finalize.chroot   → inside the image: create user, enable NM + getty,
 │      truncate machine-id (live), rebuild initramfs with live-boot hooks
 ├─ 4. mkosi.postoutput        → on the host: mksquashfs (zstd) + kernel + initrd
 │      + grub.cfg → grub-mkrescue hybrid ISO (BIOS El Torito + UEFI)
 └─ 5. output/netmask-os-minimal.iso
```

### Package list (and why — nothing extra)

| Package | Role |
|---------|------|
| `linux-image-amd64`, `live-boot` | kernel + live initramfs (mounts the squashfs with a RAM overlay) |
| `systemd`, `dbus`, `dbus-user-session`, `libpam-systemd` | init + session/logind plumbing for X |
| `i3-wm` | i3 4.22 = i3-gaps (upstream merge) |
| `polybar` | the bottom bar |
| `kitty` | terminal |
| `feh` | wallpaper |
| `xinit`, `xauth`, `xserver-xorg-core`, `xserver-xorg-input-libinput`, `xserver-xorg-video-{fbdev,vesa}`, `x11-xserver-utils` | smallest X stack that runs on VirtualBox (vboxvideo KMS + modesetting; vesa/fbdev fallbacks) |
| `network-manager` | DHCP on NAT so the network module has something to show |
| `zsh`, `nano`, `less`, `sudo` | shell + minimum viable CLI comfort |
| `fonts-firacode`, `fonts-noto-color-emoji` | Fira Code + emoji; **FiraCode Nerd Font** TTFs are vendored (see licenses below) |

## Customization

* **Wallpaper** — replace
  `mkosi.extra/usr/share/backgrounds/netmask/netmask_logo.png` (any PNG; it is
  drawn with `feh --bg-fill`). The shipped one is generated by
  `scripts/make_wallpaper.py` (pure Pillow, brand colors hardcoded).
* **Colors** — `#0D0D1A / #00D9FF / #E94560` live in exactly three places:
  `mkosi.extra/etc/skel/.config/polybar/config.ini` (`[colors]`),
  `mkosi.extra/etc/skel/.config/kitty/kitty.conf`, and the `client.*` lines in
  `mkosi.extra/etc/skel/.config/i3/config`.
* **Bar modules** — edit `modules-left` / `modules-right` in `polybar/config.ini`.
* Rebuild afterwards with `mkosi build`.

## Reproducibility

* The whole image is defined by `mkosi.conf` + `mkosi.extra/` + two scripts — no
  state, no hand-patching. Rebuilds fetch the same Debian 12 suite from the mirror.
* The ISO stage pins `SOURCE_DATE_EPOCH` for xorriso and normalizes squashfs
  ownership (`-all-root`), so ISOs are byte-reproducible **up to** the mtimes of
  packages downloaded from the mirror (best effort, as mkosi itself).

## Troubleshooting

* **Black screen / no desktop** — switch to tty2 (`Ctrl+Alt+F2`; log in as `netmask`,
  no password) and check `~/.startx.log` and `~/.local/share/xorg/Xorg.0.log`.
  i3 config errors are shown by i3 on tty1.
* **Resolution stuck at 800×600** — the default grub entry forces
  `video=1920x1080`. Boot the *verbose* entry and use `xrandr`, or edit
  `grub.cfg` in `mkosi.postoutput` and rebuild.
* **No icons in polybar** — the Nerd Font ships in the image; check
  `fc-list | grep -i "FiraCode Nerd"` inside the ISO (tty2). The glyphs used are
  verified against the vendored font: `` (U+F1023), `` (U+F4BC), `` (U+EFC5),
  `` (U+EF44), `` (U+F0150), `` (U+F1FF).
* **Secure Boot** — VirtualBox's EFI does not enforce SB by default; if you turn
  it on manually the unsigned grub in this ISO will not load.
* **Disk full on build** — the build needs ~10 GB (`mkosi.cache` + `output/`).
* **Inspect the rootfs without booting**: `mkosi shell` (interactive chroot),
  then `mkosi clean` when done.

## Licenses

* Project files (configs, scripts): MIT — do whatever, attribution appreciated.
* `FiraCodeNerdFont-*.ttf`: Fira Code (SIL OFL 1.1) patched by Nerd Fonts (MIT) —
  license shipped at `mkosi.extra/usr/share/fonts/truetype/netmask/LICENSE`
  and `assets/FIRACODE_NERD_FONT_LICENSE`.
* `fonts-noto-color-emoji`, `fonts-firacode`: Debian packages, SIL OFL.
* `netmask_logo.png` / `netmask_icon.png`: generated for Netmask OS, CC0.

---

Project layout:

```
netmask-os/
├── mkosi.conf                  # Debian 12, x86-64, package list, hostname/locale
├── mkosi.finalize.chroot       # in-image setup (user, services, live hygiene)
├── mkosi.postoutput            # squashfs + grub-mkrescue → netmask-os-minimal.iso
├── mkosi.extra/                # files copied into the image (overlay tree)
│   ├── etc/{skel,systemd,sudoers.d,hosts,environment,default}
│   └── usr/share/{backgrounds/netmask,fonts/truetype/netmask}
├── assets/
│   ├── netmask_icon.png        # 256×256 emblem
│   └── FIRACODE_NERD_FONT_LICENSE
└── .gitignore
```

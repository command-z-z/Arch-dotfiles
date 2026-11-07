-- Hyprland 0.55+ Lua configuration, migrated from hyprland.conf.
-- Documentation: https://wiki.hypr.land/0.56.0/Configuring/
-- The original hyprland.conf is available in Git history.

hl.monitor({ output = "HDMI-A-1", mode = "2560x1440@60", position = "0x0", scale = 1, transform = 3 })
hl.monitor({ output = "DP-1", mode = "3840x2160@60", position = "auto", scale = 1 })

-- Start these only when the compositor starts, not on config reload.
hl.on("hyprland.start", function ()
    hl.exec_cmd("fcitx5 & hyprpaper")
    hl.exec_cmd("mihomo")
    hl.exec_cmd("swaync")
    hl.exec_cmd("hyprctl setcursor catppuccin-frappe-dark-cursors 48")
    hl.exec_cmd("waybar")
    hl.exec_cmd("eww daemon")
    hl.exec_cmd("playerctld daemon")
    hl.exec_cmd("bash ~/.config/hypr/scripts/openrgb.sh")
    hl.exec_cmd("systemctl --user import-environment WAYLAND_DISPLAY XDG_CURRENT_DESKTOP XDG_SESSION_TYPE XDG_RUNTIME_DIR")
    hl.exec_cmd("hypridle")
    hl.exec_cmd("hyprlauncher -d")
    hl.exec_cmd("echo \"Xft.dpi: 192\" | xrdb -merge")
end)

hl.config({
    input = {
        kb_layout = "us",
        kb_variant = "",
        kb_model = "",
        kb_options = "caps:super",
        kb_rules = "",
        follow_mouse = 1,
        sensitivity = 0.0,
        touchpad = { natural_scroll = true, clickfinger_behavior = true },
    },
    cursor = { no_hardware_cursors = true },
    general = {
        gaps_in = 8,
        gaps_out = 20,
        border_size = 4,
        col = { active_border = 0xffcad3f5, inactive_border = 0xff826fa1 },
        layout = "dwindle",
    },
    decoration = {
        rounding = 11,
        blur = { enabled = true, size = 3, passes = 1, new_optimizations = true },
        active_opacity = 0.95,
        inactive_opacity = 0.90,
        shadow = { enabled = true, range = 4, render_power = 3, color = "rgba(1a1a1aee)" },
    },
    animations = { enabled = true },
    dwindle = { preserve_split = true },
    master = { new_status = "master" },
})

hl.curve("myBezier", { type = "bezier", points = { {0.05, 0.9}, {0.1, 1.05} } })
hl.animation({ leaf = "windows", enabled = true, speed = 7, bezier = "myBezier" })
hl.animation({ leaf = "windowsOut", enabled = true, speed = 7, bezier = "default", style = "popin 80%" })
hl.animation({ leaf = "border", enabled = true, speed = 10, bezier = "default" })
hl.animation({ leaf = "borderangle", enabled = true, speed = 8, bezier = "default" })
hl.animation({ leaf = "fade", enabled = true, speed = 7, bezier = "default" })
hl.animation({ leaf = "workspaces", enabled = true, speed = 6, bezier = "default" })

hl.device({ name = "epic-mouse-v1", sensitivity = -0.5 })

-- Application workspaces.
hl.window_rule({ name = "app-workspace-120", match = { class = "^(kitty)$" }, workspace = "1" })
hl.window_rule({ name = "app-workspace-121", match = { class = "^(google-chrome)$" }, workspace = "2" })
hl.window_rule({ name = "app-workspace-122", match = { class = "^(zathura)$" }, workspace = "3" })
hl.window_rule({ name = "app-workspace-123", match = { class = "^(Spotify)$" }, workspace = "4" })
hl.window_rule({ name = "app-workspace-124", match = { title = "^(Notion Desktop)$" }, workspace = "5" })
hl.window_rule({ name = "app-workspace-125", match = { class = "^(QQ)$" }, workspace = "6" })
hl.window_rule({ name = "app-workspace-126", match = { class = "^(Weixin)$" }, workspace = "6" })

-- Keybindings.
local mainMod = "SUPER"
local scripts = os.getenv("HOME") .. "/.config/hypr/scripts"

hl.bind(mainMod .. " + " .. "K", hl.dsp.exec_cmd("kitty"))
hl.bind(mainMod .. " + " .. "R", hl.dsp.exec_cmd("kitty ranger"))
hl.bind(mainMod .. " + " .. "V", hl.dsp.exec_cmd("kitty nvim"))
hl.bind(mainMod .. " + " .. "G", hl.dsp.exec_cmd("google-chrome-stable"))
hl.bind(mainMod .. " + " .. "SPACE", hl.dsp.exec_cmd("hyprlauncher"))
hl.bind(mainMod .. " + " .. "B", hl.dsp.exec_cmd("killall -SIGUSR1 waybar"))
hl.bind(mainMod .. " + " .. "Q", hl.dsp.exec_cmd("linuxqq"))
hl.bind(mainMod .. " + " .. "W", hl.dsp.exec_cmd("wechat-universal"))
hl.bind(mainMod .. " + " .. "S", hl.dsp.exec_cmd("spotify"))
hl.bind(mainMod .. " + " .. "N", hl.dsp.exec_cmd("notion-app-enhanced"))
hl.bind(mainMod .. " + " .. "L", hl.dsp.exec_cmd("hyprlock"))
hl.bind(mainMod .. " + " .. "D", hl.dsp.window.close())
hl.bind(mainMod .. " + " .. "M", hl.dsp.exit())
hl.bind("ALT" .. " + " .. "SHIFT" .. " + " .. "0", hl.dsp.exec_cmd(scripts .. "/snapshot.sh"))
hl.bind("XF86AudioRaiseVolume", hl.dsp.exec_cmd(scripts .. "/volume.sh --inc"))
hl.bind("XF86AudioLowerVolume", hl.dsp.exec_cmd(scripts .. "/volume.sh --dec"))
hl.bind("XF86AudioMute", hl.dsp.exec_cmd(scripts .. "/volume.sh --toggle"))
hl.bind("XF86KbdBrightnessUp", hl.dsp.exec_cmd(scripts .. "/light-on.sh"))
hl.bind("XF86KbdBrightnessDown", hl.dsp.exec_cmd(scripts .. "/light-off.sh"))
hl.bind(mainMod .. " + " .. "SHIFT" .. " + " .. "H", hl.dsp.focus({ direction = "left" }))
hl.bind(mainMod .. " + " .. "SHIFT" .. " + " .. "L", hl.dsp.focus({ direction = "right" }))
hl.bind(mainMod .. " + " .. "SHIFT" .. " + " .. "K", hl.dsp.focus({ direction = "up" }))
hl.bind(mainMod .. " + " .. "SHIFT" .. " + " .. "J", hl.dsp.focus({ direction = "down" }))
hl.bind(mainMod .. " + " .. "CTRL" .. " + " .. "H", hl.dsp.window.move({ direction = "left" }))
hl.bind(mainMod .. " + " .. "CTRL" .. " + " .. "L", hl.dsp.window.move({ direction = "right" }))
hl.bind(mainMod .. " + " .. "CTRL" .. " + " .. "K", hl.dsp.window.move({ direction = "up" }))
hl.bind(mainMod .. " + " .. "CTRL" .. " + " .. "J", hl.dsp.window.move({ direction = "down" }))
hl.bind(mainMod .. " + " .. "1", hl.dsp.focus({ workspace = 1 }))
hl.bind(mainMod .. " + " .. "2", hl.dsp.focus({ workspace = 2 }))
hl.bind(mainMod .. " + " .. "3", hl.dsp.focus({ workspace = 3 }))
hl.bind(mainMod .. " + " .. "4", hl.dsp.focus({ workspace = 4 }))
hl.bind(mainMod .. " + " .. "5", hl.dsp.focus({ workspace = 5 }))
hl.bind(mainMod .. " + " .. "6", hl.dsp.focus({ workspace = 6 }))
hl.bind("ALT" .. " + " .. "SHIFT" .. " + " .. "1", hl.dsp.window.move({ workspace = 1, follow = true }))
hl.bind("ALT" .. " + " .. "SHIFT" .. " + " .. "2", hl.dsp.window.move({ workspace = 2, follow = true }))
hl.bind("ALT" .. " + " .. "SHIFT" .. " + " .. "3", hl.dsp.window.move({ workspace = 3, follow = true }))
hl.bind("ALT" .. " + " .. "SHIFT" .. " + " .. "4", hl.dsp.window.move({ workspace = 4, follow = true }))
hl.bind("ALT" .. " + " .. "SHIFT" .. " + " .. "5", hl.dsp.window.move({ workspace = 5, follow = true }))
hl.bind("ALT" .. " + " .. "SHIFT" .. " + " .. "6", hl.dsp.window.move({ workspace = 6, follow = true }))
hl.bind(mainMod .. " + " .. "T", hl.dsp.window.float({ action = "toggle" }))
hl.bind(mainMod .. " + " .. "F", hl.dsp.window.fullscreen({ mode = "fullscreen", action = "toggle" }))
hl.bind(mainMod .. " + " .. "mouse:272", hl.dsp.window.drag(), { mouse = true })
hl.bind(mainMod .. " + " .. "mouse:273", hl.dsp.window.resize(), { mouse = true })

-- G304 side buttons: rear pastes, front copies.
-- Kitty uses Ctrl+Shift+C/V so copying never sends an interrupt.
local function mouse_clipboard_shortcut(key)
    local window = hl.get_active_window()
    if window == nil then
        return
    end
    local mods = window.class == "kitty" and "CTRL + SHIFT" or "CTRL"
    hl.dispatch(hl.dsp.send_shortcut({ mods = mods, key = key }))
end

hl.bind("mouse:275", function() mouse_clipboard_shortcut("V") end,
    { description = "Mouse side button: paste" })
hl.bind("mouse:276", function() mouse_clipboard_shortcut("C") end,
    { description = "Mouse side button: copy" })

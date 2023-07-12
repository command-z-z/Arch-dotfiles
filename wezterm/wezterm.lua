local wt = require("wezterm")

return {
    enable_tab_bar = false,
    -- font = wt.font("Hack Nerd Font", { weight = 325 }),
    font = wt.font("Operator Mono Lig", { weight = 325 }),
    -- font = wt.font("Fira Code", { weight = 325 }),
    font_size = 25,
    color_scheme = "Catppuccin Frappe",
    custom_block_glyphs = true,
    window_decorations = "RESIZE",
    window_close_confirmation = "NeverPrompt",
    cursor_blink_ease_in = "Constant",
    cursor_blink_ease_out = "Constant",
    enable_csi_u_key_encoding = true
}

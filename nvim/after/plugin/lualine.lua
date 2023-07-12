local statue, lualine = pcall(require, "lualine")
if not statue then
	return
end

local lspStatus = {
	function()
		local msg = "No Active Lsp"
		local buf_ft = vim.api.nvim_buf_get_option(0, "filetype")
		local clients = vim.lsp.get_active_clients()
		if next(clients) == nil then
			return msg
		end
		for _, client in ipairs(clients) do
			local filetypes = client.config.filetypes
			if filetypes and vim.fn.index(filetypes, buf_ft) ~= -1 then
				return client.name
			end
		end
		return msg
	end,
    color = "StatusLine",
    separator = { left = "", right = "" },
}

local layout = {
	lualine_a = {
		{
			function()
				return ""
			end,
			separator = { left = "", right = "" },
		},
	},
	lualine_b = {
		{
			"filetype",
			icon_only = true,
			colored = true,
			color = "StatusLine",
		},
		{
			"filename",
			color = "StatusLine",
		},
		{
			"branch",
			icon = "",
			color = { bg = "#292c3c", fg = "#c296eb" },
		},
		{
			"diff",
			colored = true,
			symbols = {
				added = "",
				modified = "",
				removed = "",
			},
			color = "StatusLine",
		},
	},
	lualine_c = {
		{
			function()
				return ""
			end,
			color = { bg = "#8FCDA9", fg = "#121319" },
			separator = { left = "", right = "" },
		},
		{
			"diagnostics",
			sources = { "nvim_lsp" },
			sections = {
				"info",
				"error",
				"warn",
				"hint",
			},
			diagnostic_color = {
				error = { fg = "#820e2d", bg = "#0f111a" },
				warn = { fg = "DiagnosticWarn", bg = "#0f111a" },
				info = { fg = "DiaganosticInfo", bg = "#0f111a" },
				hint = { fg = "#92CDE7", bg = "#0f111a" },
			},
			colored = true,
			update_in_insert = true,
			always_visible = false,
			symbols = {
				error = " ",
				warn = " ",
				hint = " ",
				info = " ",
			},
			separator = { left = "", right = "" },
		},
	},
	lualine_x = { lspStatus },
	lualine_y = {},
	lualine_z = {
		{
			"filesize",
			color = "StatusLine",
		},
		{
			function()
				return ""
			end,
			separator = { left = "", right = "" },
		},
		{
			"progress",
			color = "StatusLine",
		},
		{
			function()
				return ""
			end,
			separator = { left = "", right = "" },
		},
		{
			"location",
			color = "StatusLine",
		},
		{
			function()
				return ""
			end,
			separator = { left = "", right = "" },
		},
	},
}

local no_layout = {
	lualine_a = {},
	lualine_b = {},
	lualine_c = {},
	lualine_x = {},
	lualine_y = {},
	lualine_z = {},
}

lualine.setup({
	sections = layout,
	inactive_sections = no_layout,
	options = {
		icons_enabled = true,
		globalstatus = false,
		disabled_filetypes = { "alpha", "dashboard", "NvimTree", "Outline"},
		always_divide_middle = true,
		theme = "catppuccin",
	},
})


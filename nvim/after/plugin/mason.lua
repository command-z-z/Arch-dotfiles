local statue, mason = pcall(require, "mason")
if not statue then
	return
end

mason.setup({
  automatic_installation = true,

  ui = {
    icons = {
      package_installed = " ",
      package_pending = " ",
      package_uninstalled = " ﮊ",
    },
  },
})


local statue_, mason_lspconfig = pcall(require, "mason-lspconfig")
if not statue_ then
    return
end

mason_lspconfig.setup({
    ensure_installed = { "pyright", "clangd", "lua_ls"},
})


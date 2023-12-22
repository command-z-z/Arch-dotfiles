--提示信息自定义图标
-- icon
vim.lsp.handlers["textDocument/publishDiagnostics"] = vim.lsp.with(
  vim.lsp.diagnostic.on_publish_diagnostics, {
    underline = true,
    -- This sets the spacing and the prefix, obviously.
    virtual_text = {
      spacing = 4,
      prefix = ''
      -- prefix = '🔥',
    }
  }
)
--[[ vim.diagnostic.config({
  signs = true,
  update_in_insert = false,
  underline = true,
  severity_sort = true,
  virtual_text = {
    prefix = '🔥',
    source = true,
  },
}) ]]


local signs = {
    { name = "DiagnosticSignError", text = "" },
    { name = "DiagnosticSignWarn", text = "" },
    { name = "DiagnosticSignHint", text = "" },
    { name = "DiagnosticSignInfo", text = "" },
}

for _, sign in ipairs(signs) do
    vim.fn.sign_define(sign.name, { texthl = sign.name, text = sign.text, numhl = "" })
end

-- config language servers
local capabilities = vim.lsp.protocol.make_client_capabilities()
local servers = { "pyright", "clangd", "lua_ls" }

for _, lsp in ipairs(servers) do
    require("lspconfig")[lsp].setup {
        on_attach = on_attach,
        capabilities = capabilities,
    }
end


local ok, autopairs = pcall(require, "nvim-autopairs")
if (not ok) then
    return
end

autopairs.setup({
  disable_filetype = { "TelescopePrompt" , "vim" },
})

local status, cmp = pcall(require, 'cmp')
if not status then
    vim.cmd([[packadd nvim-cmp]])
    cmp = require('cmp')
end

local cmp_autopairs = require('nvim-autopairs.completion.cmp')
cmp.event:on(
  'confirm_done',
  cmp_autopairs.on_confirm_done()
)


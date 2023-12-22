local status, neogen = pcall(require, "neogen")
if (not status) then
    return
end

neogen.setup({
  enabled = true,
  languages = {
    python = {
      template = {
        annotation_convention = "google_docstrings",
        -- annotation_convention = "numpydoc",
        -- annotation_convention = "reST",
      },
    },
  },
})
neogen.generate(
  {
    type = "func" -- the annotation type to generate. Currently supported: func, class, type, file
  }
)

local opts = {noremap = true, silent = true}

vim.api.nvim_set_keymap("n", "<Leader>nf", ":lua require('neogen').generate({ type = 'func' })<CR>", opts)
vim.api.nvim_set_keymap("n", "<Leader>nc", ":lua require('neogen').generate({ type = 'class' })<CR>", opts)

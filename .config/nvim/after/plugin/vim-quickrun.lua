vim.g.quickrun_config = {_ = {outputter = "message"}}

local opts = { silent = true, noremap = true}
vim.api.nvim_set_keymap("n", "<leader>q", ":QuickRun<CR>", opts)

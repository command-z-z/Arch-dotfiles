local status, dap_python = pcall(require, "dap-python")
if (not status) then
    return
end

dap_python.setup('~/.local/share/nvim/mason/packages/debugpy/venv/bin/python')
dap_python.test_runner = 'pytest'

vim.api.nvim_set_keymap("n", "<leader>dn", "<Cmd>lua require('dap-python').test_method()<CR>", {noremap = true, silent = true})
vim.api.nvim_set_keymap("n", "<leader>df", "<Cmd>lua require('dap-python').test_class()<CR>", {noremap = true, silent = true})
vim.api.nvim_set_keymap("v", "<leader>ds", "<Cmd>lua require('dap-python').debug_selection()<CR>", {noremap = true, silent = true})

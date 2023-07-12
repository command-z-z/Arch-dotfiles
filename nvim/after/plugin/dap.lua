local status, dap = pcall(require, "dap")
if (not status) then
    return
end

dap.adapters.lldb = {
  type = 'executable',
  command = '/usr/local/opt/llvm/bin/lldb-vscode', -- adjust as needed
  name = "lldb"
}

dap.adapters.cppdbg = {
    type = 'executable',
    command = os.getenv('HOME') .. "/.local/share/nvim/mason/bin/OpenDebugAD7",
    id = "cppdbg",
}

dap.configurations.c = {
  {
    name = "Launch File",
    type = "lldb",
    request = "launch",
    program = function()
        return vim.fn.input("Path to executable: ", vim.fn.getcwd() .. "/", "file")
    end,
    cwd = '${workspaceFolder}',
    -- macos
    stopOnEntry = false,
    args = {},
    runInTerminal = true,
    postRunCommands = {'process handle -p true -s false -n false SIGWINCH'}
    -- linux
    -- stopOnEntry = true,
  },
}

dap.configurations.cpp = dap.configurations.c
dap.configurations.objc = dap.configurations.c
dap.configurations.rust = dap.configurations.cpp

vim.keymap.set({"n"}, "<F4>", "<cmd>lua require'dap'.terminate()<CR>", {silent = true, noremap = true, buffer = bufnr})
vim.keymap.set({"n"}, "<F5>", "<cmd>lua require'dap'.continue()<CR>", {silent = true, noremap = true, buffer = bufnr})
vim.keymap.set({"n"}, "<leader>db", "<cmd>lua require'dap'.toggle_breakpoint()<CR>", {silent = true, noremap = true, buffer = bufnr})
vim.keymap.set({"n"}, "<F6>", "<cmd>lua require'dap'.step_over()<CR>", {silent = true, noremap = true, buffer = bufnr})
vim.keymap.set({"n"}, "<F7>", "<cmd>lua require'dap'.step_into()<CR>", {silent = true, noremap = true, buffer = bufnr})

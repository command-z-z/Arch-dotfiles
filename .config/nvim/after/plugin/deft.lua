if not vim.g.loaded_defx then
  return
end

vim.api.nvim_set_keymap('n', 'sf', '<Cmd>Defx -listed -resume -split=vertical -winwidth=30 -direction=topleft ' ..
    '-columns=indent:mark:icon:icons:filename:git:size ' ..
    '-buffer-name=tab' .. vim.api.nvim_tabpage_get_number(0) ..
    ' ' .. vim.fn.expand('%:p:h') .. ' -search=' .. vim.fn.expand('%:p') .. '<CR>', { noremap = true, silent = true })

-- 当写入缓冲区后，调用 defx 重绘
vim.cmd('autocmd BufWritePost * lua defx_redraw()')
function defx_redraw()
  vim.fn['defx#redraw']()
end

-- FileType 为 defx 时的设置
vim.cmd('autocmd FileType defx lua defx_my_settings()')
function defx_my_settings()
  local opts = { noremap = true, silent = true, expr = true }
  local map = vim.api.nvim_buf_set_keymap
  local bufnr = 0  -- 0 代表当前缓冲区

    -- 定义键位映射
  map(bufnr, 'n', '<CR>', 'defx#do_action("open", "choose")', opts)
  map(bufnr, 'n', 'yy', 'defx#do_action("copy")', opts)
  map(bufnr, 'n', 'dd', 'defx#do_action("move")', opts)
  map(bufnr, 'n', 'pp', 'defx#do_action("paste")', opts)
  map(bufnr, 'n', 'l', 'defx#do_action("open", "choose")', opts)
  map(bufnr, 'n', '<Right>', 'defx#do_action("open")', opts)
  map(bufnr, 'n', 'E', 'defx#do_action("open", "vsplit")', opts)
  map(bufnr, 'n', 'n', 'defx#do_action("open", "pedit")', opts)
  map(bufnr, 'n', 'i', 'defx#do_action("open", "choose")', opts)
  map(bufnr, 'n', 'o', 'defx#do_action("open_or_close_tree")', opts)
  map(bufnr, 'n', 'K', 'defx#do_action("new_directory")', opts)
  map(bufnr, 'n', 'T', 'defx#do_action("new_file")', opts)
  map(bufnr, 'n', 'M', 'defx#do_action("new_multiple_files")', opts)
  map(bufnr, 'n', 'C', 'defx#do_action("toggle_columns", "mark:indent:icon:filename:type:size:time")', opts)
  map(bufnr, 'n', 'S', 'defx#do_action("toggle_sort", "time")', opts)
  map(bufnr, 'n', 'dD', 'defx#do_action("remove")', opts)
  map(bufnr, 'n', 'a', 'defx#do_action("rename")', opts)
  map(bufnr, 'n', '!', 'defx#do_action("execute_command")', opts)
  map(bufnr, 'n', 'x', 'defx#do_action("execute_system")', opts)
  map(bufnr, 'n', 'YY', 'defx#do_action("yank_path")', opts)
  map(bufnr, 'n', '.', 'defx#do_action("toggle_ignored_files")', opts)
  map(bufnr, 'n', '<BS>', 'defx#do_action("toggle_ignored_files")', opts)
  map(bufnr, 'n', ';', 'defx#do_action("repeat")', opts)
  map(bufnr, 'n', 'h', 'defx#do_action("cd", [".."])', opts)
  map(bufnr, 'n', '<Left>', 'defx#do_action("cd", [".."])', opts)
  map(bufnr, 'n', '~', 'defx#do_action("cd")', opts)
  map(bufnr, 'n', 'gh', 'defx#do_action("cd")', opts)
  map(bufnr, 'n', 'gn', 'defx#do_action("cd", ["~/.config/nvim"])', opts)
  map(bufnr, 'n', 'q', 'defx#do_action("quit")', opts)
  map(bufnr, 'n', '<Space>', 'defx#do_action("toggle_select") .. "j"', opts)
  map(bufnr, 'n', 'm', 'defx#do_action("toggle_select") .. "j"', opts)
  map(bufnr, 'n', 'vv', 'defx#do_action("toggle_select_all")', opts)
  map(bufnr, 'n', '*', 'defx#do_action("toggle_select_all")', opts)
  map(bufnr, 'n', 'j', 'line(".") == line("$") ? "gg" : "j"', opts)
  map(bufnr, 'n', 'k', 'line(".") == 1 ? "G" : "k"', opts)
  map(bufnr, 'n', '<C-l>', 'defx#do_action("redraw")', opts)
  map(bufnr, 'n', '<C-g>', 'defx#do_action("print")', opts)
  map(bufnr, 'n', 'cd', 'defx#do_action("change_vim_cwd")', opts)
end

-- 自定义 defx 列
-- 注意：以下调用可能需要保持原样或寻找相应的 Lua 接口
vim.fn['defx#custom#column']('icon', {
  directory_icon = '▸',
  opened_icon = '▾',
  root_icon = ' ',
})
vim.fn['defx#custom#column']('git', 'indicators', {
  Modified  = 'M',
  Staged    = '✚',
  Untracked = '✭',
  Renamed   = '➜',
  Unmerged  = '═',
  Ignored   = '☒',
  Deleted   = '✖',
  Unknown   = '?'
})


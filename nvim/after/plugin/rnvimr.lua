-- 让Ranger取代Netrw并成为文件浏览器
vim.g.rnvimr_enable_ex = 1
-- 选择文件后隐藏游侠
vim.g.rnvimr_enable_picker = 1
-- 使用multipane模式启动(单列)可以按~手动切换
vim.g.rnvimr_ranger_cmd = {'ranger', '--cmd=set draw_borders both'}
-- 设置sr 启动文件管理器
local opts = {noremap = true, silent = true}
vim.api.nvim_set_keymap("n", "sr", ":RnvimrToggle<CR>", opts)


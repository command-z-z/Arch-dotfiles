local status, blankline = pcall(require, "ibl")
if (not status) then
    return
end

blankline.setup {
    indent = { char = "│" },
    exclude = {
        filetypes = {
            'dashboard',
            'DogicPrompt',
            'log',
            'fugitive',
            'gitcommit',
            'packer',
            'markdown',
            'json',
            'txt',
            'vista',
            'help',
            'todoist',
            'NvimTree',
            'git',
            'TelescopePrompt',
            'undotree',
            'defx',
        },
        buftypes = {
            'terminal', 'nofile', 'prompt'
        },
    },
    scope = {
       enabled = false,
    },
}

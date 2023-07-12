local status, blankline = pcall(require, "indent_blankline")
if (not status) then
    return
end

blankline.setup({
    char = '│',
    use_treesitter_scope = true,
    show_first_indent_level = true,
    show_current_context = false,
    show_current_context_start = false,
    show_current_context_start_on_current_line = false,
    filetype_exclude = {
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
    buftype_exclude = { 'terminal', 'nofile', 'prompt' },
    context_patterns = {
        'class',
        'function',
        'method',
        'block',
        'list_literal',
        'selector',
        '^if',
        '^table',
        'if_statement',
        'while',
        'for',
    },
})


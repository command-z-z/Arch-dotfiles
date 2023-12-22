local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not vim.loop.fs_stat(lazypath) then
    vim.fn.system({
        "git",
        "clone",
        "--filter=blob:none",
        "https://github.com/folke/lazy.nvim.git",
        "--branch=stable", -- latest stable release
        lazypath,
    })
end
vim.opt.rtp:prepend(lazypath)

return require("lazy").setup(
{
    'nvim-tree/nvim-web-devicons',
    --statueline 
    {
        "nvim-lualine/lualine.nvim",
        dependencies = {"nvim-tree/nvim-web-devicons", opt = true}
    },
    -- bufferline 
    {
        'akinsho/bufferline.nvim',
        version = "v3.*",
        dependencies = 'nvim-tree/nvim-web-devicons'
    },
    -- notify
    {
        "folke/noice.nvim",
        dependencies = {
            "MunifTanjim/nui.nvim",
            "rcarriga/nvim-notify",
        },
    },
    -- theme
    'shaunsingh/nord.nvim',
    {
        "catppuccin/nvim",
        name = "catppuccin"
    },
    -- ranger
    "kevinhwang91/rnvimr",
    -- file management
    {
        "Shougo/defx.nvim",
        dependencies = {
            "kristijanhusak/defx-icons", -- dexf icon
            "t9md/vim-choosewin" --windows choose 
        }
    },
    --markdown preview
    {
        "iamcco/markdown-preview.nvim",
        build = function() vim.fn["mkdp#util#install"]() end,
    },
    --lsp
    {
        "neovim/nvim-lspconfig",
        "williamboman/mason.nvim",
        "williamboman/mason-lspconfig.nvim",
        "jay-babu/mason-nvim-dap.nvim",
    },
    --Nvim completion client
    {
        "hrsh7th/nvim-cmp",
        dependencies = {
            "onsails/lspkind-nvim", --for prompt message
            "hrsh7th/cmp-nvim-lsp", --neovim 
            "hrsh7th/cmp-nvim-lua", --nvim-cmp source for neovim Lua API.
            "hrsh7th/cmp-path", --for path start with /
            "hrsh7th/cmp-emoji", --for emoji start with :
        }
    }, 
    -- code snippets
    {
        "L3MON4D3/LuaSnip",
        dependencies = {
            "saadparwaiz1/cmp_luasnip", -- Snippets source for nvim-cmp
            "rafamadriz/friendly-snippets" --代码段合集
        },
    },
    -- lsp improve 
    { "glepnir/lspsaga.nvim", branch = "main"},
    -- symbols autopairs
    {"windwp/nvim-autopairs"},
    -- fuzzy search
    {
        "nvim-telescope/telescope.nvim",
        dependencies = {
            "nvim-lua/plenary.nvim",
            "nvim-tree/nvim-web-devicons"
        }
    },
    -- search faster 
    {"nvim-telescope/telescope-fzf-native.nvim", build = "make"},
    -- file browser
    {"nvim-telescope/telescope-file-browser.nvim" },
    --grammar highlight
    {
        'nvim-treesitter/nvim-treesitter',
        build = ':TSUpdate',
    },
    -- comment 
    {"b3nj5m1n/kommentary"},
    -- quickrun
    'thinca/vim-quickrun',
    -- docstrings
    {
        "danymat/neogen",
        dependencies = "nvim-treesitter/nvim-treesitter",
    },
    -- start page
    {
        'glepnir/dashboard-nvim',
        dependencies = {'nvim-tree/nvim-web-devicons'}
    },
    -- indent
    'lukas-reineke/indent-blankline.nvim',
    -- bookmark
    'MattesGroeger/vim-bookmarks',
    -- telescope to search mark
    "tom-anders/telescope-vim-bookmarks.nvim",
    -- git 
    {
        'lewis6991/gitsigns.nvim'
    },
    -- todo and trouble tool
    {
        "folke/trouble.nvim",
        dependencies = "nvim-tree/nvim-web-devicons",
    },
    {
        "folke/todo-comments.nvim",
        dependencies = "nvim-lua/plenary.nvim",
    },
    -- dap 
    "mfussenegger/nvim-dap",
    "mfussenegger/nvim-dap-python",
    "rcarriga/nvim-dap-ui",
    "theHamsta/nvim-dap-virtual-text",
    -- github
    "zbirenbaum/copilot.lua",
    "zbirenbaum/copilot-cmp",
    {
        "folke/flash.nvim",
        event = "VeryLazy",
        ---@type Flash.Config
        opts = {},
        -- stylua: ignore
        keys = {
            { "<leader>s", mode = { "n", "x", "o" }, function() require("flash").jump() end, desc = "Flash" },
            { "<leader><leader>s", mode = { "n", "o", "x" }, function() require("flash").treesitter() end, desc = "Flash Treesitter" },
        },
    },
    -- latex
    "lervag/vimtex"
})

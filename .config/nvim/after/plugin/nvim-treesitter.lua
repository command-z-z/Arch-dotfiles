local status, treesitter = pcall(require, "nvim-treesitter.configs")
if (not status) then
  return
end

require("nvim-treesitter.install").prefer_git = true
treesitter.setup {
  highlight = {
    enable = true,
    disable = {}
  },
  indent = {
    enable = false,
    disable = {}
  },
  ensure_installed = {
    "cpp",
    "c",
    "python",
    "lua",
    "rust",
    "go",
    "vim",
    "markdown",
    "markdown_inline",
    "regex",
    "bash",
  }
}

if !exists('g:loaded_defx') | finish | endif
" Define mappings
nnoremap <silent>sf :<C-u>Defx -listed -resume -split=vertical -winwidth=30 -direction=topleft
      \ -columns=indent:mark:icon:icons:filename:git:size
      \ -buffer-name=tab`tabpagenr()`
      \ `expand('%:p:h')` -search=`expand('%:p')`<CR>


" jump to relative file dir
autocmd BufWritePost * call defx#redraw()

" quit when defx is last win
" autocmd WinClosed * if winnr('$') <= 2 | qall | endif

autocmd FileType defx call s:defx_my_settings()
	function! s:defx_my_settings() abort
	  " Define mappings
	  nnoremap <silent><buffer><expr> <CR>
	  \ defx#do_action('open', 'choose')
	  nnoremap <silent><buffer><expr> yy
	  \ defx#do_action('copy')
	  nnoremap <silent><buffer><expr> dd
	 \ defx#do_action('move')
	  nnoremap <silent><buffer><expr> pp
	  \ defx#do_action('paste')
	  nnoremap <silent><buffer><expr> l
	  \ defx#do_action('open', 'choose')
	  nnoremap <silent><buffer><expr> <Right>
	  \ defx#do_action('open')
	  nnoremap <silent><buffer><expr> E
	  \ defx#do_action('open', 'vsplit')
	  nnoremap <silent><buffer><expr> n
	  \ defx#do_action('open', 'pedit')
	  nnoremap <silent><buffer><expr> i
	  \ defx#do_action('open', 'choose')
	  nnoremap <silent><buffer><expr> o
	  \ defx#do_action('open_or_close_tree')
	  nnoremap <silent><buffer><expr> K
	  \ defx#do_action('new_directory')
	  nnoremap <silent><buffer><expr> T
	  \ defx#do_action('new_file')
	  nnoremap <silent><buffer><expr> M
	  \ defx#do_action('new_multiple_files')
	  nnoremap <silent><buffer><expr> C
	  \ defx#do_action('toggle_columns',
	  \                'mark:indent:icon:filename:type:size:time')
	  nnoremap <silent><buffer><expr> S
	  \ defx#do_action('toggle_sort', 'time')
	  nnoremap <silent><buffer><expr> dD
	  \ defx#do_action('remove')
	  nnoremap <silent><buffer><expr> a
	  \ defx#do_action('rename')
	  nnoremap <silent><buffer><expr> !
	  \ defx#do_action('execute_command')
	  nnoremap <silent><buffer><expr> x
	  \ defx#do_action('execute_system')
	  nnoremap <silent><buffer><expr> YY
	  \ defx#do_action('yank_path')
	  nnoremap <silent><buffer><expr> .
	  \ defx#do_action('toggle_ignored_files')
	  nnoremap <silent><buffer><expr> <BS>
	  \ defx#do_action('toggle_ignored_files')
	  nnoremap <silent><buffer><expr> ;
	  \ defx#do_action('repeat')
	  nnoremap <silent><buffer><expr> h
	  \ defx#do_action('cd', ['..'])
	  nnoremap <silent><buffer><expr> <Left>
	  \ defx#do_action('cd', ['..'])
	  nnoremap <silent><buffer><expr> ~
	  \ defx#do_action('cd')
	  nnoremap <silent><buffer><expr> gh
	  \ defx#do_action('cd')
	  nnoremap <silent><buffer><expr> gn
	  \ defx#do_action('cd',['~/.config/nvim'])
	  nnoremap <silent><buffer><expr> q
	  \ defx#do_action('quit')
	  nnoremap <silent><buffer><expr> <Space>
	  \ defx#do_action('toggle_select') . 'j'
	  nnoremap <silent><buffer><expr> m
	  \ defx#do_action('toggle_select') . 'j'
	  nnoremap <silent><buffer><expr> vv
	  \ defx#do_action('toggle_select_all')
	  nnoremap <silent><buffer><expr> *
	  \ defx#do_action('toggle_select_all')
	  nnoremap <silent><buffer><expr> j
	  \ line('.') == line('$') ? 'gg' : 'j'
	  nnoremap <silent><buffer><expr> k
	  \ line('.') == 1 ? 'G' : 'k'
	  nnoremap <silent><buffer><expr> <C-l>
	  \ defx#do_action('redraw')
	  nnoremap <silent><buffer><expr> <C-g>
	  \ defx#do_action('print')
	  nnoremap <silent><buffer><expr> cd
	  \ defx#do_action('change_vim_cwd')
	endfunction

call defx#custom#column('icon', {
      \ 'directory_icon': '▸',
      \ 'opened_icon': '▾',
      \ 'root_icon': ' ',
      \ })
call defx#custom#column('git', 'indicators', {
  \ 'Modified'  : 'M',
  \ 'Staged'    : '✚',
  \ 'Untracked' : '✭',
  \ 'Renamed'   : '➜',
  \ 'Unmerged'  : '═',
  \ 'Ignored'   : '☒',
  \ 'Deleted'   : '✖',
  \ 'Unknown'   : '?'
  \ })
 

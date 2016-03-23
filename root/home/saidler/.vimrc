"return" 2>&- || "exit"

set nocp
set noai
set et
set shiftwidth=4
set tabstop=4
set hlsearch
set incsearch
set showmode
set showcmd
set ruler
syntax on
map <C-N> :tabnext <Return>
map <C-P> :tabprevious <Return>
highlight DiffAdd term=reverse cterm=bold ctermbg=green ctermfg=white
highlight DiffChange term=reverse cterm=bold ctermbg=cyan ctermfg=black
highlight DiffText term=reverse cterm=bold ctermbg=gray ctermfg=black
highlight DiffDelete term=reverse cterm=bold ctermbg=red ctermfg=black

highlight search term=reverse cterm=bold ctermbg=gray ctermfg=black

highlight ColorColumn ctermbg=235 guibg=#2c2d27

if exists('+colorcolumn')
  let &colorcolumn=join(range(81,120),",")
else
  autocmd BufWinEnter * let w:m2=matchadd('ErrorMsg', '\%>80v.\+', -1)
endif

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"                                  Formatting
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

filetype plugin indent on
set shiftwidth=4 tabstop=4 softtabstop=4 expandtab autoindent
"autocmd filetype c,asm,sls,yml,yaml,python,sh setlocal shiftwidth=4 tabstop=4 softtabstop=4
autocmd filetype make setlocal noexpandtab
autocmd BufWritePre * :%s/\s\+$//e


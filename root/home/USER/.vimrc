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
set showmatch
set ruler
syntax on
map <C-N> :tabnext <Return>
map <C-P> :tabprevious <Return>

set term=xterm-256color

hi Normal guibg=#32322f ctermbg=Black
hi NonText guibg=#32322f ctermbg=Black
let &colorcolumn=join(range(1,80),",")
hi ColorColumn ctermbg=235 guibg=#2c2d27
hi Search ctermfg=Red ctermbg=None cterm=bold,underline

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"                                  Formatting
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

"filetype plugin indent on
"set shiftwidth=4 tabstop=4 softtabstop=4 expandtab autoindent
"autocmd filetype c,asm,sls,yml,yaml,python,sh setlocal shiftwidth=4 tabstop=4 softtabstop=4

" Uncomment the following to have Vim jump to the last position when
" reopening a file
if has("autocmd")
  au BufReadPost * if line("'\"") > 1 && line("'\"") <= line("$") | exe "normal! g'\"" | endif
endif

"autoreload vimrc src: https://stackoverflow.com/a/2471060
augroup myvimrc
    au!
    au BufWritePost .vimrc,_vimrc,vimrc,.gvimrc,_gvimrc,gvimrc so $MYVIMRC | if has('gui_running') | so $MYGVIMRC | endif
augroup END

autocmd FileType make setlocal noexpandtab

autocmd BufWritePre * :%s/\s\+$//e

" Handle TERM quirks in vim
if $term =~ '^screen-256color'
    set t_Co=256
    nmap <Esc>OH <Home>
    imap <Esc>OH <Home>
    nmap <Esc>OF <End>
    imap <Esc>OF <End>
endif


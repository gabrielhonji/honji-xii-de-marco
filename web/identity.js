let theme='light';
try{theme=localStorage.getItem('xii-theme')||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light')}catch{}
const toggle=document.getElementById('identity-theme');
function applyTheme(){document.documentElement.dataset.theme=theme;toggle.textContent=theme==='dark'?'Tema claro':'Tema escuro';toggle.setAttribute('aria-pressed',String(theme==='dark'));toggle.setAttribute('aria-label',theme==='dark'?'Ativar tema claro':'Ativar tema escuro')}
applyTheme();
toggle.onclick=()=>{theme=theme==='dark'?'light':'dark';applyTheme();try{localStorage.setItem('xii-theme',theme)}catch{}};

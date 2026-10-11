const sharedTheme=document.cookie.split('; ').find(item=>item.startsWith('honji_theme='))?.split('=')[1];
let theme=sharedTheme==='dark'||sharedTheme==='light'?sharedTheme:'light';
try{theme=sharedTheme||localStorage.getItem('honji-theme')||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light')}catch{}
const toggle=document.getElementById('identity-theme');
function applyTheme(){document.documentElement.dataset.theme=theme;toggle.textContent=theme==='dark'?'Tema claro':'Tema escuro';toggle.setAttribute('aria-pressed',String(theme==='dark'));toggle.setAttribute('aria-label',theme==='dark'?'Ativar tema claro':'Ativar tema escuro')}
applyTheme();
toggle.onclick=()=>{theme=theme==='dark'?'light':'dark';applyTheme();try{localStorage.setItem('honji-theme',theme)}catch{};document.cookie=`honji_theme=${theme}; Domain=.honji.com.br; Path=/; Max-Age=31536000; SameSite=Lax${location.protocol==='https:'?'; Secure':''}`};

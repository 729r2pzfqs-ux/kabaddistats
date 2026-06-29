
let KB_idx=null,KB_box=null;
async function KB_load(){if(KB_idx)return KB_idx;
  const r=await fetch(location.origin+'/search-index.json');KB_idx=await r.json();return KB_idx;}
function KB_search(){if(KB_box){KB_box.remove();KB_box=null;return;}
  KB_box=document.createElement('div');
  KB_box.style.cssText='position:fixed;inset:0;z-index:200;background:rgba(42,28,18,.45);backdrop-filter:blur(3px);display:flex;align-items:flex-start;justify-content:center;padding-top:10vh';
  KB_box.innerHTML='<div onclick="event.stopPropagation()" style="width:92%;max-width:560px;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,.3)">'+
    '<input id="kbq" placeholder="खिलाड़ी, टीम, सीज़न, रिकॉर्ड खोजें…" style="width:100%;padding:16px 18px;border:0;outline:0;font-size:16px;border-bottom:1px solid #f0e3d8;font-family:Inter,Noto Sans Devanagari,sans-serif">'+
    '<div id="kbr" style="max-height:60vh;overflow:auto"></div></div>';
  KB_box.onclick=()=>KB_search();
  document.body.appendChild(KB_box);
  const q=document.getElementById('kbq');q.focus();
  KB_load().then(()=>KB_render(''));
  q.addEventListener('input',e=>KB_render(e.target.value));
  q.addEventListener('keydown',e=>{if(e.key==='Escape')KB_search();});
}
function KB_render(term){
  const box=document.getElementById('kbr');if(!box)return;
  term=(term||'').trim().toLowerCase();
  let res=KB_idx||[];
  if(term){res=res.filter(r=>r[3].includes(term)||r[0].toLowerCase().includes(term));}
  res=res.slice(0,40);
  if(!res.length){box.innerHTML='<div style="padding:18px;color:#6b5d52;font-family:Noto Sans Devanagari,sans-serif">कोई परिणाम नहीं मिला</div>';return;}
  box.innerHTML=res.map(r=>'<a href="'+location.origin+r[1]+'" style="display:flex;justify-content:space-between;gap:10px;padding:12px 18px;border-top:1px solid #f4ece4;text-decoration:none;color:#2a1c12">'+
    '<span style="font-weight:600;font-family:Inter,Noto Sans Devanagari,sans-serif">'+r[0]+'</span>'+
    '<span style="color:#FF6B00;font-size:13px;font-family:Noto Sans Devanagari,sans-serif">'+r[2]+'</span></a>').join('');
}
window.KB_search=KB_search;

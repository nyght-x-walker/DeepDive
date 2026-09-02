import { useState } from 'react';
const C={panel:'#ffffff',border:'#e2e8f0',muted:'#64748b',text:'#0f172a',indigo:'#4f46e5',green:'#059669',amber:'#d97706'};

export default function IncrementViz(){
  const [mode,setMode]=useState<'pre'|'post'|'add'>('post');
  // Simulate without mutating actual state for display
  const simulate=()=>{
    let v=5, r=0;
    if(mode==='pre'){ v=6; r=v; }
    else if(mode==='post'){ r=v; v=6; }
    else { v=7; r=v; }
    return {v,r};
  };
  const s=simulate();
  return (
    <div style={{display:'grid',gap:12}}>
      <div style={{display:'flex',gap:8,flexWrap:'wrap'}}>
        <button onClick={()=>setMode('post')} style={{background:mode==='post'?'#4f46e5':'white',color:mode==='post'?'white':C.text,border:`1px solid ${C.border}`,borderRadius:999,padding:'6px 12px',font:'600 12px Inter',cursor:'pointer'}}>i++ (post)</button>
        <button onClick={()=>setMode('pre')} style={{background:mode==='pre'?'#4f46e5':'white',color:mode==='pre'?'white':C.text,border:`1px solid ${C.border}`,borderRadius:999,padding:'6px 12px',font:'600 12px Inter',cursor:'pointer'}}>++i (pre)</button>
        <button onClick={()=>setMode('add')} style={{background:mode==='add'?'#4f46e5':'white',color:mode==='add'?'white':C.text,border:`1px solid ${C.border}`,borderRadius:999,padding:'6px 12px',font:'600 12px Inter',cursor:'pointer'}}>i += 2</button>
      </div>
      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr 1fr',gap:12}}>
        <div style={{background:C.panel,border:`1px solid ${C.border}`,borderRadius:12,padding:14,textAlign:'center'}}>
          <div style={{font:'11px JetBrains Mono',color:C.muted}}>CODE</div>
          <div style={{font:'18px JetBrains Mono',color:C.indigo,marginTop:6}}>{mode==='pre'?'x = ++i':mode==='post'?'x = i++':'x = (i += 2)'}</div>
          <div style={{font:'12px Inter',color:C.muted,marginTop:6}}>i starts 5</div>
        </div>
        <div style={{background:C.panel,border:`1px solid ${C.border}`,borderRadius:12,padding:14,textAlign:'center'}}>
          <div style={{font:'11px JetBrains Mono',color:C.muted}}>x gets</div>
          <div style={{font:'28px JetBrains Mono',color:C.text,marginTop:4}}>{s.r}</div>
          <div style={{font:'12px Inter',color:C.muted}}>{mode==='post'?'old value then +1':'new value'}</div>
        </div>
        <div style={{background:C.panel,border:`1px solid ${C.border}`,borderRadius:12,padding:14,textAlign:'center'}}>
          <div style={{font:'11px JetBrains Mono',color:C.muted}}>i after</div>
          <div style={{font:'28px JetBrains Mono',color:C.green,marginTop:4}}>{s.v}</div>
          <div style={{font:'12px Inter',color:C.muted}}>always incremented</div>
        </div>
      </div>
      <div style={{font:'12px Inter',color:C.muted,background:'#f8fafc',border:`1px solid ${C.border}`,borderRadius:10,padding:'10px 12px'}}>Overloading: you can define <span className="mono">operator++</span> or <span className="mono">operator+=</span> for your own types. Same idea, custom meaning.</div>
    </div>
  );
}

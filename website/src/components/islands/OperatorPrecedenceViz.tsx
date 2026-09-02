import { useState } from 'react';
const C={panel:'#ffffff',border:'#e2e8f0',muted:'#64748b',text:'#0f172a',indigo:'#4f46e5',amber:'#d97706'};

const examples=[
  {code:'a + b * c', tree:'(a + (b * c))', note:'* before +'},
  {code:'a = b = c', tree:'(a = (b = c))', note:'= right to left'},
  {code:'a && b || c', tree:'((a && b) || c)', note:'&& before ||'},
  {code:'*p++', tree:'(*(p++))', note:'postfix ++ before *'},
];

export default function OperatorPrecedenceViz(){
  const [idx,setIdx]=useState(0);
  const ex=examples[idx];
  return (
    <div style={{display:'grid',gap:12}}>
      <div style={{display:'flex',gap:8,flexWrap:'wrap'}}>
        {examples.map((e,i)=><button key={i} onClick={()=>setIdx(i)} style={{background:i===idx?'#4f46e5':'white',color:i===idx?'white':'#0f172a',border:`1px solid ${C.border}`,borderRadius:999,padding:'6px 12px',font:'600 12px Inter',cursor:'pointer'}}>{e.code}</button>)}
      </div>
      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:12}}>
        <div style={{background:C.panel,border:`1px solid ${C.border}`,borderRadius:12,padding:14}}>
          <div style={{font:'600 13px Inter',color:C.text}}>Expression</div>
          <div style={{marginTop:8,font:'22px JetBrains Mono',color:C.indigo,textAlign:'center',background:'#f8fafc',border:`1px solid ${C.border}`,borderRadius:10,padding:'14px 10px'}}>{ex.code}</div>
          <div style={{marginTop:10,font:'13px Inter',color:C.text,textAlign:'center'}}>Parses as <span style={{font:'600 13px JetBrains Mono',color:C.indigo}}>{ex.tree}</span></div>
          <div style={{marginTop:6,font:'12px Inter',color:C.muted,textAlign:'center'}}>{ex.note}, precedence decides grouping, associativity decides tie.</div>
        </div>
        <div style={{background:'#f8fafc',border:`1px solid ${C.border}`,borderRadius:12,padding:14}}>
          <div style={{font:'600 13px Inter'}}>Quick table</div>
          <div style={{marginTop:8,display:'grid',gap:6,font:'12px JetBrains Mono'}}>
            <div style={{display:'flex',justifyContent:'space-between',borderBottom:`1px solid ${C.border}`,paddingBottom:4}}><span>++ -- () [] . -&gt;</span><span style={{color:C.muted}}> postfix</span></div>
            <div style={{display:'flex',justifyContent:'space-between',borderBottom:`1px solid ${C.border}`,paddingBottom:4}}><span>* / %</span><span style={{color:C.muted}}>left</span></div>
            <div style={{display:'flex',justifyContent:'space-between',borderBottom:`1px solid ${C.border}`,paddingBottom:4}}><span>+ -</span><span style={{color:C.muted}}>left</span></div>
            <div style={{display:'flex',justifyContent:'space-between'}}><span>= += -=</span><span style={{color:C.muted}}>right</span></div>
          </div>
          <div style={{marginTop:8,font:'11px Inter',color:C.muted}}>When unsure, add parentheses. Clarity beats cleverness.</div>
        </div>
      </div>
    </div>
  );
}

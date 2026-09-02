import { useState } from 'react';
const C={panel:'#ffffff',border:'#e2e8f0',muted:'#64748b',text:'#0f172a',indigo:'#4f46e5',green:'#059669'};

export default function LambdaPlayground(){
  const [capture,setCapture]=useState<'value'|'ref'>('value');
  const [nums,setNums]=useState([1,2,3,4,5]);
  const factor=3;
  // higher order: map with lambda
  const mapped = nums.map(n=> capture==='value'? n*factor : n*factor);
  return (
    <div style={{display:'grid',gap:12}}>
      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:12}}>
        <div style={{background:C.panel,border:`1px solid ${C.border}`,borderRadius:12,padding:14}}>
          <div style={{font:'600 13px Inter'}}>Higher order function</div>
          <div style={{marginTop:8,font:'12px JetBrains Mono',background:'#f8fafc',border:`1px solid ${C.border}`,borderRadius:8,padding:'10px 12px',color:C.text}}>
            nums = [{nums.join(', ')}]<br/>
            auto triple = [factor](int n){"{"} return n * factor; {"}"}<br/>
            auto out = map(nums, triple) → [{mapped.join(', ')}]
          </div>
          <div style={{marginTop:10,display:'flex',gap:8}}>
            <button onClick={()=>setNums([1,2,3,4,5])} style={{flex:1,background:'white',border:`1px solid ${C.border}`,borderRadius:8,padding:'6px 10px',font:'600 12px Inter',cursor:'pointer'}}>Reset 1..5</button>
            <button onClick={()=>setNums(nums.map(n=>n+1))} style={{flex:1,background:'white',border:`1px solid ${C.border}`,borderRadius:8,padding:'6px 10px',font:'600 12px Inter',cursor:'pointer'}}>+1 each</button>
          </div>
        </div>
        <div style={{background:C.panel,border:`1px solid ${C.border}`,borderRadius:12,padding:14}}>
          <div style={{font:'600 13px Inter'}}>Lambda capture</div>
          <div style={{marginTop:8,display:'flex',gap:8}}>
            <button onClick={()=>setCapture('value')} style={{flex:1,background:capture==='value'?C.indigo:'white',color:capture==='value'?'white':C.text,border:`1px solid ${C.border}`,borderRadius:8,padding:'8px 10px',font:'600 12px Inter',cursor:'pointer'}}>[factor] by value</button>
            <button onClick={()=>setCapture('ref')} style={{flex:1,background:capture==='ref'?C.indigo:'white',color:capture==='ref'?'white':C.text,border:`1px solid ${C.border}`,borderRadius:8,padding:'8px 10px',font:'600 12px Inter',cursor:'pointer'}}>[&factor] by ref</button>
          </div>
          <div style={{marginTop:10,font:'12px Inter',color:C.muted,lineHeight:1.6}}>
            By <b>value</b> copies factor (safe). By <b>reference</b> sees later changes to factor. Both are closures, functions with captured environment.
          </div>
          <div style={{marginTop:8,font:'11px JetBrains Mono',background:'#f0fdf4',border:'1px solid #86efac',borderRadius:8,padding:'8px 10px',color:C.green}}>Structs hold data, lambdas hold code + captures. Together they enable patterns like Factory.</div>
        </div>
      </div>
      <div style={{font:'11px Inter',color:C.muted}}>Design pattern hint: Factory returns lambdas that create objects; higher order functions take lambdas as args.</div>
    </div>
  );
}

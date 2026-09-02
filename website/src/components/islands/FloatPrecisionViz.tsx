import { useState } from 'react';
const C={panel:'#ffffff',border:'#e2e8f0',muted:'#64748b',text:'#0f172a',indigo:'#4f46e5',red:'#e11d48',green:'#059669'};

export default function FloatPrecisionViz(){
  const [a,setA]=useState(0.1);
  const [b,setB]=useState(0.2);
  const sumF = (a+b);
  const sumD = (a+b);
  const equal = (a+b)===0.3;
  return (
    <div style={{display:'grid',gap:12}}>
      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:12}}>
        <div style={{background:C.panel,border:`1px solid ${C.border}`,borderRadius:12,padding:14}}>
          <div style={{font:'600 13px Inter',color:C.text}}>Try it, 0.1 + 0.2</div>
          <div style={{marginTop:10,display:'grid',gap:10}}>
            <label style={{font:'12px Inter',color:C.muted}}>a <input type="range" min="0" max="1" step="0.1" value={a} onChange={e=>setA(parseFloat(e.target.value))} style={{width:'100%'}} /><span style={{font:'12px JetBrains Mono',color:C.text,marginLeft:8}}>{a.toFixed(1)}</span></label>
            <label style={{font:'12px Inter',color:C.muted}}>b <input type="range" min="0" max="1" step="0.1" value={b} onChange={e=>setB(parseFloat(e.target.value))} style={{width:'100%'}} /><span style={{font:'12px JetBrains Mono',color:C.text,marginLeft:8}}>{b.toFixed(1)}</span></label>
            <div style={{font:'12px JetBrains Mono',background:'#f8fafc',border:`1px solid ${C.border}`,borderRadius:8,padding:'8px 10px',color:C.text}}>a + b = {sumF.toPrecision(15)}<br/>0.3 = 0.30000000000000004<br/>(a+b)===0.3 → <span style={{color:equal?C.green:C.red}}>{String(equal)}</span></div>
            <div style={{font:'11px Inter',color:C.muted}}>Float is binary fractions. Some decimals have no exact binary. Double has more bits (53) than float (24), smaller error, not zero.</div>
          </div>
        </div>
        <div style={{background:'rgba(79,70,229,.06)',border:`1px solid ${C.indigo}`,borderRadius:12,padding:14}}>
          <div style={{font:'600 13px Inter',color:C.text}}>Why it matters</div>
          <div style={{font:'13px Inter',color:C.muted,marginTop:6,lineHeight:1.6}}>Comparing <span className="mono">float</span> with <span className="mono">==</span> fails. Use epsilon: <span className="mono">fabs(a-b) &lt; 1e-9</span>. Integers are exact, floats are not.</div>
          <div style={{marginTop:10,font:'11px JetBrains Mono',background:'white',border:`1px solid ${C.border}`,borderRadius:8,padding:'8px 10px',color:C.indigo}}>float: 24 bits mantissa ~7 decimal digits<br/>double: 53 bits ~15 digits</div>
        </div>
      </div>
      <div style={{font:'11px Inter',color:C.muted}}>Integers vs floating: integers count, floats approximate. Choose based on exactness vs range.</div>
    </div>
  );
}

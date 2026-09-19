/* DeepDive course engine: narration, progress, quizzes, reveals. Vanilla JS, no dependencies. */
(function(){
"use strict";
var store = {
  get: function(k, d){ try{ var v = localStorage.getItem("deepdive."+k); return v===null?d:JSON.parse(v); }catch(e){ return d; } },
  set: function(k, v){ try{ localStorage.setItem("deepdive."+k, JSON.stringify(v)); }catch(e){} }
};

/* ---------- narration: studio file first, system voice fallback ---------- */
var narrVoice = null, narrating = false, studioAudio = null, fullTalk = false, autoAdv = false, voiceToken = 0;
function pickBestVoice(voices){
  var en = [], i;
  for(i=0;i<voices.length;i++){ var l=(voices[i].lang||"").toLowerCase(); if(l.indexOf("en")===0){en.push(voices[i]);} }
  var pool = en.length?en:voices; if(!pool.length){return null;}
  function score(v){
    var n=(v.name+" "+(v.voiceURI||"")).toLowerCase(), lang=(v.lang||"").toLowerCase(), s=0;
    if(lang.indexOf("en-us")===0){s+=100;}else if(lang.indexOf("en-gb")===0){s+=70;}else if(lang.indexOf("en")===0){s+=40;}
    if(n.indexOf("natural")>=0){s+=120;}
    if(n.indexOf("google us english")>=0||n.indexOf("google uk english female")>=0){s+=110;}else if(n.indexOf("google")>=0){s+=80;}
    if(n.indexOf("microsoft")>=0&&(n.indexOf("online")>=0||n.indexOf("aria")>=0||n.indexOf("jenny")>=0||n.indexOf("guy")>=0)){s+=100;}
    else if(n.indexOf("microsoft")>=0){s+=60;}
    if(n.indexOf("samantha")>=0||n.indexOf("karen")>=0||n.indexOf("moira")>=0||n.indexOf("tessa")>=0){s+=50;}
    if(n.indexOf("enhanced")>=0||n.indexOf("premium")>=0){s+=30;}
    return s;
  }
  var best=pool[0], bs=-1;
  for(var j=0;j<pool.length;j++){var sc=score(pool[j]); if(sc>bs){bs=sc; best=pool[j];}}
  return best;
}
function voiceButtons(on){
  narrating = on;
  var btns = document.querySelectorAll("[data-say-btn]");
  for(var i=0;i<btns.length;i++){ btns[i].classList.toggle("speaking", !!on && btns[i].getAttribute("data-say-btn")===String(speakingId)); }
  var full = document.querySelectorAll("[data-fulltalk]");
  for(var k=0;k<full.length;k++){ full[k].textContent = fullTalk ? "Stop full chapter" : full[k].getAttribute("data-label") || "Play full chapter"; }
}
var speakingId = null;
function setSpeakUI(on, id){ speakingId = on?id:null; voiceButtons(on); }
function stopStudio(){ if(studioAudio){ try{studioAudio.pause(); studioAudio.src="";}catch(e){} studioAudio=null; } }
function stopSystem(){ try{ speechSynthesis.cancel(); }catch(e){} }
function stopSpeak(){
  voiceToken++;
  if(!autoAdv){ fullTalk=false; }
  stopStudio(); stopSystem(); setSpeakUI(false, null); paintFullBtn();
}
function paintFullBtn(){
  var full = document.querySelectorAll("[data-fulltalk]");
  for(var k=0;k<full.length;k++){ full[k].textContent = fullTalk ? "Stop full chapter" : (full[k].getAttribute("data-label") || "Play full chapter"); }
}
function playVoice(src, text, id, onEnd){
  stopStudio(); stopSystem();
  var tk = ++voiceToken, settled = false;
  function fallback(){
    if(settled || tk!==voiceToken){return;}
    settled = true; studioAudio = null; speakSystem(text, id, onEnd);
  }
  if(src){
    var a = new Audio(src); studioAudio = a; setSpeakUI(true, id);
    a.onended = function(){ if(settled||tk!==voiceToken){return;} settled=true; studioAudio=null; setSpeakUI(false,null); if(onEnd){onEnd();} };
    a.onerror = function(){ fallback(); };
    try{ var p=a.play(); if(p&&p.catch){ p.catch(function(){ fallback(); }); } }
    catch(e){ fallback(); }
  }else{ speakSystem(text, id, onEnd); }
}
function speakSystem(text, id, done){
  if(!("speechSynthesis" in window)){ setSpeakUI(false,null); if(done){done();} return; }
  var synth = speechSynthesis; try{ synth.cancel(); }catch(e){}
  if(!narrVoice){ try{ narrVoice = pickBestVoice(synth.getVoices()); }catch(e2){} }
  var chunks = (text.match(/[^.!?]+[.!?]+|[^.!?]+$/g)||[text]).map(function(s){return s.trim();}).filter(Boolean);
  var i = 0; setSpeakUI(true, id);
  (function next(){
    if(!narrating){return;}
    if(i>=chunks.length){ setSpeakUI(false,null); if(done){done();} return; }
    var u = new SpeechSynthesisUtterance(chunks[i]);
    if(narrVoice){ u.voice=narrVoice; u.lang=narrVoice.lang; }
    u.rate=1; u.pitch=1; u.volume=1;
    u.onend=function(){ i++; setTimeout(next,220); };
    u.onerror=function(){ i++; setTimeout(next,220); };
    synth.speak(u);
  })();
}
function sections(){
  var out = [], els = document.querySelectorAll("[data-say]");
  for(var i=0;i<els.length;i++){ out.push(els[i]); }
  return out;
}
function narrateSection(id){
  var el = document.getElementById(id);
  if(!el){return;}
  if(narrating){ stopSpeak(); return; }
  fullTalk = false; paintFullBtn();
  playVoice(el.getAttribute("data-audio"), el.getAttribute("data-say"), id, null);
}
function nextInTalk(list, idx){
  if(!fullTalk){return;}
  if(idx>=list.length){ fullTalk=false; paintFullBtn(); return; }
  var el = list[idx];
  autoAdv = true;
  if(el.scrollIntoView){ try{ el.scrollIntoView({behavior:"smooth", block:"center"}); }catch(e){} }
  autoAdv = false;
  playVoice(el.getAttribute("data-audio"), el.getAttribute("data-say"), el.id, function(){ nextInTalk(list, idx+1); });
}
function fullChapter(){
  if(fullTalk){ stopSpeak(); return; }
  var list = sections();
  if(!list.length){return;}
  fullTalk = true; paintFullBtn();
  var first = list[0];
  if(first.scrollIntoView){ try{ window.scrollTo({top:0, behavior:"smooth"}); }catch(e){} }
  playVoice(first.getAttribute("data-audio"), first.getAttribute("data-say"), first.id, function(){ nextInTalk(list, 1); });
}

/* ---------- progress + badges ---------- */
var CHAPTERS = ["initial","phase1","phase2","phase3","final","top1","top2","top3","top4"];
function markDone(key){
  var d = store.get("done", {});
  d[key] = true; store.set("done", d);
  paintProgress();
}
function paintProgress(){
  var d = store.get("done", {}), n = 0, i;
  for(i=0;i<CHAPTERS.length;i++){ if(d[CHAPTERS[i]]){n++;} }
  var bars = document.querySelectorAll("[data-progress-bar]");
  for(i=0;i<bars.length;i++){ bars[i].style.width = (n/CHAPTERS.length*100)+"%"; }
  var labels = document.querySelectorAll("[data-progress-label]");
  for(i=0;i<labels.length;i++){ labels[i].textContent = n+" of "+CHAPTERS.length+" chapters complete"; }
  var dots = document.querySelectorAll("[data-badge]");
  for(i=0;i<dots.length;i++){ dots[i].classList.toggle("got", !!d[dots[i].getAttribute("data-badge")]); }
  var cards = document.querySelectorAll("[data-chapter]");
  for(i=0;i<cards.length;i++){
    var done = !!d[cards[i].getAttribute("data-chapter")];
    var tag = cards[i].querySelector("[data-state]");
    if(tag){ tag.textContent = done ? "Done" : "Open"; }
  }
}
function recordQuiz(key, ok){
  var q = store.get("quiz", {});
  q[key] = {ok:!!ok, at:Date.now()};
  store.set("quiz", q);
}

/* ---------- quizzes ---------- */
function bindQuizzes(){
  var boxes = document.querySelectorAll("[data-quiz]");
  for(var b=0;b<boxes.length;b++){
    (function(box){
      var opts = box.querySelectorAll("[data-opt]");
      var fb = box.querySelector("[data-feedback]");
      var key = box.getAttribute("data-quiz");
      for(var i=0;i<opts.length;i++){
        (function(btn){
          btn.addEventListener("click", function(){
            for(var j=0;j<opts.length;j++){ opts[j].classList.remove("picked-right","picked-wrong"); }
            var good = btn.getAttribute("data-opt")==="1";
            btn.classList.add(good?"picked-right":"picked-wrong");
            if(fb){ fb.textContent = good ? ("Correct. "+(box.getAttribute("data-why")||"")) : "Not quite. Try again."; }
            recordQuiz(key, good);
          });
        })(opts[i]);
      }
    })(boxes[b]);
  }
}

/* ---------- reveals + keyboard + voices ---------- */
function bindReveals(){
  if(!("IntersectionObserver" in window)){
    var els = document.querySelectorAll(".reveal");
    for(var i=0;i<els.length;i++){els[i].classList.add("seen");}
    return;
  }
  var io = new IntersectionObserver(function(es){
    for(var i=0;i<es.length;i++){ if(es[i].isIntersecting){ es[i].target.classList.add("seen"); io.unobserve(es[i].target); } }
  }, {threshold:.12});
  var all = document.querySelectorAll(".reveal");
  for(var k=0;k<all.length;k++){
    (function(el){
      try{
        var r = el.getBoundingClientRect();
        if(r.top < window.innerHeight && r.bottom > 0){ el.classList.add("seen"); return; }
      }catch(e){}
      io.observe(el);
    })(all[k]);
  }
}
function bindVoices(){
  var btns = document.querySelectorAll("[data-say-btn]");
  for(var i=0;i<btns.length;i++){
    (function(b){ b.addEventListener("click", function(){ narrateSection(b.getAttribute("data-say-btn")); }); })(btns[i]);
  }
  var full = document.querySelectorAll("[data-fulltalk]");
  for(var k=0;k<full.length;k++){
    if(!full[k].getAttribute("data-label")){ full[k].setAttribute("data-label", full[k].textContent); }
    full[k].addEventListener("click", function(){ fullChapter(); });
  }
  var stops = document.querySelectorAll("[data-stop]");
  for(var s=0;s<stops.length;s++){ stops[s].addEventListener("click", function(){ stopSpeak(); }); }
  var sel = document.querySelectorAll("[data-voicepick]");
  function fill(selEl){
    if(!("speechSynthesis" in window)){return;}
    var vs = speechSynthesis.getVoices(); if(!vs.length){return;}
    if(!narrVoice){ narrVoice = pickBestVoice(vs); }
    selEl.innerHTML = "";
    for(var i=0;i<Math.min(vs.length,40);i++){
      var o = document.createElement("option");
      o.value = vs[i].name;
      o.textContent = vs[i].name+" ("+vs[i].lang+")"+(vs[i]===narrVoice?" (recommended)":"");
      if(vs[i]===narrVoice){o.selected=true;}
      selEl.appendChild(o);
    }
    selEl.onchange = function(){
      var all = speechSynthesis.getVoices();
      for(var k=0;k<all.length;k++){ if(all[k].name===selEl.value){ narrVoice=all[k]; } }
    };
  }
  for(var q=0;q<sel.length;q++){
    (function(el){
      fill(el);
      try{ speechSynthesis.onvoiceschanged = function(){ fill(el); }; }catch(e){}
    })(sel[q]);
  }
}
function bindComplete(){
  var btns = document.querySelectorAll("[data-complete]");
  for(var i=0;i<btns.length;i++){
    (function(b){
      b.addEventListener("click", function(){
        markDone(b.getAttribute("data-complete"));
        b.textContent = "Chapter complete";
      });
    })(btns[i]);
  }
}
document.addEventListener("keydown", function(e){
  var tag = (e.target && e.target.tagName)||"";
  if(tag==="INPUT"||tag==="TEXTAREA"||tag==="SELECT"){return;}
  if(e.key==="ArrowRight"){ var nx=document.querySelector("[data-next]"); if(nx){window.location.href=nx.getAttribute("href");} }
  else if(e.key==="ArrowLeft"){ var pv=document.querySelector("[data-prev]"); if(pv){window.location.href=pv.getAttribute("href");} }
});
document.addEventListener("DOMContentLoaded", function(){
  paintProgress(); bindQuizzes(); bindReveals(); bindVoices(); bindComplete();
});
window.Course = { markDone:markDone, stop:stopSpeak, narrate:narrateSection, full:fullChapter };
})();

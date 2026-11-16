/* ShikboLab ডেমো প্ল্যান সিস্টেম (js/demo-saas.js)
   ⚠️ সবকিছু শুধু ব্রাউজারের localStorage-এ থাকে। এটা শুধু ডেমো দেখানোর জন্য, আসল সিকিউরিটি নয়। */
(function(){
 if(window.SL)return;
 var d=document,inCh=/\/chapters\/[^\/]*$/.test(location.pathname),B=inCh?'../':'';
 /* ====== এখানে দাম, লিমিট, ফ্রি অধ্যায় বদলাতে পারবে ====== */
 var CFG={
  TRIAL_DAYS:7,
  FREE:['chem-concepts-of-chemistry','phy-physical-quantities','math-functions-graphs','bio-heredity-mendel','chem-x-lab-safety'],
  PAY:{bkash:'01XXXXXXXXX',nagad:'01XXXXXXXXX',wa:'8801XXXXXXXXX'},
  INSTANT:true, /* true = ডেমোতে পেমেন্ট দিলেই সাথে সাথে চালু। false = শুধু অ্যাডমিনকে অনুরোধ পাঠানো যাবে (আসল ম্যানুয়াল মোড) */
  PLANS:{
   student:{key:'student',name:'স্টুডেন্ট প্ল্যান',emoji:'🎒',desc:'একজন শিক্ষার্থীর জন্য',students:1,teachers:0,devices:2,price:{month:99,week:35},color:'#2a9d8f'},
   family:{key:'family',name:'ফ্যামিলি প্ল্যান',emoji:'👨‍👩‍👧‍👦',desc:'পরিবারের ৪ জন পর্যন্ত',students:4,teachers:0,devices:2,price:{month:249,week:89},color:'#3f6fd1'},
   school:{key:'school',name:'স্কুল প্ল্যান',emoji:'🏫',desc:'স্কুল ও কোচিং সেন্টারের জন্য',students:100,teachers:5,devices:1,price:{month:1999,week:699},color:'#e76f51'}
  }
 };
 function applyPrices(src){if(!src||!src.plans)return;Object.keys(src.plans).forEach(function(k){var p=CFG.PLANS[k],o=src.plans[k];if(!p||!o)return;if(o.month>=0)p.price.month=+o.month;if(o.week>=0)p.price.week=+o.week;p.disc=Math.min(90,Math.max(0,+o.disc||0));p.dlabel=o.label||'';p.duntil=+o.until||0;});}
 applyPrices(window.SL_PRICES);try{if(isAdmin())applyPrices(JSON.parse(localStorage.getItem('sl_prices')||'null'));}catch(e){}
 function price(k,per){var p=CFG.PLANS[k],b=p.price[per==='week'?'week':'month'],on=p.disc>0&&(!p.duntil||p.duntil>Date.now()),e=on?Math.round(b*(1-p.disc/100)):b;return {base:b,eff:e,disc:on?p.disc:0,label:on?(p.dlabel||''):'',until:on?(p.duntil||0):0};}
 function maxDisc(){var m=0;Object.keys(CFG.PLANS).forEach(function(k){m=Math.max(m,price(k,'month').disc);});return m;}
 var K='sl_demo_v1',DAY=864e5;
 function bn(n){return String(n).replace(/\d/g,function(c){return '০১২৩৪৫৬৭৮৯'.charAt(c);});}
 function en(s){return String(s).replace(/[০-৯]/g,function(c){return '০১২৩৪৫৬৭৮৯'.indexOf(c);});}
 function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
 function get(){try{var x=JSON.parse(localStorage.getItem(K));if(x&&x.acc)return x;}catch(e){}return {acc:{},ses:null,prog:{}};}
 function put(x){try{localStorage.setItem(K,JSON.stringify(x));}catch(e){}}
 function acc(){var x=get();return x.ses&&x.acc[x.ses]||null;}
 function status(a){
  if(!a)return {state:'none',left:0};
  if(a.suspended)return {state:'suspended',left:0};
  var n=Date.now();
  if(a.paidUntil&&a.paidUntil>n)return {state:'active',left:Math.ceil((a.paidUntil-n)/DAY),until:a.paidUntil};
  if(a.trialEnd>n)return {state:'trial',left:Math.ceil((a.trialEnd-n)/DAY),until:a.trialEnd};
  return {state:'expired',left:0,until:Math.max(a.trialEnd||0,a.paidUntil||0)};
 }
 function isAdmin(){try{return +localStorage.getItem('sl_admin_until')>Date.now();}catch(e){return false;}}
 function hasAccess(){if(isAdmin())return true;var s=status(acc()).state;return s==='trial'||s==='active';}
 function chFile(){return decodeURIComponent(location.pathname.split('/').pop()||'').replace(/\.html$/,'');}
 function isFree(f){return CFG.FREE.indexOf(f)>-1;}
 function hash(s){
  s=String(s);
  if(window.crypto&&crypto.subtle&&window.TextEncoder){
   return crypto.subtle.digest('SHA-256',new TextEncoder().encode('sl|'+s)).then(function(b){return [].map.call(new Uint8Array(b),function(x){return ('0'+x.toString(16)).slice(-2);}).join('');});
  }
  var h=5381;for(var i=0;i<s.length;i++)h=((h<<5)+h+s.charCodeAt(i))|0;return Promise.resolve('x'+h);
 }
 function limits(a){return CFG.PLANS[a.kind]||CFG.PLANS.student;}
 function ownerRole(a){return a.kind==='school'?'admin':a.kind==='family'?'parent':'student';}
 function profiles(a){
  var l=[{id:'owner',name:a.name,role:ownerRole(a)}];
  (a.members||[]).forEach(function(m){l.push(m);});return l;
 }
 function counts(a){
  var st=(a.members||[]).filter(function(m){return m.role==='student';}).length+(a.kind==='student'?1:0);
  var te=(a.members||[]).filter(function(m){return m.role==='teacher';}).length;
  return {students:st,teachers:te};
 }
 var ROLE={admin:'স্কুল অ্যাডমিন',parent:'অভিভাবক',student:'শিক্ষার্থী',teacher:'শিক্ষক'};
 function mut(fn){var x=get(),a=x.ses&&x.acc[x.ses];if(!a)return {ok:false,err:'আগে লগইন করো।'};var r=fn(a,x)||{ok:true};if(r.ok)put(x);return r;}
 function pack(a,withMem){var o={e:a.email,h:a.hash,n:a.name,k:a.kind,s:a.school||'',te:a.trialEnd,pu:a.paidUntil||0,su:a.suspended?1:0,c:a.created,v:Date.now()};if(withMem)o.m=a.members||[];return btoa(unescape(encodeURIComponent(JSON.stringify(o)))).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');}
 function unpack(c){try{c=String(c).trim();var i=c.indexOf('#a=');if(i>-1)c=c.slice(i+3);c=c.replace(/-/g,'+').replace(/_/g,'/');while(c.length%4)c+='=';var o=JSON.parse(decodeURIComponent(escape(atob(c))));return o&&o.e&&o.h?o:null;}catch(e){return null;}}
 function mergeIn(o,useMem){var x=get(),a=x.acc[o.e],nw=!a;
  if(!a)a=x.acc[o.e]={email:o.e,hash:o.h,name:o.n,kind:o.k,school:o.s||'',logo:'',created:o.c||Date.now(),trialEnd:o.te,paidUntil:o.pu,suspended:false,members:[],active:'owner',pays:[]};
  a.hash=o.h;a.name=o.n;a.kind=CFG.PLANS[o.k]?o.k:a.kind;a.school=o.s||'';a.trialEnd=o.te;a.paidUntil=o.pu;a.suspended=!!o.su;if(useMem&&o.m)a.members=o.m;
  put(x);return {ok:true,isNew:nw,acc:a};}
 var SL={price:price,maxDisc:maxDisc,applyPrices:applyPrices,isAdmin:isAdmin,pack:pack,unpack:unpack,mergeIn:mergeIn,cfg:CFG,bn:bn,en:en,esc:esc,get:get,put:put,acc:acc,status:status,hasAccess:hasAccess,isFree:isFree,limits:limits,profiles:profiles,counts:counts,ROLE:ROLE,hash:hash,B:B,
  signup:function(o){
   var em=(o.email||'').trim().toLowerCase();
   if(!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(em))return Promise.resolve({ok:false,err:'সঠিক ইমেইল লেখো।'});
   if((o.pass||'').length<6)return Promise.resolve({ok:false,err:'পাসওয়ার্ড কমপক্ষে ৬ অক্ষরের হতে হবে।'});
   if(!(o.name||'').trim())return Promise.resolve({ok:false,err:'নাম লেখো।'});
   if(o.kind==='school'&&!(o.school||'').trim())return Promise.resolve({ok:false,err:'স্কুলের নাম লেখো।'});
   var x=get();if(x.acc[em])return Promise.resolve({ok:false,err:'এই ইমেইলে আগেই অ্যাকাউন্ট আছে। লগইন করো।'});
   return hash(o.pass).then(function(h){
    var n=Date.now();
    x.acc[em]={email:em,hash:h,name:o.name.trim(),kind:CFG.PLANS[o.kind]?o.kind:'student',school:(o.school||'').trim(),logo:o.logo||'',created:n,trialEnd:n+CFG.TRIAL_DAYS*DAY,paidUntil:0,members:[],active:'owner',pays:[]};
    x.ses=em;put(x);return {ok:true};
   });
  },
  login:function(em,pw){
   em=(em||'').trim().toLowerCase();var x=get(),a=x.acc[em];
   if(!a)return Promise.resolve({ok:false,err:'এই ইমেইলে অ্যাকাউন্ট নেই।'});
   return hash(pw).then(function(h){if(h!==a.hash)return {ok:false,err:'পাসওয়ার্ড ভুল।'};x.ses=em;put(x);return {ok:true};});
  },
  logout:function(){var x=get();x.ses=null;put(x);},
  addMember:function(name,role){return mut(function(a){
   name=(name||'').trim();if(!name)return {ok:false,err:'নাম লেখো।'};
   var L=limits(a),c=counts(a);
   if(a.kind==='student')return {ok:false,err:'স্টুডেন্ট প্ল্যানে আর কাউকে যোগ করা যায় না। ফ্যামিলি প্ল্যান নাও।'};
   if(role==='teacher'){if(a.kind!=='school')return {ok:false,err:'শুধু স্কুল প্ল্যানে শিক্ষক যোগ করা যায়।'};if(c.teachers>=L.teachers)return {ok:false,err:'শিক্ষকের লিমিট ('+bn(L.teachers)+' জন) শেষ।'};}
   else{role='student';if(c.students>=L.students)return {ok:false,err:'শিক্ষার্থীর লিমিট ('+bn(L.students)+' জন) শেষ। বড় প্ল্যান নাও।'};}
   a.members.push({id:'m'+Date.now().toString(36)+Math.floor(Math.random()*99),name:name,role:role});return {ok:true};
  });},
  removeMember:function(id){return mut(function(a,x){a.members=a.members.filter(function(m){return m.id!==id;});if(a.active===id)a.active='owner';if(x.prog[a.email])delete x.prog[a.email][id];return {ok:true};});},
  setActive:function(id){return mut(function(a){a.active=id;return {ok:true};});},
  pay:function(plan,period,trx){return mut(function(a){
   trx=(trx||'').trim();if(trx.length<6)return {ok:false,err:'ট্রানজেকশন আইডি (TrxID) লেখো (কমপক্ষে ৬ অক্ষর)।'};
   var P=CFG.PLANS[plan];if(!P)return {ok:false,err:'প্ল্যান বেছে নাও।'};
   var c=counts(a),own=a.kind==='student'?1:0;
   if(plan==='student'&&(a.members||[]).length)return {ok:false,err:'এই অ্যাকাউন্টে সদস্য আছে, স্টুডেন্ট প্ল্যানে নামানো যাবে না।'};
   if(c.students-own+(plan==='student'?1:0)>P.students||c.teachers>P.teachers)return {ok:false,err:'বর্তমান সদস্য সংখ্যা এই প্ল্যানের লিমিটের বেশি।'};
   var days=period==='week'?7:30,n=Date.now(),base=Math.max(n,a.paidUntil||0);
   a.kind=plan;a.paidUntil=base+days*DAY;a.pays.unshift({t:n,plan:plan,period:period,price:price(plan,period).eff,trx:trx});return {ok:true};
  });},
  progress:function(email){return (get().prog[email])||{};},
  record:function(file,s,t){
   var x=get(),a=x.ses&&x.acc[x.ses];if(!a||!t)return;var p=a.active||'owner';
   x.prog[a.email]=x.prog[a.email]||{};x.prog[a.email][p]=x.prog[a.email][p]||{};
   var o=x.prog[a.email][p][file],pc=Math.round(s*100/t);
   if(!o||pc>=o.pc)x.prog[a.email][p][file]={s:s,t:t,pc:pc,w:Date.now()};
   put(x);
  },
  logoFromFile:function(f,cb){
   if(!f)return cb('');var r=new FileReader();r.onload=function(){var im=new Image();im.onload=function(){var c=d.createElement('canvas'),m=Math.min(1,128/Math.max(im.width,im.height));c.width=Math.max(1,im.width*m);c.height=Math.max(1,im.height*m);c.getContext('2d').drawImage(im,0,0,c.width,c.height);cb(c.toDataURL('image/png'));};im.onerror=function(){cb('');};im.src=r.result;};r.onerror=function(){cb('');};r.readAsDataURL(f);
  }
 };
 window.SL=SL;
 /* CSS লোড */
 var lk=d.createElement('link');lk.rel='stylesheet';lk.href=B+'css/saas.css';d.head.appendChild(lk);
 function ready(f){d.readyState==='loading'?d.addEventListener('DOMContentLoaded',f):f();}
 /* উপরের বার */
 function bar(){
  if(d.querySelector('.sl-bar')||d.body.hasAttribute('data-nobar'))return;
  var a=acc(),s=status(a),b=d.createElement('div');b.className='sl-bar';
  var h='';
  if(isAdmin()){
   h+='<div class="who"><b>👑 সুপার অ্যাডমিন</b></div><span class="bd">সব ফ্রি, কোনো লিমিট নেই</span><span class="sp"></span><a href="'+B+'admin.html">অ্যাডমিন প্যানেল</a><a href="'+B+'index.html" class="hide-m">হোম</a>';
  }else if(a){
   var title=a.kind==='school'&&a.school?a.school:'ShikboLab',pl=profiles(a),cur=a.active||'owner';
   h+='<div class="who">'+(a.logo?'<img alt="" src="'+esc(a.logo)+'">':'')+'<b>'+esc(title)+'</b></div>';
   var cls=s.state==='active'?'':s.state==='trial'?' w':' x';
   if(s.state==='suspended')cls=' x';
   var tx=s.state==='active'?'✅ '+CFG.PLANS[a.kind].name+' · '+bn(s.left)+' দিন বাকি':s.state==='trial'?'🎁 ফ্রি ট্রায়াল · '+bn(s.left)+' দিন বাকি':s.state==='suspended'?'🚫 অ্যাকাউন্ট বন্ধ':'⛔ মেয়াদ শেষ';
   h+='<span class="bd'+cls+'">'+tx+'</span><span class="sp"></span>';
   if(pl.length>1)h+='<select id="slwho" aria-label="কে পড়ছে">'+pl.map(function(p){return '<option value="'+esc(p.id)+'"'+(p.id===cur?' selected':'')+'>👤 '+esc(p.name)+'</option>';}).join('')+'</select>';
   h+='<a href="'+B+'account.html">অ্যাকাউন্ট</a><a href="'+B+'plans.html" class="hide-m">প্ল্যান</a><button id="sllo">লগআউট</button>';
  }else{
   h+='<div class="who"><b>ShikboLab</b></div><span class="bd w">🎁 '+bn(CFG.TRIAL_DAYS)+' দিনের ফ্রি ট্রায়াল</span>'+(maxDisc()?'<a class="bd x" href="'+B+'plans.html" style="text-decoration:none">🔥 '+bn(maxDisc())+'% পর্যন্ত ছাড়</a>':'')+'<span class="sp"></span><a href="'+B+'plans.html">প্ল্যান</a><a href="'+B+'account.html#login">লগইন</a><a class="cta" href="'+B+'account.html#signup">ফ্রি শুরু করো</a>';
  }
  b.innerHTML=h;d.body.insertBefore(b,d.body.firstChild);
  var lo=b.querySelector('#sllo');if(lo)lo.onclick=function(){SL.logout();location.reload();};
  var sw=b.querySelector('#slwho');if(sw)sw.onchange=function(){SL.setActive(sw.value);};
 }
 /* অধ্যায়ের তালা */
 function gate(){
  var f=chFile(),a=acc(),s=status(a);
  if(isFree(f)||hasAccess())return;
  var g=d.createElement('div');g.className='sl-gate';
  var msg,btns;
  if(!a){msg='এই অধ্যায় দেখতে একটা ফ্রি অ্যাকাউন্ট খুলে '+bn(CFG.TRIAL_DAYS)+' দিনের ফ্রি ট্রায়াল শুরু করো। সব অধ্যায় ও ল্যাব খোলা থাকবে।';btns='<a class="slb o" href="'+B+'account.html#signup">🎁 ফ্রি ট্রায়াল শুরু করো</a><a class="slb s" href="'+B+'account.html#login">লগইন</a>';}
  else if(s.state==='suspended'){msg='তোমার অ্যাকাউন্ট সাময়িক বন্ধ আছে। অ্যাডমিনের সাথে যোগাযোগ করো।';btns='<a class="slb s" href="'+B+'account.html">অ্যাকাউন্ট দেখো</a>';}
  else{msg='তোমার ট্রায়াল/প্ল্যানের মেয়াদ শেষ। প্ল্যান নিলে আবার সব অধ্যায় খুলবে।';btns='<a class="slb o" href="'+B+'account.html#pay">💳 প্ল্যান নাও</a><a class="slb s" href="'+B+'plans.html">প্ল্যান দেখো</a>';}
  g.innerHTML='<div class="card"><span class="lk">🔒</span><h2>এই অধ্যায়টি প্ল্যানের অন্তর্ভুক্ত</h2><p>'+msg+'</p><div class="row">'+btns+'</div><p style="margin:16px 0 0"><a href="'+B+'index.html" style="color:#1f3a5f;font-weight:600">← সব অধ্যায়</a></p></div>';
  d.body.appendChild(g);d.documentElement.style.overflow='hidden';d.body.style.overflow='hidden';
 }
 /* কুইজ স্কোর ট্র্যাক */
 function track(){
  var sc=d.getElementById('score');if(!sc||!acc())return;var f=chFile();
  new MutationObserver(function(){var m=en(sc.textContent||'').match(/(\d+)\s*\/\s*(\d+)/);if(m&&+m[2]>0)SL.record(f,+m[1],+m[2]);}).observe(sc,{childList:true,characterData:true,subtree:true});
 }
 /* হোমপেজে কার্ডে 🔒/ফ্রি ব্যাজ */
 function badges(){
  function mark(){
   var ok=hasAccess();
   [].forEach.call(d.querySelectorAll('a[href*="chapters/"]:not([data-sl])'),function(el){
    var f=decodeURIComponent((el.getAttribute('href')||'').split('/').pop()).replace(/\.html.*$/,'');
    el.setAttribute('data-sl','1');
    var s=d.createElement('span');
    if(isFree(f)){s.className='sl-lock f';s.textContent='ফ্রি';}else if(ok){return;}else{s.className='sl-lock';s.textContent='🔒 প্ল্যান';}
    el.appendChild(s);
   });
  }
  mark();new MutationObserver(mark).observe(d.body,{childList:true,subtree:true});
 }
 ready(function(){
  bar();
  if(inCh){gate();track();}
  else if(/index\.html$|\/$/.test(location.pathname)||location.pathname.split('/').pop()==='')badges();
 });
})();

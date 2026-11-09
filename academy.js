(function () {
  const courses=window.PaintAcademyCourses||[];
  const storageKey='black-paint-academy-progress-v1';
  const checksKey='black-paint-academy-checks-v1';
  let progress={};
  try { progress=JSON.parse(localStorage.getItem(storageKey)||'{}')||{}; } catch {}
  let checked={};
  try { checked=JSON.parse(localStorage.getItem(checksKey)||'{}')||{}; } catch {}
  let activeTrack='Todos';
  let activeId=courses[0]?.id;
  const escapeHtml=value=>String(value).replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const modal=document.getElementById('modal');
  const body=document.getElementById('modal-body');
  const tracks=['Todos',...new Set(courses.map(course=>course.track))];
  const current=()=>courses.find(course=>course.id===activeId)||courses[0];

  function applySetup(course) {
    const setup=course.setup||{};
    const set=(id,value,event)=>{const el=document.getElementById(id);if(!el)return;el.value=value;el.dispatchEvent(new Event(event,{bubbles:true}));};
    set('brush-material',setup.material||'oil','change');
    set('brush-size',setup.size||12,'input');
    set('brush-opacity',setup.opacity||65,'input');
    set('color-picker',setup.color||'#c9947a','input');
    set('color-picker',setup.color||'#c9947a','change');
    const message=document.getElementById('academy-feedback');
    if(String(course.id||'').startsWith('misuki-') && window.MisukiStudio?.drawConstruction){
      const canvas=document.getElementById('paint-canvas');
      const ctx=canvas?.getContext?.('2d');
      if(ctx){
        const dpr=ctx.getTransform?.().a||1;
        window.MisukiStudio.drawConstruction(ctx, canvas.width/dpr, canvas.height/dpr);
      }
      if(message) message.textContent='Pincel da Misuki + eixos no canvas. A pintura anterior permanece.';
    } else if(message) message.textContent='Configuração aplicada aos controles. A tela não foi alterada.';
  }

  function render() {
    if(!courses.length)return;
    const lesson=current();
    const filtered=courses.filter(course=>activeTrack==='Todos'||course.track===activeTrack);
    const done=courses.filter(course=>progress[course.id]).length;
    const lessonChecks=lesson.checks||[];
    const recorded=Array.isArray(checked[lesson.id])?checked[lesson.id]:[];
    const reference=window.PaintAcademyReferences?.[lesson.referenceId];
    const options=filtered.map(course=>`<option value="${escapeHtml(course.id)}" ${course.id===lesson.id?'selected':''}>${progress[course.id]?'✓ ':''}${escapeHtml(course.title)}</option>`).join('');
    body.innerHTML=`<section class="academy-shell">
      <p class="academy-intro">${courses.length} aulas práticas originais disponíveis sem internet. Faça o exercício no canvas e confira o resultado antes de concluir.</p>
      <div class="academy-progress"><span>${done} de ${courses.length} concluídas</span><progress max="${courses.length}" value="${done}"></progress></div>
      <div class="academy-selectors"><label>Trilha<select id="academy-track">${tracks.map(track=>`<option ${track===activeTrack?'selected':''}>${escapeHtml(track)}</option>`).join('')}</select></label><label>Aula<select id="academy-lesson">${options}</select></label></div>
      <article class="academy-lesson"><small>${escapeHtml(lesson.track)} · ${escapeHtml(lesson.minutes||'15 min')}</small><h4>${escapeHtml(lesson.title)}</h4><p>${escapeHtml(lesson.goal)}</p><ol>${lesson.steps.map(step=>`<li>${escapeHtml(step)}</li>`).join('')}</ol>
      ${lesson.practice?`<h5>Exercício no canvas</h5><p>${escapeHtml(lesson.practice)}</p>`:''}
      ${lessonChecks.length?`<h5>Confira antes de concluir</h5><div class="academy-checklist">${lessonChecks.map((item,i)=>`<label><input type="checkbox" class="academy-check" data-index="${i}" ${recorded[i]?'checked':''}><span>${escapeHtml(item)}</span></label>`).join('')}</div>`:''}
      ${lesson.pitfall?`<p class="academy-pitfall"><strong>Se não funcionou:</strong> ${escapeHtml(lesson.pitfall)}</p>`:''}
      ${reference?`<p><a href="${escapeHtml(reference.url)}" target="_blank" rel="noopener noreferrer">Aprofundar: ${escapeHtml(reference.name)} ↗</a></p>`:''}</article>
      <div class="academy-actions"><button id="academy-setup" class="btn-pill accent">🎨 Preparar pincel</button><button id="academy-done" class="btn-pill primary">${progress[lesson.id]?'✓ Concluída':'Marcar como concluída'}</button></div>
      <div class="academy-actions academy-nav"><button id="academy-prev" class="btn-pill">← Aula anterior</button><button id="academy-next" class="btn-pill">Próxima aula →</button></div>
      <p id="academy-feedback" class="academy-feedback" aria-live="polite">Seu progresso fica salvo neste aparelho.</p>
      <details class="academy-references"><summary>Referências e aulas abertas</summary><p>Os exercícios acima são originais e funcionam sem conexão. Estes sites oferecem material complementar; vídeos e artigos externos não estão incluídos no pacote.</p>${Object.values(window.PaintAcademyReferences||{}).map(ref=>`<p><a href="${escapeHtml(ref.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(ref.name)} ↗</a></p>`).join('')}</details>
    </section>`;
    body.querySelector('#academy-track').addEventListener('change',event=>{activeTrack=event.target.value;const first=courses.find(course=>activeTrack==='Todos'||course.track===activeTrack);if(first)activeId=first.id;render();});
    body.querySelector('#academy-lesson').addEventListener('change',event=>{activeId=event.target.value;render();});
    body.querySelector('#academy-setup').addEventListener('click',()=>applySetup(lesson));
    body.querySelectorAll('.academy-check').forEach(box=>box.addEventListener('change',()=>{
      const choices=Array.isArray(checked[lesson.id])?checked[lesson.id]:[];
      choices[Number(box.dataset.index)]=box.checked;checked[lesson.id]=choices;
      try{localStorage.setItem(checksKey,JSON.stringify(checked));}catch{}
    }));
    body.querySelector('#academy-done').addEventListener('click',()=>{
      if(!progress[lesson.id] && lessonChecks.length && !lessonChecks.every((_,i)=>checked[lesson.id]?.[i])){
        body.querySelector('#academy-feedback').textContent='Confira os três pontos do exercício antes de concluir.';
        return;
      }
      progress[lesson.id]=!progress[lesson.id];
      try{localStorage.setItem(storageKey,JSON.stringify(progress));}catch{}render();
    });
    const index=courses.findIndex(course=>course.id===lesson.id);
    body.querySelector('#academy-prev').addEventListener('click',()=>{activeId=courses[(index-1+courses.length)%courses.length].id;render();});
    body.querySelector('#academy-next').addEventListener('click',()=>{activeId=courses[(index+1)%courses.length].id;render();});
  }

  document.getElementById('btn-academy')?.addEventListener('click',()=>{
    document.getElementById('modal-title').textContent='🎓 Academia de Pintura · Black Paint';
    modal.querySelector('.modal-content').classList.add('academy-modal');
    render();modal.classList.remove('hidden');
  });
})();

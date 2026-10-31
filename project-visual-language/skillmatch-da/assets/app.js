(() => {
  'use strict';

  const DATA = 'data/';
  const number = new Intl.NumberFormat('en-GB');
  const money = value => `£${new Intl.NumberFormat('en-GB', {minimumFractionDigits:Number.isInteger(Number(value)) ? 0 : 2, maximumFractionDigits:2}).format(Number(value) || 0)}`;
  const fmtInt = value => number.format(Number(value) || 0);
  const pct = value => `${(Number(value) * 100).toFixed(1)}%`;
  const $ = selector => document.querySelector(selector);
  const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const get = (findings, id) => Number(findings?.[id]?.value ?? 0);
  const tabLinks = [...document.querySelectorAll('[role="tab"]')];
  const panels = [...document.querySelectorAll('[role="tabpanel"]')];
  const hero = $('#page-hero');
  const heroTitle = $('#hero-title');
  const heroKicker = $('#hero-kicker');
  const overviewPanel = panels.find(panel => panel.id === 'panel-overview');
  const overviewTitle = overviewPanel?.dataset.title;
  let aiGridRevealed = false;

  if ('scrollRestoration' in history) history.scrollRestoration = 'manual';

  function scrollPageTop() {
    requestAnimationFrame(() => window.scrollTo({top: 0, left: 0, behavior: 'instant'}));
  }

  function syncTab(hash = location.hash) {
    const selectedLink = tabLinks.find(link => link.getAttribute('href') === hash);
    let panel = selectedLink
      ? panels.find(item => item.id === selectedLink.getAttribute('aria-controls'))
      : null;
    if (!panel) {
      panel = overviewPanel;
      if (location.hash !== '#overview') history.replaceState(null, '', '#overview');
    }
    if (!panel) return;

    document.documentElement.classList.add('js');
    for (const item of panels) {
      const active = item === panel;
      item.classList.toggle('is-active', active);
      item.setAttribute('aria-hidden', String(!active));
    }
    for (const link of tabLinks) {
      const active = link.getAttribute('aria-controls') === panel.id;
      link.setAttribute('aria-selected', String(active));
      link.tabIndex = active ? 0 : -1;
    }
    const isOverview = panel.id === 'panel-overview';
    hero?.classList.toggle('sm-hero--compact', !isOverview);
    if (heroTitle) heroTitle.textContent = panel.dataset.title || overviewTitle || '';
    if (heroKicker) heroKicker.textContent = panel.dataset.kicker || '';
    const description = $('#hero-description');
    if (description) description.textContent = isOverview
      ? 'One captured week of adverts. Follow the search from the first sighting to the jobs matched to a graduate.'
      : '';
    if (panel.id === 'panel-ai' && !aiGridRevealed) {
      aiGridRevealed = true;
      requestAnimationFrame(() => document.querySelectorAll('#ai-grids .sm-ai-grid-card').forEach(card => card.classList.add('is-revealed')));
    }
  }

  tabLinks.forEach((link, index) => link.addEventListener('keydown', event => {
    let next = null;
    if (event.key === 'ArrowRight' || event.key === 'ArrowDown') next = (index + 1) % tabLinks.length;
    if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') next = (index - 1 + tabLinks.length) % tabLinks.length;
    if (event.key === 'Home') next = 0;
    if (event.key === 'End') next = tabLinks.length - 1;
    if (next !== null) {
      event.preventDefault();
      tabLinks[next].focus();
      activateTab(tabLinks[next].getAttribute('href'));
    }
  }));

  function activateTab(hash) {
    if (!tabLinks.some(link => link.getAttribute('href') === hash)) return;
    if (location.hash !== hash) history.pushState(null, '', hash);
    syncTab(hash);
    scrollPageTop();
  }

  document.addEventListener('click', event => {
    const link = event.target.closest('a[href^="#"]');
    if (!link || !link.matches('[role="tab"], .sm-tab-card, .sm-bridge--link')) return;
    const hash = link.getAttribute('href');
    if (!tabLinks.some(tab => tab.getAttribute('href') === hash)) return;
    event.preventDefault();
    activateTab(hash);
  });

  const restoreTabFromHistory = () => {
    syncTab(location.hash);
    scrollPageTop();
  };
  window.addEventListener('hashchange', restoreTabFromHistory);
  window.addEventListener('popstate', restoreTabFromHistory);
  syncTab();
  scrollPageTop();
  if (document.readyState === 'complete') scrollPageTop();
  else window.addEventListener('load', scrollPageTop, {once: true});

  document.querySelectorAll('[data-course-list]').forEach(list => {
    const cards = [...list.querySelectorAll(':scope > li[data-course-card]')];
    const button = list.nextElementSibling;
    if (cards.length <= 2 || !button?.matches('[data-course-toggle]')) return;
    const extras = cards.slice(2);
    extras.forEach(card => { card.hidden = true; });
    button.hidden = false;
    button.addEventListener('click', () => {
      const expanded = button.getAttribute('aria-expanded') !== 'true';
      extras.forEach(card => { card.hidden = !expanded; });
      button.setAttribute('aria-expanded', String(expanded));
      button.textContent = expanded ? 'Show fewer' : 'Show all';
    });
  });

  function parseCsv(text) {
    const rows = [];
    let row = [], value = '', quoted = false;
    for (let i = 0; i < text.length; i++) {
      const char = text[i];
      if (quoted && char === '"' && text[i + 1] === '"') { value += '"'; i++; }
      else if (char === '"') quoted = !quoted;
      else if (char === ',' && !quoted) { row.push(value); value = ''; }
      else if ((char === '\n' || char === '\r') && !quoted) {
        if (char === '\r' && text[i + 1] === '\n') i++;
        row.push(value); value = '';
        if (row.some(cell => cell !== '')) rows.push(row);
        row = [];
      } else value += char;
    }
    if (value !== '' || row.length) { row.push(value); rows.push(row); }
    if (!rows.length) return [];
    const header = rows.shift();
    return rows.map(cells => Object.fromEntries(header.map((key, i) => [key, cells[i] ?? ''])));
  }

  function chartRows(container, rows, options = {}) {
    if (!container) return;
    const values = rows.map(row => {
      const value = Number(row.value);
      return Number.isFinite(value) ? Math.max(0, value) : 0;
    });
    const requestedMax = Number(options.max);
    const max = Number.isFinite(requestedMax) && requestedMax > 0 ? requestedMax : Math.max(1, ...values);
    const colorClass = options.colorClass || (() => '');
    container.innerHTML = `<div class="sm-bar-chart">${rows.map((row,index)=>{
      const value=values[index];
      const width=Math.min(100,Math.max(0,value/max*100));
      const valueText=options.valueFormat?options.valueFormat(value,row):fmtInt(value);
      const tip=row.tooltip||`${row.label}: ${fmtInt(row.count??value)}${row.denominator?` of ${fmtInt(row.denominator)} (${pct(row.share??value/row.denominator)})`:''}`;
      const zero=value===0?'is-zero':'';
      return `<div class="sm-bar-row" tabindex="0" data-tooltip="${esc(tip)}" aria-label="${esc(tip)}"><span class="sm-bar-label">${esc(row.label)}</span><span class="sm-bar-track"><span class="sm-bar-fill ${colorClass(row)} ${zero}" style="--bar-end:${width}%;width:var(--bar-end)"></span></span><span class="sm-bar-value">${esc(valueText)}</span></div>`;
    }).join('')}</div>`;
    warnOnBrokenBarWidths(container,'.sm-bar-fill',values,rows.map(row=>row.label));
  }

  function warnOnBrokenBarWidths(container, selector, values, labels) {
    const finiteValues = values.filter(Number.isFinite);
    if (!finiteValues.length) return;
    const min = Math.min(...finiteValues);
    const max = Math.max(...finiteValues);
    let observer;
    const check = () => {
      if (container.getBoundingClientRect().width <= 0) return;
      observer?.disconnect();
      window.removeEventListener('hashchange', check);
      container.querySelectorAll(selector).forEach((bar, index) => {
        const value = values[index];
        if (!Number.isFinite(value) || value === min || value === max) return;
        const trackWidth = bar.parentElement?.getBoundingClientRect().width || 0;
        if (!trackWidth) return;
        const width = bar.getBoundingClientRect().width / trackWidth * 100;
        if (width <= 0.1 || width >= 99.9) {
          console.warn(`[SkillMatch bar check] ${container.id} "${labels[index] || `bar ${index + 1}`}" rendered at ${width.toFixed(1)}% for a non-extreme value (${value}; min ${min}, max ${max}).`);
        }
      });
    };
    if (window.ResizeObserver) {
      observer = new ResizeObserver(check);
      observer.observe(container);
    } else {
      window.addEventListener('hashchange', check);
    }
    requestAnimationFrame(check);
  }

  function stackedPair(container, shares) {
    if(!container) return;
    const order=['agency','direct_employer','unclear'];
    const labels={agency:'Agency',direct_employer:'Employer-labelled',unclear:'Unclear'};
    const rows=['data_role_pool','shown'].map(pool=>{
      const subset=shares.filter(row=>row.classification==='after_seed42_review'&&row.pool===pool);
      const name=pool==='shown'?'Jobs matched to a graduate':'Data job adverts';
      const segments=order.map(kind=>subset.find(row=>row.advertiser_type===kind)).filter(Boolean);
      return `<div class="sm-stack-card"><div class="sm-stack-label">${name}</div><div class="sm-stack" role="group" aria-label="${name} advertiser shares">${segments.map(segment=>{
        const share=Number(segment.share)||0,kind=segment.advertiser_type;
        const tip=`${name}: ${labels[kind]}, ${fmtInt(segment.adverts)} adverts (${pct(share)})`;
        return `<span class="sm-stack-segment" data-kind="${kind}" data-tooltip="${esc(tip)}" style="width:${share*100}%" tabindex="0" aria-label="${esc(tip)}">${share>=.055?pct(share).replace('.0',''):''}</span>`;
      }).join('')}</div><div class="sm-stack-counts">${segments.map(segment=>`<span><b>${fmtInt(segment.adverts)}</b> ${labels[segment.advertiser_type]} · ${pct(segment.share).replace('.0','')}</span>`).join(' · ')}</div></div>`;
    }).join('');
    container.innerHTML=`<div class="sm-stack-pair">${rows}</div>`;
  }

  function renderTable(details, columns, rows, download) {
    if (!details) return;
    const host = details.querySelector('div');
    if (!host) return;
    const body = rows.map(row => `<tr>${columns.map(column => {
      const key = typeof column === 'string' ? column : column.key;
      const label = typeof column === 'string' ? column : column.label;
      let value = row[key];
      if (typeof value === 'number') {
        if (/share|percent/i.test(key)) value = pct(value);
        else if (/p_value/i.test(key)) value = value < .001 ? '<0.001' : value.toFixed(3);
        else if (/_gbp|midpoint|salary_(?:min|max)|daily_rate_(?:min|max|median)/i.test(key)) value = money(value);
        else value = fmtInt(value);
      }
      return `<td>${esc(value)}</td>`;
    }).join('')}</tr>`).join('');
    const headers = columns.map(column => `<th scope="col">${esc(typeof column === 'string' ? column : column.label)}</th>`).join('');
    host.innerHTML = `<div class="sm-table-scroll"><div class="sm-table-inner"><table class="sm-data-table"><thead><tr>${headers}</tr></thead><tbody>${body}</tbody></table>${download ? `<a class="sm-download" href="${DATA}${esc(download)}" download>Download this summary CSV</a>` : ''}</div></div>`;
  }

  function renderSummaryTables(summary,csv,findings,ai,skills,pay) {
    const map={
      overview:['overview','snapshot_scope.csv'],churn:['churn','weekly_churn_summary.csv'],funnel:['funnel','funnel_steps_page.csv'],
      advertiser_mix:['advertiser_mix','advertiser_type_shares.csv'],advertiser_hidden:['hidden_by_advertiser','hidden_pay_by_advertiser.csv'],
      advertiser_tests:['advertiser_tests','advertiser_salary_tests.csv'],skills_top15:['skills_top15','skills_top15.csv'],
      generic_summary:['generic_summary','generic_sentence_summary.csv'],generic_groups:['generic_groups','generic_group_comparison.csv'],
      pay_band:['pay_band','pay_band_shown.csv'],hidden_by_source:['hidden_by_source','hidden_pay_by_source.csv'],
      ai_grids:['ai_grids','ai_grid_summary.csv'],ai_specificity:['ai_specificity','ai_specificity_summary.csv'],method:['method','method_summary.csv']
    };
    document.querySelectorAll('[data-table]').forEach(details=>{
      const key=details.dataset.table;
      if(key==='advertiser_hidden'||key==='advertiser_mix'){
        const source=key==='advertiser_hidden'?summary.hidden_by_advertiser:summary.advertiser_mix;
        const rows=source.rows.map(row=>({
          'Label set':row.classification==='after_seed42_review'?'After sample check':'Initial labels',
          'Job group':row.pool==='shown'?'Jobs matched to a graduate':'Full data-job group',
          'Advertiser':row.advertiser_type==='direct_employer'?'Direct employer':row.advertiser_type==='unknown'?'Unclear':row.advertiser_type==='unclear'?'Unclear':'Agency',
          Adverts:Number(row.adverts),
          'Adverts with no salary':Number(row.salary_hidden),
          'Share with no salary':row.share_salary_hidden===null?'—':Number(row.share_salary_hidden),
          Share:Number(row.share)
        }));
        const columns=key==='advertiser_hidden'
          ?['Label set','Job group','Advertiser','Adverts','Adverts with no salary','Share with no salary']
          :['Label set','Job group','Advertiser','Adverts','Share'];
        renderTable(details,columns,rows,key==='advertiser_hidden'?'hidden_pay_by_advertiser.csv':'advertiser_type_shares.csv');
      }else if(key==='wish_list'){
        const rows=csv.wish.map(row=>({Group:row.plot_group,'Essential-count value':fmtInt(row.essential_requirement_count),Adverts:fmtInt(row.adverts),'Share of group':pct(Number(row.share))}));
        renderTable(details,['Group','Essential-count value','Adverts','Share of group'],rows,'wish_list_histogram.csv');
      }else if(key==='daily_rates'){
        const row=csv.daily[0]||{};
        renderTable(details,['Adverts','Minimum daily rate','Median daily rate','Maximum daily rate'],[{Adverts:Number(row.daily_rate_adverts),'Minimum daily rate':Number(row.daily_rate_min_gbp),'Median daily rate':Number(row.daily_rate_median_gbp),'Maximum daily rate':Number(row.daily_rate_max_gbp)}],'daily_rates_summary.csv');
      }else if(key==='generic_by_advertiser'){
        const rows=csv.genericAdvertiser.map(row=>({'Advertiser group':row.advertiser_group,Adverts:Number(row.adverts),median_share:Number(row.median_generic_share),q25_share:Number(row.q25_generic_share),q75_share:Number(row.q75_generic_share)}));
        renderTable(details,[{key:'Advertiser group',label:'Advertiser group'},'Adverts',{key:'median_share',label:'Median share'},{key:'q25_share',label:'Lower quartile'},{key:'q75_share',label:'Upper quartile'}],rows,'generic_share_by_advertiser.csv');
      }else if(key==='course_coverage'){
        const covered=get(findings,'course_covered_essential_demand_pairs');
        const total=get(findings,'explorer_essential_skill_advert_pairs')||Math.round(covered/get(findings,'course_covered_essential_demand_share'));
        renderTable(details,['Course status','Requests','Share'],[
          {'Course status':'Covered in course',Requests:covered,Share:covered/total},
          {'Course status':'Not covered in course',Requests:total-covered,Share:(total-covered)/total}
        ]);
      }else if(key==='advertiser_sample'||key==='method_sample'){
        renderTable(details,['Sample label','Adverts'],[
          {'Sample label':'Agency',Adverts:get(findings,'advertiser_check_agency_count')},
          {'Sample label':'Employer',Adverts:get(findings,'advertiser_check_employer_count')},
          {'Sample label':'Unclear',Adverts:get(findings,'advertiser_check_unclear_count')},
          {'Sample label':'All sampled adverts',Adverts:get(findings,'advertiser_check_sample_size')},
          {'Sample label':'Distinct advertiser names',Adverts:get(findings,'advertiser_check_distinct_names')}
        ]);
      }else if(key==='method_names'){
        renderTable(details,['Measure','Count'],[
          {Measure:'Sampled adverts',Count:get(findings,'advertiser_check_sample_size')},
          {Measure:'Distinct advertiser names',Count:get(findings,'advertiser_check_distinct_names')}
        ]);
      }else if(key==='pay_audit'){
        const noSalary=Number(pay.shown_adverts_without_stated_salary),daily=Number(pay.daily_rate_adverts_separate),total=get(findings,'anchor_shown_adverts');
        renderTable(details,['Measure','Count'],[
          {Measure:'Adverts with stated salary',Count:total-noSalary-daily},
          {Measure:'No stated salary',Count:noSalary},
          {Measure:'Daily rate',Count:daily}
        ]);
      }else if(key==='ai_screening'){
        const total=Number(skills.data_role_full_adverts),mentions=Number(ai.applicant_screening_adverts);
        renderTable(details,['Screening wording','Adverts'],[
          {'Screening wording':'Mentions AI screening',Adverts:mentions},
          {'Screening wording':'No AI screening mention',Adverts:total-mentions},
          {'Screening wording':'All adverts in this group',Adverts:total}
        ]);
      }else if(map[key]){
        const [tableKey,filename]=map[key],table=summary[tableKey];
        if(table) renderTable(details,table.columns,table.rows,filename);
      }
    });
  }

  function barRowsForSkills(skills, group) {
    const denominator = group === 'shown' ? skills.shown_adverts : skills.data_role_full_adverts;
    return skills.skills.map(skill => {
      const part = skill[group];
      return {label:skill.skill,value:Number(part.share_essential),count:Number(part.essential),denominator,share:Number(part.share_essential),course_covered:Boolean(skill.course_covered),tooltip:`${skill.skill}: essential in ${fmtInt(part.essential)} of ${fmtInt(denominator)} adverts (${pct(part.share_essential)}); ${skill.course_covered ? 'covered in this course' : 'not covered in this course'}`};
    }).sort((a,b) => b.value-a.value);
  }

  const skillSort = {key:'essential', direction:'desc'};

  function updateSkillSortHeaders() {
    document.querySelectorAll('#skill-table [data-sort]').forEach(button => {
      const th = button.closest('th');
      const active = button.dataset.sort === skillSort.key;
      if (th) th.setAttribute('aria-sort', active ? (skillSort.direction === 'asc' ? 'ascending' : 'descending') : 'none');
      button.setAttribute('aria-label', `Sort by ${button.textContent.trim()}${active ? `, ${skillSort.direction === 'asc' ? 'ascending' : 'descending'}` : ''}`);
    });
  }

  function renderSkillTable(skills, group, search = '') {
    const body = $('#skill-table tbody');
    if (!body) return;
    const query = search.trim().toLocaleLowerCase('en-GB');
    const entries = skills.skills.filter(item => item.skill.toLocaleLowerCase('en-GB').includes(query));
    const metric = item => {
      if (skillSort.key === 'skill') return item.skill.toLocaleLowerCase('en-GB');
      if (skillSort.key === 'course_covered') return Number(Boolean(item.course_covered));
      if (skillSort.key === 'share_essential') return Number(item[group].share_essential);
      return Number(item[group][skillSort.key]);
    };
    entries.sort((a,b) => {
      const left=metric(a), right=metric(b);
      const comparison=typeof left==='string' ? left.localeCompare(right,'en-GB') : left-right;
      return skillSort.direction==='asc' ? comparison : -comparison;
    });
    updateSkillSortHeaders();
    body.innerHTML = entries.map(item => {
      const part = item[group];
      return `<tr><td>${esc(item.skill)}</td><td>${item.course_covered ? 'Covered' : 'Gap'}</td><td>${fmtInt(part.adverts_asking)}</td><td>${fmtInt(part.essential)}</td><td>${fmtInt(part.desirable)}</td><td>${pct(part.share_essential)}</td></tr>`;
    }).join('');
    const status = $('#skill-table-status');
    if (status) status.textContent = `${entries.length} skills · ${group === 'shown' ? fmtInt(skills.shown_adverts) : fmtInt(skills.data_role_full_adverts)} adverts in this group`;
  }

  function renderOverviewMiniFunnel(container,data) {
    if(!container) return;
    const total=Number(data.total_dots),shown=Number(data.steps[data.steps.length-1]?.count||0);
    const dotCount=Math.ceil(total/10),shownDots=Math.ceil(shown/10);
    const columns=Math.ceil(Math.sqrt(dotCount*1.25)),rows=Math.ceil(dotCount/columns),size=13;
    const width=columns*size+18,height=rows*size+18;
    const circles=Array.from({length:dotCount},(_,index)=>{
      const x=9+(index%columns)*size+size/2,y=9+Math.floor(index/columns)*size+size/2;
      return `<circle cx="${x}" cy="${y}" r="3.8" class="${index<shownDots?'is-shown':'is-filtered'}"/>`;
    }).join('');
    const message=`${fmtInt(total)} collected adverts; ${fmtInt(shown)} matched to a graduate. The full view gives each advert its own dot.`;
    container.innerHTML=`<svg class="sm-mini-funnel-svg" viewBox="0 0 ${width} ${height}" aria-hidden="true">${circles}</svg>`;
    container.tabIndex=0;
    container.dataset.tooltip=message;
    container.setAttribute('aria-label',message);
  }

  function renderFunnelGrid(container,data) {
    if(!container) return;
    const box=container,countNode=$('#funnel-count'),labelNode=$('#funnel-step-label');
    const buttons=[...document.querySelectorAll('#funnel-controls [data-step]')];
    const labels=['Collected','Data jobs','Near me','Entry level','Matched'];
    const colors=['#a9b8de','#8fb0ff','#86a7e8','#7295dc','#e07a5f'];
    const steps=data.steps.map((step,index)=>({label:labels[index]||step.label,count:Number(step.count)}));
    const total=Number(data.total_dots);
    let orderSeed=42;
    const order=Array.from({length:total},(_,index)=>index);
    const random=()=>{orderSeed=(orderSeed*1664525+1013904223)>>>0;return orderSeed/4294967296;};
    for(let index=order.length-1;index>0;index--){const swap=Math.floor(random()*(index+1));[order[index],order[swap]]=[order[swap],order[index]];}
    const canvas=document.createElement('canvas');
    canvas.className='sm-funnel-canvas__surface';
    box.replaceChildren(canvas);
    const context=canvas.getContext('2d');
    if(!context){box.innerHTML='<p class="sm-chart-fallback">The advert counts remain in The data panel below.</p>';return;}
    box.tabIndex=0;
    let currentStep=0,resizeTimer;
    const paint=()=>{
      const rect=box.getBoundingClientRect(),width=Math.max(300,rect.width||900),height=Math.max(380,rect.height||560);
      const ratio=Math.min(2,window.devicePixelRatio||1);
      canvas.width=Math.round(width*ratio);canvas.height=Math.round(height*ratio);
      canvas.style.width='100%';canvas.style.height='100%';
      context.setTransform(ratio,0,0,ratio,0,0);context.clearRect(0,0,width,height);
      const columns=Math.ceil(Math.sqrt(total*width/height)),rows=Math.ceil(total/columns);
      const xGap=(width-24)/Math.max(1,columns-1),yGap=(height-24)/Math.max(1,rows-1);
      const radius=Math.max(1.35,Math.min(3.2,Math.min(xGap,yGap)*.32));
      const retained=steps[currentStep].count;
      for(let index=0;index<total;index++){
        const keep=order[index]<retained;
        const x=12+(index%columns)*xGap,y=12+Math.floor(index/columns)*yGap;
        context.globalAlpha=1;
        context.fillStyle=keep?colors[currentStep]:'#46536b';
        context.shadowColor=currentStep===steps.length-1&&keep?'rgba(224,122,95,.72)':'transparent';
        context.shadowBlur=currentStep===steps.length-1&&keep?radius*2.7:0;
        context.beginPath();context.arc(x,y,radius,0,Math.PI*2);context.fill();
      }
      context.shadowBlur=0;context.globalAlpha=1;
    };
    const setStep=index=>{
      const step=steps[index];currentStep=index;
      if(countNode) countNode.textContent=fmtInt(step.count);
      if(labelNode) labelNode.textContent=step.label;
      buttons.forEach((button,buttonIndex)=>button.setAttribute('aria-pressed',String(buttonIndex===index)));
      const message=`${fmtInt(step.count)} adverts at ${step.label}. One dot is one advert.`;
      box.dataset.tooltip=message;box.setAttribute('aria-label',message);
      paint();
    };
    buttons.forEach(button=>button.addEventListener('click',()=>{
      const target=Number(button.dataset.step);
      if(Number.isInteger(target)&&steps[target])setStep(target);
    }));
    const resize=()=>{clearTimeout(resizeTimer);resizeTimer=setTimeout(paint,80);};
    if(window.ResizeObserver){const observer=new ResizeObserver(resize);observer.observe(box);}
    else window.addEventListener('resize',resize);
    setStep(0);
  }

  function renderWhatIf(data) {
    if(!data?.scenarios?.length) return;
    const scenarios={
      as_taught:data.scenarios.find(row=>row.scenario==='As taught'),
      with_sql_excel:data.scenarios.find(row=>row.scenario==='With SQL and Excel')
    };
    const buttons=[...document.querySelectorAll('#what-if-toggle [data-scenario]')];
    const bar=$('#what-if-coverage-bar'),fill=bar?.querySelector('.sm-stack-segment');
    const scale=$('#what-if-coverage-scale');
    if(scale) scale.innerHTML=(data.scale_ticks||[]).map(value=>`<span><i></i><b>${fmtInt(value)}%</b></span>`).join('');
    const show=name=>{
      const row=scenarios[name];
      if(!row) return;
      const percent=Number(row.coverage_percent);
      const share=Number(row.adverts_every_essential_skill_covered_percent);
      if(fill) fill.style.width=`${percent}%`;
      if(bar){
        bar.setAttribute('aria-valuenow',String(percent));
        bar.setAttribute('aria-valuetext',`${fmtInt(row.covered_skill_requests)} of ${fmtInt(row.essential_skill_requests)} essential skill requests covered, ${percent.toFixed(1)} percent`);
      }
      const kicker=$('#what-if-kicker');
      if(kicker) kicker.textContent=`COURSE COVERAGE · ${row.scenario.toUpperCase()}`;
      const readout=$('#what-if-coverage-readout');
      if(readout) readout.textContent=`${fmtInt(row.covered_skill_requests)} of ${fmtInt(row.essential_skill_requests)} · ${percent.toFixed(1)}%`;
      const count=$('#what-if-advert-count'),total=$('#what-if-advert-total'),description=$('#what-if-advert-share');
      if(count) count.textContent=fmtInt(row.adverts_every_essential_skill_covered);
      if(total) total.textContent=fmtInt(row.adverts_with_essential_skills);
      if(description) description.textContent=`${Math.round(share)}% of eligible adverts.`;
      buttons.forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.scenario===name)));
    };
    buttons.forEach(button=>button.addEventListener('click',()=>show(button.dataset.scenario)));
    show('as_taught');
  }

  function renderStackedSummary(container,labels,values,colors) {
    if(!container)return;
    const total=values.reduce((sum,value)=>sum+Number(value.count),0)||1;
    const html=values.map((item,index)=>{
      const share=Number(item.count)/total,tip=`${item.label}: ${fmtInt(item.count)} of ${fmtInt(total)} (${pct(share)})`;
      return `<span class="sm-stack-segment ${index===0?'is-primary':'is-secondary'}" data-tooltip="${esc(tip)}" style="width:${share*100}%;background:${colors[index]}" tabindex="0" aria-label="${esc(tip)}">${share>=.075?pct(share).replace('.0',''):''}</span>`;
    }).join('');
    container.innerHTML=`<div class="sm-generic-stack" role="group" aria-label="${esc(labels)}"><div class="sm-stack">${html}</div><div class="sm-stack-counts">${values.map(item=>`<span><b>${fmtInt(item.count)}</b> ${esc(item.label)}</span>`).join(' · ')}</div></div>`;
  }

  function renderWishHistogram(container, rows) {
    if (!container) return;
    const bins = [
      {label:'0', test:n=>n===0}, {label:'1–2', test:n=>n>=1&&n<=2}, {label:'3–4', test:n=>n>=3&&n<=4},
      {label:'5–6', test:n=>n>=5&&n<=6}, {label:'7–8', test:n=>n>=7&&n<=8}, {label:'9–10', test:n=>n>=9&&n<=10}, {label:'11+', test:n=>n>=11}
    ];
    const grouped = ['Matched','Senior'].map(group => {
      const subset = rows.filter(row => row.plot_group === group);
      const total = subset.reduce((sum,row)=>sum+Number(row.adverts),0);
      return {group,total,bins:bins.map(bin=>({label:bin.label,count:subset.filter(row=>bin.test(Number(row.essential_requirement_count))).reduce((sum,row)=>sum+Number(row.adverts),0)}))};
    });
    const plotted = bins.flatMap((bin,index)=>grouped.map(group=>({
      label:`${group.group}, ${bin.label}`,
      value:group.bins[index].count/group.total
    })));
    const maxShare = Math.max(...plotted.map(item=>item.value),.01);
    const html = bins.map((bin,index)=>`<div class="sm-hist-row"><span class="sm-hist-bin">${bin.label}</span><div class="sm-hist-series">${grouped.map(group=>{
      const item=group.bins[index],share=item.count/group.total;
      const title=`${group.group}, ${bin.label} essential requirements: ${fmtInt(item.count)} of ${fmtInt(group.total)} adverts (${pct(share)})`;
      const width=Math.min(100,Math.max(0,share/maxShare*100));
      return `<div class="sm-hist-track" tabindex="0" data-tooltip="${esc(title)}" aria-label="${esc(title)}"><span class="sm-hist-name">${group.group}</span><span class="sm-hist-bar"><span class="sm-hist-fill ${group.group==='Senior'?'is-senior':''}" style="width:${width}%"></span></span><span class="sm-hist-count">${fmtInt(item.count)}</span></div>`;
    }).join('')}</div></div>`).join('');
    container.innerHTML=`<div class="sm-histogram">${html}</div>`;
    warnOnBrokenBarWidths(container, '.sm-hist-fill', plotted.map(item=>item.value), plotted.map(item=>item.label));
  }

  function renderPayBand(container,low,q1,median,q3,high) {
    if(!container)return;
    const scaleMin=Number(low),scaleMax=Number(high),pos=value=>(Number(value)-scaleMin)/(scaleMax-scaleMin)*100;
    const marks=[['Lower quartile',q1],['Median',median],['Upper quartile',q3]];
    const tip=`Annual salary midpoints: minimum ${money(low)}, lower quartile ${money(q1)}, median ${money(median)}, upper quartile ${money(q3)}, maximum ${money(high)}`;
    container.innerHTML=`<div class="sm-pay-band" role="img" tabindex="0" data-tooltip="${esc(tip)}" aria-label="${esc(tip)}"><div class="sm-pay-track"><span class="sm-pay-range" style="left:0;width:100%"></span><span class="sm-pay-iqr" style="left:${pos(q1)}%;width:${pos(q3)-pos(q1)}%"></span><span class="sm-pay-median" style="left:${pos(median)}%"></span></div><div class="sm-pay-axis"><span>${money(scaleMin)}</span><span>${money(scaleMax)}</span></div><div class="sm-pay-mark-grid sm-pay-mark-grid--three">${marks.map(([label,value])=>`<div><span>${label}</span><strong>${money(value)}</strong></div>`).join('')}</div></div>`;
  }

  function renderDailyRange(container,row) {
    if(!container||!row)return;
    const min=Number(row.daily_rate_min_gbp),median=Number(row.daily_rate_median_gbp),max=Number(row.daily_rate_max_gbp);
    const pos=value=>(value-min)/(max-min)*100;
    const tip=`Daily rates: ${fmtInt(row.daily_rate_adverts)} adverts; minimum ${money(min)}, median ${money(median)}, maximum ${money(max)} per day`;
    container.innerHTML=`<div class="sm-pay-band" role="img" tabindex="0" data-tooltip="${esc(tip)}" aria-label="${esc(tip)}"><div class="sm-pay-track"><span class="sm-pay-range" style="left:0;width:100%"></span><span class="sm-pay-median" style="left:${pos(median)}%"></span></div><div class="sm-pay-axis"><span>${money(min)}</span><span>${money(max)}</span></div><div class="sm-pay-mark-grid sm-pay-mark-grid--three"><div><span>Minimum</span><strong>${money(min)}/day</strong></div><div><span>Median</span><strong>${money(median)}/day</strong></div><div><span>Maximum</span><strong>${money(max)}/day</strong></div></div></div>`;
  }

  function renderPayVisibility(container,pay,total) {
    if(!container)return;
    const missing=Number(pay.shown_adverts_without_stated_salary),daily=Number(pay.daily_rate_adverts_separate),salary=Math.max(0,Number(total)-missing-daily);
    const squares=Array.from({length:Number(total)},(_,index)=>{
      const type=index<missing?'is-missing':index<missing+daily?'is-context':'is-covered';
      return `<i class="sm-pay-square ${type}" aria-hidden="true"></i>`;
    }).join('');
    const tip=`${fmtInt(missing)} of ${fmtInt(total)} matched adverts give no salary; ${fmtInt(salary)} give annual or hourly pay; ${fmtInt(daily)} give daily rates`;
    container.innerHTML=`<div class="sm-pay-squares" style="--pay-columns:${Math.ceil(Math.sqrt(Number(total)))}" role="img" tabindex="0" data-tooltip="${esc(tip)}" aria-label="${esc(tip)}">${squares}</div>`;
  }

  function renderAiGrids(container,data) {
    if(!container)return;
    container.innerHTML=data.groups.map(group=>{
      const total=Number(group.total),mentioned=Number(group.mentioned),without=total-mentioned,columns=Math.ceil(Math.sqrt(total));
      const squares=Array.from({length:total},(_,index)=>{
        const type=index<mentioned?'is-lit':'is-gap';
        return `<i class="sm-square ${type}" style="--square-delay:${Math.min(index*2,300)}ms" aria-hidden="true"></i>`;
      }).join('');
      const tip=`${fmtInt(mentioned)} of ${fmtInt(total)} ${group.label.toLowerCase()} mention AI; ${fmtInt(without)} do not (${pct(mentioned/total)})`;
      return `<article class="sm-ai-grid-card"><h4>${esc(group.label)}</h4><p>${fmtInt(mentioned)} mention AI · ${fmtInt(without)} do not</p><div class="sm-squares" style="--square-columns:${columns}" role="img" tabindex="0" data-tooltip="${esc(tip)}" aria-label="${esc(tip)}">${squares}</div><p class="sm-ai-grid-foot">${fmtInt(mentioned)} / ${fmtInt(total)} · ${pct(mentioned/total)}</p></article>`;
    }).join('');
  }

  function draw(data) {
    const {findings,summary,funnel,ai,pay,skills,csv}=data;
    const stepLabels=['Collected','Data jobs','Near me','Entry level','Matched'];
    const overviewSteps=funnel.steps.map((step,index)=>({label:stepLabels[index]||step.label,value:Number(step.count),count:Number(step.count),tooltip:`${stepLabels[index]||step.label}: ${fmtInt(step.count)} adverts`}));
    renderOverviewMiniFunnel($('#overview-funnel'),funnel);
    chartRows($('#method-funnel'),overviewSteps,{max:Math.max(...overviewSteps.map(step=>step.value)),valueFormat:value=>fmtInt(value)});

    const churnRows=[
      {label:'New adverts',value:get(findings,'weekly_churn_new_listings'),count:get(findings,'weekly_churn_new_listings'),tooltip:`New adverts: ${fmtInt(get(findings,'weekly_churn_new_listings'))}`},
      {label:'No longer seen',value:get(findings,'weekly_churn_gone_listings'),count:get(findings,'weekly_churn_gone_listings'),tooltip:`Adverts missing from the next collection: ${fmtInt(get(findings,'weekly_churn_gone_listings'))}`}
    ];
    const churnMax=Math.max(...churnRows.map(row=>row.value));
    chartRows($('#overview-churn'),churnRows,{max:churnMax,colorClass:row=>row.label==='No longer seen'?'is-gap':''});
    renderFunnelGrid($('#funnel-grid'),funnel);
    chartRows($('#haystack-churn'),churnRows,{max:churnMax,colorClass:row=>row.label==='No longer seen'?'is-gap':''});

    stackedPair($('#advertiser-mix'),summary.advertiser_mix.rows);
    const hiddenRows=summary.hidden_by_advertiser.rows.filter(row=>row.classification==='after_seed42_review'&&row.pool==='data_role_pool');
    const advertiserHidden=hiddenRows.map(row=>{
      const label=row.advertiser_type==='direct_employer'?'Direct employers':row.advertiser_type==='agency'?'Agencies':'Unclear names';
      return {label,value:Number(row.share_salary_hidden),count:Number(row.salary_hidden),denominator:Number(row.adverts),share:Number(row.share_salary_hidden),tooltip:`${label}: ${fmtInt(row.salary_hidden)} of ${fmtInt(row.adverts)} adverts omit pay (${pct(row.share_salary_hidden)})`};
    });
    chartRows($('#advertiser-hidden'),advertiserHidden,{max:1,valueFormat:value=>pct(value),colorClass:row=>row.label==='Direct employers'?'is-accent':row.label==='Unclear names'?'is-stretch':''});

    const fullSkills=barRowsForSkills(skills,'data_role_full').slice(0,15);
    chartRows($('#skills-bars'),fullSkills,{max:Math.max(...fullSkills.map(row=>row.value)),valueFormat:value=>pct(value),colorClass:row=>row.course_covered?'':'is-gap'});
    renderWhatIf(data.what_if_coverage);
    renderWishHistogram($('#wishlist-chart'),csv.wish);
    const genericRows=summary.generic_summary.rows;
    const generic=genericRows.find(row=>row.label==='generic')||{sentences:get(findings,'generic_sentence_count'),share:get(findings,'generic_sentence_share')};
    const concrete=genericRows.find(row=>row.label==='concrete')||{sentences:0,share:0};
    renderStackedSummary($('#generic-split'),'Broad and specific requests',[
      {label:'Broad requests',count:Number(generic.sentences)},{label:'Specific requests',count:Number(concrete.sentences)}
    ],['#e07a5f','#2b3a55']);
    const genericGroups=csv.genericAdvertiser.map(row=>{const label=row.advertiser_group==='Direct employer (reviewed)'?'Direct employers':row.advertiser_group;return {label,value:Number(row.median_generic_share),count:Number(row.adverts),tooltip:`${label}: median ${pct(row.median_generic_share)} across ${fmtInt(row.adverts)} adverts`};});
    chartRows($('#generic-groups'),genericGroups,{max:Math.max(.25,...genericGroups.map(row=>row.value)),valueFormat:value=>pct(value),colorClass:row=>row.label.toLowerCase().includes('unclear')?'is-stretch':''});

    renderPayBand($('#pay-band'),pay.annual_midpoint_min,pay.annual_midpoint_q25,pay.annual_midpoint_median,pay.annual_midpoint_q75,pay.annual_midpoint_max);
    renderPayVisibility($('#pay-visibility'),pay,get(findings,'anchor_shown_adverts'));
    renderDailyRange($('#daily-rates'),csv.daily[0]);
    const sourceRows=summary.hidden_by_source.rows.map(row=>({label:row.source_family,value:Number(row.share_salary_hidden),count:Number(row.salary_hidden),denominator:Number(row.adverts),tooltip:`${row.source_family}: ${fmtInt(row.salary_hidden)} of ${fmtInt(row.adverts)} adverts omit pay (${pct(row.share_salary_hidden)})`}));
    chartRows($('#pay-hidden'),sourceRows,{max:1,valueFormat:value=>pct(value),colorClass:()=>'is-gap'});

    renderAiGrids($('#ai-grids'),ai);
    const specificity=ai.specificity;
    renderStackedSummary($('#ai-specificity'),'AI sentence labels',[
      {label:'Specific',count:Number(specificity.specific_sentences)},{label:'Vague',count:Number(specificity.sentence_total-specificity.specific_sentences)}
    ],['#2b3a55','#e07a5f']);

    const groupSelect=$('#skill-group'),searchInput=$('#skill-search'),showAll=$('#skill-show-all');
    const updateExplore=()=>{
      const group=groupSelect?.value||'data_role_full';
      const query=searchInput?.value||'';
      const rows=barRowsForSkills(skills,group).filter(row=>row.label.toLocaleLowerCase('en-GB').includes(query.trim().toLocaleLowerCase('en-GB')));
      const visibleRows=showAll?.checked?rows:rows.slice(0,15);
      chartRows($('#explore-bars'),visibleRows,{max:Math.max(1,...visibleRows.map(row=>row.value)),valueFormat:value=>pct(value),colorClass:row=>row.course_covered?'':'is-gap'});
      renderSkillTable(skills,group,query);
    };
    groupSelect?.addEventListener('change',updateExplore);
    searchInput?.addEventListener('input',updateExplore);
    showAll?.addEventListener('change',updateExplore);
    document.querySelectorAll('#skill-table [data-sort]').forEach(button=>button.addEventListener('click',()=>{
      if(skillSort.key===button.dataset.sort)skillSort.direction=skillSort.direction==='asc'?'desc':'asc';
      else{skillSort.key=button.dataset.sort;skillSort.direction=button.dataset.sort==='skill'?'asc':'desc';}
      updateExplore();
    }));
    updateExplore();

    const sampleSize=get(findings,'advertiser_check_sample_size');
    const sample=[
      {label:'Agency',value:get(findings,'advertiser_check_agency_count'),count:get(findings,'advertiser_check_agency_count'),tooltip:`Agency: ${get(findings,'advertiser_check_agency_count')} of ${sampleSize} sampled adverts`},
      {label:'Employer',value:get(findings,'advertiser_check_employer_count'),count:get(findings,'advertiser_check_employer_count'),tooltip:`Employer: ${get(findings,'advertiser_check_employer_count')} of ${sampleSize} sampled adverts`},
      {label:'Unclear',value:get(findings,'advertiser_check_unclear_count'),count:get(findings,'advertiser_check_unclear_count'),tooltip:`Unclear from the name: ${get(findings,'advertiser_check_unclear_count')} of ${sampleSize} sampled adverts`}
    ];
    chartRows($('#method-sample'),sample,{max:sampleSize,colorClass:row=>row.label==='Unclear'?'is-stretch':''});
    const names=[
      {label:'Sampled adverts',value:sampleSize,count:sampleSize},
      {label:'Distinct names',value:get(findings,'advertiser_check_distinct_names'),count:get(findings,'advertiser_check_distinct_names')}
    ];
    chartRows($('#method-names'),names,{max:Math.max(...names.map(row=>row.value)),colorClass:row=>row.label==='Distinct names'?'is-accent':''});

    renderSummaryTables(summary,csv,findings,ai,skills,pay);
    syncTab();
  }

  async function load() {
    let data = window.DA_DATA;
    if (!data) {
      const [findings,summary,funnel,ai,pay,skills,wishText,dailyText,genericText]=await Promise.all([
        fetch(`${DATA}findings.json`).then(response=>{if(!response.ok)throw new Error('findings');return response.json();}),
        fetch(`${DATA}summary_tables.json`).then(response=>{if(!response.ok)throw new Error('summary tables');return response.json();}),
        fetch(`${DATA}funnel_steps.json`).then(response=>{if(!response.ok)throw new Error('funnel');return response.json();}),
        fetch(`${DATA}ai_grids.json`).then(response=>{if(!response.ok)throw new Error('AI groups');return response.json();}),
        fetch(`${DATA}pay_band.json`).then(response=>{if(!response.ok)throw new Error('pay band');return response.json();}),
        fetch(`${DATA}skill_explorer.json`).then(response=>{if(!response.ok)throw new Error('skill explorer');return response.json();}),
        fetch(`${DATA}wish_list_histogram.csv`).then(response=>{if(!response.ok)throw new Error('wish histogram');return response.text();}),
        fetch(`${DATA}daily_rates_summary.csv`).then(response=>{if(!response.ok)throw new Error('daily rates');return response.text();}),
        fetch(`${DATA}generic_share_by_advertiser.csv`).then(response=>{if(!response.ok)throw new Error('generic advertiser summary');return response.text();})
      ]);
      data = {
        findings,
        summary_tables: summary,
        funnel_steps: funnel,
        ai_grids: ai,
        pay_band: pay,
        skill_explorer: skills,
        wish_list_histogram: parseCsv(wishText),
        daily_rates_summary: parseCsv(dailyText),
        generic_share_by_advertiser: parseCsv(genericText)
      };
    }
    draw({
      findings: data.findings,
      summary: data.summary_tables,
      funnel: data.funnel_steps,
      ai: data.ai_grids,
      pay: data.pay_band,
      skills: data.skill_explorer,
      csv: {
        wish: Array.isArray(data.wish_list_histogram) ? data.wish_list_histogram : parseCsv(data.wish_list_histogram),
        daily: Array.isArray(data.daily_rates_summary) ? data.daily_rates_summary : parseCsv(data.daily_rates_summary),
        genericAdvertiser: Array.isArray(data.generic_share_by_advertiser) ? data.generic_share_by_advertiser : parseCsv(data.generic_share_by_advertiser)
      }
    });
  }

  load().catch(error=>{
    console.error('Summary chart data failed to load:',error);
    document.querySelectorAll('.sm-chart').forEach(chart=>{
      if(!chart.innerHTML) chart.innerHTML='<p class="sm-chart-fallback">The visual summary did not load. The counts and explanation beside this chart remain available.</p>';
    });
  });
})();

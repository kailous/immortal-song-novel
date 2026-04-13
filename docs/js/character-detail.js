/**
 * 角色/道具详情页逻辑 — 加载JSON、渲染属性、词典浮窗
 */
(function () {
  'use strict';

  // 词典数据（由 fetchGlossary 填充）
  let glossaryData = {};

  // 本地 .md 文件名 → 图鉴页 id（跳转）
  const localMdMap = {
    '01_初始外挂_次元手环.md': 'bracelet',
  };

  // 本地 .md 文件名 → 词典词条 key（浮窗）
  const glossaryFileMap = {
    '07_核心机制_量子重置与时空变异.md':   'quantum-reset',
    '02_量子重置与时空变异起源.md':        'quantum-reset',
    '01_核心防崩坏法则_反套路铁律.md':    'anti-collapse',
    '03_基因变异与异能限度_血脉传承.md':  'gene-mutation',
    '02_技术殖民与和平演变准则.md':       'tech-colonize',
    '01_千年集权史_社会制度与阶级矛盾.md':'social-system',
    '03_贪腐危机与血亲审判_法律铁律.md': 'corruption-trial',
    '04_特殊监察体系_守望者.md':          'watcher-nezha',
  };

  // ── 初始化 ──────────────────────────────────────────────
  document.addEventListener('DOMContentLoaded', function () {
    const params = new URLSearchParams(window.location.search);
    const id = params.get('id');

    if (!id) {
      window.location.href = 'characters.html';
      return;
    }

    initGlossaryPopover();

    Promise.all([
      fetch('data/characters.json').then(r => r.json()),
      fetch('data/glossary.json').then(r => r.json()).catch(() => ({})),
    ]).then(([chars, glossary]) => {
      glossaryData = glossary;
      const item = chars[id];
      if (!item) {
        window.location.href = 'characters.html';
        return;
      }
      renderDetail(item);
    }).catch(err => {
      console.error('Error loading data:', err);
      document.getElementById('loader').innerHTML =
        '<p style="color:var(--accent-red);">档案读取失败</p>';
    });
  });

  // ── 词典浮窗 ────────────────────────────────────────────
  function initGlossaryPopover() {
    const overlay = document.createElement('div');
    overlay.id = 'glossary-overlay';
    overlay.innerHTML = `
      <div id="glossary-panel" role="dialog" aria-modal="true">
        <div id="glossary-panel-header">
          <div>
            <div id="glossary-panel-title"></div>
            <div id="glossary-panel-subtitle"></div>
          </div>
          <button id="glossary-close" aria-label="关闭">✕</button>
        </div>
        <div id="glossary-panel-body"></div>
      </div>
    `;
    document.body.appendChild(overlay);

    overlay.addEventListener('click', function (e) {
      if (e.target === overlay) closeGlossary();
    });
    document.getElementById('glossary-close').addEventListener('click', closeGlossary);

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeGlossary();
    });
  }

  function openGlossary(key) {
    const entry = glossaryData[key];
    if (!entry) return;

    document.getElementById('glossary-panel-title').textContent = entry.title || '';
    document.getElementById('glossary-panel-subtitle').textContent = entry.subtitle || '';

    let html = '';
    if (entry.sections && entry.sections.length) {
      entry.sections.forEach(s => {
        html += `<div class="glossary-section">`;
        if (s.heading) html += `<h4>${s.heading}</h4>`;
        html += parseMarkdown(s.content || '');
        html += `</div>`;
      });
    } else if (entry.content) {
      html = parseMarkdown(entry.content);
    }

    document.getElementById('glossary-panel-body').innerHTML = html;
    document.getElementById('glossary-panel-body').scrollTop = 0;

    const overlay = document.getElementById('glossary-overlay');
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function closeGlossary() {
    document.getElementById('glossary-overlay').classList.remove('active');
    document.body.style.overflow = '';
  }

  // 委托：捕获浮窗触发点击
  document.addEventListener('click', function (e) {
    const trigger = e.target.closest('.glossary-link');
    if (trigger) {
      e.preventDefault();
      openGlossary(trigger.dataset.key);
    }
  });

  // ── 渲染主体 ─────────────────────────────────────────────
  function renderDetail(item) {
    const loader    = document.getElementById('loader');
    const container = document.getElementById('char-detail-container');
    const titleEl   = document.getElementById('char-title');
    const aliasEl   = document.getElementById('char-alias');
    const imgEl     = document.getElementById('char-img');
    const introEl   = document.getElementById('char-intro');
    const sectionsEl= document.getElementById('char-sections');

    document.title = `${item.title} — 档案公开`;
    titleEl.textContent = item.title;
    aliasEl.textContent = item.alias;

    if (item.image) {
      imgEl.src = `images/${item.image}`;
      imgEl.alt = item.title;
      const heroBg = document.getElementById('hero-bg');
      heroBg.style.backgroundImage    = `url(images/${item.image})`;
      heroBg.style.backgroundSize     = 'cover';
      heroBg.style.backgroundPosition = 'center';
    }

    introEl.innerHTML = parseMarkdown(item.intro);

    let html = '';
    item.sections.forEach(s => {
      const isTimeline = s.heading.includes('生平志');
      html += `
        <div class="detail-section">
          <h2>${s.heading}</h2>
          <div class="detail-body">
            ${isTimeline ? renderTimeline(s.content) : parseMarkdown(s.content)}
          </div>
        </div>
      `;
    });
    sectionsEl.innerHTML = html;

    loader.style.display    = 'none';
    container.style.display = 'block';

    setTimeout(() => {
      document.querySelectorAll('.timeline-item').forEach((el, index) => {
        setTimeout(() => el.classList.add('visible'), index * 150);
      });
    }, 300);
  }

  // ── 时间线渲染 ───────────────────────────────────────────
  function renderTimeline(content) {
    if (!content) return '';

    const lines = content.trim().split('\n');
    let html = '<div class="timeline">';

    lines.forEach(line => {
      let item = line.trim().replace(/^\*\s+/, '').replace(/^-\s+/, '');
      if (!item) return;
      item = item.replace(/\[[\/\sxX]\]\s*/, '');

      const isCurrent = item.includes('当前状态');
      let time = '', body = '';
      const timeMatch = item.match(/^\*\*(.*?)\*\*[:：]\s*(.*)$/);
      if (timeMatch) {
        time = timeMatch[1];
        body = timeMatch[2];
      } else {
        body = item;
      }

      html += `
        <div class="timeline-item ${isCurrent ? 'active' : ''}">
          <div class="timeline-node"></div>
          <div class="timeline-content">
            ${time ? `<span class="timeline-time">${time}</span>` : ''}
            <div class="timeline-body">${parseMarkdown(body)}</div>
          </div>
        </div>
      `;
    });

    html += '</div>';
    return html;
  }

  // ── Markdown 解析 ────────────────────────────────────────
  function parseMarkdown(text) {
    if (!text) return '';

    let html = text.trim();

    // 去掉任务标记 [/] [ ] [x]
    html = html.replace(/\[[\/\sxX]\]\s*/g, '');

    // 标题 # / ## / ###
    html = html.replace(/^######\s+(.*)$/gm, '<h6>$1</h6>');
    html = html.replace(/^#####\s+(.*)$/gm,  '<h5>$1</h5>');
    html = html.replace(/^####\s+(.*)$/gm,   '<h4>$1</h4>');
    html = html.replace(/^###\s+(.*)$/gm,    '<h3>$1</h3>');
    html = html.replace(/^##\s+(.*)$/gm,     '<h2>$1</h2>');
    html = html.replace(/^#\s+(.*)$/gm,      '<h1>$1</h1>');

    // 水平分割线
    html = html.replace(/^---+$/gm, '<hr class="md-hr">');

    // GitHub Alerts  > [!NOTE] ...
    html = html.replace(/>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\n>\s*(.*)/g,
      (_, type, content) =>
        `<div class="alert alert-${type.toLowerCase()}"><strong>${type}:</strong> ${content}</div>`
    );

    // 引用块 > 文字
    html = html.replace(/^((?:>\s?.*\n?)+)/gm, match => {
      const inner = match.replace(/^>\s?/gm, '').trim();
      return `<blockquote>${inner}</blockquote>`;
    });

    // 链接 [文字](url)
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (match, label, url) => {
      // 外部链接
      if (/^https?:\/\//i.test(url)) {
        return `<a href="${url}" target="_blank" rel="noopener">${label}</a>`;
      }
      const filename = url.split('/').pop();
      // 跳转到图鉴详情页
      if (localMdMap[filename]) {
        return `<a href="character-detail.html?id=${localMdMap[filename]}" class="md-local-link">${label}</a>`;
      }
      // 词典浮窗
      if (glossaryFileMap[filename]) {
        return `<a href="#" class="glossary-link md-local-link" data-key="${glossaryFileMap[filename]}">${label}</a>`;
      }
      return `<span class="md-local-ref">${label}</span>`;
    });

    // 加粗 **text**
    html = html.replace(/\*\*([\s\S]*?)\*\*/g, '<strong>$1</strong>');

    // 斜体 *text*
    html = html.replace(/(?<!\*)\*(?!\*)([\s\S]*?)(?<!\*)\*(?!\*)/g, '<em>$1</em>');

    // 行内代码 `code`
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

    // 无序列表
    html = html.replace(/^[*-]\s+(.*)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>[\s\S]*?<\/li>(?:\n<li>[\s\S]*?<\/li>)*)/g, '<ul>$1</ul>');

    // 有序列表 1. item
    html = html.replace(/^\d+\.\s+(.*)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>[\s\S]*?<\/li>(?:\n<li>[\s\S]*?<\/li>)*)/g, m => {
      if (m.startsWith('<li>')) return `<ol>${m}</ol>`;
      return m;
    });

    // 段落分组
    const paragraphs = html.split(/\n\n+/);
    html = paragraphs.map(p => {
      const t = p.trim();
      if (!t) return '';
      if (/^<(ul|ol|blockquote|div|hr|h[1-6])/.test(t)) return t;
      return `<p>${t.replace(/\n/g, '<br>')}</p>`;
    }).join('');

    return html;
  }

})();

/**
 * 角色/道具详情页逻辑 — 加载JSON、渲染属性
 */
(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {
    const params = new URLSearchParams(window.location.search);
    const id = params.get('id');

    if (!id) {
      window.location.href = 'characters.html';
      return;
    }

    fetch('data/characters.json')
      .then(res => res.json())
      .then(data => {
        const item = data[id];
        if (!item) {
          window.location.href = 'characters.html';
          return;
        }

        renderDetail(item);
      })
      .catch(err => {
        console.error('Error loading character:', err);
        document.getElementById('loader').innerHTML = '<p style="color:var(--accent-red);">档案读取失败</p>';
      });
  });

  function renderDetail(item) {
    const loader = document.getElementById('loader');
    const container = document.getElementById('char-detail-container');
    const titleEl = document.getElementById('char-title');
    const aliasEl = document.getElementById('char-alias');
    const imgEl = document.getElementById('char-img');
    const introEl = document.getElementById('char-intro');
    const sectionsEl = document.getElementById('char-sections');

    // Title & Metadata
    document.title = `${item.title} — 档案公开`;
    titleEl.textContent = item.title;
    aliasEl.textContent = item.alias;
    
    // Image
    if (item.image) {
      imgEl.src = `images/${item.image}`;
      imgEl.alt = item.title;
      // Also blur background
      document.getElementById('hero-bg').style.backgroundImage = `url(images/${item.image})`;
      document.getElementById('hero-bg').style.backgroundSize = 'cover';
      document.getElementById('hero-bg').style.backgroundPosition = 'center';
    }

    // Intro
    introEl.innerHTML = parseMarkdown(item.intro);

    // Sections
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

    // Show content
    loader.style.display = 'none';
    container.style.display = 'block';

    // Trigger reveal for timeline items
    setTimeout(() => {
        document.querySelectorAll('.timeline-item').forEach((el, index) => {
            setTimeout(() => {
                el.classList.add('visible');
            }, index * 150);
        });
    }, 300);
  }

  function renderTimeline(content) {
    if (!content) return "";
    
    const lines = content.trim().split('\n');
    let html = '<div class="timeline">';
    
    lines.forEach((line, index) => {
        let item = line.trim().replace(/^\*\s+/, '').replace(/^-\s+/, '');
        if (!item) return;

        // Strip project task markers like [/] or [ ] or [x] for the UI
        item = item.replace(/\[[\/\sxX]\]\s*/, '');

        const isCurrent = item.includes('当前状态');
        
        // Parse time and body
        let time = '';
        let body = '';
        
        // Match **Time**：Description or **Time**: Description
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

  function parseMarkdown(text) {
    if (!text) return "";

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

    // 水平分割线 ---（独立行）
    html = html.replace(/^---+$/gm, '<hr class="md-hr">');

    // GitHub Alerts  >  [!NOTE] ...
    html = html.replace(/>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\n>\s*(.*)/g, (match, type, content) => {
      return `<div class="alert alert-${type.toLowerCase()}"><strong>${type}:</strong> ${content}</div>`;
    });

    // 引用块 > 文字（整段）
    html = html.replace(/^((?:>\s?.*\n?)+)/gm, (match) => {
      const inner = match.replace(/^>\s?/gm, '').trim();
      return `<blockquote>${inner}</blockquote>`;
    });

    // 链接 [文字](url)
    // 本地文件路径（不以 http 开头）→ 只保留文字，不生成链接
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (match, label, url) => {
      if (/^https?:\/\//i.test(url)) {
        return `<a href="${url}" target="_blank" rel="noopener">${label}</a>`;
      }
      return `<span class="md-local-ref">${label}</span>`;
    });

    // 加粗 **text**
    html = html.replace(/\*\*([\s\S]*?)\*\*/g, '<strong>$1</strong>');

    // 斜体 *text*（不与加粗冲突）
    html = html.replace(/(?<!\*)\*(?!\*)([\s\S]*?)(?<!\*)\*(?!\*)/g, '<em>$1</em>');

    // 行内代码 `code`
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

    // 无序列表 * item 或 - item
    html = html.replace(/^[*-]\s+(.*)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>[\s\S]*?<\/li>(?:\n<li>[\s\S]*?<\/li>)*)/g, '<ul>$1</ul>');

    // 段落分组（双换行分段）
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

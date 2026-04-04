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
    // Very simple MD to HTML converter for specific use case
    if (!text) return "";

    let html = text.trim();

    // Strip project task markers like [/] or [ ] or [x]
    html = html.replace(/\[[\/\sxX]\]\s*/g, '');
    
    // Handle Alerts
    html = html.replace(/>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\n>\s*(.*)/g, (match, type, content) => {
        return `<div class="alert alert-${type.toLowerCase()}"><strong>${type}:</strong> ${content}</div>`;
    });

    // Handle Bold
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Handle Lists
    html = html.replace(/^\*\s+(.*)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>(\n<li>.*<\/li>)*)/g, '<ul>$1</ul>');

    // Handle Newlines (Paragraphs)
    const paragraphs = html.split(/\n\n+/);
    html = paragraphs.map(p => {
        if (p.startsWith('<ul>') || p.startsWith('<div')) return p;
        return `<p>${p.replace(/\n/g, '<br>')}</p>`;
    }).join('');

    return html;
  }

})();

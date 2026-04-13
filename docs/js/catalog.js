/**
 * 目录页 — 从 chapters/index.json 动态渲染卷一章节列表
 * 新章节执行 make publish 后自动出现，无需手动修改 HTML
 */
(function () {
  'use strict';

  const list = document.getElementById('vol1-chapter-list');
  if (!list) return;

  fetch('chapters/index.json')
    .then(r => r.json())
    .then(chapters => {
      list.innerHTML = '';

      chapters.forEach(ch => {
        // 从 title 里提取章节名（去掉"第N章 "前缀）
        const titleText = ch.title.replace(/^第.+?章\s*/, '');
        const num = String(ch.id).padStart(2, '0');

        const li = document.createElement('li');
        li.className = 'chapter-item';
        li.innerHTML = `
          <a href="reader.html?ch=${ch.id}">
            <div class="chapter-meta">
              <span class="chapter-num">${num}</span>
              <span class="chapter-title-text">${titleText}</span>
            </div>
            <span class="chapter-status-badge available">可阅读</span>
          </a>
        `;
        list.appendChild(li);
      });

      // 末尾追加「即将更新」占位条
      const next = String(chapters.length + 1).padStart(2, '0');
      const placeholder = document.createElement('li');
      placeholder.className = 'chapter-item';
      placeholder.innerHTML = `
        <div class="chapter-locked">
          <div class="chapter-meta">
            <span class="chapter-num">${next}</span>
            <span class="chapter-title-text">——</span>
          </div>
          <span class="chapter-status-badge locked">即将更新</span>
        </div>
      `;
      list.appendChild(placeholder);
    })
    .catch(() => {
      list.innerHTML = '<li class="chapter-item" style="opacity:.5;">章节数据加载失败，请刷新重试。</li>';
    });
})();

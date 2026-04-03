/**
 * 阅读页逻辑 — 加载章节JSON、渲染正文、进度条
 */
(function () {
  'use strict';

  // --- Reading progress bar ---
  const progressBar = document.querySelector('.reader-progress');
  if (progressBar) {
    window.addEventListener('scroll', function () {
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const progress = (window.scrollY / docHeight) * 100;
      progressBar.style.width = Math.min(progress, 100) + '%';
    }, { passive: true });
  }

  // --- Load chapter content ---
  const container = document.getElementById('chapter-content');
  if (!container) return;

  // Get chapter from URL param, default to 1
  const params = new URLSearchParams(window.location.search);
  const chapterId = params.get('ch') || '1';

  // Update header
  const headerEl = document.getElementById('chapter-header-title');
  const metaEl = document.getElementById('chapter-meta-info');

  fetch('chapters/chapter-' + chapterId + '.json')
    .then(function (res) {
      if (!res.ok) throw new Error('Chapter not found');
      return res.json();
    })
    .then(function (data) {
      // Update page info
      document.title = data.title + ' — 长生不死的我，在南宋点歪了科技树';
      if (headerEl) headerEl.textContent = data.title;
      if (metaEl) metaEl.textContent = '约 ' + data.wordCount + ' 字';

      // Render content
      container.innerHTML = renderContent(data.sections);

      // Update nav
      updateNav(data.prevChapter, data.nextChapter);
    })
    .catch(function (err) {
      container.innerHTML = '<p style="text-align:center;color:var(--text-muted);">章节内容加载失败，请稍后再试。</p>';
      console.error(err);
    });

  function renderContent(sections) {
    let html = '';
    sections.forEach(function (section) {
      // Section heading
      if (section.heading) {
        html += '<h2>' + escapeHtml(section.heading) + '</h2>';
      }

      // Section break ornament
      html += '<div class="section-break"><span class="diamond"></span></div>';

      // Paragraphs
      section.paragraphs.forEach(function (p) {
        if (p.trim() === '') return;
        // Handle bold text
        let processed = escapeHtml(p);
        // Re-apply bold markers **text** -> <strong>text</strong>
        processed = processed.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        html += '<p>' + processed + '</p>';
      });
    });
    return html;
  }

  function updateNav(prev, next) {
    const prevEl = document.getElementById('prev-chapter');
    const nextEl = document.getElementById('next-chapter');

    if (prevEl) {
      if (prev) {
        prevEl.href = 'reader.html?ch=' + prev.id;
        prevEl.textContent = '← ' + prev.title;
      } else {
        prevEl.removeAttribute('href');
        prevEl.className = 'disabled';
        prevEl.textContent = '← 没有上一章';
      }
    }

    if (nextEl) {
      if (next) {
        nextEl.href = 'reader.html?ch=' + next.id;
        nextEl.textContent = next.title + ' →';
      } else {
        nextEl.removeAttribute('href');
        nextEl.className = 'disabled';
        nextEl.textContent = '敬请期待 →';
      }
    }
  }

  function escapeHtml(str) {
    var div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }
})();

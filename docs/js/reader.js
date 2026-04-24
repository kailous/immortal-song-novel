/**
 * 阅读页逻辑 — 章节加载、进度条、字号、书签、朗读
 */
(function () {
  'use strict';

  // ============================================================
  // Reading progress bar
  // ============================================================
  const progressBar = document.querySelector('.reader-progress');
  if (progressBar) {
    window.addEventListener('scroll', function () {
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const progress = (window.scrollY / docHeight) * 100;
      progressBar.style.width = Math.min(progress, 100) + '%';
    }, { passive: true });
  }

  // ============================================================
  // Comments — 基于 Cusdis REST API 自渲染，样式完全匹配站点
  // ============================================================
  var CUSDIS_APP_ID = '2f184b19-aabe-4e89-a58e-b33a8b123403';
  var CUSDIS_HOST   = 'https://cusdis.com';

  function t(key) {
    return window.i18n ? window.i18n.t(key) : key;
  }

  function escHtml(s) {
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function safeHref(rawUrl) {
    var value = String(rawUrl || '').trim();
    if (!value || /[\u0000-\u001f\u007f\s]/.test(value)) return '';
    if (value[0] === '#') return value;
    try {
      var url = new URL(value, window.location.href);
      if (['http:', 'https:', 'mailto:'].indexOf(url.protocol) !== -1) {
        return url.href;
      }
      if (url.origin === window.location.origin && /^[./\w\u4e00-\u9fa5%-]/.test(value)) {
        return value;
      }
    } catch (e) {}
    return '';
  }

  function safeImageSrc(rawUrl) {
    var value = String(rawUrl || '').trim();
    if (!value || /[\u0000-\u001f\u007f]/.test(value)) return '';
    try {
      var url = new URL(value, window.location.href);
      if (url.origin !== window.location.origin) return '';
      if (/^(?:https?:)?\/\//.test(value) && url.origin !== window.location.origin) return '';
      if (!/^([./]|images\/)/.test(value) && url.origin === window.location.origin) {
        return '';
      }
      return url.href;
    } catch (e) {}
    return '';
  }

  function parseStandaloneImage(markdown) {
    var match = String(markdown || '').trim().match(/^!\[([^\]]*)\]\(([^)\s]+)(?:\s+"([^"]+)")?\)$/);
    if (!match) return null;
    var src = safeImageSrc(match[2]);
    if (!src) return null;
    return {
      alt: match[1] || '',
      src: src,
      caption: match[3] || match[1] || ''
    };
  }

  function fmtDate(iso) {
    var d = new Date(iso);
    return d.getFullYear() + '.' +
           String(d.getMonth() + 1).padStart(2, '0') + '.' +
           String(d.getDate()).padStart(2, '0');
  }

  function isApproved(c) {
    return c.approved === undefined || c.approved === true || c.approved === 1;
  }

  function renderComment(c, isReply) {
    var replies = '';
    if (!isReply && c.replies && c.replies.data && c.replies.data.length) {
      var approvedReplies = c.replies.data.filter(isApproved);
      if (approvedReplies.length) {
        replies = '<div class="comment-replies">' +
          approvedReplies.map(function (r) { return renderComment(r, true); }).join('') +
        '</div>';
      }
    }
    return '<div class="comment-item' + (isReply ? ' comment-reply' : '') + '">' +
      '<div class="comment-meta">' +
        (isReply ? '<span class="comment-reply-mark">↳</span>' : '') +
        '<span class="comment-author">' + escHtml(c.by_nickname || c.nickname || '匿名') + '</span>' +
        '<span class="comment-date">' + fmtDate(c.createdAt) + '</span>' +
      '</div>' +
      '<div class="comment-body">' + escHtml(c.content) + '</div>' +
    '</div>' + replies;
  }

  function renderComments(list) {
    if (!list || !list.length) {
      return '<p class="comments-empty">' + t('reader.comments.empty') + '</p>';
    }
    var items = list.filter(isApproved).map(function (c) { return renderComment(c, false); });
    return items.length
      ? items.join('')
      : '<p class="comments-empty">' + t('reader.comments.empty') + '</p>';
  }

  function loadCusdis(chId, title) {
    var wrap = document.getElementById('giscus-container');
    if (!wrap) return;
    var pageTitle = title || ('第' + chId + '章');
    var pageId    = pageTitle;   // 仪表盘直接显示章节名，如"第一章 坠星"
    var pageUrl   = window.location.href;

    wrap.innerHTML =
      '<div class="comments-list" id="comments-list"><p class="comments-empty">' + t('reader.comments.load') + '</p></div>' +
      '<form class="comment-form" id="comment-form">' +
        '<div class="comment-form-row">' +
          '<input class="comment-input" id="c-name" type="text" placeholder="' + escHtml(t('reader.form.name')) + '" maxlength="50">' +
          '<input class="comment-input" id="c-email" type="email" placeholder="' + escHtml(t('reader.form.email')) + '" maxlength="100">' +
        '</div>' +
        '<textarea class="comment-textarea" id="c-content" placeholder="' + escHtml(t('reader.form.content')) + '" rows="4" maxlength="1000"></textarea>' +
        '<div class="comment-form-footer">' +
          '<span class="comment-hint">' + t('reader.form.hint') + '</span>' +
          '<button class="comment-submit" type="submit">' + t('reader.form.submit') + '</button>' +
        '</div>' +
        '<p class="comment-status" id="c-status"></p>' +
      '</form>';

    // 拉取已有留言
    fetch(CUSDIS_HOST + '/api/open/comments?appId=' + CUSDIS_APP_ID + '&pageId=' + encodeURIComponent(pageId))
      .then(function (r) { return r.json(); })
      .then(function (json) {
        // Cusdis open API 返回结构: { data: { data: [...], count: N } }
        // 兼容 { data: [...] } 直接数组结构
        var list;
        if (Array.isArray(json.data)) {
          list = json.data;
        } else if (json.data && Array.isArray(json.data.data)) {
          list = json.data.data;
        } else if (json.data && Array.isArray(json.data.rows)) {
          list = json.data.rows;
        } else {
          list = [];
        }
        document.getElementById('comments-list').innerHTML = renderComments(list);
      })
      .catch(function (err) {
        console.error('[comments]', err);
        document.getElementById('comments-list').innerHTML = '<p class="comments-empty">' + t('reader.comments.fail') + '</p>';
      });

    // 提交留言
    document.getElementById('comment-form').addEventListener('submit', function (e) {
      e.preventDefault();
      var name    = document.getElementById('c-name').value.trim();
      var email   = document.getElementById('c-email').value.trim();
      var content = document.getElementById('c-content').value.trim();
      var status  = document.getElementById('c-status');

      if (!name)    { status.textContent = t('reader.form.err.name');    status.className = 'comment-status error'; return; }
      if (!content) { status.textContent = t('reader.form.err.content'); status.className = 'comment-status error'; return; }

      var btn = this.querySelector('.comment-submit');
      btn.disabled = true;
      status.textContent = t('reader.form.submitting');
      status.className = 'comment-status';

      fetch(CUSDIS_HOST + '/api/open/comments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          appId:     CUSDIS_APP_ID,
          pageId:    pageId,
          pageUrl:   pageUrl,
          pageTitle: pageTitle,
          content:   content,
          nickname:  name,
          email:     email || undefined
        })
      })
        .then(function (r) { return r.json(); })
        .then(function () {
          status.textContent = t('reader.form.ok');
          status.className = 'comment-status success';
          document.getElementById('c-name').value = '';
          document.getElementById('c-email').value = '';
          document.getElementById('c-content').value = '';
          btn.disabled = false;
        })
        .catch(function () {
          status.textContent = t('reader.form.err.fail');
          status.className = 'comment-status error';
          btn.disabled = false;
        });
    });
  }

  // ============================================================
  // Chapter load
  // ============================================================
  const container = document.getElementById('chapter-content');
  if (!container) return;

  const params = new URLSearchParams(window.location.search);
  const chapterId = params.get('ch') || '1';
  const headerEl = document.getElementById('chapter-header-title');
  const metaEl   = document.getElementById('chapter-meta-info');

  let chapterTitle = '';
  let currentCatalog = [];

  function chapterIndexUrl(lang) {
    return 'data/chapters_' + (lang === 'en' ? 'en' : 'zh') + '.json';
  }

  function loadChapterIndex(lang) {
    return fetch(chapterIndexUrl(lang))
      .then(function (res) {
        if (!res.ok) {
          if (lang === 'en') return fetch(chapterIndexUrl('zh'));
          throw new Error('Chapter index not found');
        }
        return res;
      })
      .then(function (res) { return res.json(); });
  }

  function parseMarkdownSections(markdown) {
    var lines = String(markdown || '').replace(/\r\n/g, '\n').split('\n');
    var title = '';
    var sections = [];
    var currentSection = null;

    function ensureSection() {
      if (!currentSection) {
        currentSection = { heading: '', paragraphs: [] };
        sections.push(currentSection);
      }
    }

    function pushParagraph(paragraphLines) {
      var value = paragraphLines.join('\n').trim();
      if (!value) return;
      ensureSection();
      currentSection.paragraphs.push(value);
    }

    var paragraphLines = [];
    lines.forEach(function (line) {
      var trimmed = line.trim();
      if (!title && trimmed.indexOf('# ') === 0) {
        title = trimmed.slice(2).trim();
        return;
      }
      if (trimmed.indexOf('## ') === 0) {
        pushParagraph(paragraphLines);
        paragraphLines = [];
        currentSection = { heading: trimmed.slice(3).trim(), paragraphs: [] };
        sections.push(currentSection);
        return;
      }
      if (trimmed === '---') {
        pushParagraph(paragraphLines);
        paragraphLines = [];
        currentSection = { heading: '', paragraphs: ['---'] };
        sections.push(currentSection);
        currentSection = null;
        return;
      }
      if (!trimmed) {
        pushParagraph(paragraphLines);
        paragraphLines = [];
        return;
      }
      paragraphLines.push(line);
    });
    pushParagraph(paragraphLines);

    return { title: title, sections: sections };
  }

  function findChapterEntry(index, id) {
    return (index || []).find(function (item) { return String(item.id) === String(id); }) || null;
  }

  function buildChapterData(index, entry, parsed) {
    var currentIndex = index.findIndex(function (item) { return String(item.id) === String(entry.id); });
    return {
      id: String(entry.id),
      title: parsed.title || entry.title,
      wordCount: entry.wordCount || '0',
      sections: parsed.sections,
      prevChapter: currentIndex > 0 ? {
        id: String(index[currentIndex - 1].id),
        title: index[currentIndex - 1].title
      } : null,
      nextChapter: currentIndex >= 0 && currentIndex < index.length - 1 ? {
        id: String(index[currentIndex + 1].id),
        title: index[currentIndex + 1].title
      } : null
    };
  }

  function loadChapter(lang) {
    loadChapterIndex(lang)
      .then(function (index) {
        var activeIndex = index;
        var entry = findChapterEntry(index, chapterId);
        if (!entry && lang === 'en') {
          return loadChapterIndex('zh').then(function (zhIndex) {
            activeIndex = zhIndex;
            entry = findChapterEntry(zhIndex, chapterId);
            if (!entry) throw new Error('Chapter not found');
            return { entry: entry, index: zhIndex };
          });
        }
        if (!entry) throw new Error('Chapter not found');
        return { entry: entry, index: activeIndex };
      })
      .then(function (payload) {
        currentCatalog = payload.index;
        return fetch(payload.entry.source)
          .then(function (res) {
            if (!res.ok) throw new Error('Chapter markdown not found');
            return res.text();
          })
          .then(function (markdown) {
            return buildChapterData(payload.index, payload.entry, parseMarkdownSections(markdown));
          });
      })
      .then(function (data) {
        chapterTitle = data.title;
        var siteName = lang === 'en'
          ? 'Immortal in Southern Song'
          : '长生不死的我，在南宋点歪了科技树';
        document.title = data.title + ' — ' + siteName;
        if (headerEl) headerEl.textContent = data.title;
        if (metaEl)   metaEl.textContent   = (lang === 'en' ? 'approx. ' : '约 ') + data.wordCount + (lang === 'en' ? ' words' : ' 字');

        container.innerHTML = renderContent(data.sections);

        updateNav(data.prevChapter, data.nextChapter);

        if (window._collectTtsParagraphs) window._collectTtsParagraphs();
        checkBookmarkToast();
        loadCusdis(chapterId, data.title);
      })
      .catch(function (err) {
        container.innerHTML = '<p style="text-align:center;color:var(--text-muted);">' + t('reader.chapter.fail') + '</p>';
        console.error(err);
      });
  }

  var initLang = window.i18n ? window.i18n.lang() : 'zh';
  loadChapter(initLang);

  document.addEventListener('langchange', function (e) {
    loadChapter(e.detail);
  });

  function renderInline(escaped) {
    // 处理行内 Markdown 语法（在 escapeHtml 之后调用，安全）
    // **加粗**
    escaped = escaped.replace(/\*\*([\s\S]*?)\*\*/g, '<strong>$1</strong>');
    // *斜体* 或 _斜体_（不与加粗冲突）
    escaped = escaped.replace(/(?<!\*)\*(?!\*)([\s\S]*?)(?<!\*)\*(?!\*)/g, '<em>$1</em>');
    escaped = escaped.replace(/_([\s\S]*?)_/g, '<em>$1</em>');
    // `行内代码`
    escaped = escaped.replace(/`([^`]+)`/g, '<code>$1</code>');
    // [链接文字](url)
    escaped = escaped.replace(/\[([^\]]+)\]\(([^)]+)\)/g, function (match, label, url) {
      var href = safeHref(url.replace(/&amp;/g, '&'));
      if (!href) return label;
      return '<a href="' + escHtml(href) + '" target="_blank" rel="noopener noreferrer">' + label + '</a>';
    });
    return escaped;
  }

  function renderContent(sections) {
    let html = '';
    sections.forEach(function (section) {
      if (section.heading) {
        html += '<h2>' + escapeHtml(section.heading) + '</h2>';
      }
      html += '<div class="section-break"><span class="diamond"></span></div>';
      section.paragraphs.forEach(function (p) {
        var trimmed = p.trim();
        if (trimmed === '') return;
        // 独立的 --- 水平分割线（Python脚本已将其转为空heading section，
        // 但段落里如果残留 --- 也兜底处理）
        if (trimmed === '---') {
          html += '<hr class="section-hr">';
          return;
        }
        var standaloneImage = parseStandaloneImage(trimmed);
        if (standaloneImage) {
          html += '<figure class="reader-figure">' +
            '<img src="' + escHtml(standaloneImage.src) + '" alt="' + escHtml(standaloneImage.alt) + '" loading="lazy">' +
            (standaloneImage.caption
              ? '<figcaption>' + escHtml(standaloneImage.caption) + '</figcaption>'
              : '') +
          '</figure>';
          return;
        }
        var processed = renderInline(escapeHtml(p));
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
        prevEl.className = '';
      } else {
        prevEl.removeAttribute('href');
        prevEl.className = 'disabled';
        prevEl.textContent = t('reader.prev');
      }
    }
    if (nextEl) {
      if (next) {
        nextEl.href = 'reader.html?ch=' + next.id;
        nextEl.textContent = next.title + ' →';
        nextEl.className = '';
      } else {
        nextEl.removeAttribute('href');
        nextEl.className = 'disabled';
        nextEl.textContent = t('reader.next');
      }
    }
  }

  function escapeHtml(str) {
    var div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  // ============================================================
  // Floating Catalog
  // ============================================================
  const catalogOverlay   = document.getElementById('reader-catalog-overlay');
  const openCatalogBtn   = document.getElementById('reader-open-catalog');
  const closeCatalogBtn  = document.getElementById('close-catalog');
  const catalogIndexEl   = document.getElementById('reader-catalog-index');

  function openCatalog(e) {
    if (e) e.preventDefault();
    catalogOverlay.classList.add('active');
    document.body.style.overflow = 'hidden';
    loadCatalogIndex();
  }

  if (openCatalogBtn && catalogOverlay) {
    openCatalogBtn.addEventListener('click', openCatalog);
  }

  // 工具栏"目录"按钮复用同一逻辑
  const toolbarCatalogBtn = document.getElementById('toolbar-catalog');
  if (toolbarCatalogBtn && catalogOverlay) {
    toolbarCatalogBtn.addEventListener('click', openCatalog);
  }

  if (closeCatalogBtn && catalogOverlay) {
    closeCatalogBtn.addEventListener('click', closeCatalog);
    catalogOverlay.addEventListener('click', function (e) {
      if (e.target === catalogOverlay) closeCatalog();
    });
  }

  function closeCatalog() {
    catalogOverlay.classList.remove('active');
    document.body.style.overflow = '';
  }

  function loadCatalogIndex() {
    if (!catalogIndexEl) return;
    if (currentCatalog.length) {
      renderCatalogIndex(currentCatalog);
      return;
    }
    loadChapterIndex(window.i18n ? window.i18n.lang() : 'zh')
      .then(function (data) {
        currentCatalog = data;
        renderCatalogIndex(data);
      })
      .catch(function (err) {
        catalogIndexEl.innerHTML = '<p style="text-align:center;color:var(--text-muted);padding:2rem;">' + t('reader.overlay.load') + '</p>';
        console.error(err);
      });
  }

  function renderCatalogIndex(data) {
    if (!catalogIndexEl) return;
    var html = '<ul class="overlay-chapter-list">';
    data.forEach(function (ch) {
      var isActive = ch.id === chapterId ? 'active' : '';
      html += '<li class="overlay-chapter-item ' + isActive + '">' +
        '<a href="reader.html?ch=' + ch.id + '">' +
          '<span class="ch-id">' + ch.id.padStart(2, '0') + '</span>' +
          '<span class="ch-name">' + ch.title + '</span>' +
        '</a></li>';
    });
    html += '</ul>';
    catalogIndexEl.innerHTML = html;
  }

  // ============================================================
  // Font Size
  // ============================================================
  const FONT_SIZES     = [0.88, 0.95, 1.0, 1.05, 1.12, 1.22, 1.35];
  const DEFAULT_IDX    = 3; // 1.05rem
  const STORAGE_FONT   = 'reader-font-index';

  let fontIndex = parseInt(localStorage.getItem(STORAGE_FONT) || DEFAULT_IDX, 10);
  if (isNaN(fontIndex) || fontIndex < 0 || fontIndex >= FONT_SIZES.length) fontIndex = DEFAULT_IDX;

  function applyFontSize() {
    document.documentElement.style.setProperty('--reader-font-size', FONT_SIZES[fontIndex] + 'rem');
    localStorage.setItem(STORAGE_FONT, fontIndex);
    const decBtn = document.getElementById('font-decrease');
    const incBtn = document.getElementById('font-increase');
    if (decBtn) decBtn.classList.toggle('toolbar-btn-disabled', fontIndex <= 0);
    if (incBtn) incBtn.classList.toggle('toolbar-btn-disabled', fontIndex >= FONT_SIZES.length - 1);
  }

  applyFontSize();

  const fontDecBtn = document.getElementById('font-decrease');
  const fontIncBtn = document.getElementById('font-increase');

  if (fontDecBtn) {
    fontDecBtn.addEventListener('click', function () {
      if (fontIndex > 0) { fontIndex--; applyFontSize(); }
    });
  }
  if (fontIncBtn) {
    fontIncBtn.addEventListener('click', function () {
      if (fontIndex < FONT_SIZES.length - 1) { fontIndex++; applyFontSize(); }
    });
  }

  // ============================================================
  // Bookmark
  // ============================================================
  const STORAGE_BOOKMARK = 'reader-bookmark';
  let savedToastTimer = null;

  // 更新书签按钮高亮状态
  function updateBookmarkBtn() {
    const btn = document.getElementById('bookmark-save');
    if (!btn) return;
    const raw = localStorage.getItem(STORAGE_BOOKMARK);
    try {
      const bm = raw ? JSON.parse(raw) : null;
      if (bm && bm.chapterId === chapterId) {
        btn.classList.add('toolbar-btn-active');
        btn.title = '书签：第 ' + bm.percent + '% 处（点击重新标记）';
      } else {
        btn.classList.remove('toolbar-btn-active');
        btn.title = '保存书签';
      }
    } catch (e) {}
  }

  // 保存成功时弹出瞬时提示（2.5s 自动消失）
  function showSavedSnack(pct) {
    let snack = document.getElementById('bookmark-snack');
    if (!snack) {
      snack = document.createElement('div');
      snack.id = 'bookmark-snack';
      snack.className = 'bookmark-snack';
      document.body.appendChild(snack);
    }
    snack.textContent = '📌 书签已保存  第 ' + pct + '% 处';
    snack.classList.add('active');
    clearTimeout(savedToastTimer);
    savedToastTimer = setTimeout(function () {
      snack.classList.remove('active');
    }, 2500);
  }

  function saveBookmark() {
    const total = document.documentElement.scrollHeight - window.innerHeight;
    const pct   = total > 0 ? Math.round((window.scrollY / total) * 100) : 0;
    const bm = {
      chapterId : chapterId,
      title     : chapterTitle,
      scrollY   : Math.round(window.scrollY),
      percent   : pct,
      timestamp : Date.now()
    };
    localStorage.setItem(STORAGE_BOOKMARK, JSON.stringify(bm));
    updateBookmarkBtn();
    showSavedSnack(pct);
    // 隐藏「跳转」toast（保存后不必再提示跳转）
    const restoreToast = document.getElementById('bookmark-toast');
    if (restoreToast) restoreToast.classList.remove('active');
  }

  // 进入章节时：如有书签则提示跳转
  function checkBookmarkToast() {
    updateBookmarkBtn();
    const raw = localStorage.getItem(STORAGE_BOOKMARK);
    if (!raw) return;
    try {
      const bm = JSON.parse(raw);
      if (bm.chapterId !== chapterId) return;
      if (bm.scrollY < 200) return;
      // 稍作延迟，让页面渲染完再弹出
      setTimeout(function () {
        const toast = document.getElementById('bookmark-toast');
        if (toast) toast.classList.add('active');
      }, 800);
    } catch (e) {}
  }

  const bookmarkSaveBtn    = document.getElementById('bookmark-save');
  const bookmarkToast      = document.getElementById('bookmark-toast');
  const bookmarkJumpBtn    = document.getElementById('bookmark-jump');
  const bookmarkDismissBtn = document.getElementById('bookmark-dismiss');

  if (bookmarkSaveBtn) {
    bookmarkSaveBtn.addEventListener('click', saveBookmark);
  }

  if (bookmarkJumpBtn) {
    bookmarkJumpBtn.addEventListener('click', function () {
      const raw = localStorage.getItem(STORAGE_BOOKMARK);
      if (!raw) return;
      try {
        const bm = JSON.parse(raw);
        window.scrollTo({ top: bm.scrollY, behavior: 'smooth' });
      } catch (e) {}
      if (bookmarkToast) bookmarkToast.classList.remove('active');
    });
  }

  if (bookmarkDismissBtn) {
    bookmarkDismissBtn.addEventListener('click', function () {
      if (bookmarkToast) bookmarkToast.classList.remove('active');
    });
  }

  // ============================================================
  // TTS — Web Speech API (free, browser-native)
  // ============================================================
  if (!('speechSynthesis' in window)) {
    // Hide TTS buttons if not supported
    ['tts-toggle', 'tts-stop', 'tts-speed'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.style.display = 'none';
    });
    const div = document.querySelector('.toolbar-divider:last-of-type');
    if (div) div.style.display = 'none';
  } else {
    const synth      = window.speechSynthesis;
    const toggleBtn  = document.getElementById('tts-toggle');
    const stopBtn    = document.getElementById('tts-stop');
    const speedBtn   = document.getElementById('tts-speed');

    const SPEEDS     = [0.8, 1.0, 1.3];
    const SPEED_LBLS = ['慢', '1x', '快'];
    let speedIdx     = 1;
    let ttsParas     = []; // [{el, text}]
    let ttsIdx       = 0;
    let ttsPlaying   = false;
    let chineseVoice = null;

    // Load voices
    function loadVoices() {
      const voices = synth.getVoices();
      chineseVoice =
        voices.find(v => v.lang === 'zh-CN') ||
        voices.find(v => v.lang === 'zh-TW') ||
        voices.find(v => v.lang.startsWith('zh')) ||
        null;
    }
    loadVoices();
    if (synth.onvoiceschanged !== undefined) {
      synth.addEventListener('voiceschanged', loadVoices);
    }

    function collectTtsParagraphs() {
      ttsParas = Array.from(container.querySelectorAll('p')).map(el => ({
        el: el,
        text: el.innerText.trim()
      })).filter(item => item.text.length > 0);
    }

    // Expose so it can be called after chapter loads
    window._collectTtsParagraphs = collectTtsParagraphs;

    function ttsHighlight(idx) {
      container.querySelectorAll('.tts-active').forEach(e => e.classList.remove('tts-active'));
      if (ttsParas[idx]) {
        ttsParas[idx].el.classList.add('tts-active');
        ttsParas[idx].el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }

    function playFrom(idx) {
      if (idx >= ttsParas.length) { ttsStop(); return; }
      ttsIdx = idx;
      ttsHighlight(idx);

      const utt = new SpeechSynthesisUtterance(ttsParas[idx].text);
      utt.lang  = 'zh-CN';
      utt.rate  = SPEEDS[speedIdx];
      if (chineseVoice) utt.voice = chineseVoice;

      utt.onend = function () {
        if (ttsPlaying) playFrom(ttsIdx + 1);
      };
      utt.onerror = function (e) {
        if (e.error !== 'interrupted' && e.error !== 'canceled') {
          console.warn('TTS error:', e.error);
          ttsStop();
        }
      };

      synth.speak(utt);
    }

    function ttsPlay() {
      if (ttsPlaying) return;
      if (ttsParas.length === 0) return;
      ttsPlaying = true;

      // Start from the paragraph closest to viewport center
      if (ttsIdx === 0) {
        const mid = window.scrollY + window.innerHeight / 2;
        let closest = 0, minDist = Infinity;
        ttsParas.forEach(function (item, i) {
          const rect = item.el.getBoundingClientRect();
          const dist = Math.abs(rect.top + rect.height / 2 - window.innerHeight / 2);
          if (dist < minDist) { minDist = dist; closest = i; }
        });
        ttsIdx = closest;
      }

      playFrom(ttsIdx);
      updateTtsUI();
    }

    function ttsPause() {
      ttsPlaying = false;
      synth.cancel(); // more reliable than pause() across browsers
      // ttsIdx stays where it is, next play() resumes from same para
      updateTtsUI();
    }

    function ttsStop() {
      ttsPlaying = false;
      ttsIdx = 0;
      synth.cancel();
      container.querySelectorAll('.tts-active').forEach(e => e.classList.remove('tts-active'));
      updateTtsUI();
    }

    function updateTtsUI() {
      if (!toggleBtn || !stopBtn) return;
      const startIcon  = toggleBtn.querySelector('.tts-icon-start');
      const resumeIcon = toggleBtn.querySelector('.tts-icon-resume');
      const pauseIcon  = toggleBtn.querySelector('.tts-icon-pause');

      if (ttsPlaying) {
        // 播放中：显示 pause-one
        if (startIcon)  startIcon.style.display  = 'none';
        if (resumeIcon) resumeIcon.style.display = 'none';
        if (pauseIcon)  pauseIcon.style.display  = 'flex';
        toggleBtn.title = '暂停朗读';
        stopBtn.style.display = 'flex';
        if (speedBtn) speedBtn.style.display = 'flex';
      } else if (ttsIdx > 0) {
        // 暂停中：显示 play-one
        if (startIcon)  startIcon.style.display  = 'none';
        if (resumeIcon) resumeIcon.style.display = 'flex';
        if (pauseIcon)  pauseIcon.style.display  = 'none';
        toggleBtn.title = '继续朗读';
        stopBtn.style.display = 'flex';
        if (speedBtn) speedBtn.style.display = 'flex';
      } else {
        // 停止状态：显示 acoustic
        if (startIcon)  startIcon.style.display  = 'flex';
        if (resumeIcon) resumeIcon.style.display = 'none';
        if (pauseIcon)  pauseIcon.style.display  = 'none';
        toggleBtn.title = '开始朗读';
        stopBtn.style.display = 'none';
        if (speedBtn) speedBtn.style.display = 'none';
      }
    }

    if (toggleBtn) {
      toggleBtn.addEventListener('click', function () {
        if (ttsPlaying) ttsPause(); else ttsPlay();
      });
    }
    if (stopBtn) {
      stopBtn.addEventListener('click', ttsStop);
      stopBtn.style.display = 'none';
    }
    if (speedBtn) {
      speedBtn.style.display = 'none';
      speedBtn.addEventListener('click', function () {
        speedIdx = (speedIdx + 1) % SPEEDS.length;
        speedBtn.textContent = SPEED_LBLS[speedIdx];
        // If playing, restart current para with new rate
        if (ttsPlaying) {
          const cur = ttsIdx;
          synth.cancel();
          setTimeout(() => { if (ttsPlaying) playFrom(cur); }, 100);
        }
      });
    }

    // Stop TTS on page navigation
    window.addEventListener('beforeunload', function () { synth.cancel(); });
    window.addEventListener('pagehide',     function () { synth.cancel(); });
  }

})();

/**
 * 目录页 — 从 chapters/index.json 动态渲染卷一章节列表
 * 新章节执行 make publish 后自动出现，无需手动修改 HTML
 */
(function () {
  'use strict';

  var list = document.getElementById('vol1-chapter-list');
  if (!list) return;

  var cachedChapters = null;

  function t(key) {
    return (window.i18n && window.i18n.t) ? window.i18n.t(key) : key;
  }

  function render(chapters) {
    list.innerHTML = '';

    chapters.forEach(function (ch) {
      var titleText = ch.title.replace(/^第.+?章\s*/, '');
      var num = String(ch.id).padStart(2, '0');

      var li = document.createElement('li');
      li.className = 'chapter-item';
      li.innerHTML =
        '<a href="reader.html?ch=' + ch.id + '">' +
          '<div class="chapter-meta">' +
            '<span class="chapter-num">' + num + '</span>' +
            '<span class="chapter-title-text">' + titleText + '</span>' +
          '</div>' +
          '<span class="chapter-status-badge available">' + t('catalog.badge.avail') + '</span>' +
        '</a>';
      list.appendChild(li);
    });

    var next = String(chapters.length + 1).padStart(2, '0');
    var placeholder = document.createElement('li');
    placeholder.className = 'chapter-item';
    placeholder.innerHTML =
      '<div class="chapter-locked">' +
        '<div class="chapter-meta">' +
          '<span class="chapter-num">' + next + '</span>' +
          '<span class="chapter-title-text">——</span>' +
        '</div>' +
        '<span class="chapter-status-badge locked">' + t('catalog.badge.next') + '</span>' +
      '</div>';
    list.appendChild(placeholder);
  }

  fetch('chapters/index.json')
    .then(function (r) { return r.json(); })
    .then(function (chapters) {
      cachedChapters = chapters;
      render(chapters);
    })
    .catch(function () {
      list.innerHTML = '<li class="chapter-item" style="opacity:.5;">' + t('catalog.fail') + '</li>';
    });

  document.addEventListener('langchange', function () {
    if (cachedChapters) render(cachedChapters);
  });
})();

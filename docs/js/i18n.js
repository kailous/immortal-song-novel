/**
 * i18n — 双语切换系统（中文 / English）
 * 用法：data-i18n="key" 自动替换文本；data-i18n-html="key" 替换 innerHTML
 * JS 动态内容监听 'langchange' 事件重新渲染
 */
(function () {
  'use strict';

  /* ============================================================
     Translation Dictionary
     ============================================================ */
  var T = {
    zh: {
      /* --- Nav --- */
      'nav.brand':       '长生不死',
      'nav.home':        '首页',
      'nav.catalog':     '目录',
      'nav.characters':  '图鉴',
      'nav.about':       '关于',
      'nav.menu':        '菜单',

      /* --- Footer --- */
      'footer.brand':    '长生不死的我，在南宋点歪了科技树',
      'footer.copy':     '© 2026 kailous. All rights reserved.',

      /* --- Index: Hero --- */
      'hero.label':     '硬核科幻 × 重工大宋',
      'hero.title':     '长生不死的我<br>在南宋<span class="highlight">点歪了科技树</span>',
      'hero.tagline':   '公元二〇五六年，人类最后的兵王穿越时空，坠入南宋深山。<br>一枚来自千年后的次元手环，将改写整个文明的命运。',
      'hero.cta':       '开始阅读',

      /* --- Index: Volumes --- */
      'vol.section.label': '全卷概览',
      'vol.section.title': '四卷史诗 · 从乡野到星海',
      'vol.section.desc':  '从南宋乡间的坠落与觉醒，到席卷整个大宋的工业革命，再到冲出蓝星的终极反击。',
      'vol1.num':    '卷一',
      'vol1.title':  '觉醒与立足',
      'vol1.desc':   '主角坠入南宋深山，被寡妇陆晓晓所救。在记忆断层与杀戮本能的交织中，从乡野流民到大宋战场传奇。',
      'vol1.status': '连载中',
      'vol2.num':    '卷二',
      'vol2.title':  '五帝横空与乱世狂飙',
      'vol2.desc':   '手环觉醒，工业革命点燃大宋。蒸汽机轰鸣在临安城，燧发枪改写冷兵器时代的铁律。',
      'vol2.status': '即将开启',
      'vol3.num':    '卷三',
      'vol3.title':  '大一统与降维远征',
      'vol3.desc':   '完成全球统一，建立世界政府。面对内部腐败与权力异化，文明法则凌驾于血亲之上。',
      'vol3.status': '即将开启',
      'vol4.num':    '卷四',
      'vol4.title':  '世界政府与星海的命运回响',
      'vol4.desc':   '人类文明终于站在了星际的门槛上。当年那个致命信号的倒计时，已经开始。',
      'vol4.status': '即将开启',

      /* --- Index: Characters Preview --- */
      'chars.section.label': '核心角色',
      'chars.section.title': '命运的棋局',
      'char.luchen.role':     '不死兵王 · 文明导师',
      'char.xiaoxiao.role':   '南宋寡妇 · 绝境豪赌者',
      'char.zhaohuan.role':   '帝国棋子 · 凤凰涅槃',
      'char.zhangxian.role':  '岳家军副统制 · 第一猛将 · 陆辰导师',

      /* --- Catalog --- */
      'catalog.label':        'CATALOG',
      'catalog.title':        '章节目录',
      'catalog.desc':         '从坠星深山到星海彼端，一步一步改写文明的轨迹。',
      'catalog.loading':      '加载中…',
      'catalog.locked':       '本卷尚未开始，敬请期待',
      'catalog.badge.locked': '未开放',
      'catalog.badge.avail':  '可阅读',
      'catalog.badge.next':   '即将更新',
      'catalog.fail':         '章节数据加载失败，请刷新重试。',
      'vol1.catalog.num':  '卷一',
      'vol1.catalog.name': '觉醒与立足',
      'vol2.catalog.num':  '卷二',
      'vol2.catalog.name': '五帝横空与乱世狂飙',
      'vol3.catalog.num':  '卷三',
      'vol3.catalog.name': '大一统与降维远征',
      'vol4.catalog.num':  '卷四',
      'vol4.catalog.name': '世界政府与星海的命运回响',

      /* --- Characters Page --- */
      'chars.label':       'CHARACTERS',
      'chars.title':       '角色图鉴',
      'chars.desc':        '命运棋局中的关键落子',
      'items.label':       'KEY ITEMS',
      'items.title':       '关键道具',

      /* --- Character Detail --- */
      'detail.back':       '← 返回图鉴',
      'detail.loading':    '正在读取档案...',

      /* --- About --- */
      'about.label':    'ABOUT',
      'about.title':    '关于本书',
      'about.subtitle': '重工大宋，星海怒火',
      'about.s1.title': '故事简介',
      'about.s1.body':  '<p>公元二〇五六年。外星舰队的降维打击将地球表面化为焦土。人类文明在地下一千二百米的"终末方舟"中做出了最后的决断——用缴获的半损毁外星穿梭引擎，将唯一一个能承受超时空跃迁的人送回过去。</p><p>他叫林默。或者更早以前，在那座731焚化炉里被活活烧成白骨之前，他叫孙满仓。一百一十六岁的不死兵王，人类文明最后的赌注。</p><p>然而，损毁的引擎在传送的最后三秒发生了灾难性的时间线偏移。他没有到达1970年代的射电天文台，而是坠入了南宋绍兴年间的一座无名深山。</p><p>从一团裹附在次元手环上的血肉碎屑开始，他的肉体在古代的月光下缓慢重塑。记忆断层、身份空白、身处八百年前的蛮荒——但他的手腕上，那枚来自千年后的黑色手环里，封存着全人类文明最尖端的科技结晶。</p><p>这是一个关于技术复利、文明续存与人性极限的故事。没有魔法，没有系统，没有任何超自然力量——只有一个会犯错、会疲惫、会面对惨烈伤亡而自我怀疑的凡人兵王，用工业的力量、科学的逻辑和一千年的时间差，试图将一个十二世纪的封建农业帝国，拖入星际防御纪元。</p>',
      'about.s2.title': '创作理念',
      'about.s2.body':  '<p>本书的核心理念是 <strong>"重工大宋，星海怒火"</strong>。我们追求的是一种冷峻、宏大、逻辑严密的叙事风格——从十二世纪的封建社会向星际文明的跃迁，必须通过"技术复利的恐怖力量"合理实现。</p><p>语言上，融合宋代古风的典雅谈吐与精准的工业技术术语。画面上，追求临安城的蒸汽机、配有燧发枪的重甲骑兵、以及龙脉之巅的"超空间引力波广播矩阵"这样的冲突意象。</p>',
      'about.rules.title': '◆ 核心铁律',
      'about.rules.body':  '<li><strong>去系统化</strong> — 绝对禁止引入任何"系统加点"或"系统现成图纸"。技术的突破必须体现出"概念→工匠研发→失败→定型"的工业过程。</li><li><strong>去魔法化</strong> — 严禁出现纯粹的魔法或武侠套路。所有技术优势必须源自主角的2056年知识、外星手环（有限资源）或大宋的工业潜力。</li><li><strong>敌方智能</strong> — 敌人不是纸片人。优先考虑其对大宋技术的策反、窃取与反制逻辑。</li><li><strong>非神性视角</strong> — 主角是一个会犯错、会疲惫、会面对惨烈伤亡而自我怀疑的凡人兵王。</li><li><strong>碳基变异限度</strong> — 子嗣的异能必须严格遵循碳基生物极限，严禁出现超自然超能力。</li><li><strong>仁慈统一</strong> — 优先利用技术输出解决生存压力，在描写敌方领袖时，强调其面对文明落差时的心理挣扎。</li><li><strong>文明法则</strong> — 当后方出现贪腐和特权时，主角必须展现绝对的冷酷与法制，文明法则凌驾于血亲之上。</li>',
      'about.s3.title': '世界观简述',
      'about.s3.body':  '<p><strong>2056年 —</strong> 外星舰队降维打击后的第三十年。地球表面化为焦土，人类残余退守地下工事。在漫长的绝望战争中，用堆尸体的方式缴获了外星人的空间手环与半损毁穿梭引擎。</p><p><strong>南宋绍兴年间 —</strong> 偏安江南的赵宋王朝，外有金人虎视，内有积弱腐败。天目山深处的一座无名山谷里，一枚黝黑的手环与一团蠕动的血肉从天而降。</p><p>两个时代的碰撞，从这一刻开始。</p>',
      'about.author.bio': '硬核科幻爱好者。相信技术是文明的底层代码，而故事是承载它的最好容器。',

      /* --- Reader --- */
      'reader.header.loading':  '加载中…',
      'reader.prev':            '← 没有上一章',
      'reader.catalog.btn':     '目录',
      'reader.next':            '敬请期待 →',
      'reader.comments.title':  '读者留言',
      'reader.comments.empty':  '暂无留言，来做第一个留言的读者吧。',
      'reader.comments.load':   '留言加载中…',
      'reader.comments.fail':   '留言加载失败，请稍后再试。',
      'reader.form.name':       '你的名字（必填）',
      'reader.form.email':      '邮箱（选填，不公开）',
      'reader.form.content':    '写下你的留言…',
      'reader.form.hint':       '留言需审核后显示',
      'reader.form.submit':     '发送留言',
      'reader.form.submitting': '提交中…',
      'reader.form.ok':         '留言已提交，审核通过后将显示。感谢你的留言！',
      'reader.form.err.name':   '请填写名字。',
      'reader.form.err.content':'请填写留言内容。',
      'reader.form.err.fail':   '提交失败，请稍后再试。',
      'reader.bookmark.toast':  '📌 发现上次书签',
      'reader.bookmark.jump':   '跳转',
      'reader.overlay.title':   '查看目录',
      'reader.overlay.load':    '正在加载目录…',
      'reader.chapter.fail':    '章节内容加载失败，请稍后再试。',
    },

    en: {
      /* --- Nav --- */
      'nav.brand':       'Immortal Song',
      'nav.home':        'Home',
      'nav.catalog':     'Catalog',
      'nav.characters':  'Characters',
      'nav.about':       'About',
      'nav.menu':        'Menu',

      /* --- Footer --- */
      'footer.brand':    'The Immortal Soldier: Warping the Tech Tree in the Song Dynasty',
      'footer.copy':     '© 2026 kailous. All rights reserved.',

      /* --- Index: Hero --- */
      'hero.label':   'Hard Sci-Fi × Industrial Song Dynasty',
      'hero.title':   'The Undying Soldier<br>Who <span class="highlight">Warped the Tech Tree</span>',
      'hero.tagline': 'Year 2056. The last super-soldier of humanity leaps through time, crashing into the mountains of the Southern Song Dynasty.<br>A dimensional bracelet from a thousand years in the future will rewrite the fate of all civilization.',
      'hero.cta':     'Start Reading',

      /* --- Index: Volumes --- */
      'vol.section.label': 'VOLUMES',
      'vol.section.title': 'A Four-Volume Epic · From Village to Stars',
      'vol.section.desc':  'From an awakening in the mountains of the Song Dynasty, to an industrial revolution sweeping the empire, to humanity\'s ultimate counterattack beyond Earth.',
      'vol1.num':    'Vol. I',
      'vol1.title':  'Awakening & Foothold',
      'vol1.desc':   'The protagonist crashes into the mountains of the Southern Song and is rescued by widow Lu Xiaoxiao. Torn between memory loss and killing instincts, he rises from a wandering refugee to a battlefield legend.',
      'vol1.status': 'Ongoing',
      'vol2.num':    'Vol. II',
      'vol2.title':  'Five Emperors & The Storm of Ages',
      'vol2.desc':   'The bracelet awakens, igniting an industrial revolution across the Song Empire. Steam engines roar in Lin\'an as flintlock rifles rewrite the iron laws of cold-weapon warfare.',
      'vol2.status': 'Coming Soon',
      'vol3.num':    'Vol. III',
      'vol3.title':  'Unification & The Dimensional Expedition',
      'vol3.desc':   'Global unification complete, a world government established. Confronting internal corruption and the abuse of power, the laws of civilization override all ties of blood.',
      'vol3.status': 'Coming Soon',
      'vol4.num':    'Vol. IV',
      'vol4.title':  'World Government & The Echo of Stellar Fate',
      'vol4.desc':   'Human civilization finally stands at the threshold of the stars. The countdown from that deadly signal, long ago, has already begun.',
      'vol4.status': 'Coming Soon',

      /* --- Index: Characters Preview --- */
      'chars.section.label': 'CHARACTERS',
      'chars.section.title': 'The Chessboard of Fate',
      'char.luchen.role':    'Undying Soldier · Civilizational Mentor',
      'char.xiaoxiao.role':  'Song Dynasty Widow · High-Stakes Gambler',
      'char.zhaohuan.role':  'Imperial Pawn · Phoenix Reborn',
      'char.zhangxian.role': 'Yue Family Army Deputy · First General · Lu Chen\'s Mentor',

      /* --- Catalog --- */
      'catalog.label':        'CATALOG',
      'catalog.title':        'Chapter Catalog',
      'catalog.desc':         'From the mountains where a star fell, to the far edge of the stellar sea — rewriting civilization, one step at a time.',
      'catalog.loading':      'Loading…',
      'catalog.locked':       'This volume has not begun yet. Stay tuned.',
      'catalog.badge.locked': 'Locked',
      'catalog.badge.avail':  'Available',
      'catalog.badge.next':   'Coming Soon',
      'catalog.fail':         'Failed to load chapter data. Please refresh.',
      'vol1.catalog.num':  'Vol. I',
      'vol1.catalog.name': 'Awakening & Foothold',
      'vol2.catalog.num':  'Vol. II',
      'vol2.catalog.name': 'Five Emperors & The Storm of Ages',
      'vol3.catalog.num':  'Vol. III',
      'vol3.catalog.name': 'Unification & The Dimensional Expedition',
      'vol4.catalog.num':  'Vol. IV',
      'vol4.catalog.name': 'World Government & The Echo of Stellar Fate',

      /* --- Characters Page --- */
      'chars.label':       'CHARACTERS',
      'chars.title':       'Character Gallery',
      'chars.desc':        'Key pieces on the chessboard of fate',
      'items.label':       'KEY ITEMS',
      'items.title':       'Key Items',

      /* --- Character Detail --- */
      'detail.back':    '← Back to Gallery',
      'detail.loading': 'Loading profile...',

      /* --- About --- */
      'about.label':    'ABOUT',
      'about.title':    'About the Novel',
      'about.subtitle': 'Industrial Song Dynasty, Stellar Fury',
      'about.s1.title': 'Synopsis',
      'about.s1.body':  '<p>Year 2056. A dimensional assault by an alien fleet has scorched the Earth\'s surface to ash. Deep in the underground "Final Ark," humanity makes its last decision — to send the only human capable of surviving a spacetime leap back through time, using a captured, half-broken alien shuttle engine.</p><p>His name is Lin Mo. Or before that, before he was burned to charred bone in Unit 731\'s incinerator, his name was Sun Mancang. A 116-year-old undying super-soldier — humanity\'s last bet.</p><p>But the broken engine suffers a catastrophic timeline deviation in the final three seconds of transmission. He doesn\'t arrive at the radio telescope in the 1970s. Instead, he crashes into an unnamed mountain range in the Southern Song Dynasty during the Shaoxing era.</p><p>Beginning as a mass of flesh clinging to a dimensional bracelet, his body slowly reconstitutes itself under ancient moonlight. Fractured memory, blank identity, stranded eight hundred years in the past — but on his wrist, sealed inside a black bracelet from a thousand years in the future, lies the pinnacle of all human technological achievement.</p><p>This is a story about technological compounding, civilizational survival, and the limits of humanity. No magic, no systems, no supernatural forces — only a mortal soldier who makes mistakes, grows tired, and doubts himself in the face of brutal casualties, wielding the power of industry, the logic of science, and a thousand-year head start to drag a 12th-century feudal empire into the era of interstellar defense.</p>',
      'about.s2.title': 'Creative Vision',
      'about.s2.body':  '<p>The core philosophy of this novel is <strong>"Industrial Song Dynasty, Stellar Fury."</strong> We pursue a cold, grand, and logically rigorous narrative style — the leap from 12th-century feudal society to interstellar civilization must be achieved through the terrifying force of technological compounding.</p><p>In language, we blend the elegant diction of the Song Dynasty with precise industrial and technical terminology. Visually, we pursue striking contrasts: steam engines in Lin\'an, armored cavalry armed with flintlock rifles, and the "hyperspace gravitational wave broadcast matrix" atop the dragon vein ridge.</p>',
      'about.rules.title': '◆ Core Iron Rules',
      'about.rules.body':  '<li><strong>No Game Systems</strong> — Absolutely forbidden to introduce any "skill point systems" or "ready-made blueprints." Every technological breakthrough must reflect the industrial process: concept → craftsman R&D → failure → finalization.</li><li><strong>No Magic</strong> — Pure magic or martial arts tropes are strictly forbidden. All technological advantages must originate from the protagonist\'s 2056 knowledge, the alien bracelet (limited resource), or the Song Dynasty\'s industrial potential.</li><li><strong>Intelligent Enemies</strong> — Enemies are not cardboard cutouts. Priority is given to their logic of counter-spying, stealing, and countering Song technology.</li><li><strong>Non-Divine Perspective</strong> — The protagonist is a mortal soldier who makes mistakes, grows tired, and doubts himself in the face of brutal casualties.</li><li><strong>Carbon-Based Mutation Limits</strong> — Offspring abilities must strictly follow carbon-based biological limits. Supernatural powers are absolutely forbidden.</li><li><strong>Merciful Unification</strong> — Priority is given to resolving survival pressures through technology transfer. When depicting enemy leaders, emphasize their psychological struggle facing the civilizational gap.</li><li><strong>Law of Civilization</strong> — When corruption and privilege arise in the rear, the protagonist must display absolute cold discipline. Civilizational law overrides blood ties.</li>',
      'about.s3.title': 'World Overview',
      'about.s3.body':  '<p><strong>Year 2056 —</strong> Thirty years after the alien fleet\'s dimensional assault. Earth\'s surface has been scorched to ash, and humanity\'s survivors have retreated to underground fortifications. In a long and desperate war, they\'ve captured alien spatial bracelets and a half-broken shuttle engine — paid for in mountains of corpses.</p><p><strong>Southern Song Dynasty, Shaoxing Era —</strong> The Zhao Song dynasty, clinging to the south of the Yangtze, faces the Jin Empire\'s predatory gaze from without, and decay and corruption from within. In an unnamed valley deep in the Tianmu Mountains, a black bracelet and a writhing mass of flesh fall from the sky.</p><p>The collision of two eras begins at this very moment.</p>',
      'about.author.bio': 'Hard sci-fi enthusiast. Believes technology is the foundational code of civilization, and that story is the best vessel to carry it.',

      /* --- Reader --- */
      'reader.header.loading':  'Loading…',
      'reader.prev':            '← No Previous Chapter',
      'reader.catalog.btn':     'Catalog',
      'reader.next':            'Coming Soon →',
      'reader.comments.title':  'Reader Comments',
      'reader.comments.empty':  'No comments yet. Be the first to leave one!',
      'reader.comments.load':   'Loading comments…',
      'reader.comments.fail':   'Failed to load comments. Please try again.',
      'reader.form.name':       'Your name (required)',
      'reader.form.email':      'Email (optional, not shown publicly)',
      'reader.form.content':    'Write your comment…',
      'reader.form.hint':       'Comments appear after approval',
      'reader.form.submit':     'Submit',
      'reader.form.submitting': 'Submitting…',
      'reader.form.ok':         'Comment submitted! It will appear after approval. Thank you!',
      'reader.form.err.name':   'Please enter your name.',
      'reader.form.err.content':'Please enter your comment.',
      'reader.form.err.fail':   'Submission failed. Please try again.',
      'reader.bookmark.toast':  '📌 Bookmark Found',
      'reader.bookmark.jump':   'Jump',
      'reader.overlay.title':   'View Catalog',
      'reader.overlay.load':    'Loading catalog…',
      'reader.chapter.fail':    'Failed to load chapter. Please try again.',
    }
  };

  /* ============================================================
     Core
     ============================================================ */
  var lang = localStorage.getItem('lang') || 'zh';

  function t(key) {
    return (T[lang] && T[lang][key]) || (T.zh && T.zh[key]) || key;
  }

  function applyLang() {
    document.documentElement.lang = lang === 'zh' ? 'zh-CN' : 'en';

    document.querySelectorAll('[data-i18n]').forEach(function (el) {
      el.textContent = t(el.getAttribute('data-i18n'));
    });

    document.querySelectorAll('[data-i18n-html]').forEach(function (el) {
      el.innerHTML = t(el.getAttribute('data-i18n-html'));
    });

    document.querySelectorAll('[data-i18n-placeholder]').forEach(function (el) {
      el.placeholder = t(el.getAttribute('data-i18n-placeholder'));
    });

    document.querySelectorAll('[data-i18n-aria]').forEach(function (el) {
      el.setAttribute('aria-label', t(el.getAttribute('data-i18n-aria')));
    });

    var btn = document.getElementById('lang-toggle');
    if (btn) btn.textContent = lang === 'zh' ? 'EN' : '中';

    document.dispatchEvent(new CustomEvent('langchange', { detail: lang }));
  }

  function toggle() {
    lang = lang === 'zh' ? 'en' : 'zh';
    localStorage.setItem('lang', lang);
    applyLang();
  }

  /* ============================================================
     Public API
     ============================================================ */
  window.i18n = { t: t, lang: function () { return lang; }, apply: applyLang };

  document.addEventListener('DOMContentLoaded', function () {
    var btn = document.getElementById('lang-toggle');
    if (btn) btn.addEventListener('click', toggle);
    applyLang();
  });
})();

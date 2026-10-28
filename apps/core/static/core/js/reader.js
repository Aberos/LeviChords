(function () {
  "use strict";

  var FONT_KEY = "levichords.fontSize";
  var THEME_KEY = "levichords.theme";
  var COLUMNS_KEY = "levichords.columns";
  var FIT_KEY = "levichords.fit";
  var TABS_KEY = "levichords.hideTabs";
  var PAGES_KEY = "levichords.pages";
  var FONT_MIN = 10;
  var FONT_MAX = 48;
  var FONT_STEP = 2;
  var FONT_DEFAULT = 22;
  var FIT_MIN = 10;
  var FIT_MAX = 48;
  var FIT_MARGIN = 24;
  var COLUMNS_MAX = 3;
  var COLUMNS_MIN_WIDTH = 600;
  var PAGE_MARGIN = 12;
  var PAGE_OVERLAP_LINES = 2;
  var LINE_HEIGHT = 1.3;
  var HINT_DURATION = 2500;
  var NEXT_KEYS = [32, 34, 39, 40];
  var PREVIOUS_KEYS = [33, 37, 38];
  var SCROLL_DELAYS = [0, 120, 70, 35];
  var SCROLL_LABELS = ["Rolar", "Rolar 1", "Rolar 2", "Rolar 3"];

  function read(key, fallback) {
    try {
      var value = window.localStorage.getItem(key);
      return value === null ? fallback : value;
    } catch (error) {
      return fallback;
    }
  }

  function write(key, value) {
    try {
      window.localStorage.setItem(key, value);
    } catch (error) {
      return;
    }
  }

  function applyTheme(theme) {
    var classes = document.body.className.replace(/\s*\blight\b/g, "");
    document.body.className = theme === "light" ? classes + " light" : classes;
  }

  applyTheme(read(THEME_KEY, "dark"));

  var reader = document.getElementById("reader");
  if (!reader) {
    return;
  }

  var sheets = reader.querySelectorAll(".sheet");
  var fontSize = parseInt(read(FONT_KEY, FONT_DEFAULT), 10) || FONT_DEFAULT;
  var columns = parseInt(read(COLUMNS_KEY, "1"), 10) || 1;
  var fitting = read(FIT_KEY, "0") === "1";
  var paging = read(PAGES_KEY, "0") === "1";
  var hideTabs = read(TABS_KEY, "0") === "1";
  var hasTabs = reader.querySelector(".block-tab") !== null;
  var page = 0;
  var scrollLevel = 0;
  var scrollTimer = null;
  var hintTimer = null;
  var lastWidth = window.innerWidth;
  var scrollButton = document.getElementById("scroll-button");
  var fitButton = document.getElementById("fit-button");
  var pagesButton = document.getElementById("pages-button");
  var columnsButton = document.getElementById("columns-button");
  var tabsButton = document.getElementById("tabs-button");
  var moreButton = document.getElementById("more-button");
  var morePanel = document.getElementById("reader-more");
  var fullscreenButton = document.getElementById("fullscreen-button");
  var toolbar = document.querySelector(".reader-toolbar");
  var root = document.documentElement;
  var hint = null;

  if (toolbar && hasTabs) {
    toolbar.className += " has-tabs";
  }

  function fullscreenAllowed() {
    var request = root.requestFullscreen || root.webkitRequestFullscreen ||
      root.webkitRequestFullScreen;
    var enabled = document.fullscreenEnabled;
    if (enabled === undefined) {
      enabled = document.webkitFullscreenEnabled;
    }
    return Boolean(request) && enabled !== false;
  }

  if (toolbar && fullscreenAllowed()) {
    toolbar.className += " has-fullscreen";
  }

  function toolbarHeight() {
    return toolbar ? toolbar.offsetHeight : 0;
  }

  function applyFont() {
    reader.style.fontSize = fontSize + "px";
  }

  function blocksOverflow() {
    var blocks = reader.querySelectorAll(".block");
    for (var index = 0; index < blocks.length; index += 1) {
      var block = blocks[index];
      if (/\bblock-tab\b/.test(block.className) || !block.offsetWidth) {
        continue;
      }
      if (block.scrollWidth > block.clientWidth + 1) {
        return true;
      }
    }
    return false;
  }

  function sheetsFit() {
    var available = window.innerHeight - toolbarHeight() - FIT_MARGIN;
    for (var index = 0; index < sheets.length; index += 1) {
      var sheet = sheets[index];
      var header = sheet.previousElementSibling;
      var height = sheet.offsetHeight + (header ? header.offsetHeight : 0);
      if (height > available) {
        return false;
      }
    }
    return !blocksOverflow();
  }

  function shrinkToWidth() {
    var size = fontSize;
    while (size > FIT_MIN && blocksOverflow()) {
      size -= 1;
      reader.style.fontSize = size + "px";
    }
  }

  function fitToScreen() {
    var low = FIT_MIN;
    var high = FIT_MAX;
    var best = FIT_MIN;
    while (low <= high) {
      var middle = Math.floor((low + high) / 2);
      reader.style.fontSize = middle + "px";
      if (sheetsFit()) {
        best = middle;
        low = middle + 1;
      } else {
        high = middle - 1;
      }
    }
    fontSize = best;
    applyFont();
  }

  function scrollToSheet() {
    if (sheets.length !== 1) {
      return;
    }
    var top = reader.getBoundingClientRect().top + window.pageYOffset;
    window.scrollTo(0, Math.max(0, top - 8));
  }

  function bookMode() {
    return paging && sheets.length === 1 && columns > 1 &&
      window.innerWidth >= COLUMNS_MIN_WIDTH;
  }

  function columnGap(sheet) {
    var style = window.getComputedStyle(sheet);
    var gap = parseFloat(style.columnGap || style.webkitColumnGap);
    return isNaN(gap) ? 0 : gap;
  }

  function pageWidth(sheet) {
    return sheet.clientWidth + columnGap(sheet);
  }

  function bookPageCount(sheet) {
    var total = (sheet.scrollWidth + columnGap(sheet)) / pageWidth(sheet);
    return Math.max(1, Math.ceil(total - 0.05));
  }

  function verticalStep() {
    var overlap = fontSize * LINE_HEIGHT * PAGE_OVERLAP_LINES;
    return Math.max(100, window.innerHeight - toolbarHeight() - overlap);
  }

  function verticalPageCount() {
    var scrollable = document.documentElement.scrollHeight - window.innerHeight;
    return Math.max(1, Math.ceil(scrollable / verticalStep() - 0.05) + 1);
  }

  function setBookHeight(sheet) {
    var top = sheet.getBoundingClientRect().top;
    var height = window.innerHeight - toolbarHeight() - top - PAGE_MARGIN;
    sheet.style.height = Math.max(160, Math.floor(height)) + "px";
  }

  function showBookPage() {
    var sheet = sheets[0];
    page = Math.max(0, Math.min(page, bookPageCount(sheet) - 1));
    sheet.scrollLeft = page * pageWidth(sheet);
  }

  function setupBook() {
    var sheet = sheets[0];
    scrollToSheet();
    setBookHeight(sheet);
    scrollToSheet();
    setBookHeight(sheet);
    showBookPage();
  }

  function clearBook() {
    for (var index = 0; index < sheets.length; index += 1) {
      sheets[index].style.height = "";
      sheets[index].scrollLeft = 0;
    }
  }

  function updatePagesButton() {
    if (!pagesButton) {
      return;
    }
    pagesButton.className = paging ? "active" : "";
    if (!paging) {
      pagesButton.textContent = "Páginas";
      return;
    }
    if (bookMode()) {
      pagesButton.textContent = (page + 1) + "/" + bookPageCount(sheets[0]);
      return;
    }
    var total = verticalPageCount();
    var current = Math.round(window.pageYOffset / verticalStep()) + 1;
    pagesButton.textContent = Math.min(current, total) + "/" + total;
  }

  function applyLayout() {
    var book = bookMode();
    var classes = reader.className
      .replace(/\s*\bcolumns-\d\b/g, "")
      .replace(/\s*\bhide-tabs\b/g, "")
      .replace(/\s*\bpaged\b/g, "");
    reader.className = classes + " columns-" + columns +
      (hideTabs ? " hide-tabs" : "") + (book ? " paged" : "");
    clearBook();
    if (fitting) {
      fitToScreen();
    } else {
      applyFont();
      shrinkToWidth();
    }
    if (book) {
      setupBook();
    }
    if (columnsButton) {
      columnsButton.textContent = columns +
        (columns > 1 ? " colunas" : " coluna");
    }
    if (tabsButton) {
      tabsButton.className = "toolbar-tabs" + (hideTabs ? " active" : "");
    }
    if (fitButton) {
      fitButton.className = fitting ? "active" : "";
    }
    updatePagesButton();
  }

  function showHint() {
    if (!hint) {
      hint = document.createElement("div");
      hint.className = "page-hint";
      hint.textContent = "Toque à direita para avançar e à esquerda " +
        "para voltar";
      document.body.appendChild(hint);
    }
    hint.className = "page-hint page-hint-visible";
    if (hintTimer !== null) {
      window.clearTimeout(hintTimer);
    }
    hintTimer = window.setTimeout(function () {
      hint.className = "page-hint";
      hintTimer = null;
    }, HINT_DURATION);
  }

  function turnPage(step) {
    if (bookMode()) {
      page += step;
      showBookPage();
    } else {
      window.scrollBy(0, step * verticalStep());
    }
    updatePagesButton();
  }

  function changeFont(delta) {
    var shown = parseInt(reader.style.fontSize, 10) || fontSize;
    fitting = false;
    write(FIT_KEY, "0");
    fontSize = Math.max(FONT_MIN, Math.min(FONT_MAX, shown + delta));
    write(FONT_KEY, String(fontSize));
    applyLayout();
  }

  function restoreFont() {
    fontSize = parseInt(read(FONT_KEY, FONT_DEFAULT), 10) || FONT_DEFAULT;
  }

  function toggleFit() {
    fitting = !fitting;
    write(FIT_KEY, fitting ? "1" : "0");
    if (fitting) {
      paging = false;
      write(PAGES_KEY, "0");
    } else {
      restoreFont();
    }
    applyLayout();
    if (fitting) {
      scrollToSheet();
    }
  }

  function togglePages() {
    paging = !paging;
    write(PAGES_KEY, paging ? "1" : "0");
    page = 0;
    if (paging && fitting) {
      fitting = false;
      write(FIT_KEY, "0");
      restoreFont();
    }
    applyLayout();
    if (paging) {
      scrollToSheet();
      updatePagesButton();
      showHint();
    }
  }

  function toggleTabs() {
    hideTabs = !hideTabs;
    write(TABS_KEY, hideTabs ? "1" : "0");
    applyLayout();
  }

  function cycleColumns() {
    columns = columns % COLUMNS_MAX + 1;
    write(COLUMNS_KEY, String(columns));
    page = 0;
    applyLayout();
  }

  function isMoreOpen() {
    return morePanel !== null && /\bopen\b/.test(morePanel.className);
  }

  function setMoreOpen(open) {
    if (!morePanel || !moreButton) {
      return;
    }
    morePanel.className = "reader-more" + (open ? " open" : "");
    moreButton.className = open ? "active" : "";
  }

  function toggleMore() {
    setMoreOpen(!isMoreOpen());
  }

  function isInsideToolbar(element) {
    while (element) {
      if (element === toolbar) {
        return true;
      }
      element = element.parentNode;
    }
    return false;
  }

  function fullscreenElement() {
    return document.fullscreenElement || document.webkitFullscreenElement ||
      document.webkitCurrentFullScreenElement || null;
  }

  function toggleFullscreen() {
    var result = null;
    if (fullscreenElement()) {
      var exit = document.exitFullscreen || document.webkitExitFullscreen ||
        document.webkitCancelFullScreen;
      if (exit) {
        result = exit.call(document);
      }
    } else {
      var request = root.requestFullscreen || root.webkitRequestFullscreen ||
        root.webkitRequestFullScreen;
      if (request) {
        result = request.call(root);
      }
    }
    if (result && result.then) {
      result.then(null, function () {
        return null;
      });
    }
    setMoreOpen(false);
  }

  function onFullscreenChange() {
    var active = fullscreenElement() !== null;
    if (fullscreenButton) {
      fullscreenButton.className = "toolbar-fullscreen" +
        (active ? " active" : "");
      fullscreenButton.textContent = active ? "Sair da tela cheia" :
        "Tela cheia";
    }
    window.setTimeout(function () {
      lastWidth = window.innerWidth;
      if (fitting || paging) {
        applyLayout();
      }
    }, 300);
  }

  function toggleTheme() {
    var next = /\blight\b/.test(document.body.className) ? "dark" : "light";
    write(THEME_KEY, next);
    applyTheme(next);
  }

  function cycleScroll() {
    scrollLevel = (scrollLevel + 1) % SCROLL_DELAYS.length;
    if (scrollTimer !== null) {
      window.clearInterval(scrollTimer);
      scrollTimer = null;
    }
    if (scrollLevel > 0) {
      scrollTimer = window.setInterval(function () {
        window.scrollBy(0, 1);
      }, SCROLL_DELAYS[scrollLevel]);
    }
    if (scrollButton) {
      scrollButton.textContent = SCROLL_LABELS[scrollLevel];
      scrollButton.className = scrollLevel > 0 ? "active" : "";
    }
  }

  function keepScreenOn() {
    if (!navigator.wakeLock || document.visibilityState !== "visible") {
      return;
    }
    navigator.wakeLock.request("screen").then(null, function () {
      return null;
    });
  }

  function isInteractive(element) {
    while (element && element !== reader) {
      if (/^(A|BUTTON|INPUT|SELECT|TEXTAREA)$/.test(element.tagName)) {
        return true;
      }
      element = element.parentNode;
    }
    return false;
  }

  function isInsideReader(element) {
    while (element) {
      if (element === reader) {
        return true;
      }
      element = element.parentNode;
    }
    return false;
  }

  function relayoutOnResize() {
    if (window.innerWidth === lastWidth) {
      return;
    }
    lastWidth = window.innerWidth;
    if (fitting || paging) {
      applyLayout();
    }
  }

  var actions = {
    "font-down": function () {
      changeFont(-FONT_STEP);
    },
    "font-up": function () {
      changeFont(FONT_STEP);
    },
    fit: toggleFit,
    pages: togglePages,
    columns: cycleColumns,
    tabs: toggleTabs,
    scroll: cycleScroll,
    theme: toggleTheme,
    more: toggleMore,
    fullscreen: toggleFullscreen
  };

  document.addEventListener("click", function (event) {
    var target = event.target;
    var action = target.getAttribute && target.getAttribute("data-action");
    if (action && actions[action]) {
      actions[action]();
      return;
    }
    if (isMoreOpen() && !isInsideToolbar(target)) {
      setMoreOpen(false);
      return;
    }
    if (paging && isInsideReader(target) && !isInteractive(target)) {
      turnPage(event.clientX < window.innerWidth / 3 ? -1 : 1);
    }
  });

  document.addEventListener("keydown", function (event) {
    var tag = event.target.tagName;
    if (!paging || /^(INPUT|SELECT|TEXTAREA)$/.test(tag)) {
      return;
    }
    var step = 0;
    if (NEXT_KEYS.indexOf(event.keyCode) !== -1) {
      step = 1;
    } else if (PREVIOUS_KEYS.indexOf(event.keyCode) !== -1) {
      step = -1;
    }
    if (step !== 0) {
      event.preventDefault();
      turnPage(step);
    }
  });

  window.addEventListener("scroll", function () {
    if (paging && !bookMode()) {
      updatePagesButton();
    }
  });

  document.addEventListener("visibilitychange", keepScreenOn);
  document.addEventListener("fullscreenchange", onFullscreenChange);
  document.addEventListener("webkitfullscreenchange", onFullscreenChange);
  window.addEventListener("resize", relayoutOnResize);
  window.addEventListener("orientationchange", function () {
    window.setTimeout(function () {
      lastWidth = -1;
      relayoutOnResize();
    }, 300);
  });

  applyLayout();
  if ((fitting || paging) && !window.location.hash) {
    scrollToSheet();
  }
  keepScreenOn();
}());

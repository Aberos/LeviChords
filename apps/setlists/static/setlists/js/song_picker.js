(function () {
  "use strict";

  var ACCENTED = "àáâãäåçèéêëìíîïñòóôõöùúûüýÿ";
  var PLAIN = "aaaaaaceeeeiiiinooooouuuuyy";
  var ACCENT_PATTERN = new RegExp("[" + ACCENTED + "]", "g");
  var PLACEHOLDER = "Escolha uma música";
  var EMPTY_OPTION = "Nenhuma música";
  var KEY_ENTER = 13;
  var KEY_ESCAPE = 27;
  var KEY_UP = 38;
  var KEY_DOWN = 40;
  var PANEL_GAP = 6;

  var openPicker = null;

  function simplify(text) {
    return text.toLowerCase().replace(ACCENT_PATTERN, function (letter) {
      return PLAIN.charAt(ACCENTED.indexOf(letter));
    });
  }

  function hasClass(element, name) {
    return new RegExp("(^|\\s)" + name + "(\\s|$)").test(element.className);
  }

  function setClass(element, name, enabled) {
    var cleaned = element.className
      .replace(new RegExp("(^|\\s)" + name + "(?=\\s|$)", "g"), "")
      .replace(/^\s+/, "");
    element.className = enabled ? cleaned + (cleaned ? " " : "") + name :
      cleaned;
  }

  function isInside(element, container) {
    while (element) {
      if (element === container) {
        return true;
      }
      element = element.parentNode;
    }
    return false;
  }

  function fireChange(select) {
    var event = document.createEvent("HTMLEvents");
    event.initEvent("change", true, false);
    select.dispatchEvent(event);
  }

  function create(tag, className) {
    var element = document.createElement(tag);
    element.className = className;
    return element;
  }

  function bottomBarHeight(below) {
    var bar = document.querySelector(".tabs");
    if (!bar) {
      return 0;
    }
    var top = bar.getBoundingClientRect().top;
    return top > below ? window.innerHeight - top : 0;
  }

  function enhance(select) {
    if (select.getAttribute("data-song-picker") === "ready") {
      return;
    }
    select.setAttribute("data-song-picker", "ready");

    var wrapper = create("div", "song-picker");
    var toggle = create("button", "song-picker-toggle");
    var panel = create("div", "song-picker-panel");
    var search = create("input", "song-picker-search");
    var list = create("ul", "song-picker-options");
    var empty = create("p", "song-picker-empty");
    var items = [];
    var current = -1;
    var picker = {};

    toggle.type = "button";
    toggle.id = select.id + "_picker";
    toggle.setAttribute("aria-haspopup", "listbox");
    toggle.setAttribute("aria-expanded", "false");
    search.type = "search";
    search.placeholder = "Buscar por título ou artista";
    search.setAttribute("autocomplete", "off");
    search.setAttribute("aria-label", "Buscar música");
    list.setAttribute("role", "listbox");
    empty.textContent = "Nenhuma música encontrada.";

    for (var index = 0; index < select.options.length; index += 1) {
      var option = select.options[index];
      var item = document.createElement("li");
      item.setAttribute("role", "option");
      item.setAttribute("data-value", option.value);
      item.textContent = option.value ? option.text : EMPTY_OPTION;
      items.push({
        element: item,
        value: option.value,
        text: simplify(option.text)
      });
      list.appendChild(item);
    }

    select.parentNode.insertBefore(wrapper, select);
    wrapper.appendChild(select);
    wrapper.appendChild(toggle);
    panel.appendChild(search);
    panel.appendChild(list);
    panel.appendChild(empty);
    wrapper.appendChild(panel);
    setClass(select, "song-picker-native", true);

    var label = document.querySelector("label[for='" + select.id + "']");
    if (label) {
      label.setAttribute("for", toggle.id);
    }

    function updateToggle() {
      var selected = select.options[select.selectedIndex];
      toggle.innerHTML = "";
      if (!selected || !selected.value) {
        var placeholder = create("span", "song-picker-placeholder");
        placeholder.textContent = PLACEHOLDER;
        toggle.appendChild(placeholder);
        return;
      }
      toggle.textContent = selected.text;
    }

    function isVisible(position) {
      return !hasClass(items[position].element, "song-picker-hidden");
    }

    function scrollToItem(element) {
      var top = element.offsetTop;
      var bottom = top + element.offsetHeight;
      if (top < list.scrollTop) {
        list.scrollTop = top;
      } else if (bottom > list.scrollTop + list.clientHeight) {
        list.scrollTop = bottom - list.clientHeight;
      }
    }

    function highlight(position) {
      if (current !== -1) {
        setClass(items[current].element, "song-picker-current", false);
      }
      current = position;
      if (current !== -1) {
        setClass(items[current].element, "song-picker-current", true);
        scrollToItem(items[current].element);
      }
    }

    function filter() {
      var terms = simplify(search.value).split(/\s+/);
      var searching = terms.join("") !== "";
      var first = -1;
      var selectedPosition = -1;
      for (var position = 0; position < items.length; position += 1) {
        var entry = items[position];
        var visible = !searching || entry.value !== "";
        for (var term = 0; visible && term < terms.length; term += 1) {
          visible = entry.text.indexOf(terms[term]) !== -1;
        }
        setClass(entry.element, "song-picker-hidden", !visible);
        setClass(entry.element, "song-picker-selected",
          entry.value === select.value);
        if (visible && first === -1) {
          first = position;
        }
        if (visible && entry.value === select.value) {
          selectedPosition = position;
        }
      }
      setClass(wrapper, "song-picker-no-results", first === -1);
      list.scrollTop = 0;
      highlight(searching || selectedPosition === -1 ? first :
        selectedPosition);
    }

    function step(direction) {
      var position = current;
      do {
        position += direction;
      } while (position >= 0 && position < items.length &&
        !isVisible(position));
      if (position >= 0 && position < items.length) {
        highlight(position);
      }
    }

    function place() {
      var rect = toggle.getBoundingClientRect();
      var needed = panel.offsetHeight + PANEL_GAP;
      var below = window.innerHeight - rect.bottom -
        bottomBarHeight(rect.bottom);
      setClass(wrapper, "song-picker-above",
        below < needed && rect.top > below);
    }

    function close(focusToggle) {
      setClass(wrapper, "song-picker-open", false);
      toggle.setAttribute("aria-expanded", "false");
      if (openPicker === picker) {
        openPicker = null;
      }
      if (focusToggle) {
        toggle.focus();
      }
    }

    function open() {
      if (openPicker) {
        openPicker.close(false);
      }
      openPicker = picker;
      setClass(wrapper, "song-picker-open", true);
      toggle.setAttribute("aria-expanded", "true");
      search.value = "";
      setClass(wrapper, "song-picker-above", false);
      filter();
      place();
      search.focus();
    }

    function choose(position) {
      if (position === -1) {
        return;
      }
      select.value = items[position].value;
      fireChange(select);
      updateToggle();
      close(true);
    }

    function itemPosition(element) {
      for (var position = 0; position < items.length; position += 1) {
        if (isInside(element, items[position].element)) {
          return position;
        }
      }
      return -1;
    }

    toggle.addEventListener("click", function () {
      if (hasClass(wrapper, "song-picker-open")) {
        close(true);
      } else {
        open();
      }
    });

    list.addEventListener("click", function (event) {
      choose(itemPosition(event.target));
    });

    search.addEventListener("input", filter);

    search.addEventListener("keydown", function (event) {
      if (event.keyCode === KEY_DOWN) {
        event.preventDefault();
        step(1);
      } else if (event.keyCode === KEY_UP) {
        event.preventDefault();
        step(-1);
      } else if (event.keyCode === KEY_ENTER) {
        event.preventDefault();
        choose(current);
      } else if (event.keyCode === KEY_ESCAPE) {
        event.preventDefault();
        close(true);
      }
    });

    picker.wrapper = wrapper;
    picker.close = close;
    updateToggle();
  }

  function enhanceAll(root) {
    var selects = root.querySelectorAll("select[data-song-picker]");
    for (var index = 0; index < selects.length; index += 1) {
      enhance(selects[index]);
    }
  }

  document.addEventListener("click", function (event) {
    if (openPicker && !isInside(event.target, openPicker.wrapper)) {
      openPicker.close(false);
    }
  });

  window.songPicker = {enhanceAll: enhanceAll};
  enhanceAll(document);
}());

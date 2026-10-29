(function () {
  "use strict";

  var list = document.getElementById("setlist-items");
  var template = document.getElementById("empty-item");
  var addButton = document.getElementById("add-item");
  if (!list || !template) {
    return;
  }

  var prefix = list.getAttribute("data-prefix");
  var total = document.getElementById("id_" + prefix + "-TOTAL_FORMS");

  function rows() {
    return list.querySelectorAll(".setlist-item");
  }

  function renumber() {
    var all = rows();
    for (var index = 0; index < all.length; index += 1) {
      var position = all[index].querySelector("input[name$='-position']");
      if (position) {
        position.value = index + 1;
      }
    }
  }

  function closestRow(element) {
    while (element && element !== list) {
      if (/\bsetlist-item\b/.test(element.className)) {
        return element;
      }
      element = element.parentNode;
    }
    return null;
  }

  function move(row, direction) {
    if (direction === "up" && row.previousElementSibling) {
      list.insertBefore(row, row.previousElementSibling);
    }
    if (direction === "down" && row.nextElementSibling) {
      list.insertBefore(row.nextElementSibling, row);
    }
    renumber();
  }

  function addRow() {
    var index = parseInt(total.value, 10);
    var holder = document.createElement("div");
    holder.innerHTML = template.innerHTML
      .replace(/__prefix__/g, index)
      .replace(/^\s+|\s+$/g, "");
    var row = holder.firstChild;
    list.appendChild(row);
    total.value = index + 1;
    renumber();
    if (window.songPicker) {
      window.songPicker.enhanceAll(row);
    }
  }

  function closestAction(element) {
    while (element && element !== list) {
      if (element.getAttribute && element.getAttribute("data-action")) {
        return element.getAttribute("data-action");
      }
      element = element.parentNode;
    }
    return null;
  }

  list.addEventListener("click", function (event) {
    var action = closestAction(event.target);
    var row = closestRow(event.target);
    if (row && (action === "up" || action === "down")) {
      move(row, action);
    }
  });

  if (addButton) {
    addButton.addEventListener("click", addRow);
  }

  renumber();
}());

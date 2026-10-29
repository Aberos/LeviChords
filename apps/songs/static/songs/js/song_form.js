(function () {
  "use strict";

  var PARTIAL_PARAMETER = "parcial=1";

  var button = document.querySelector("button[name='preview']");
  if (!button || !window.XMLHttpRequest || !window.FormData) {
    return;
  }

  var form = button.form;
  var fallback = false;
  var pending = null;

  function pageUrl() {
    return window.location.href.split("#")[0];
  }

  function partialUrl(url) {
    return url + (url.indexOf("?") === -1 ? "?" : "&") + PARTIAL_PARAMETER;
  }

  function submitWithoutScript() {
    fallback = true;
    button.click();
  }

  function showPreview(html) {
    var holder = document.createElement("div");
    holder.innerHTML = html;
    var preview = holder.querySelector("#previa");
    if (!preview) {
      submitWithoutScript();
      return;
    }
    var current = document.getElementById("previa");
    if (current) {
      current.parentNode.replaceChild(preview, current);
    } else {
      form.parentNode.insertBefore(preview, form);
    }
    preview.scrollIntoView();
  }

  function requestPreview() {
    var data = new FormData(form);
    var request = new XMLHttpRequest();
    data.append("preview", "1");
    pending = request;
    request.onreadystatechange = function () {
      if (request.readyState !== 4) {
        return;
      }
      pending = null;
      if (request.status === 200) {
        showPreview(request.responseText);
      } else {
        submitWithoutScript();
      }
    };
    request.open("POST", partialUrl(pageUrl()), true);
    request.send(data);
  }

  button.addEventListener("click", function (event) {
    if (fallback) {
      return;
    }
    event.preventDefault();
    if (pending === null) {
      requestPreview();
    }
  });
}());

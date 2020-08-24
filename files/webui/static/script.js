const _ = selector => {
  let list = document.querySelectorAll(selector);
  return list.length == 1 ? list[0] : list;
}

function get(url, callback) {
  var xhr = new XMLHttpRequest();
  xhr.open('GET', url, true);
  xhr.onreadystatechange = function () {
    if (xhr.readyState == 4 && xhr.status == 200 || xhr.status == 304) {
      callback(this, xhr.responseText);
    }
  };
  xhr.send();
}

function parse(response) {
  let data = JSON.parse(response.responseText);
  _("#commands").innerText = data["stats"]["commands"];
}

setInterval(get, 1000, 'http://127.0.0.1:26363/ajax', parse);
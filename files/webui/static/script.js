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

let cmdNum = 0;

function parse(response) {
  let data = JSON.parse(response.responseText);
  let newCmdNum = data['info']["commands"];
  _("#commands").innerText = `${newCmdNum} (${newCmdNum - cmdNum}/s)`;
  cmdNum = newCmdNum;
  _("#time").innerText = new Date(data.time * 1000).toLocaleString();
  let modulesTag = _("#modules");
  modulesTag.innerHTML = '';
  for (let key in data["info"]["modules"]) {
    let module = data["info"]["modules"][key];
    let moduleDiv = document.createElement('div');
    moduleDiv.setAttribute('class', 'content shadow article');
    let moduleName = document.createElement('h4');
    moduleName.setAttribute('class', 'name center');
    moduleDiv.appendChild(moduleName);
    moduleName.innerText = module.id;
    let description = document.createElement('div');
    description.setAttribute('class', 'description center');
    description.appendChild(document.createTextNode(module.description));
    moduleDiv.appendChild(description);
    let configGrid = document.createElement('tr');
    moduleDiv.appendChild(configGrid);
    for (let key2 in module.config) {
      let config = module.config[key2];
      let configEntry = document.createElement('div');
      configEntry.setAttribute('class', 'entry');
      switch (typeof config) {
        case 'boolean':
          let checkBox = document.createElement('input');
          checkBox.setAttribute('type', 'checkbox');
          checkBox.checked = config;
          configEntry.appendChild(checkBox);
          configEntry.appendChild(document.createTextNode(key2));
          break;
        case "number":
          let spinner = document.createElement('input');
          spinner.setAttribute('type', 'number');
          spinner.value = config;
          configEntry.appendChild(document.createTextNode(key2));
          configEntry.appendChild(spinner);
          break;
        case "string":
          let textField = document.createElement('input');
          textField.size = 6;
          textField.value = config;
          configEntry.appendChild(document.createTextNode(key2));
          configEntry.appendChild(textField);
          break;
      }
      configGrid.appendChild(configEntry);
    }
    modulesTag.appendChild(moduleDiv);
  }
}

function parsesys(response) {
  let data = JSON.parse(response.responseText);
  _("#os").innerText = data["platform"];
  _("#hostname").innerText = data["hostname"];
  _("#python").innerText = data["python"];
}

setInterval(get, 1000, 'ajax', parse);
get('sysinfo', parsesys);
get('ajax', parse);
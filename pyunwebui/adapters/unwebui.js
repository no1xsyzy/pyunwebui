(function() {

const undefined = void 0

window.UNWEBUI = window.UNWEBUI || {}

const props = new Set([ "autoplay", "checked", "checked", "contentEditable", "controls",
  "default", "hidden", "loop", "selected", "spellcheck", "value", "id", "title",
  "accessKey", "dir", "dropzone", "lang", "src", "alt", "preload", "poster",
  "kind", "label", "srclang", "sandbox", "srcdoc", "type", "value", "accept",
  "placeholder", "acceptCharset", "action", "autocomplete", "enctype", "method",
  "name", "pattern", "htmlFor", "max", "min", "step", "wrap", "useMap", "shape",
  "coords", "align", "cite", "href", "target", "download", "download",
  "hreflang", "ping", "start", "headers", "scope", "span" ]);

function setProperty(el, prop, value) {
  if (props.has(prop)) {
    el[prop] = value;
  } else {
    el.setAttribute(prop, value);
  }
}

window.UNWEBUI.setProperty = setProperty

function eventTypeFromAttributeName(str) {
  if (str.indexOf("e:") == 0) {
    return str.slice(2).toLowerCase();
  }
  return null;
}

function setMessage(el, eventType, msg) {
  if (el.getAttribute('e:'+eventType) === null) {
    el.addEventListener(eventType, omniListener);
  }
  el.setAttribute('e:'+eventType, msg)
}

window.UNWEBUI.setMessage = setMessage

function omniListener(event) {
  const el = event.currentTarget;
  const msg = el.getAttribute('e:'+event.type)
  if (msg !== null) {
    UNWEBUI.send_message(msg)
  }
}

function autoSet(el, attrName, value){
  console.log("autoSet", el, attrName, value)
  const eventType = eventTypeFromAttributeName(attrName);
  if (eventType !== null){
    setMessage(el, eventType, value)
  } else {
    setProperty(el, attrName, value)
  }
}

function create(vnode) {
  console.log("create", vnode)
   // Create a text node
  if (typeof vnode === 'string') {
    const el = document.createTextNode(vnode);
    return el;
  }

  // Create the DOM element with the correct tag and
  // already add our object of listeners to it.
  const el = document.createElement(vnode.tag_name);
    console.log("vnode.attributes", vnode.attributes)
  for (const attrName in vnode.attributes) {
  console.log("attrName", attrName)
    const value = vnode.attributes[attrName];
    autoSet(el, attrName, value)
  }

  // Recursively create all the children and append one by one.
  for (const childVNode of vnode.children) {
    const child = create(childVNode);
    el.appendChild(child);
  }

  return el;
}

window.UNWEBUI.create = create

function apply(el, childrenDiff) {
  const children = Array.from(el.childNodes);

  childrenDiff.forEach((diff, i) => {
    const action = Object.keys(diff)[0];
    switch (action) {
      case "remove":
        children[i].remove()
        break

      case "modify":
        modify(children[i], diff.modify)
        break

      case "create":
        el.appendChild(create(diff.create))
        break

      case "replace":
        children[i].replaceWith(create(diff.replace))
        break

      case "noop":
        break
    }
  });
}

window.UNWEBUI.apply = apply

function modify(el, diff) {
  // Remove props
  for (const attrName of diff.removes) {
    const eventType = eventTypeFromAttributeName(attrName);
    el.removeAttribute(attrName);
    if (eventType !== null) {
      el.removeEventListener(eventType, listener);
    }
  }

  for (const attrName in diff.sets) {
    const value = diff.set[attrName];
    autoSet(el, attrName, value)
  }

  apply(el, diff.children);
}

window.UNWEBUI.modify = modify

window.addEventListener("load", (event) => {
    const app = document.querySelector('#app')
    let socket
    let past = 1

    function make_socket(){
        socket = new WebSocket("ws");

        socket.addEventListener("open", (event) => {
            socket.send("sync");
            past = 1
        })

        socket.addEventListener("message", (event) => {
            switch (event.data[0]) {
                case "p":  // progressive
                    const diff = JSON.parse(event.data.slice(1))
                    apply(app, diff)
                    break;
                case "i":  // independent
                    const vnl = JSON.parse(event.data.slice(1))
                    app.replaceChildren(...vnl.map(vn=>create(vn)))
                    break;
                default:
                    console.warn("Unknown message from server ", event.data);
            }
        })

        socket.addEventListener('close', (e) => {
            socket.close()
            console.log('ws event <close>', e)
            setTimeout(() => {past=past*2; make_socket()}, past*1000)
        })

        socket.addEventListener('error', (e) => {
            socket.close()
            console.log('ws event <error>', e)
            setTimeout(() => {past=past*2; make_socket()}, past*1000)
        })
    }

    window.UNWEBUI.make_socket = make_socket

    function send_message(m){
        socket.send('msg'+m)
    }

    window.UNWEBUI.send_message = send_message

    make_socket()
})

})();

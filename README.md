pyunwebui
====

Use (almost) only python code to build webui, although it DOES require understanding of DOM.
The design is mostly based on [A virtual DOM in 200 lines of JavaScript](https://lazamar.github.io/virtual-dom/)

Features
----

* Write almost only python to create a webui.
* Functional-style Programming. Virtual DOM and transmit only diff to browser over WebSocket.
* Model-View-Message. Using only event/message to update data. Easy to trace and debug.

Future Plans
----

* More adapters
* Example: TodoMVC
* Documentation
* Unit tests
* Use event data
* Emulates JS Web API (such as copy/paste)
* More ...

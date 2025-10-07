let backend; // this will represent Python
let historyPages = [];

// connect to Python side
new QWebChannel(qt.webChannelTransport, function (channel) {
  backend = channel.objects.backend;
});

const menu = document.getElementById("menu");
const editor = document.getElementById("editor");

// show menu on selection
document.addEventListener("mouseup", () => {
  const selection = window.getSelection();
  if (selection && !selection.isCollapsed) {
    const range = selection.getRangeAt(0);
    const rect = range.getBoundingClientRect();
    menu.style.top = `${window.scrollY + rect.top - 50}px`;
    menu.style.left = `${window.scrollX + rect.left}px`;
    menu.style.display = "block";
  } else {
    menu.style.display = "none";
  }
});
function saveContent() {
  const content = editor.innerHTML;
  backend.save_content(historyPages.at(-1), content);
}
// create a new page and wrap selection with a link that points to the created file
async function create_page() {
  const selection = window.getSelection();
  if (!selection || selection.rangeCount === 0 || selection.isCollapsed) {
    console.warn("No selection");
    return;
  }
  const range = selection.getRangeAt(0);

  // send selection to Python - get a safe filename back
  const content = editor.innerHTML;
  const loader = LoadingBox("Fetching data...");
  loader.show();
  const pagename = await backend.createpage(
    selection.toString(),
    getContextAroundSelection(
      extractTextFromHTML(content),
      selection.toString().trim()
    ),
    "grade 11"
  );

  loader.hide();

  // build the link and attach the filename as data attribute
  const link = document.createElement("a");
  link.href = "#";
  // link.onclick = (e) => showPage(pagename, e);
  link.setAttribute("onclick", "showPage('" + pagename + "',event)");

  link.draggable = false; // prevent accidental drags

  // preserve formatting
  const contents = range.extractContents();
  link.appendChild(contents);

  // optional: wrap so it's non-editable (but if that blocks clicks in your environment, remove contentEditable=false)
  const wrapper = document.createElement("span");
  wrapper.contentEditable = "false"; // if this breaks clickability, remove this line
  wrapper.appendChild(link);

  range.insertNode(wrapper);

  // move caret after inserted wrapper
  selection.removeAllRanges();
  const caret = document.createRange();
  caret.setStartAfter(wrapper);
  caret.collapse(true);
  selection.addRange(caret);

  menu.style.display = "none";
}

async function showPage(page, e, isloading = false) {
  if (e) {
    e.preventDefault();
  }

  if (!isloading) {
    saveContent();
  }
  historyPages.push(page);
  fetch("../pages/" + page)
    .then((res) => res.text())
    .then((html) => (document.getElementById("editor").innerHTML = html));
  loadpage();
}
function goBack() {
  saveContent();
  historyPages.pop();
  fetch("../pages/" + historyPages.at(-1))
    .then((res) => res.text())
    .then((html) => (document.getElementById("editor").innerHTML = html));
  loadpage();
}
function loadpage() {
  // load lecture
  const lecture_div = document.getElementById("lecture_location");
  const lecture_player = document.getElementById("lecture_player");
  lecture_player.src = lecture_div.dataset.lectureLocation;
}
async function create_lecture() {
  const content = editor.innerHTML;

  const loader = LoadingBox("Fetching data...");
  loader.show();
  lecture_filelocation = await backend.create_lecture(content);
  loader.hide();
  // build the link and attach the filename as data attribute
  const lecture_player = document.getElementById("lecture_player");
  lecture_filelocation = "../" + lecture_filelocation;
  lecture_player.src = lecture_filelocation;
  lecture_player.play(); // optional — plays automatically
  editor.innerHTML =
    editor.innerHTML +
    '<div id="lecture_location" data-lecture-location="' +
    lecture_filelocation +
    '" ></div>';
  saveContent();
  // move caret after inserted wrapper
  selection.removeAllRanges();
}
function extractTextFromHTML(htmlString) {
  const parser = new DOMParser();
  const doc = parser.parseFromString(htmlString, "text/html");
  return doc.body.textContent || "";
}
function getContextAroundSelection(text, selection, range = 10) {
  // Split text into words (keeping punctuation)
  const words = text.split(/\s+/);

  // Find the first index of the selected word (basic match)
  const index = words.findIndex(
    (w) => w.replace(/[^\w]/g, "") === selection.replace(/[^\w]/g, "")
  );

  if (index === -1) return null; // selection not found

  // Compute start and end boundaries
  const start = Math.max(0, index - range);
  const end = Math.min(words.length, index + range + 1);

  // Join them back into one string
  const context = words.slice(start, end).join(" ");

  return context;
}

async function create_mindmap() {
  const content = editor.innerHTML;
}

function LoadingBox(message = "Loading...") {
  let box = document.createElement("div");
  box.id = "loadingBox";
  box.style.cssText = `
    position:fixed; top:50%; left:50%;
    transform:translate(-50%,-50%);
    background:#fff; padding:20px 40px;
    border-radius:8px; box-shadow:0 2px 8px rgba(0,0,0,.3);
    font-family:sans-serif;
  `;
  box.innerHTML = message;
  document.body.appendChild(box);

  return {
    show: () => (box.style.display = "block"),
    hide: () => (box.style.display = "none"),
    remove: () => box.remove(),
  };
}

const observer = new MutationObserver(() => {
  const lecture_div = document.getElementById("lecture_location");
  if (lecture_div) {
    loadpage(); // ✅ element appeared — safe to run
  }
});

observer.observe(editor, { childList: true, subtree: true });

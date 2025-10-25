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
    return;
  }
  const range = selection.getRangeAt(0);

  // send selection to Python - get a safe filename back
  const content = editor.innerHTML;
  const loader = LoadingBox("Fetching data...");
  loader.show();
  current_page = historyPages.at(-1);
  backend.createpage(
    selection.toString(),
    getContextAroundSelection(
      extractTextFromHTML(content),
      selection.toString().trim()
    ),
    current_page,
    "grade 11"
  );
  backend.pageCreated.connect(function (note_id) {
    loader.hide();

    // build the link and attach the filename as data attribute
    const link = document.createElement("a");
    link.href = "#";
    // link.onclick = (e) => showPage(pagename, e);
    link.setAttribute("onclick", "showPage('" + note_id + "',event)");

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
    loadNotes();

    menu.style.display = "none";
  });
}

async function showPage(noteID, e, isloading = false) {
  if (e) {
    e.preventDefault();
  }
  if (!isloading) {
    saveContent();
  } else {
    loadNotes();
  }
  historyPages.push(noteID);
  var link =
    (await backend.getNotesDIR()) + "/" + noteID + "/" + noteID + ".html";

  console.warn("dsfsdfsd  " + link);
  fetch(link)
    .then((res) => {
      if (!res.ok) {
        throw new Error(`Note not found: ${notePath}`);
      }
      return res.text();
    })
    .then((html) => (document.getElementById("editor").innerHTML = html))
    .catch(async (err) => {
      alert("Note not found, going back...");
      historyPages.pop();
      return;
    });
  loadpage();
}
async function goBack() {
  saveContent();
  if (historyPages.length == 1) {
    alert("No more history");
    return;
  }
  historyPages.pop();
  noteID = historyPages.at(-1);

  fetch((await backend.getNotesDIR()) + "/" + noteID + "/" + noteID + ".html")
    .then((res) => res.text())
    .then((html) => (document.getElementById("editor").innerHTML = html));
  loadpage();
}
async function loadpage() {
  current_page = historyPages.at(-1);
  assets_locations = {};
  await fetch((await backend.getNotesDIR()) + "/" + current_page + "/meta.json")
    .then((response) => {
      if (!response.ok) throw new Error("Failed to fetch JSON file");

      // Read it only once
      return response.json();
    })
    .then((data) => {
      assets_locations = data["assets_location"];
    })
    .catch((error) => console.error("Error loading JSON:", error));
  //init
  const lecture_player = document.getElementById("lecture_player");
  const flashcard_viewer = document.getElementById("flashcard_viewer");
  const mindmap_viewer = document.getElementById("mindmap_viewer");

  // load lecture
  lecture_player.src = "../" + assets_locations["lecture_location"];
  // load mindmap
  mindmap_viewer.src = "../" + assets_locations["mindmap_location"];
  // load flashcards
  flashcard_viewer.src = `flaschcard_carousel/flashcard.html?flashcardslocation=${encodeURIComponent(
    "../../" + assets_locations["flashcards_location"]
  )} `;
  toggleVisibility();
  addImageWrapper();
}

async function addImageWrapper() {
  document.querySelectorAll("img").forEach((img) => {
    // Skip if already wrapped
    if (img.parentElement.classList.contains("img-wrapper")) return;

    const wrapper = document.createElement("div");
    wrapper.className = "img-wrapper";
    wrapper.contentEditable = "false"; // prevent editing inside wrapper

    img.parentNode.insertBefore(wrapper, img);
    wrapper.appendChild(img);
  });
}
async function create_lecture() {
  const content = editor.innerHTML;

  const loader = LoadingBox("Fetching data...");
  loader.show();
  current_page = historyPages.at(-1);
  lecture_filelocation = await backend.create_lecture(content, current_page);
  backend.lectureCreated.connect(function (lecture_filelocation) {
    loader.hide();
    // build the link and attach the filename as data attribute
    const lecture_player = document.getElementById("lecture_player");
    lecture_filelocation = "../" + lecture_filelocation;
    lecture_player.src = lecture_filelocation;
    lecture_player.play(); // optional — plays automatically
    toggleVisibility();
  });
  // move caret after inserted wrapper
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
  const loader = LoadingBox("Fetching data...");
  loader.show();
  await backend.create_mindmap(content, historyPages.at(-1));
  backend.mindmapCreated.connect(function (mindmap_filelocation) {
    loader.hide();
    // build the link and attach the filename as data attribute
    const mindmap_viewer = document.getElementById("mindmap_viewer");
    mindmap_filelocation = "../" + mindmap_filelocation;
    mindmap_viewer.src = mindmap_filelocation;
    toggleVisibility();
  });
}

async function create_flashcards() {
  const content = editor.innerHTML;
  NOflashcards = prompt("Enter the desired Number of flashcards:");
  while (NOflashcards == null || NOflashcards > 10) {
    NOflashcards = prompt("Enter the desired Number of flashcards:");
  }
  const loader = LoadingBox("Fetching data...");
  loader.show();
  await backend.create_flashcards(content, NOflashcards, historyPages.at(-1));
  backend.flashcardsCreated.connect(function (flashcards_filelocation) {
    loader.hide();
    // build the link and attach the filename as data attribute
    const flashcard_viewer = document.getElementById("flashcard_viewer");
    flashcards_filelocation = "../" + flashcards_filelocation;

    flashcard_viewer.src = `flaschcard_carousel/flashcard.html?flashcards=${encodeURIComponent(
      flashcards_filelocation
    )} `;
    toggleVisibility();
  });
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
  const lecture_player = document.getElementById("lecture_player");
  if (!lecture_player) return; // ⛔ element not yet available
  loadpage(); // ✅ element appeared — safe to run
});

async function loadNotes() {
  const treeRoot = document.getElementById("tree-root");
  notesTree = JSON.parse(await backend.getNoteTreeJson());
  treeRoot.innerHTML = "";

  const rootNode = notesTree.root ?? notesTree;
  treeRoot.appendChild(createTreeNode(rootNode));
}
observer.observe(editor, { childList: true, subtree: true });
document.addEventListener("keydown", function (event) {
  // Check if Alt is pressed AND the left arrow key
  if (event.ctrlKey && event.key === "ArrowLeft") {
    event.preventDefault(); // prevent default browser behavior (like going back)
    goBack();
  }
});
document.addEventListener("keydown", function (event) {
  if (event.ctrlKey && event.key === "s") {
    event.preventDefault();
    saveContent();
  }
});
document.addEventListener("keydown", function (event) {
  if (event.ctrlKey && event.key === "e") {
    event.preventDefault();
    create_page();
  }
});
// Recursive function to create the HTML tree
function createTreeNode(note) {
  const li = document.createElement("li");
  li.classList.add("tree-node");
  li.dataset.id = note.id;

  // clickable title span
  const titleSpan = document.createElement("span");
  titleSpan.textContent = note.title;
  titleSpan.classList.add("node-title");
  li.appendChild(titleSpan);

  // recursively build children if they exist
  if (note.children && note.children.length > 0) {
    li.classList.add("collapsible");

    const ul = document.createElement("ul");
    note.children.forEach((child) => ul.appendChild(createTreeNode(child)));
    li.appendChild(ul);

    // 🔹 Expand/collapse on arrow click (the ::before pseudo-element)
    // We'll detect clicks near the left side of the title area.
    li.addEventListener("click", (e) => {
      // click within first 16px from left → toggle
      const clickX = e.offsetX;
      if (clickX < 16) {
        e.stopPropagation();
        li.classList.toggle("expanded");
      }
    });
  }

  // 🔹 Click title to open the note
  titleSpan.addEventListener("click", (e) => {
    e.stopPropagation();
    showPage(note.id);
  });

  return li;
}

const sidebar = document.getElementById("sidebar");
const resizer = document.getElementById("sidebar-resizer");

let isResizing = false;

resizer.addEventListener("mousedown", (e) => {
  isResizing = true;
  document.body.style.cursor = "ew-resize";
});

document.addEventListener("mousemove", (e) => {
  if (!isResizing) return;
  const newWidth = Math.min(Math.max(e.clientX, 180), 500); // min/max width
  sidebar.style.width = `${newWidth}px`;
});

document.addEventListener("mouseup", () => {
  isResizing = false;
  document.body.style.cursor = "default";
});
const toggleBtn = document.getElementById("theme-toggle");
const body = document.body;

// Load saved theme preference
if (localStorage.getItem("theme") === "dark") {
  body.setAttribute("data-theme", "dark");
}

function toggleTheme() {
  const isDark = body.getAttribute("data-theme") === "dark";
  body.setAttribute("data-theme", isDark ? "light" : "dark");
  localStorage.setItem("theme", isDark ? "light" : "dark");
}
document.addEventListener("keydown", function (event) {
  if (event.ctrlKey && event.key === "d") {
    event.preventDefault();
    backend.delete_Note(historyPages.at(-1));
    loadNotes();
  }
});
function toggleVisibility() {
  const lectureSection = document.getElementById("lecture_player1");
  const lecture = document.getElementById("lecture_player");
  const mindmapSection = document.getElementById("mindmap-section");
  const mindmap = document.getElementById("mindmap_viewer");
  const flashcardsSection = document.getElementById("flashcards-section");
  const flashcards = document.getElementById("flashcard_viewer");

  if (
    !lecture.src ||
    lecture.src.trim() ===
      "file:///F:/SourceProg/Projects/AI_Learning_Assistant/ai_learning_assistant3/" ||
    lecture.src === "../"
  ) {
    lectureSection.style.display = "none";
  } else {
    lectureSection.style.display = "block";
  }
  // Hide/show Mindmap
  if (
    !mindmap.src ||
    mindmap.src.trim() ===
      "file:///F:/SourceProg/Projects/AI_Learning_Assistant/ai_learning_assistant3/" ||
    mindmap.src === "../"
  ) {
    mindmapSection.style.display = "none";
  } else {
    mindmapSection.style.display = "block";
  }

  // Hide/show Flashcards
  if (
    !flashcards.src ||
    flashcards.src.trim() ===
      "file:///F:/SourceProg/Projects/AI_Learning_Assistant/ai_learning_assistant3/web/flaschcard_carousel/flashcard.html?flashcardslocation=..%2F..%2F" ||
    flashcards.src === "flaschcard_carousel/flashcard.html"
  ) {
    flashcardsSection.style.display = "none";
  } else {
    flashcardsSection.style.display = "block";
  }
}

async function goHome() {
  backend.goHome();
}

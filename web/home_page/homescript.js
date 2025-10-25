let backend; // this will represent Python
// connect to Python side
new QWebChannel(qt.webChannelTransport, function (channel) {
  backend = channel.objects.backend;
});
document.addEventListener("DOMContentLoaded", async () => {
  const container = document.getElementById("kb-grid");
  const addButton = document.getElementById("add-kb-btn");
  const modal = document.getElementById("kb-modal");
  const saveBtn = document.getElementById("save-kb-btn");
  const cancelBtn = document.getElementById("cancel-kb-btn");

  if (!container) {
    console.error("❌ Could not find element #kb-grid in DOM.");
    return;
  }

  // 🔹 Function to create a card
  const createCard = (kb_id, title, description, summary) => {
    const card = document.createElement("article");
    card.classList.add("kb-card");
    card.setAttribute("role", "listitem");

    card.innerHTML = `
      <div class="kb-thumbnail">
        <div class="kb-note-embed">
          <h4>${title}</h4>
          <p>${description}</p>
        </div>
      </div>
      <div class="kb-content">
        <p>${summary}</p>
        <a href="#" data-id="${kb_id}" class="kb-button">View Article</a>
      </div>
    `;
    return card;
  };

  // 🔹 Load initial Knowledge Bases
  try {
    const response = await fetch("../../Knowbases/bases.json");
    const kbData = await response.json();

    kbData.forEach((item) => {
      const card = createCard(
        item.id,
        item.title,
        item.description,
        item.summary
      );
      container.appendChild(card);
    });
  } catch (error) {
    console.error("❌ Error loading Knowledge Bases:", error);
    container.innerHTML = "<p>⚠️ Failed to load knowledge base items.</p>";
  }

  // 🔹 Show modal when Add button is clicked
  addButton.addEventListener("click", () => {
    modal.classList.add("active");
  });

  // 🔹 Close modal
  cancelBtn.addEventListener("click", () => {
    modal.classList.remove("active");
  });

  // 🔹 Save new KB from modal input
  saveBtn.addEventListener("click", () => {
    const title = document.getElementById("kb-title-input").value.trim();
    const description = document
      .getElementById("kb-description-input")
      .value.trim();
    const summary = document.getElementById("kb-summary-input").value.trim();
    const id = backend.create_kb(title, summary, description);

    if (!title || !description) {
      alert("⚠️ Please fill in both the Title and Description.");
      return;
    }

    const newCard = createCard(title, description, summary, id);

    // Add to top with fade-in
    newCard.style.opacity = "0";
    container.prepend(newCard);
    setTimeout(() => {
      newCard.style.transition = "opacity 0.4s ease";
      newCard.style.opacity = "1";
    }, 50);

    // Close modal + clear inputs
    modal.classList.remove("active");
    document
      .querySelectorAll("#kb-modal input, #kb-modal textarea")
      .forEach((el) => (el.value = ""));
  });
  document.querySelectorAll(".kb-button").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      const id = e.target.dataset.id;
      console.warn(id);
      backend.open_kb(id);
    });
  });
  function toggleTheme() {
    const isDark = body.getAttribute("data-theme") === "dark";
    body.setAttribute("data-theme", isDark ? "light" : "dark");
    localStorage.setItem("theme", isDark ? "light" : "dark");
  }
});

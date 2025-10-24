async function loadflashcards() {
  /*****************
   * 1. Flashcard data
   *****************/
  const params = new URLSearchParams(window.location.search);
  flashcardslocation = params.get("flashcardslocation");
  flashcards = [
    {
      id: "card1",
      front: "Do you want to Add flashcards to test your knowledge",
      back: "Click on the create button and then on the flashcards",
      hint: "look in the top left",
      hintDetails: "Occurs in chloroplasts",
      type: "Init",
      difficulty: 1,
    },
  ];
  if (flashcardslocation != null) {
    await fetch(flashcardslocation)
      .then((response) => {
        if (!response.ok) throw new Error("Failed to fetch JSON file");

        return response.json();
      })
      .then((data) => {
        flashcards = data["flashcards"];
      })
      .catch((error) => console.error("Error loading JSON:", error));
  } else {
    flashcards = [];
  }
  const gallery = document.getElementById("gallery");

  /*****************
   * 2. Render cards
   *****************/
  flashcards.forEach((card) => {
    const wrapper = document.createElement("div");
    wrapper.classList.add("card-wrap");
    wrapper.innerHTML = `
          <input type="checkbox" id="${card.id}" class="card-toggle" />
          <label for="${card.id}" class="card">
            <div class="card-face card-front">
              <header class="card-header">
                <span class="badge type-badge">${card.type}</span>
                <div class="difficulty" data-difficulty="${card.difficulty}"></div>
              </header>
              <div class="card-body">
                <h2 class="card-question">${card.front}</h2>
                <p class="meta hint-text" hidden>Hint: ${card.hint}</p>
              </div>
            </div>
            <div class="card-face card-back">
              <header class="card-header">
                <span class="badge type-badge">${card.type}</span>
                <div class="difficulty" data-difficulty="${card.difficulty}"></div>
              </header>
              <div class="card-body">
                <h3 class="card-answer">${card.back}</h3>
                <details class="hint">
                  <summary>Show hint</summary>
                  <p>${card.hintDetails}</p>
                </details>
              </div>
            </div>
          </label>
        `;
    gallery.appendChild(wrapper);
  });

  /*****************
   * 3. Carousel state
   *****************/
  const total = flashcards.length;
  let currentIndex = 0 % total;

  const updateCarousel = () => {
    const cardWidth = gallery.children[0].offsetWidth + 60; // 60px gap
    const offset = (gallery.offsetWidth - cardWidth) / 2; // center active card
    gallery.style.transform = `translateX(${
      offset - currentIndex * cardWidth
    }px)`;

    // highlight active card
    [...gallery.children].forEach((wrap, i) => {
      wrap.classList.toggle("active", i === currentIndex);
    });
  };

  // Wait until DOM paints so offsetWidth is accurate
  window.addEventListener("load", updateCarousel);
  window.addEventListener("resize", updateCarousel);

  document.querySelector(".next").addEventListener("click", () => {
    currentIndex = (currentIndex + 1) % total;
    updateCarousel();
  });

  document.querySelector(".prev").addEventListener("click", () => {
    currentIndex = (currentIndex - 1 + total) % total;
    updateCarousel();
  });

  /*****************
   * 4. Keyboard control
   *****************/
  window.addEventListener("click", () => {
    window.focus();
    document.body.focus();
  });

  let lastSpaceTime = 0;
  document.addEventListener("keydown", (e) => {
    const now = Date.now();
    const wrap = gallery.children[currentIndex];
    const toggle = wrap.querySelector(".card-toggle");
    const hintText = wrap.querySelector(".hint-text");

    if (e.code === "KeyD") {
      e.preventDefault(); // stop Chromium from stealing it

      currentIndex = (currentIndex + 1) % total;
      updateCarousel();
    } else if (e.code === "KeyA") {
      e.preventDefault(); // stop Chromium from stealing it

      currentIndex = (currentIndex - 1 + total) % total;
      updateCarousel();
    } else if (e.code === "Space") {
      e.preventDefault();
      // Double-press threshold
      if (now - lastSpaceTime < 300) {
        // double space -> flip
        toggle.checked = !toggle.checked;
        hintText.hidden = true; // hide hint when flipping
      } else {
        // single space -> toggle hint
        hintText.hidden = !hintText.hidden;
      }
      lastSpaceTime = now;
    }
  });
  updateCarousel();
}

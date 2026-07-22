// Reusable function for opening and closing modals

function setupModal(cardId, modalId, closeClass) {

    const card = document.getElementById(cardId);
    const modal = document.getElementById(modalId);
    const closeBtn = document.querySelector(closeClass);

    if (!card || !modal || !closeBtn) return;

    // Open Modal
    card.addEventListener("click", () => {
        modal.style.display = "flex";
    });

    // Close using X
    closeBtn.addEventListener("click", () => {
        modal.style.display = "none";
    });

    // Close when clicking outside
    window.addEventListener("click", (event) => {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });

}


// AI Summary
setupModal(
    "ai-summary-card",
    "summaryModal",
    ".close"
);

// Repository Health
setupModal(
    "health-card",
    "healthModal",
    ".health-close"
);

// Architecture
setupModal(
    "architecture-card",
    "architectureModal",
    ".architecture-close"
);

// Security
setupModal(
    "security-card",
    "securityModal",
    ".security-close"
);

// Tech Stack
setupModal(
    "tech-card",
    "techModal",
    ".tech-close"
);

// AI Chat
setupModal(
    "chat-card",
    "chatModal",
    ".chat-close"
);
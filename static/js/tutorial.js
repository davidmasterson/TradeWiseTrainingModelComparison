let currentStep = 1;


function showTutorial() {
    // Display the tutorial overlay
    document.getElementById("tutorial-overlay").classList.remove("hidden");
    // Show the first step of the tutorial
    showStep(currentStep);
}

function showStep(step) {
    // Clear all previous highlights
    document.querySelectorAll(".highlight").forEach((el) => el.classList.remove("highlight"));

    // Show the current tutorial step
    document.querySelectorAll(".tutorial-step").forEach((stepElement) => {
        stepElement.classList.add("hidden");
    });
    document.getElementById(`tutorial-step-${step}`).classList.remove("hidden");

    // Highlight specific elements for each step
    if (step === 2) {
        document.getElementById("feature-element-id").classList.add("highlight");
    }
    if (step === 3) {
        document.getElementById("feature-element-id").classList.add("highlight");
    }
    if (step === 4) {
        document.getElementById("feature-element-id").classList.add("highlight");
    }
    if (step === 5) {
        document.getElementById("feature-element-id").classList.add("highlight");
    }
    
}

function nextStep() {
    currentStep++;
    if (document.getElementById(`tutorial-step-${currentStep}`)) {
        showStep(currentStep);
    } else {
        endTutorial();
    }
}

function endTutorial() {
    document.getElementById("tutorial-overlay").classList.add("hidden");
    currentStep = 1;  // Reset to the beginning
}

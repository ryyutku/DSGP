document.addEventListener("DOMContentLoaded", () => {
    const visualizeBtn = document.getElementById("visualizeBtn");
    const predictionPanel = document.getElementById("predictionPanel");
    const generateChartBtn = document.getElementById("generateChart");
    const chartContainer = document.getElementById("chartContainer");
    const predictionChart = document.getElementById("predictionChart");

    visualizeBtn.addEventListener("click", () => {
        predictionPanel.style.display = "block";
        gsap.to(predictionPanel, { opacity: 1, y: 0, duration: 0.8 });
    });

    generateChartBtn.addEventListener("click", () => {
        chartContainer.style.display = "block";
        gsap.from(chartContainer, { opacity: 0, y: 50, duration: 0.8 });

        // Simulating chart update
        predictionChart.src = "fuelpricepredictions.png";
    });
});

document.addEventListener("scroll", function() {
    let scrollPosition = window.scrollY;
    document.querySelector(".hero-bg").style.transform = `translateY(${scrollPosition * 0.5}px)`;
});


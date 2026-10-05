function updateTime() {
    const now = new Date();
    document.getElementById("currentTime").textContent =
        "Current Time: " + now.toLocaleTimeString();
}

updateTime();
setInterval(updateTime, 1000);
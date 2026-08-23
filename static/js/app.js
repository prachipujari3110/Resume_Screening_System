document.addEventListener("DOMContentLoaded", function () {

    const button = document.getElementById("themeToggle");

    if (button) {
        button.addEventListener("click", function () {
            document.body.classList.toggle("light-mode");

            if (document.body.classList.contains("light-mode")) {
                localStorage.setItem("theme", "light");
            } else {
                localStorage.setItem("theme", "dark");
            }
        });
    }

    if (localStorage.getItem("theme") === "light") {
        document.body.classList.add("light-mode");
    }

    const flashes = document.querySelectorAll(".flash");

    flashes.forEach(function (flash) {
        setTimeout(function () {
            flash.style.opacity = "0";

            setTimeout(function () {
                flash.remove();
            }, 300);

        }, 3500);
    });

});


$(document).ready(function () {

    
    $("#registerForm").on("submit", function (e) {
        const name = this.name.value.trim();
        const email = this.email.value.trim();
        const age = this.age.value;
        const gender = this.gender.value;
        const course = this.course.value;
        const password = this.password.value;

        if (!name || !email || !age || !gender || !course || !password) {
            e.preventDefault();
            alert("Please fill all required fields.");
        } else if (age === "" || !Number.isFinite(Number(age)) || Number(age) <= 0) {
            e.preventDefault();
            alert("Enter a valid age.");
        } else if (password.length < 6) {
            e.preventDefault();
            alert("Password must contain at least 6 characters.");
        }
    });

    
    function updateClock() {
        const clock = document.getElementById("clock");

        if (clock) {
            clock.textContent = new Date().toLocaleTimeString();
        }
    }

    updateClock();
    setInterval(updateClock, 1000);

    
    $("#toggleBtn").on("click", function () {
        $("#studentDetails").toggle();
    });

    // Level 4: AJAX course update
    $("#courseForm").on("submit", function (e) {
        e.preventDefault();

        const course = $("#course").val();
        $("#message").text("Updating course...");

        $.post("/update-course", { course: course })
            .done(function (response) {
                $("#currentCourse").text(response.course);
                $("#message")
                    .text("Course updated to: " + response.course)
                    .css("color", "green");
                alert("Course updated to: " + response.course);
            })
            .fail(function (xhr) {
                let message = "Could not update course.";

                if (xhr.responseJSON && xhr.responseJSON.message) {
                    message = xhr.responseJSON.message;
                }

                $("#message").text(message).css("color", "red");
            });
    });

});

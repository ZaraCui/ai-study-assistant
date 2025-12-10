async function ask() {
    const course = document.getElementById("courseInput").value.trim();
    const question = document.getElementById("questionInput").value.trim();
    const box = document.getElementById("responseBox");

    if (!course || !question) {
        box.innerText = "Please enter both course and question!";
        return;
    }

    box.innerText = "Loading...";

    try {
        const response = await fetch("https://YOUR_BACKEND_URL/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                course: course,
                question: question
            })
        });

        if (!response.ok) {
            box.innerText = `Error: ${response.status}`;
            return;
        }

        const data = await response.json();
        box.innerText = data.answer || "No answer returned.";
    }
    catch (err) {
        box.innerText = "Connection error: " + err;
    }
}

async function ask() {
    const course = document.getElementById("courseInput").value.trim();
    const question = document.getElementById("questionInput").value.trim();
    const box = document.getElementById("responseBox");

    // Check if both course and question are entered
    if (!course || !question) {
        box.innerText = "Please enter both course and question!";
        return;
    }

    // Show loading message while fetching
    box.innerText = "Loading...";

    try {
        const response = await fetch("https://ai-study-assistant-5xa4.onrender.com/ask", { // Replace with your backend API URL
            method: "POST",
            headers: { 
                "Content-Type": "application/json" 
            },
            body: JSON.stringify({
                course: course,
                question: question
            })
        });

        // If response is not okay, show the error
        if (!response.ok) {
            box.innerText = `Error: ${response.status}`;
            return;
        }

        // If request is successful, parse the response and display the answer
        const data = await response.json();
        box.innerText = data.answer || "No answer returned.";
    }
    catch (err) {
        // If there is a connection error, display the error message
        box.innerText = "Connection error: " + err;
    }
}

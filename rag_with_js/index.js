const form = document.querySelector("form");
const input = document.querySelector("input");
const reply = document.querySelector(".reply");

form.addEventListener("submit", function (e) {
  e.preventDefault();
  main(input.value);
  console.log("Question submitted:", input.value);
  input.value = "";
});

async function main(question) {
  try {
    console.log("Question received:", question);
    reply.innerHTML = "Thinking...";

    const response = await fetch("http://localhost:3000/api/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    const data = await response.json();
    console.log("Final response:", data);
    reply.innerHTML = data.content;
  } catch (error) {
    console.error("Error in main function.", error.message);
    reply.innerHTML = "Sorry, something went wrong. Please try again.";
  }
}

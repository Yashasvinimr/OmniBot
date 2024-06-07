// async function postData(url="", data={}){
//     const response = await fetch(url, {
//         method: "POST", headers: {
//             "Content-Type": "application/json",
//         }, body: JSON.stringify(data),
//     });
//     return response.json();
// }
// sendButton1.addEventListener("click", async()=>{
//     questionInput=document.getElementById("questionInput").value;
//     document.getElementById("questionInput").value="";
//     document.querySelector(".right2").style.display="block"
//     document.querySelector(".right1").style.display="none"

//     question.innerHTML=questionInput;
//     //get the naswer and populate it
//     let result = await postData("/api", {"question":questionInput})
//     solution.innerHTML = result.result

// })
// sendButton1.addEventListener("Enter", async()=>{
    
//         questionInput=document.getElementById("questionInput").value;
//         document.getElementById("questionInput").value="";
//         document.querySelector(".right2").style.display="block"
//         document.querySelector(".right1").style.display="none"

//         question.innerHTML=questionInput;
//         //get the naswer and populate it
//         let result = await postData("/api", {"question":questionInput})
//         solution.innerHTML = result.result
    
// })
// sendButton1.addEventListener("click", async () => {
//     await handleQuestionSubmission();
// });
// sendButton2.addEventListener("click", async () => {
//     await handleQuestionSubmission();
// });
// document.getElementById("questionInput").addEventListener("keydown", async (event) => {
//     if (event.key === "Enter") {
//         event.preventDefault(); // Prevent the default action of the Enter key (e.g., form submission)
//         await handleQuestionSubmission();
//     }
// });

// async function handleQuestionSubmission() {
//     const questionInputElement = document.getElementById("questionInput");
//     const questionInput = questionInputElement.value;
//     questionInputElement.value = "";
//     document.querySelector(".right2").style.display = "block";
//     document.querySelector(".right1").style.display = "none";

//     question.innerHTML = questionInput;
//     // Get the answer and populate it
//     let result = await postData("/api", { "question": questionInput });
//     solution.innerHTML = result.result;
// }

// // Assuming postData is a function that sends a POST request and returns the response
// async function postData(url = '', data = {}) {
//     const response = await fetch(url, {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json'
//         },
//         body: JSON.stringify(data)
//     });
//     return response.json(); // Assuming the server returns JSON
// }
// Function to handle question submission
async function handleQuestionSubmission(inputElementId) {
    const questionInputElement = document.getElementById(inputElementId);
    const questionInput = questionInputElement.value.trim();

    if (!questionInput) {
        return; // Do nothing if the input is empty
    }

    questionInputElement.value = "";
    document.querySelector(".right2").style.display = "block";
    document.querySelector(".right1").style.display = "none";

    const chatContainer = document.getElementById("chatContainer");
    const questionDiv = document.createElement("div");
    questionDiv.className = "chat-box question";
    questionDiv.innerHTML = `<img class="w-9" src="https://cdn4.iconfinder.com/data/icons/small-n-flat/24/user-group-512.png" alt=""><div class="chat-text">${questionInput}</div>`;
    chatContainer.appendChild(questionDiv);

    const solutionDiv = document.createElement("div");
    solutionDiv.className = "chat-box answer";
    solutionDiv.innerHTML = `<img class="w-9 h-9" src="https://chat.openai.com/favicon.ico" alt=""><div class="chat-text"><div class="solution">Loading...</div></div>`;
    chatContainer.appendChild(solutionDiv);

    // Scroll to the bottom of the chat container
    chatContainer.scrollTop = chatContainer.scrollHeight;

    // Get the answer and populate it
    let result = await postData("/api", { "question": questionInput });
    solutionDiv.querySelector(".solution").innerHTML = result.result;

    // Scroll to the bottom of the chat container
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Event listener for sendButton2
document.getElementById("sendButton2").addEventListener("click", async () => {
    await handleQuestionSubmission("questionInput2");
});

// Event listener for Enter key in the question input field
document.getElementById("questionInput2").addEventListener("keydown", async (event) => {
    if (event.key === "Enter") {
        event.preventDefault(); // Prevent the default action of the Enter key (e.g., form submission)
        await handleQuestionSubmission("questionInput2");
    }
});


// Function to send a POST request
async function postData(url = '', data = {}) {
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });
    return response.json(); // Assuming the server returns JSON
}

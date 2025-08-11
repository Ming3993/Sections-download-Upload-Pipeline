const dropArea = document.querySelector(".drag-area"),
  dragText = dropArea.querySelector("header"),
  button = dropArea.querySelector("button"),
  input = dropArea.querySelector("input");

let uploadQueue = []; // chỉ dùng để hiển thị file vừa upload, nhưng trạng thái lấy từ server

button.onclick = () => {
  input.click();
};

input.addEventListener("change", function () {
  for (let f of this.files) {
    uploadFile(f); // gửi lên server
  }
  this.value = ""; // reset để chọn lại file giống nhau
});

dropArea.addEventListener("dragover", (event) => {
  event.preventDefault();
  dropArea.classList.add("active");
  dragText.textContent = "Release to Upload File";
});

dropArea.addEventListener("dragleave", () => {
  dropArea.classList.remove("active");
  dragText.textContent = "Drag & Drop to Upload File";
});

dropArea.addEventListener("drop", (event) => {
  event.preventDefault();
  for (let f of event.dataTransfer.files) {
    uploadFile(f);
  }
  dropArea.classList.remove("active");
  dragText.textContent = "Drag & Drop to Upload File";
});

function updateQueueUI(statusData) {
  const queueList = document.querySelector("#queue-list");
  queueList.innerHTML = "";

  // Hiển thị file đang xử lý
  if (statusData.processing) {
    const liProcessing = document.createElement("li");
    liProcessing.textContent = `Processing: ${statusData.processing}`;
    liProcessing.style.fontWeight = "bold";
    queueList.appendChild(liProcessing);
  }

  // Hiển thị các file pending
  statusData.pending.forEach((filename, idx) => {
    const li = document.createElement("li");
    li.textContent = `${idx + 1}. ${filename} - pending`;
    queueList.appendChild(li);
  });
}

function pollStatus() {
  fetch("/status")
    .then(res => res.json())
    .then(data => {
      updateQueueUI(data);
    })
    .catch(err => console.error(err));
}

setInterval(pollStatus, 1500);
pollStatus(); // gọi ngay lần đầu

function uploadFile(file) {
  let validExtensions = ["text/plain"];
  if (!validExtensions.includes(file.type)) {
    alert(".txt files only");
    return;
  }

  let formData = new FormData();
  formData.append("file", file);

  fetch("/upload", {
    method: "POST",
    body: formData
  })
    .then(res => res.json())
    .then(data => {
      console.log("Uploaded:", data.filename);
      // Không cần push vào uploadQueue nữa, sẽ hiển thị dựa trên status server
    })
    .catch(err => {
      console.error("Error uploading:", err);
      alert("Upload failed");
    });
}

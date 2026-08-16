const apiBase = "/api/v1";
const elements = {
  status: document.querySelector("#status"),
  fileInput: document.querySelector("#file-input"),
  dropzone: document.querySelector("#dropzone"),
  progress: document.querySelector("#upload-progress"),
  list: document.querySelector("#document-list"),
  count: document.querySelector("#document-count"),
  form: document.querySelector("#ask-form"),
  question: document.querySelector("#question"),
  askButton: document.querySelector("#ask-button"),
  empty: document.querySelector("#empty-answer"),
  answerCard: document.querySelector("#answer-card"),
  answerText: document.querySelector("#answer-text"),
  citations: document.querySelector("#citations"),
  provider: document.querySelector("#provider"),
  message: document.querySelector("#message"),
};

async function api(path, options = {}) {
  const response = await fetch(path, options);
  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      detail = body.detail || detail;
    } catch (_) {
      // Keep the status-based fallback when the response is not JSON.
    }
    throw new Error(detail);
  }
  if (response.status === 204) return null;
  return response.json();
}

function showMessage(message = "") {
  elements.message.textContent = message;
}

async function checkHealth() {
  try {
    await api("/health");
    elements.status.classList.add("online");
    elements.status.lastChild.textContent = " Online";
  } catch (_) {
    elements.status.classList.remove("online");
    elements.status.lastChild.textContent = " Offline";
  }
}

async function loadDocuments() {
  const documents = await api(`${apiBase}/documents`);
  elements.list.replaceChildren();
  elements.count.textContent = String(documents.length);

  if (!documents.length) {
    const empty = document.createElement("small");
    empty.textContent = "No documents indexed yet.";
    empty.style.color = "var(--muted)";
    elements.list.append(empty);
    return;
  }

  for (const documentItem of documents) {
    const item = document.createElement("div");
    item.className = "document-item";
    const name = document.createElement("strong");
    name.textContent = documentItem.filename;
    name.title = documentItem.filename;
    const meta = document.createElement("small");
    meta.textContent = `${documentItem.page_count} pages · ${documentItem.chunk_count} chunks`;
    const remove = document.createElement("button");
    remove.className = "delete-button";
    remove.type = "button";
    remove.title = `Delete ${documentItem.filename}`;
    remove.setAttribute("aria-label", `Delete ${documentItem.filename}`);
    remove.textContent = "×";
    remove.addEventListener("click", async () => {
      try {
        await api(`${apiBase}/documents/${documentItem.id}`, { method: "DELETE" });
        await loadDocuments();
      } catch (error) {
        showMessage(error.message);
      }
    });
    item.append(name, meta, remove);
    elements.list.append(item);
  }
}

async function uploadFile(file) {
  if (!file) return;
  showMessage();
  elements.progress.classList.remove("hidden");
  const form = new FormData();
  form.append("file", file);
  try {
    await api(`${apiBase}/documents`, { method: "POST", body: form });
    await loadDocuments();
  } catch (error) {
    showMessage(error.message);
  } finally {
    elements.progress.classList.add("hidden");
    elements.fileInput.value = "";
  }
}

elements.fileInput.addEventListener("change", () => uploadFile(elements.fileInput.files[0]));
for (const eventName of ["dragenter", "dragover"]) {
  elements.dropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    elements.dropzone.classList.add("dragging");
  });
}
for (const eventName of ["dragleave", "drop"]) {
  elements.dropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    elements.dropzone.classList.remove("dragging");
  });
}
elements.dropzone.addEventListener("drop", (event) => uploadFile(event.dataTransfer.files[0]));

elements.form.addEventListener("submit", async (event) => {
  event.preventDefault();
  showMessage();
  elements.askButton.disabled = true;
  elements.askButton.firstChild.textContent = "Thinking… ";
  try {
    const result = await api(`${apiBase}/chat/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: elements.question.value.trim() }),
    });
    elements.empty.classList.add("hidden");
    elements.answerCard.classList.remove("hidden");
    elements.answerText.textContent = result.answer;
    elements.provider.textContent = result.provider.toUpperCase();
    elements.citations.replaceChildren();
    for (const citation of result.citations) {
      const card = document.createElement("div");
      card.className = "citation";
      const title = document.createElement("strong");
      title.textContent = `[${citation.number}] ${citation.filename} · page ${citation.page}`;
      const excerpt = document.createElement("div");
      excerpt.textContent = `${citation.excerpt}…`;
      card.append(title, excerpt);
      elements.citations.append(card);
    }
  } catch (error) {
    showMessage(error.message);
  } finally {
    elements.askButton.disabled = false;
    elements.askButton.firstChild.textContent = "Ask documents ";
  }
});

Promise.allSettled([checkHealth(), loadDocuments()]).then((results) => {
  const failed = results.find((result) => result.status === "rejected");
  if (failed) showMessage(failed.reason.message);
});


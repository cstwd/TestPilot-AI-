const form = document.getElementById("run-engine");
if (form) {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = form.querySelector("button");
    const notice = document.getElementById("notice");
    const fields = new FormData(form);
    button.disabled = true;
    notice.removeAttribute("data-error");
    notice.textContent = "正在生成测试并运行隔离 Pytest，请稍候。";
    try {
      const response = await fetch("/api/engine/files/" + form.dataset.fileId + "/tasks", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({target: fields.get("target"), generation_mode: fields.get("generation_mode"),
                              max_repairs: Number(fields.get("max_repairs"))})
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.detail || "请求失败");
      location.assign("/engine?task_id=" + encodeURIComponent(result.id));
    } catch (error) {
      notice.setAttribute("data-error", "");
      notice.textContent = error.message;
      button.disabled = false;
    }
  });
}

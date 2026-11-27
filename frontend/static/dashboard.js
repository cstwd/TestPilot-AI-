"use strict";

const apiStatus = document.getElementById("api-status");
const databaseStatus = document.getElementById("database-status");
const connectionDetail = document.getElementById("connection-detail");
const refreshButton = document.getElementById("refresh-button");
const selfTestButton = document.getElementById("self-test-button");
const selfTestStatus = document.getElementById("self-test-status");
const selfTestDetail = document.getElementById("self-test-detail");

function showStatus(element, text, state = "pending") {
  element.textContent = text;
  element.dataset.state = state;
}

async function readStatus(url, method, timeout) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);
  try {
    const response = await fetch(url, {
      method,
      cache: "no-store",
      signal: controller.signal,
      headers: { Accept: "application/json" },
    });
    const payload = await response.json();
    if (typeof payload?.status !== "string") throw new Error("状态响应格式异常");
    return payload;
  } finally {
    clearTimeout(timer);
  }
}

async function checkConnections() {
  refreshButton.disabled = true;
  showStatus(apiStatus, "检查中");
  showStatus(databaseStatus, "检查中");
  connectionDetail.textContent = "正在读取服务状态…";
  try {
    const health = await readStatus("/api/health", "GET", 8000);
    if (!["ok", "degraded"].includes(health.status)) throw new Error("服务状态异常");
    showStatus(apiStatus, "已连接", "good");
    const ready = health.database === "ok";
    showStatus(databaseStatus, ready ? "已连接" : "异常", ready ? "good" : "error");
    connectionDetail.textContent = "最近检查时间 " + new Date().toLocaleTimeString("zh-CN");
  } catch {
    showStatus(apiStatus, "检查失败", "error");
    showStatus(databaseStatus, "无法确认");
    connectionDetail.textContent = "请查看 PyCharm 运行日志，确认服务已启动后重新检查。";
  } finally {
    refreshButton.disabled = false;
  }
}

async function runSelfTest() {
  selfTestButton.disabled = true;
  showStatus(selfTestStatus, "运行中");
  selfTestDetail.textContent = "";
  try {
    const result = await readStatus("/api/self-test", "POST", 60000);
    if (result.status === "passed") {
      showStatus(selfTestStatus, "通过", "good");
      selfTestDetail.textContent = result.detail;
    } else if (result.status === "busy") {
      showStatus(selfTestStatus, "执行器忙碌");
      selfTestDetail.textContent = "已有自检正在运行，请稍后重试。";
    } else {
      showStatus(selfTestStatus, "未通过", "error");
      selfTestDetail.textContent = "请查看 PyCharm 运行日志以定位执行器问题。";
    }
  } catch {
    showStatus(selfTestStatus, "无法获取结果", "error");
    selfTestDetail.textContent = "请重新检查服务连接，并查看 PyCharm 运行日志。";
  } finally {
    selfTestButton.disabled = false;
  }
}

refreshButton.addEventListener("click", checkConnections);
selfTestButton.addEventListener("click", runSelfTest);
checkConnections();

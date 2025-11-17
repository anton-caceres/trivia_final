// ---------------------------
// Estado del juego en cliente
// ---------------------------
let questions = [];
let currentIndex = 0;
let answers = [];
let playerName = "";

// Timer por pregunta
const timePerQuestion = 20; // segundos
let timeLeft = timePerQuestion;
let timerId = null;

// ---------------------------
// Referencias al DOM
// ---------------------------
const setupSection = document.getElementById("setup-section");
const gameSection = document.getElementById("game-section");
const resultSection = document.getElementById("result-section");
const statusSpan = document.getElementById("network-status");

const playerInput = document.getElementById("player-name");
const questionCountSelect = document.getElementById("question-count");
const startBtn = document.getElementById("start-btn");

const labelPlayer = document.getElementById("label-player");
const currentQuestionIndexSpan = document.getElementById(
  "current-question-index"
);
const totalQuestionsSpan = document.getElementById("total-questions");
const questionCategorySpan = document.getElementById("question-category");
const questionDifficultySpan =
  document.getElementById("question-difficulty");
const questionText = document.getElementById("question-text");
const optionsContainer = document.getElementById("options-container");
const nextBtn = document.getElementById("next-btn");

const resultPlayerName = document.getElementById("result-player-name");
const resultScore = document.getElementById("result-score");
const resultExtra = document.getElementById("result-extra");
const networkDetail = document.getElementById("network-detail");
const playAgainBtn = document.getElementById("play-again-btn");

// Elementos del timer
const timerSpan = document.getElementById("timer");
const timeMessage = document.getElementById("time-message");

// ---------------------------
// Monitoreo básico de red
// ---------------------------
function checkNetworkStatus() {
  fetch("/api/questions?amount=1", { method: "GET" })
    .then((r) => {
      if (!r.ok) throw new Error("Error");
      statusSpan.textContent = "🟢 Conectado al servidor";
      statusSpan.classList.remove("status-error");
      statusSpan.classList.add("status-ok");
    })
    .catch(() => {
      statusSpan.textContent = "🔴 Servidor no disponible";
      statusSpan.classList.remove("status-ok");
      statusSpan.classList.add("status-error");
    });
}

// Primera verificación al cargar
window.onload = () => {
  checkNetworkStatus();
  setInterval(checkNetworkStatus, 5000);
};

// ---------------------------
// Timer por pregunta
// ---------------------------
function updateTimerDisplay() {
  if (!timerSpan) return;
  timerSpan.textContent = timeLeft;

  // reset clases
  timerSpan.classList.remove("timer-ok", "timer-warning", "timer-danger");

  const ratio = timeLeft / timePerQuestion;
  if (ratio > 0.5) {
    timerSpan.classList.add("timer-ok");
  } else if (ratio > 0.2) {
    timerSpan.classList.add("timer-warning");
  } else {
    timerSpan.classList.add("timer-danger");
  }
}

function startTimer() {
  stopTimer(); // por las dudas

  timeLeft = timePerQuestion;
  updateTimerDisplay();
  if (timeMessage) {
    timeMessage.textContent = "";
  }

  timerId = setInterval(() => {
    timeLeft -= 1;
    if (timeLeft >= 0) {
      updateTimerDisplay();
    }
    if (timeLeft <= 0) {
      // Tiempo agotado
      stopTimer();
      handleTimeOut();
    }
  }, 1000);
}

function stopTimer() {
  if (timerId !== null) {
    clearInterval(timerId);
    timerId = null;
  }
}

function handleTimeOut() {
  // Deshabilitar opciones
  const all = optionsContainer.querySelectorAll(".option-btn");
  all.forEach((b) => {
    b.disabled = true;
  });

  if (timeMessage) {
    timeMessage.textContent = "⏱ Tiempo agotado para esta pregunta.";
  }

  // Mostrar botón "Siguiente" para continuar
  nextBtn.classList.remove("hidden");
}

// ---------------------------
// Inicio de partida
// ---------------------------
startBtn.onclick = () => {
  playerName = playerInput.value.trim() || "Anónimo";
  const amount = parseInt(questionCountSelect.value, 10);

  startBtn.disabled = true;
  startBtn.textContent = "Cargando preguntas...";

  fetch(`/api/questions?amount=${amount}`)
    .then((r) => r.json())
    .then((data) => {
      questions = data.questions || [];
      currentIndex = 0;
      answers = [];

      totalQuestionsSpan.textContent = questions.length;
      labelPlayer.textContent = `Jugador/a: ${playerName}`;

      setupSection.classList.add("hidden");
      resultSection.classList.add("hidden");
      gameSection.classList.remove("hidden");

      if (questions.length > 0) {
        renderQuestion();
      } else {
        questionText.textContent =
          "No se recibieron preguntas del servidor.";
      }
    })
    .catch((err) => {
      console.error("Error al obtener preguntas", err);
      alert("No se pudieron cargar las preguntas. Ver consola.");
    })
    .finally(() => {
      startBtn.disabled = false;
      startBtn.textContent = "Comenzar partida";
    });
};

// ---------------------------
// Renderizar una pregunta
// ---------------------------
function renderQuestion() {
  const q = questions[currentIndex];
  if (!q) return;

  currentQuestionIndexSpan.textContent = currentIndex + 1;
  questionCategorySpan.textContent = q.category || "";
  questionDifficultySpan.textContent = q.difficulty
    ? `Dificultad: ${q.difficulty}`
    : "";
  questionText.textContent = q.question || "";

  optionsContainer.innerHTML = "";
  nextBtn.classList.add("hidden");

  if (timeMessage) {
    timeMessage.textContent = "";
  }

  (q.options || []).forEach((opt, idx) => {
    const btn = document.createElement("button");
    btn.className = "option-btn";
    btn.textContent = opt;
    btn.onclick = () => selectOption(idx, btn);
    optionsContainer.appendChild(btn);
  });

  // Iniciamos el timer para esta pregunta
  startTimer();
}

// ---------------------------
// Selección de opción
// ---------------------------
function selectOption(idx, btnElement) {
  // Parar timer al responder
  stopTimer();

  // Marcar selección visual
  const all = optionsContainer.querySelectorAll(".option-btn");
  all.forEach((b) => {
    b.classList.remove("option-selected");
    b.disabled = true; // una vez que eligió, se bloquean
  });
  btnElement.classList.add("option-selected");

  // Guardar respuesta (si ya existía, reemplazar)
  const qid = questions[currentIndex].id;
  const existingIndex = answers.findIndex((a) => a.questionId === qid);

  if (existingIndex >= 0) {
    answers[existingIndex].selectedIndex = idx;
  } else {
    answers.push({ questionId: qid, selectedIndex: idx });
  }

  nextBtn.classList.remove("hidden");
}

// ---------------------------
// Botón "Siguiente"
// ---------------------------
nextBtn.onclick = () => {
  stopTimer();

  if (currentIndex < questions.length - 1) {
    currentIndex++;
    renderQuestion();
  } else {
    finishGame();
  }
};

// ---------------------------
// Fin de partida
// ---------------------------
function finishGame() {
  stopTimer();
  gameSection.classList.add("hidden");
  resultSection.classList.remove("hidden");

  fetch("/api/submit", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      playerName,
      answers,
    }),
  })
    .then((r) => r.json())
    .then((data) => {
      resultPlayerName.textContent = data.playerName || playerName;
      resultScore.textContent = `${data.score} / ${data.total}`;

      const ratio = data.total > 0 ? data.score / data.total : 0;
      let msg = "";
      if (ratio === 1) msg = "¡Perfecto! 🎉";
      else if (ratio >= 0.7) msg = "¡Muy bien! 🙌";
      else if (ratio >= 0.4) msg = "Bien, pero se puede mejorar 😉";
      else msg = "Toca estudiar un poquito más 😅";

      resultExtra.textContent = msg;

      networkDetail.textContent = `La partida se registró desde la IP ${data.clientIp} usando: ${data.userAgent}. Esto muestra la parte de redes del proyecto (cliente–servidor, HTTP y registro por IP).`;
    })
    .catch((err) => {
      console.error("Error al enviar resultados", err);
      resultExtra.textContent =
        "Hubo un problema al registrar el resultado en el servidor.";
    });
}

// ---------------------------
// Volver a jugar
// ---------------------------
playAgainBtn.onclick = () => {
  stopTimer();
  setupSection.classList.remove("hidden");
  resultSection.classList.add("hidden");
  gameSection.classList.add("hidden");
};

// ---------------------------
// Botón de admin: resetear datos del servidor
// ---------------------------
const resetDataBtn = document.getElementById("reset-data-btn");

if (resetDataBtn) {
  resetDataBtn.onclick = () => {
    const ok = confirm(
      "¿Seguro que querés borrar el historial de partidas y eventos del servidor?"
    );
    if (!ok) return;

    fetch("/reset_data", { method: "POST" })
      .then((r) => r.json())
      .then((data) => {
        alert(data.msg || "Datos reseteados.");
        window.location.reload();
      })
      .catch((err) => {
        console.error("Error al resetear datos:", err);
        alert("Hubo un error al intentar resetear los datos.");
      });
  };
}

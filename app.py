from flask import Flask, render_template, request, jsonify
import random
import csv
import datetime
import os

app = Flask(__name__)

# -------------------------- PREGUNTAS --------------------------

TRIVIA_QUESTIONS = [
    {
        "id": 1,
        "category": "Redes",
        "difficulty": "Fácil",
        "question": "¿Qué significa la sigla IP en redes?",
        "options": ["Internet Protocol", "Internal Process", "Inter Password", "Input Package"],
        "answer_index": 0,
    },
    {
        "id": 2,
        "category": "Redes",
        "difficulty": "Fácil",
        "question": "¿Cuál es la máscara de red típica para una red clase C?",
        "options": ["255.255.0.0", "255.255.255.0", "255.0.0.0", "255.255.255.255"],
        "answer_index": 1,
    },
    {
        "id": 3,
        "category": "Protocolos",
        "difficulty": "Media",
        "question": "¿Cuál de estos protocolos se usa para obtener una dirección IP automáticamente?",
        "options": ["DNS", "HTTP", "DHCP", "FTP"],
        "answer_index": 2,
    },
    {
        "id": 4,
        "category": "Protocolos",
        "difficulty": "Media",
        "question": "¿Qué protocolo se utiliza para traducir nombres de dominio en direcciones IP?",
        "options": ["SMTP", "DNS", "TCP", "ARP"],
        "answer_index": 1,
    },
    {
        "id": 5,
        "category": "Capa física",
        "difficulty": "Fácil",
        "question": "¿Qué dispositivo se utiliza normalmente para conectar dispositivos en una red LAN?",
        "options": ["Switch", "Router", "Repetidor", "Firewall"],
        "answer_index": 0,
    },
    {
        "id": 6,
        "category": "Capa de enlace",
        "difficulty": "Fácil",
        "question": "¿Cuál de estos corresponde a una dirección MAC válida?",
        "options": ["192.168.1.1", "00:1A:2B:3C:4D:5E", "255.255.255.0", "A1-B2-C3"],
        "answer_index": 1,
    },
    {
        "id": 7,
        "category": "TCP/IP",
        "difficulty": "Media",
        "question": "¿Qué protocolo garantiza transmisión confiable de datos?",
        "options": ["UDP", "ARP", "TCP", "ICMP"],
        "answer_index": 2,
    },
    {
        "id": 8,
        "category": "TCP/IP",
        "difficulty": "Media",
        "question": "¿Cuál es la función principal de un router?",
        "options": [
            "Conectar redes diferentes",
            "Repetir señal eléctrica",
            "Asignar direcciones MAC",
            "Proteger contra virus"
        ],
        "answer_index": 0,
    },
    {
        "id": 9,
        "category": "Redes",
        "difficulty": "Media",
        "question": "¿Qué tipo de IP es '192.168.0.15'?",
        "options": ["IP pública", "IP privada", "IP de Loopback", "IP inválida"],
        "answer_index": 1,
    },
    {
        "id": 10,
        "category": "Servicios",
        "difficulty": "Fácil",
        "question": "¿Cuál es el puerto estándar de HTTP?",
        "options": ["21", "25", "80", "443"],
        "answer_index": 2,
    },
    {
        "id": 11,
        "category": "Servicios",
        "difficulty": "Media",
        "question": "¿Qué servicio funciona en el puerto 443?",
        "options": ["FTP Seguro", "HTTPS", "DHCP", "SSH"],
        "answer_index": 1,
    },
    {
        "id": 12,
        "category": "Conceptos",
        "difficulty": "Difícil",
        "question": "¿Qué comando en Linux se utiliza para mostrar la tabla de rutas?",
        "options": ["ping", "ifconfig", "route -n", "nslookup"],
        "answer_index": 2,
    },
    {
        "id": 13,
        "category": "Conceptos",
        "difficulty": "Media",
        "question": "¿Qué es NAT?",
        "options": [
            "Un protocolo de correo",
            "Una técnica para traducir direcciones de red",
            "Un comando de prueba de conexión",
            "Un tipo de firewall"
        ],
        "answer_index": 1,
    },
    {
        "id": 14,
        "category": "Cableado",
        "difficulty": "Fácil",
        "question": "¿Cuál de estos cables se usa comúnmente en redes Ethernet?",
        "options": ["Coaxial fino", "UTP", "HDMI", "Fibra USB"],
        "answer_index": 1,
    },
    {
        "id": 15,
        "category": "Diagnóstico",
        "difficulty": "Media",
        "question": "¿Qué comando sirve para verificar si un host responde en la red?",
        "options": ["dig", "ssh", "traceroute", "ping"],
        "answer_index": 3,
    },
]

SCORES_FILE = "scores.csv"
EVENTS_FILE = "events_trivia.csv"


# -------------------------- HELPERS DE LOGS --------------------------


def save_score(player_name, score, total, client_ip, user_agent):
    """Guarda resultado de una partida (para scoreboard)."""
    file_exists = os.path.isfile(SCORES_FILE)
    with open(SCORES_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(
                [
                    "timestamp",
                    "player_name",
                    "score",
                    "total",
                    "client_ip",
                    "user_agent",
                ]
            )
        writer.writerow(
            [
                datetime.datetime.now().isoformat(timespec="seconds"),
                player_name,
                score,
                total,
                client_ip,
                user_agent,
            ]
        )


def log_event(event_type, extra=None):
    """Loguea eventos de red / juego (no es obligatorio pero suma para redes)."""
    if extra is None:
        extra = {}
    client_ip = request.remote_addr if request else "N/A"
    user_agent = request.headers.get("User-Agent", "Unknown") if request else "N/A"

    file_exists = os.path.isfile(EVENTS_FILE)
    with open(EVENTS_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(
                [
                    "timestamp",
                    "event_type",
                    "client_ip",
                    "user_agent",
                    "extra",
                ]
            )
        writer.writerow(
            [
                datetime.datetime.now().isoformat(timespec="seconds"),
                event_type,
                client_ip,
                user_agent,
                repr(extra),
            ]
        )


# -------------------------- RUTAS HTML --------------------------


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/scoreboard")
def scoreboard():
    """Historial de partidas jugadas (para mostrar en pantalla)."""
    rows = []
    if os.path.isfile(SCORES_FILE):
        with open(SCORES_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    return render_template("scoreboard.html", rows=rows)


@app.route("/debug")
def debug_view():
    """Vista para mostrar info interna útil en la defensa de redes."""
    total_partidas = 0
    if os.path.isfile(SCORES_FILE):
        with open(SCORES_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            total_partidas = sum(1 for _ in reader)

    info = {
        "total_preguntas_configuradas": len(TRIVIA_QUESTIONS),
        "archivo_scores": SCORES_FILE,
        "archivo_eventos": EVENTS_FILE,
        "total_partidas_registradas": total_partidas,
    }
    return render_template("debug.html", info=info)


# -------------------------- API JSON --------------------------


@app.route("/api/questions")
def api_questions():
    """Devuelve un subconjunto aleatorio de preguntas al cliente."""
    amount = int(request.args.get("amount", 5))
    questions = random.sample(TRIVIA_QUESTIONS, min(amount, len(TRIVIA_QUESTIONS)))

    client_questions = []
    for q in questions:
        client_questions.append(
            {
                "id": q["id"],
                "category": q["category"],
                "difficulty": q["difficulty"],
                "question": q["question"],
                "options": q["options"],
            }
        )

    log_event("get_questions", {"amount": amount})
    return jsonify({"questions": client_questions})


@app.route("/api/submit", methods=["POST"])
def api_submit():
    """Recibe respuestas del jugador, calcula el puntaje y registra la partida."""
    data = request.get_json() or {}
    player_name = data.get("playerName", "Anónimo")
    answers = data.get("answers", [])

    correct = 0
    total = len(answers)

    # Mapeo rápido de id -> pregunta original
    question_map = {q["id"]: q for q in TRIVIA_QUESTIONS}

    for ans in answers:
        qid = ans.get("questionId")
        selected = ans.get("selectedIndex")
        q = question_map.get(qid)
        if q and selected == q["answer_index"]:
            correct += 1

    client_ip = request.remote_addr
    user_agent = request.headers.get("User-Agent", "Unknown")

    # Guardar score y evento
    save_score(player_name, correct, total, client_ip, user_agent)
    log_event(
        "submit_game",
        {
            "player_name": player_name,
            "score": correct,
            "total": total,
        },
    )

    return jsonify(
        {
            "playerName": player_name,
            "score": correct,
            "total": total,
            "clientIp": client_ip,
            "userAgent": user_agent,
        }
    )

@app.route("/api/stats")
def api_stats():
    """
    Devuelve estadísticas básicas del servidor:
    - total de partidas
    - mejor puntaje
    - promedio de puntaje
    """
    total_games = 0
    best_score = 0
    best_total = 0
    sum_scores = 0
    sum_totals = 0

    if os.path.isfile(SCORES_FILE):
        with open(SCORES_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    score = int(row["score"])
                    total = int(row["total"])
                except (KeyError, ValueError):
                    continue

                total_games += 1
                sum_scores += score
                sum_totals += total

                if score > best_score or (score == best_score and total > best_total):
                    best_score = score
                    best_total = total

    avg_score = 0.0
    if total_games > 0:
        avg_score = sum_scores / total_games

    return jsonify(
        {
            "total_games": total_games,
            "best_score": best_score,
            "best_total": best_total,
            "avg_score": avg_score,
        }
    )



# -------------------------- RUTA: RESET DE DATOS --------------------------


@app.route("/reset_data", methods=["POST"])
def reset_data():
    """
    Borra los archivos de scores y eventos.
    Útil para dejar el sistema limpio antes de la defensa.
    """
    deleted = []
    for file in (SCORES_FILE, EVENTS_FILE):
        if os.path.isfile(file):
            os.remove(file)
            deleted.append(file)

    return jsonify(
        {
            "ok": True,
            "deleted": deleted,
            "msg": "Datos de trivia reseteados correctamente.",
        }
    )


if __name__ == "__main__":
    # IMPORTANTE: host=0.0.0.0 para que otros dispositivos de la red puedan entrar
    # Cambiá el puerto si querés (ej: 8180 o 8080)
    app.run(host="0.0.0.0", port=8081, debug=True)

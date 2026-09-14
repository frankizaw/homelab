#!/usr/bin/env bash
# ==============================================================================
# Cyber Homelab Management CLI
# Controls lab lifecycle (Docker & Native), attack simulations, and log analysis.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/.lab.pid"
LOG_FILE="$SCRIPT_DIR/logs/access.log"
TARGET_PORT="${LAB_PORT:-8080}"
TARGET_URL="http://localhost:$TARGET_PORT"

# Colors
RED="\033[91m"
GREEN="\033[92m"
YELLOW="\033[93m"
CYAN="\033[96m"
BOLD="\033[1m"
RESET="\033[0m"

has_docker() {
    command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1
}

start_lab() {
    echo -e "${BOLD}=== Starting Cybersecurity Homelab ===${RESET}"
    mkdir -p "$SCRIPT_DIR/logs"

    if has_docker; then
        echo -e "${GREEN}[+] Docker detected.${RESET} Starting containerized lab with compose.yaml..."
        cd "$SCRIPT_DIR" && docker compose up -d
        echo -e "${GREEN}[OK] Homelab running in Docker on $TARGET_URL${RESET}"
    else
        echo -e "${YELLOW}[!] Docker not running or not found.${RESET}"
        echo -e "${CYAN}[+] Starting Native Python Lab Server (zero-dependency)...${RESET}"

        if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
            echo -e "${YELLOW}[!] Lab is already running with PID $(cat "$PID_FILE")${RESET}"
            return 0
        fi

        python3 "$SCRIPT_DIR/targets/vulnerable-app/app.py" \
            --port "$TARGET_PORT" \
            --log-file "$LOG_FILE" \
            --daemon \
            --pid-file "$PID_FILE"

        sleep 0.5

        if kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
            echo -e "${GREEN}[OK] Native Lab Server started successfully!${RESET}"
            echo -e "    PID       : $(cat "$PID_FILE")"
            echo -e "    URL       : ${CYAN}$TARGET_URL${RESET}"
            echo -e "    Log File  : ${CYAN}$LOG_FILE${RESET}"
        else
            echo -e "${RED}[-] Failed to start native server.${RESET}"
            exit 1
        fi
    fi
}

stop_lab() {
    echo -e "${BOLD}=== Stopping Cybersecurity Homelab ===${RESET}"

    if has_docker && docker compose ps -q 2>/dev/null | grep -q .; then
        echo -e "${CYAN}[*] Stopping Docker containers...${RESET}"
        cd "$SCRIPT_DIR" && docker compose down
    fi

    if [ -f "$PID_FILE" ]; then
        PID="$(cat "$PID_FILE")"
        if kill -0 "$PID" 2>/dev/null; then
            echo -e "${CYAN}[*] Stopping native server PID $PID...${RESET}"
            kill "$PID" 2>/dev/null || true
            sleep 0.5
        fi
        rm -f "$PID_FILE"
    fi

    echo -e "${GREEN}[OK] Homelab stopped.${RESET}"
}

status_lab() {
    echo -e "${BOLD}=== Homelab Status ===${RESET}"

    RUNNING=false
    if has_docker && docker compose ps --status running -q 2>/dev/null | grep -q .; then
        echo -e "State     : ${GREEN}RUNNING (Docker Compose)${RESET}"
        RUNNING=true
    elif [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        echo -e "State     : ${GREEN}RUNNING (Native Python Mode, PID $(cat "$PID_FILE"))${RESET}"
        RUNNING=true
    else
        echo -e "State     : ${RED}STOPPED${RESET}"
    fi

    echo -e "Endpoint  : ${CYAN}$TARGET_URL${RESET}"
    if [ -f "$LOG_FILE" ]; then
        LOG_COUNT=$(wc -l < "$LOG_FILE")
        echo -e "Log file  : $LOG_FILE (${CYAN}$LOG_COUNT entries${RESET})"
    else
        echo -e "Log file  : $LOG_FILE (not created yet)"
    fi
}

run_attacks() {
    MODE="${1:-all}"
    echo -e "${BOLD}=== Running Red Team Attacks ===${RESET}"
    python3 "$SCRIPT_DIR/attacks/exploit_runner.py" --target "$TARGET_URL" --mode "$MODE"
}

run_analysis() {
    echo -e "${BOLD}=== Running Log-Sentry Detection Analysis ===${RESET}"
    ANALYZER_PATH="$SCRIPT_DIR/../log-sentry/analyzer.py"

    if [ ! -f "$LOG_FILE" ] || [ ! -s "$LOG_FILE" ]; then
        echo -e "${YELLOW}[!] Log file $LOG_FILE is empty or missing. Run attacks first!${RESET}"
        return 1
    fi

    if [ -f "$ANALYZER_PATH" ]; then
        python3 "$ANALYZER_PATH" "$LOG_FILE"
    else
        echo -e "${RED}[-] log-sentry analyzer not found at $ANALYZER_PATH${RESET}"
        exit 1
    fi
}

tail_logs() {
    mkdir -p "$SCRIPT_DIR/logs"
    touch "$LOG_FILE"
    echo -e "${CYAN}[*] Following $LOG_FILE (Ctrl+C to exit)...${RESET}"
    tail -f "$LOG_FILE"
}

clean_logs() {
    if [ -f "$LOG_FILE" ]; then
        > "$LOG_FILE"
        echo -e "${GREEN}[OK] Log file cleared.${RESET}"
    else
        echo -e "${YELLOW}[!] Log file already clean.${RESET}"
    fi
}

# Main routing
CMD="${1:-help}"
shift || true

case "$CMD" in
    start)
        start_lab
        ;;
    stop)
        stop_lab
        ;;
    restart)
        stop_lab
        sleep 1
        start_lab
        ;;
    status)
        status_lab
        ;;
    attack|attacks)
        run_attacks "${1:-all}"
        ;;
    analyze)
        run_analysis
        ;;
    logs)
        tail_logs
        ;;
    clean)
        clean_logs
        ;;
    *)
        echo -e "${BOLD}Usage:${RESET} $0 {start|stop|restart|status|attack [blatant|evasion|all]|analyze|logs|clean}"
        echo
        echo "Commands:"
        echo "  start     Start the homelab target (Docker or Native Python)"
        echo "  stop      Stop all running homelab services"
        echo "  restart   Restart the homelab services"
        echo "  status    Check lab status and log metrics"
        echo "  attack    Execute simulated Red Team attacks"
        echo "  analyze   Run log-sentry on the lab access.log"
        echo "  logs      Live tail access.log"
        echo "  clean     Empty access.log"
        ;;
esac

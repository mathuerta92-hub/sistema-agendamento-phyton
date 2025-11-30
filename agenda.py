# agenda.py
# Versão reduzida do sistema de agendamento.
# Uso:
# $ python agenda.py

import sqlite3
from datetime import datetime, timedelta
import uuid

DB = "agenda_reduzida.db"

# ----------------------------- BANCO -----------------------------------
def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        phone TEXT
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS services (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        duration INTEGER NOT NULL
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS professionals (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id TEXT PRIMARY KEY,
        client_id TEXT,
        professional_id TEXT,
        service_id TEXT,
        start TEXT,
        end TEXT
    )""")

    conn.commit()
    conn.close()


# ----------------------------- FUNÇÕES -----------------------------------
def add_client(name, phone=None):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    client_id = str(uuid.uuid4())
    cur.execute("INSERT INTO clients VALUES (?, ?, ?)", (client_id, name, phone))
    conn.commit()
    conn.close()
    return client_id


def add_professional(name):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    prof_id = str(uuid.uuid4())
    cur.execute("INSERT INTO professionals VALUES (?, ?)", (prof_id, name))
    conn.commit()
    conn.close()
    return prof_id


def add_service(name, duration):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    serv_id = str(uuid.uuid4())
    cur.execute("INSERT INTO services VALUES (?, ?, ?)", (serv_id, name, duration))
    conn.commit()
    conn.close()
    return serv_id


def has_conflict(professional_id, start, end):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM appointments
        WHERE professional_id = ?
        AND (
            (start <= ? AND end > ?) OR
            (start < ? AND end >= ?) OR
            (start >= ? AND end <= ?)
        )
    """, (professional_id, start, start, end, end, start, end))

    conflict = cur.fetchone()
    conn.close()
    return conflict is not None


def add_appointment(client_id, professional_id, service_id, start_time):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # pega duração do serviço
    cur.execute("SELECT duration FROM services WHERE id = ?", (service_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise ValueError("Serviço não encontrado")

    duration = row[0]
    start_dt = datetime.fromisoformat(start_time)
    end_dt = start_dt + timedelta(minutes=duration)

    if has_conflict(professional_id, start_dt.isoformat(), end_dt.isoformat()):
        conn.close()
        raise ValueError("Conflito de horário")

    appt_id = str(uuid.uuid4())
    cur.execute("INSERT INTO appointments VALUES (?, ?, ?, ?, ?, ?)",
                (appt_id, client_id, professional_id, service_id,
                 start_dt.isoformat(), end_dt.isoformat()))

    conn.commit()
    conn.close()

    return appt_id


def list_appointments():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        SELECT a.id, c.name, p.name, s.name, a.start, a.end
        FROM appointments a
        JOIN clients c ON a.client_id = c.id
        JOIN professionals p ON a.professional_id = p.id
        JOIN services s ON a.service_id = s.id
        ORDER BY a.start
    """)
    items = cur.fetchall()
    conn.close()
    return items


# ----------------------------- MAIN (EXEMPLO) -----------------------------------
if __name__ == "__main__":
    init_db()

    print("----- SISTEMA DE AGENDAMENTO (VERSÃO REDUZIDA) -----")

    # criar dados de exemplo
    cliente = add_client("Maria", "1199999-0000")
    prof = add_professional("Ana Cabeleireira")
    serv = add_service("Corte feminino", 45)

    # tenta agendar
    try:
        appt = add_

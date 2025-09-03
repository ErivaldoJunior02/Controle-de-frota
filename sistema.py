import os
import sys
import csv
import hashlib
from datetime import datetime, date
from typing import List, Tuple

try:
    import pandas as pd
    HAS_PANDAS = True
except Exception:
    HAS_PANDAS = False

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QTabWidget,
    QLabel, QMessageBox, QDialog, QFormLayout, QComboBox, QSpinBox,
    QDateEdit, QFileDialog, QHeaderView, QAction, QPlainTextEdit, QDoubleSpinBox
)
from PyQt5.QtCore import QDate, Qt

import mysql.connector

# --------------------
# DB CONFIG - edit these to match your MySQL Workbench setup
# --------------------
DB_HOST = "127.0.0.1"
DB_PORT = 3306
DB_USER = "junior"
DB_PASSWORD = "juninho0209"
DB_NAME = "limpind"
# --------------------


def get_server_connection():
    return mysql.connector.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, autocommit=False
    )


def get_connection():
    return mysql.connector.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_NAME, autocommit=False
    )


def ensure_database_and_tables():
    # Create database if not exists, then create tables
    server = get_server_connection()
    cur = server.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    server.commit()
    cur.close()
    server.close()

    conn = get_connection()
    cur = conn.cursor()
    # create tables
    ddl_statements = [
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE,
            senha_hash VARCHAR(255),
            perfil ENUM('admin','mecanico','gestor') DEFAULT 'gestor',
            status ENUM('ativo','inativo') DEFAULT 'ativo'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
        """
        CREATE TABLE IF NOT EXISTS fornecedores (
            id_fornecedor INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            cnpj_cpf VARCHAR(50),
            endereco VARCHAR(255),
            telefone VARCHAR(50),
            email VARCHAR(100),
            observacoes TEXT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
        """
        CREATE TABLE IF NOT EXISTS equipamentos (
            id_equipamento INT AUTO_INCREMENT PRIMARY KEY,
            placa VARCHAR(50),
            descricao VARCHAR(255) NOT NULL,
            modelo VARCHAR(100),
            ano INT,
            chassi VARCHAR(100),
            status ENUM('ativo','em_manutencao','inativo') DEFAULT 'ativo'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
        """
        CREATE TABLE IF NOT EXISTS pecas (
            id_peca INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            descricao TEXT,
            codigo_interno VARCHAR(100),
            unidade_medida VARCHAR(20) DEFAULT 'un'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
        """
        CREATE TABLE IF NOT EXISTS pecas_fornecedores (
            id_peca_fornecedor INT AUTO_INCREMENT PRIMARY KEY,
            id_peca INT NOT NULL,
            id_fornecedor INT NOT NULL,
            preco_unitario DECIMAL(15,4) NOT NULL,
            data_cotacao DATE NOT NULL,
            FOREIGN KEY (id_peca) REFERENCES pecas(id_peca) ON DELETE CASCADE,
            FOREIGN KEY (id_fornecedor) REFERENCES fornecedores(id_fornecedor) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
        """
        CREATE TABLE IF NOT EXISTS estoque (
            id_estoque INT AUTO_INCREMENT PRIMARY KEY,
            id_peca INT NOT NULL UNIQUE,
            quantidade_atual DECIMAL(20,4) NOT NULL DEFAULT 0,
            quantidade_minima DECIMAL(20,4) NOT NULL DEFAULT 0,
            FOREIGN KEY (id_peca) REFERENCES pecas(id_peca) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
        """
        CREATE TABLE IF NOT EXISTS compras (
            id_compra INT AUTO_INCREMENT PRIMARY KEY,
            id_fornecedor INT NOT NULL,
            data_compra DATE NOT NULL,
            valor_total DECIMAL(18,4) NOT NULL DEFAULT 0,
            FOREIGN KEY (id_fornecedor) REFERENCES fornecedores(id_fornecedor) ON DELETE RESTRICT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
        """
        CREATE TABLE IF NOT EXISTS compras_itens (
            id_item INT AUTO_INCREMENT PRIMARY KEY,
            id_compra INT NOT NULL,
            id_peca INT NOT NULL,
            quantidade DECIMAL(20,4) NOT NULL,
            preco_unitario DECIMAL(18,4) NOT NULL,
            FOREIGN KEY (id_compra) REFERENCES compras(id_compra) ON DELETE CASCADE,
            FOREIGN KEY (id_peca) REFERENCES pecas(id_peca) ON DELETE RESTRICT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
        """
        CREATE TABLE IF NOT EXISTS manutencoes (
            id_manutencao INT AUTO_INCREMENT PRIMARY KEY,
            id_equipamento INT NOT NULL,
            data_inicio DATE NOT NULL,
            data_fim DATE,
            tipo ENUM('preventiva','corretiva','revisao','outro') DEFAULT 'outro',
            descricao_servico TEXT,
            custo_total DECIMAL(18,4) NOT NULL DEFAULT 0,
            responsavel INT,
            FOREIGN KEY (id_equipamento) REFERENCES equipamentos(id_equipamento) ON DELETE RESTRICT,
            FOREIGN KEY (responsavel) REFERENCES usuarios(id_usuario) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
        """
        CREATE TABLE IF NOT EXISTS manutencoes_pecas (
            id_item_manutencao INT AUTO_INCREMENT PRIMARY KEY,
            id_manutencao INT NOT NULL,
            id_peca INT NOT NULL,
            quantidade_usada DECIMAL(20,4) NOT NULL,
            preco_unitario DECIMAL(18,4) NOT NULL,
            FOREIGN KEY (id_manutencao) REFERENCES manutencoes(id_manutencao) ON DELETE CASCADE,
            FOREIGN KEY (id_peca) REFERENCES pecas(id_peca) ON DELETE RESTRICT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
        """
        CREATE TABLE IF NOT EXISTS estoque_movimentacoes (
            id_movimentacao INT AUTO_INCREMENT PRIMARY KEY,
            id_peca INT NOT NULL,
            tipo ENUM('entrada','saida','ajuste') NOT NULL,
            quantidade DECIMAL(20,4) NOT NULL,
            data_movimentacao DATETIME NOT NULL,
            origem VARCHAR(100),
            id_referencia INT,
            observacao TEXT,
            FOREIGN KEY (id_peca) REFERENCES pecas(id_peca) ON DELETE RESTRICT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
        """
        CREATE TABLE IF NOT EXISTS importacoes (
            id_importacao INT AUTO_INCREMENT PRIMARY KEY,
            arquivo_nome VARCHAR(255) NOT NULL,
            arquivo_hash VARCHAR(255),
            tipo_importacao VARCHAR(50) NOT NULL,
            data_importacao DATETIME NOT NULL,
            usuario_responsavel INT,
            status ENUM('sucesso','parcial','erro') NOT NULL,
            mensagem_log TEXT,
            FOREIGN KEY (usuario_responsavel) REFERENCES usuarios(id_usuario) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
        """
        CREATE TABLE IF NOT EXISTS orcamentos (
            id_orcamento INT AUTO_INCREMENT PRIMARY KEY,
            data_orcamento DATETIME NOT NULL,
            id_usuario INT,
            observacao TEXT,
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
        """
        CREATE TABLE IF NOT EXISTS orcamentos_itens (
            id_orcamento_item INT AUTO_INCREMENT PRIMARY KEY,
            id_orcamento INT NOT NULL,
            id_peca INT NOT NULL,
            id_fornecedor INT NOT NULL,
            quantidade DECIMAL(20,4) NOT NULL,
            preco_unitario DECIMAL(18,4) NOT NULL,
            FOREIGN KEY (id_orcamento) REFERENCES orcamentos(id_orcamento) ON DELETE CASCADE,
            FOREIGN KEY (id_peca) REFERENCES pecas(id_peca) ON DELETE RESTRICT,
            FOREIGN KEY (id_fornecedor) REFERENCES fornecedores(id_fornecedor) ON DELETE RESTRICT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
    ]

    for ddl in ddl_statements:
        cur.execute(ddl)
    conn.commit()


# --------------------
# DB helpers (simple, open/close per call for reliability)
# --------------------
def run_select(query: str, params: Tuple = ()):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def run_commit(query: str, params: Tuple = ()):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    last = cur.lastrowid
    cur.close()
    conn.close()
    return last


# --------------------
# Generic small dialog for records
# --------------------
class RecordDialog(QDialog):
    def __init__(self, title, fields, values=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.layout = QFormLayout()
        self.inputs = {}
        for name, wtype, extra in fields:
            if wtype == 'line':
                le = QLineEdit()
                if values and name in values and values[name] is not None:
                    le.setText(str(values[name]))
                self.inputs[name] = le
                self.layout.addRow(QLabel(name.replace('_',' ').capitalize()), le)
            elif wtype == 'int':
                sb = QSpinBox()
                sb.setMaximum(10_000_000)
                if values and name in values:
                    sb.setValue(int(values[name]))
                self.inputs[name] = sb
                self.layout.addRow(QLabel(name.replace('_',' ').capitalize()), sb)
            elif wtype == 'date':
                de = QDateEdit()
                de.setCalendarPopup(True)
                if values and name in values and values[name]:
                    de.setDate(QDate.fromString(values[name], "yyyy-MM-dd"))
                else:
                    de.setDate(QDate.currentDate())
                self.inputs[name] = de
                self.layout.addRow(QLabel(name.replace('_',' ').capitalize()), de)
            elif wtype == 'combo':
                cb = QComboBox()
                for disp, val in extra:
                    cb.addItem(disp, val)
                if values and name in values:
                    idx = next((i for i in range(cb.count()) if cb.itemData(i) == values[name]), 0)
                    cb.setCurrentIndex(idx)
                self.inputs[name] = cb
                self.layout.addRow(QLabel(name.replace('_',' ').capitalize()), cb)
            elif wtype == 'text':
                ta = QPlainTextEdit()
                if values and name in values and values[name] is not None:
                    ta.setPlainText(str(values[name]))
                self.inputs[name] = ta
                self.layout.addRow(QLabel(name.replace('_',' ').capitalize()), ta)

        btn_save = QPushButton("Salvar")
        btn_save.clicked.connect(self.accept)
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btn_row = QHBoxLayout()
        btn_row.addWidget(btn_save)
        btn_row.addWidget(btn_cancel)
        self.layout.addRow(btn_row)
        self.setLayout(self.layout)

    def get_data(self):
        data = {}
        for k, widget in self.inputs.items():
            if isinstance(widget, QLineEdit):
                data[k] = widget.text().strip()
            elif isinstance(widget, QSpinBox):
                data[k] = widget.value()
            elif isinstance(widget, QDateEdit):
                data[k] = widget.date().toString("yyyy-MM-dd")
            elif isinstance(widget, QComboBox):
                data[k] = widget.currentData()
            elif isinstance(widget, QPlainTextEdit):
                data[k] = widget.toPlainText().strip()
        return data

def load_stylesheet(estilo):
    with open('estilo.qss', "r") as f:
        return f.read()

# --------------------
# Dialogs: Compra (multi-item)
# --------------------
class CompraDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar Compra")
        self.resize(800, 400)
        self.layout = QVBoxLayout(self)

        # fornecedor combo
        self.cb_fornecedor = QComboBox()
        self.load_fornecedores()

        self.date_edit = QDateEdit(QDate.currentDate()); self.date_edit.setCalendarPopup(True)

        form = QHBoxLayout()
        form.addWidget(QLabel("Fornecedor:")); form.addWidget(self.cb_fornecedor)
        form.addWidget(QLabel("Data:")); form.addWidget(self.date_edit)
        self.layout.addLayout(form)

        # items table
        self.tbl = QTableWidget(0, 3)
        self.tbl.setHorizontalHeaderLabels(["Peça", "Quantidade", "Preço Unit."])
        self.tbl.horizontalHeader().setStretchLastSection(True)
        self.layout.addWidget(self.tbl)

        btns = QHBoxLayout()
        btn_add = QPushButton("Adicionar Item"); btn_add.clicked.connect(self.add_item)
        btn_remove = QPushButton("Remover Item"); btn_remove.clicked.connect(self.remove_item)
        btns.addWidget(btn_add); btns.addWidget(btn_remove); btns.addStretch()
        self.layout.addLayout(btns)

        hl = QHBoxLayout()
        self.lbl_total = QLabel("Total: 0,00")
        btn_save = QPushButton("Salvar"); btn_save.clicked.connect(self.save)
        btn_cancel = QPushButton("Cancelar"); btn_cancel.clicked.connect(self.reject)
        hl.addWidget(self.lbl_total); hl.addStretch(); hl.addWidget(btn_save); hl.addWidget(btn_cancel)
        self.layout.addLayout(hl)

        self.add_item()

    def load_fornecedores(self):
        self.cb_fornecedor.clear()
        rows = run_select("SELECT id_fornecedor, nome FROM fornecedores ORDER BY nome")
        for r in rows:
            self.cb_fornecedor.addItem(r['nome'], r['id_fornecedor'])

    def add_item(self):
        r = self.tbl.rowCount(); self.tbl.insertRow(r)
        cb = QComboBox()
        pecas = run_select("SELECT id_peca, nome FROM pecas ORDER BY nome")
        for p in pecas:
            cb.addItem(p['nome'], p['id_peca'])
        self.tbl.setCellWidget(r, 0, cb)
        sp_q = QDoubleSpinBox(); sp_q.setDecimals(4); sp_q.setMaximum(1e9); sp_q.setValue(1)
        sp_q.valueChanged.connect(self.update_total); self.tbl.setCellWidget(r, 1, sp_q)
        sp_p = QDoubleSpinBox(); sp_p.setDecimals(4); sp_p.setMaximum(1e12)
        sp_p.valueChanged.connect(self.update_total); self.tbl.setCellWidget(r, 2, sp_p)
        self.update_total()

    def remove_item(self):
        r = self.tbl.currentRow()
        if r >= 0:
            self.tbl.removeRow(r)
            self.update_total()

    def update_total(self):
        total = 0.0
        for r in range(self.tbl.rowCount()):
            qtd = float(self.tbl.cellWidget(r,1).value())
            preco = float(self.tbl.cellWidget(r,2).value())
            total += qtd * preco
        self.lbl_total.setText(f"Total: {total:,.2f}".replace(",", "X").replace(".", ",").replace("X","."))

    def save(self):
        if self.cb_fornecedor.currentIndex() < 0:
            QMessageBox.warning(self, "Erro", "Selecione um fornecedor.")
            return
        if self.tbl.rowCount() == 0:
            QMessageBox.warning(self, "Erro", "Adicione ao menos um item.")
            return
        fornecedor_id = self.cb_fornecedor.currentData()
        data_compra = self.date_edit.date().toString("yyyy-MM-dd")
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("INSERT INTO compras (id_fornecedor, data_compra, valor_total) VALUES (%s,%s,%s)",
                        (fornecedor_id, data_compra, 0))
            compra_id = cur.lastrowid
            total = 0.0
            for r in range(self.tbl.rowCount()):
                peca_id = self.tbl.cellWidget(r,0).currentData()
                qtd = float(self.tbl.cellWidget(r,1).value())
                preco = float(self.tbl.cellWidget(r,2).value())
                if qtd <= 0:
                    continue
                cur.execute("INSERT INTO compras_itens (id_compra, id_peca, quantidade, preco_unitario) VALUES (%s,%s,%s,%s)",
                            (compra_id, peca_id, qtd, preco))
                # update estoque
                cur.execute("INSERT IGNORE INTO estoque (id_peca, quantidade_atual, quantidade_minima) VALUES (%s,0,0)", (peca_id,))
                cur.execute("UPDATE estoque SET quantidade_atual = quantidade_atual + %s WHERE id_peca = %s", (qtd, peca_id))
                # movimentacao
                cur.execute("""INSERT INTO estoque_movimentacoes (id_peca, tipo, quantidade, data_movimentacao, origem, id_referencia, observacao)
                               VALUES (%s,'entrada',%s,%s,'compra',%s,%s)""", (peca_id, qtd, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), compra_id, f"Compra item - R$ {preco}"))
                # upsert preco por fornecedor (inserir nova cotação)
                cur.execute("""INSERT INTO pecas_fornecedores (id_peca, id_fornecedor, preco_unitario, data_cotacao)
                               VALUES (%s,%s,%s,%s)""", (peca_id, fornecedor_id, preco, data_compra))
                total += qtd * preco
            cur.execute("UPDATE compras SET valor_total = %s WHERE id_compra = %s", (total, compra_id))
            conn.commit()
            cur.close(); conn.close()
            QMessageBox.information(self, "OK", "Compra registrada com sucesso.")
            self.accept()
        except Exception as e:
            try:
                conn.rollback()
            except: pass
            QMessageBox.critical(self, "Erro", f"Falha ao registrar compra: {e}")


# --------------------
# Dialogs: Manutenção (multi-item)
# --------------------
class ManutencaoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar Manutenção")
        self.resize(900, 500)
        self.layout = QVBoxLayout(self)

        # equipment and metadata
        self.cb_equip = QComboBox()
        equips = run_select("SELECT id_equipamento, descricao FROM equipamentos ORDER BY descricao")
        for e in equips:
            self.cb_equip.addItem(e['descricao'], e['id_equipamento'])

        self.date_ini = QDateEdit(QDate.currentDate()); self.date_ini.setCalendarPopup(True)
        self.date_fim = QDateEdit(QDate.currentDate()); self.date_fim.setCalendarPopup(True)
        self.cb_tipo = QComboBox(); self.cb_tipo.addItems(["preventiva","corretiva","revisao","outro"])
        self.txt_desc = QPlainTextEdit()
        self.cb_resp = QComboBox()
        users = run_select("SELECT id_usuario, nome FROM usuarios WHERE status='ativo' ORDER BY nome")
        for u in users:
            self.cb_resp.addItem(u['nome'], u['id_usuario'])

        form = QFormLayout()
        form.addRow("Equipamento:", self.cb_equip)
        form.addRow("Data Início:", self.date_ini)
        form.addRow("Data Fim:", self.date_fim)
        form.addRow("Tipo:", self.cb_tipo)
        form.addRow("Responsável:", self.cb_resp)
        form.addRow("Descrição:", self.txt_desc)
        self.layout.addLayout(form)

        # items table
        self.tbl = QTableWidget(0,3)
        self.tbl.setHorizontalHeaderLabels(["Peça","Quantidade","Preço Unit. ref."])
        self.tbl.horizontalHeader().setStretchLastSection(True)
        self.layout.addWidget(self.tbl)
        btns = QHBoxLayout()
        btn_add = QPushButton("Adicionar Peça"); btn_add.clicked.connect(self.add_item)
        btn_remove = QPushButton("Remover Peça"); btn_remove.clicked.connect(self.remove_item)
        btns.addWidget(btn_add); btns.addWidget(btn_remove); btns.addStretch()
        self.layout.addLayout(btns)

        hl = QHBoxLayout()
        self.lbl_total = QLabel("Custo total: 0,00")
        btn_save = QPushButton("Salvar"); btn_save.clicked.connect(self.save)
        btn_cancel = QPushButton("Cancelar"); btn_cancel.clicked.connect(self.reject)
        hl.addWidget(self.lbl_total); hl.addStretch(); hl.addWidget(btn_save); hl.addWidget(btn_cancel)
        self.layout.addLayout(hl)

        self.add_item()

    def add_item(self):
        r = self.tbl.rowCount(); self.tbl.insertRow(r)
        cb = QComboBox()
        pecas = run_select("SELECT id_peca, nome FROM pecas ORDER BY nome")
        for p in pecas:
            cb.addItem(p['nome'], p['id_peca'])
        self.tbl.setCellWidget(r,0,cb)
        sp_q = QDoubleSpinBox(); sp_q.setDecimals(4); sp_q.setMaximum(1e9); sp_q.setValue(1); sp_q.valueChanged.connect(self.update_total)
        self.tbl.setCellWidget(r,1,sp_q)
        sp_p = QDoubleSpinBox(); sp_p.setDecimals(4); sp_p.setMaximum(1e12); sp_p.valueChanged.connect(self.update_total)
        self.tbl.setCellWidget(r,2,sp_p)
        self.update_total()

    def remove_item(self):
        r = self.tbl.currentRow()
        if r >= 0:
            self.tbl.removeRow(r)
            self.update_total()

    def update_total(self):
        total = 0.0
        for r in range(self.tbl.rowCount()):
            qtd = float(self.tbl.cellWidget(r,1).value())
            preco = float(self.tbl.cellWidget(r,2).value())
            total += qtd * preco
        self.lbl_total.setText(f"Custo total: {total:,.2f}".replace(",", "X").replace(".", ",").replace("X","."))

    def save(self):
        if self.cb_equip.currentIndex() < 0:
            QMessageBox.warning(self, "Erro", "Selecione um equipamento.")
            return
        if self.tbl.rowCount() == 0:
            QMessageBox.warning(self, "Erro", "Adicione ao menos uma peça.")
            return
        equip_id = self.cb_equip.currentData()
        data_ini = self.date_ini.date().toString("yyyy-MM-dd")
        data_fim = self.date_fim.date().toString("yyyy-MM-dd")
        tipo = self.cb_tipo.currentText()
        desc = self.txt_desc.toPlainText().strip()
        resp = self.cb_resp.currentData()
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("INSERT INTO manutencoes (id_equipamento, data_inicio, data_fim, tipo, descricao_servico, custo_total, responsavel) VALUES (%s,%s,%s,%s,%s,0,%s)",
                        (equip_id, data_ini, data_fim, tipo, desc, resp))
            manut_id = cur.lastrowid
            total = 0.0
            for r in range(self.tbl.rowCount()):
                peca_id = self.tbl.cellWidget(r,0).currentData()
                qtd = float(self.tbl.cellWidget(r,1).value())
                preco = float(self.tbl.cellWidget(r,2).value())
                if qtd <= 0:
                    continue
                # check stock
                cur.execute("SELECT quantidade_atual FROM estoque WHERE id_peca = %s", (peca_id,))
                row = cur.fetchone()
                have = float(row[0]) if row and row[0] is not None else 0.0
                if have < qtd:
                    raise RuntimeError(f"Estoque insuficiente para a peça id {peca_id} (tem {have}, precisa {qtd})")
                cur.execute("INSERT INTO manutencoes_pecas (id_manutencao, id_peca, quantidade_usada, preco_unitario) VALUES (%s,%s,%s,%s)",
                            (manut_id, peca_id, qtd, preco))
                # decrement estoque
                cur.execute("UPDATE estoque SET quantidade_atual = quantidade_atual - %s WHERE id_peca = %s", (qtd, peca_id))
                # movimentacao
                cur.execute("""INSERT INTO estoque_movimentacoes (id_peca, tipo, quantidade, data_movimentacao, origem, id_referencia, observacao)
                               VALUES (%s,'saida',%s,%s,'manutencao',%s,%s)""", (peca_id, qtd, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), manut_id, "Uso em manutenção"))
                total += qtd * preco
            cur.execute("UPDATE manutencoes SET custo_total = %s WHERE id_manutencao = %s", (total, manut_id))
            conn.commit()
            cur.close(); conn.close()
            QMessageBox.information(self, "OK", "Manutenção registrada com sucesso.")
            self.accept()
        except Exception as e:
            try: conn.rollback()
            except: pass
            QMessageBox.critical(self, "Erro", f"Falha ao registrar manutenção: {e}")


# --------------------
# Dialog: Orçamento Dinâmico
# --------------------
class OrcamentoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Orçamento Dinâmico")
        self.resize(820, 450)
        self.layout = QVBoxLayout(self)
        self.tbl = QTableWidget(0, 3)
        self.tbl.setHorizontalHeaderLabels(["Peça", "Quantidade", "Menor Fornecedor/Preço"])
        self.tbl.horizontalHeader().setStretchLastSection(True)
        self.layout.addWidget(self.tbl)
        btns = QHBoxLayout()
        btn_add = QPushButton("Adicionar Peça"); btn_add.clicked.connect(self.add_row)
        btn_calc = QPushButton("Calcular"); btn_calc.clicked.connect(self.calculate)
        btn_export = QPushButton("Exportar CSV"); btn_export.clicked.connect(self.export_csv)
        btns.addWidget(btn_add); btns.addStretch(); btns.addWidget(btn_calc); btns.addWidget(btn_export)
        self.layout.addLayout(btns)
        self.lbl_total = QLabel("Total estimado: 0,00")
        self.layout.addWidget(self.lbl_total)
        self.add_row()
        self.result_rows = []

    def add_row(self):
        r = self.tbl.rowCount(); self.tbl.insertRow(r)
        cb = QComboBox(); pecas = run_select("SELECT id_peca, nome FROM pecas ORDER BY nome")
        for p in pecas: cb.addItem(p['nome'], p['id_peca'])
        self.tbl.setCellWidget(r, 0, cb)
        sp = QDoubleSpinBox(); sp.setDecimals(3); sp.setMaximum(1e9); sp.setValue(1); self.tbl.setCellWidget(r,1,sp)
        lbl = QLabel("—"); self.tbl.setCellWidget(r,2,lbl)

    def calculate(self):
        self.result_rows.clear(); total = 0.0
        for r in range(self.tbl.rowCount()):
            peca_id = self.tbl.cellWidget(r,0).currentData()
            peca_nome = self.tbl.cellWidget(r,0).currentText()
            qtd = float(self.tbl.cellWidget(r,1).value())
            # find latest cotation and cheapest among latest
            # get latest date for this piece
            rows = run_select("""SELECT pf.id_fornecedor, f.nome AS fornecedor, pf.preco_unitario, pf.data_cotacao
                                 FROM pecas_fornecedores pf JOIN fornecedores f USING (id_fornecedor)
                                 WHERE pf.id_peca = %s AND pf.data_cotacao = (
                                     SELECT MAX(pf2.data_cotacao) FROM pecas_fornecedores pf2 WHERE pf2.id_peca = pf.id_peca
                                 )
                                 ORDER BY pf.preco_unitario ASC LIMIT 1""", (peca_id,))
            if rows:
                forn_id = rows[0]['id_fornecedor']; forn_nome = rows[0]['fornecedor']; preco = float(rows[0]['preco_unitario'])
                line_total = preco * qtd; total += line_total
                self.result_rows.append((peca_id, peca_nome, qtd, forn_id, forn_nome, preco, line_total))
                self.tbl.cellWidget(r,2).setText(f"{forn_nome} @ {preco:,.4f}".replace(',','X').replace('.',',').replace('X','.'))
            else:
                self.tbl.cellWidget(r,2).setText("Sem cotação")
        self.lbl_total.setText(f"Total estimado: {total:,.2f}".replace(',','X').replace('.',',').replace('X','.'))

    def export_csv(self):
        if not self.result_rows:
            QMessageBox.warning(self, "Erro", "Calcule o orçamento primeiro.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Salvar CSV", "orcamento.csv", "CSV (*.csv)")
        if not path: return
        with open(path, "w", newline='', encoding='utf-8') as f:
            w = csv.writer(f, delimiter=';')
            w.writerow(["Peça","Quantidade","Fornecedor","Preço Unit.","Total"])
            for (_, nome, qtd, _, forn, preco, total) in self.result_rows:
                w.writerow([nome, qtd, forn, f"{preco:.4f}".replace('.',','), f"{total:.2f}".replace('.',',')])
        QMessageBox.information(self, "Exportado", f"CSV salvo em: {path}")


# --------------------
# Dialog: Import Excel
# --------------------
class ImportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Importar Excel")
        self.resize(600, 200)
        self.layout = QVBoxLayout(self)
        h = QHBoxLayout()
        self.file_edit = QLineEdit(); btn_browse = QPushButton("Procurar"); btn_browse.clicked.connect(self.browse)
        h.addWidget(self.file_edit); h.addWidget(btn_browse)
        self.layout.addLayout(h)
        self.cb_tipo = QComboBox(); self.cb_tipo.addItems(["fornecedores","pecas","pecas_fornecedores", "veículos"])
        self.layout.addWidget(QLabel("Tipo de importação:")); self.layout.addWidget(self.cb_tipo)
        self.cb_usuario = QComboBox(); users = run_select("SELECT id_usuario, nome FROM usuarios WHERE status='ativo'"); 
        for u in users: self.cb_usuario.addItem(u['nome'], u['id_usuario'])
        self.layout.addWidget(QLabel("Usuário responsável:")); self.layout.addWidget(self.cb_usuario)
        hl = QHBoxLayout(); btn_ok = QPushButton("Importar"); btn_ok.clicked.connect(self.do_import); btn_cancel = QPushButton("Cancelar"); btn_cancel.clicked.connect(self.reject)
        hl.addStretch(); hl.addWidget(btn_ok); hl.addWidget(btn_cancel); self.layout.addLayout(hl)
        if not HAS_PANDAS:
            QMessageBox.warning(self, "Dependência", "Pandas não encontrado. Instale: pip install pandas openpyxl")

    def browse(self):
        path, _ = QFileDialog.getOpenFileName(self, "Selecionar Excel", "", "Planilhas (*.xlsx *.xls)")
        if path: self.file_edit.setText(path)

    def do_import(self):
        path = self.file_edit.text().strip()
        if not path or not os.path.exists(path): QMessageBox.warning(self, "Erro", "Selecione um arquivo válido."); return
        if not HAS_PANDAS: QMessageBox.warning(self, "Erro", "Pandas não está instalado."); return
        tipo = self.cb_tipo.currentText(); user_id = self.cb_usuario.currentData()
        h = hashlib.sha256(open(path, "rb").read()).hexdigest()
        try:
            df = pd.read_excel(path)
            conn = get_connection(); cur = conn.cursor()
            if tipo == "fornecedores":
                # expect columns: nome (required), cnpj_cpf, endereco, telefone, email, observacoes
                for _, row in df.iterrows():
                    nome = str(row.get('nome', '') or row.get('Nome','')).strip()
                    if not nome: continue
                    cnpj = str(row.get('cnpj_cpf','') or row.get('CNPJ_CPF',''))
                    endereco = str(row.get('endereco','') or row.get('Endereco',''))
                    telefone = str(row.get('telefone','') or row.get('Telefone',''))
                    email = str(row.get('email','') or row.get('Email',''))
                    observ = str(row.get('observacoes','') or row.get('Observacoes',''))
                    cur.execute("INSERT INTO fornecedores (nome, cnpj_cpf, endereco, telefone, email, observacoes) VALUES (%s,%s,%s,%s,%s,%s)",
                                (nome, cnpj, endereco, telefone, email, observ))
            elif tipo == "pecas":
                for _, row in df.iterrows():
                    nome = str(row.get('nome', '') or row.get('Nome','')).strip()
                    if not nome: continue
                    codigo = str(row.get('codigo_interno','') or row.get('Codigo_interno',''))
                    unidade = str(row.get('unidade_medida','un') or row.get('Unidade_medida','un'))
                    cur.execute("INSERT INTO pecas (nome, codigo_interno, unidade_medida) VALUES (%s,%s,%s)",
                                (nome, codigo, unidade))
                    # ensure estoque row exists
                    cur.execute("INSERT IGNORE INTO estoque (id_peca, quantidade_atual, quantidade_minima) VALUES (LAST_INSERT_ID(),0,0)")
            elif tipo == "pecas_fornecedores":
                for _, row in df.iterrows():
                    id_peca = int(row.get('id_peca') or row.get('ID_PECA') or 0)
                    id_fornecedor = int(row.get('id_fornecedor') or row.get('ID_FORNECEDOR') or 0)
                    preco = float(row.get('preco_unitario') or row.get('PRECO_UNITARIO') or 0)
                    dt = row.get('data_cotacao') or row.get('DATA_COTACAO')
                    if isinstance(dt, (datetime,)):
                        dt_s = dt.strftime("%Y-%m-%d")
                    else:
                        dt_s = str(dt)
                    if id_peca and id_fornecedor:
                        cur.execute("INSERT INTO pecas_fornecedores (id_peca, id_fornecedor, preco_unitario, data_cotacao) VALUES (%s,%s,%s,%s)",
                                    (id_peca, id_fornecedor, preco, dt_s))
            elif tipo == "veículos":
                for _, row in df.iterrows():
                    placa = str(row.get('placa', '') or row.get('PLACA',''))
                    descricao = str(row.get('descricao','') or row.get('DESCRICAO',''))
                    modelo = str(row.get('modelo') or row.get('MODELO') or 0)
                    ano = int(row.get('ano') or row.get('ANO') or 0)
                    chassi = str(row.get('chassi','') or row.get('CHASSI',''))
                    renavam = int(row.get('renavam') or row.get('RENAVAM') or 0)
                    cur.execute("INSERT INTO equipamentos (placa, descricao, modelo, ano, chassi, renavam) VALUES (%s,%s,%s,%s,%s,%s)", (placa, descricao, modelo, ano, chassi, renavam))
            else:
                raise RuntimeError("Tipo inválido")
            # log
            cur.execute("INSERT INTO importacoes (arquivo_nome, arquivo_hash, tipo_importacao, data_importacao, usuario_responsavel, status, mensagem_log) VALUES (%s,%s,%s,%s,%s,'sucesso',%s)",
                        (os.path.basename(path), h, tipo, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id, f"Linhas: {len(df)}"))
            conn.commit(); cur.close(); conn.close()
            QMessageBox.information(self, "Importado", "Importação finalizada com sucesso.")
            self.accept()
        except Exception as e:
            try: conn.rollback()
            except: pass
            QMessageBox.critical(self, "Erro", f"Falha na importação: {e}")


# --------------------
# Main Window
# --------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Frota (MySQL)")
        self.resize(1200, 700)
        tabs = QTabWidget()

        # Tabs: fornecedores, pecas, precos, estoque, compras, manutencoes, orcamento, import, usuarios, equipamentos
        self.tab_fornecedores = QWidget(); self.init_fornecedores_tab()
        self.tab_pecas = QWidget(); self.init_pecas_tab()
        self.tab_precos = QWidget(); self.init_precos_tab()
        self.tab_estoque = QWidget(); self.init_estoque_tab()
        self.tab_compras = QWidget(); self.init_compras_tab()
        self.tab_manut = QWidget(); self.init_manut_tab()
        self.tab_orc = QWidget(); self.init_orc_tab()
        self.tab_import = QWidget(); self.init_import_tab()
        self.tab_usuarios = QWidget(); self.init_usuarios_tab()
        self.tab_equip = QWidget(); self.init_equip_tab()

        tabs.addTab(self.tab_fornecedores, "Fornecedores")
        tabs.addTab(self.tab_pecas, "Peças")
        tabs.addTab(self.tab_precos, "Preços por Fornecedor")
        tabs.addTab(self.tab_estoque, "Estoque")
        tabs.addTab(self.tab_compras, "Compras")
        tabs.addTab(self.tab_manut, "Manutenções")
        tabs.addTab(self.tab_orc, "Orçamentador")
        tabs.addTab(self.tab_import, "Importações")
        tabs.addTab(self.tab_usuarios, "Usuários")
        tabs.addTab(self.tab_equip, "Equipamentos")

        self.setCentralWidget(tabs)

        # Toolbar
        tb = self.addToolBar("Ações")
        act_compra = QAction("Nova Compra", self); act_compra.triggered.connect(self.open_compra_dialog)
        act_manut = QAction("Nova Manutenção", self); act_manut.triggered.connect(self.open_manut_dialog)
        act_orc = QAction("Orçamento Dinâmico", self); act_orc.triggered.connect(self.open_orc_dialog)
        act_imp = QAction("Importar Excel", self); act_imp.triggered.connect(self.open_import_dialog)
        tb.addAction(act_compra); tb.addAction(act_manut); tb.addAction(act_orc); tb.addAction(act_imp)

    # ------- Fornecedores -------
    def init_fornecedores_tab(self):
        layout = QVBoxLayout(self.tab_fornecedores)
        h = QHBoxLayout()
        self.filtro_fornecedor = QLineEdit(); self.filtro_fornecedor.setPlaceholderText("Pesquisar fornecedor...")
        btn = QPushButton("Filtrar"); btn.clicked.connect(self.load_fornecedores)
        h.addWidget(self.filtro_fornecedor); h.addWidget(btn)
        layout.addLayout(h)
        self.tbl_fornecedores = QTableWidget(); layout.addWidget(self.tbl_fornecedores)
        bl = QHBoxLayout()
        btn_add = QPushButton("Adicionar"); btn_add.clicked.connect(self.add_fornecedor)
        btn_edit = QPushButton("Editar"); btn_edit.clicked.connect(self.edit_fornecedor)
        btn_del = QPushButton("Excluir"); btn_del.clicked.connect(self.del_fornecedor)
        bl.addWidget(btn_add); bl.addWidget(btn_edit); bl.addWidget(btn_del); bl.addStretch()
        layout.addLayout(bl)
        self.load_fornecedores()

    def load_fornecedores(self):
        filtro = self.filtro_fornecedor.text().strip()
        sql = "SELECT id_fornecedor, nome, cnpj_cpf, telefone, email, endereco FROM fornecedores"
        params = ()
        if filtro:
            sql += " WHERE nome LIKE %s OR cnpj_cpf LIKE %s"
            params = (f"%{filtro}%", f"%{filtro}%")
        rows = run_select(sql, params)
        self.tbl_fornecedores.setColumnCount(6)
        self.tbl_fornecedores.setHorizontalHeaderLabels(["ID","Nome","CNPJ/CPF","Telefone","Email","Endereço"])
        self.tbl_fornecedores.setRowCount(len(rows))
        for i, r in enumerate(rows):
            self.tbl_fornecedores.setItem(i,0,QTableWidgetItem(str(r['id_fornecedor'])))
            self.tbl_fornecedores.setItem(i,1,QTableWidgetItem(r['nome']))
            self.tbl_fornecedores.setItem(i,2,QTableWidgetItem(str(r.get('cnpj_cpf') or '')))
            self.tbl_fornecedores.setItem(i,3,QTableWidgetItem(str(r.get('telefone') or '')))
            self.tbl_fornecedores.setItem(i,4,QTableWidgetItem(str(r.get('email') or '')))
            self.tbl_fornecedores.setItem(i,5,QTableWidgetItem(str(r.get('endereco') or '')))
        header = self.tbl_fornecedores.horizontalHeader(); header.setSectionResizeMode(QHeaderView.ResizeToContents); header.setStretchLastSection(True)

    def add_fornecedor(self):
        fields = [("nome","line",None),("cnpj_cpf","line",None),("endereco","line",None),("telefone","line",None),("email","line",None),("observacoes","text",None)]
        dlg = RecordDialog("Novo Fornecedor", fields, parent=self)
        if dlg.exec_():
            data = dlg.get_data()
            try:
                run_commit("INSERT INTO fornecedores (nome, cnpj_cpf, endereco, telefone, email, observacoes) VALUES (%s,%s,%s,%s,%s,%s)",
                           (data['nome'], data['cnpj_cpf'], data['endereco'], data['telefone'], data['email'], data['observacoes']))
                QMessageBox.information(self, "OK", "Fornecedor inserido.")
                self.load_fornecedores()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha: {e}")

    def edit_fornecedor(self):
        row = self.tbl_fornecedores.currentRow()
        if row < 0: QMessageBox.warning(self, "Selecionar", "Selecione um fornecedor."); return
        id_ = int(self.tbl_fornecedores.item(row,0).text())
        vals = {
            "nome": self.tbl_fornecedores.item(row,1).text(),
            "cnpj_cpf": self.tbl_fornecedores.item(row,2).text(),
            "telefone": self.tbl_fornecedores.item(row,3).text(),
            "email": self.tbl_fornecedores.item(row,4).text(),
            "endereco": self.tbl_fornecedores.item(row,5).text()
        }
        fields = [("nome","line",None),("cnpj_cpf","line",None),("telefone","line",None),("email","line",None),("endereco","line",None)]
        dlg = RecordDialog("Editar Fornecedor", fields, values=vals, parent=self)
        if dlg.exec_():
            data = dlg.get_data()
            try:
                run_commit("UPDATE fornecedores SET nome=%s, cnpj_cpf=%s, telefone=%s, email=%s, endereco=%s WHERE id_fornecedor=%s",
                           (data['nome'], data['cnpj_cpf'], data['telefone'], data['email'], data['endereco'], id_))
                QMessageBox.information(self, "OK", "Fornecedor atualizado."); self.load_fornecedores()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha: {e}")

    def del_fornecedor(self):
        row = self.tbl_fornecedores.currentRow()
        if row < 0: QMessageBox.warning(self, "Selecionar", "Selecione um fornecedor."); return
        id_ = int(self.tbl_fornecedores.item(row,0).text())
        if QMessageBox.question(self, "Confirmar", "Excluir fornecedor?") == QMessageBox.Yes:
            try:
                run_commit("DELETE FROM fornecedores WHERE id_fornecedor=%s", (id_,))
                QMessageBox.information(self, "OK", "Fornecedor excluído."); self.load_fornecedores()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha: {e}")

    # ------- Peças -------
    def init_pecas_tab(self):
        layout = QVBoxLayout(self.tab_pecas)
        h = QHBoxLayout()
        self.filtro_peca = QLineEdit(); self.filtro_peca.setPlaceholderText("Pesquisar peça...")
        btn = QPushButton("Filtrar"); btn.clicked.connect(self.load_pecas)
        h.addWidget(self.filtro_peca); h.addWidget(btn); layout.addLayout(h)
        self.tbl_pecas = QTableWidget(); layout.addWidget(self.tbl_pecas)
        bl = QHBoxLayout()
        btn_add = QPushButton("Adicionar"); btn_add.clicked.connect(self.add_peca)
        btn_edit = QPushButton("Editar"); btn_edit.clicked.connect(self.edit_peca)
        btn_del = QPushButton("Excluir"); btn_del.clicked.connect(self.del_peca)
        bl.addWidget(btn_add); bl.addWidget(btn_edit); bl.addWidget(btn_del); bl.addStretch()
        layout.addLayout(bl)
        self.load_pecas()

    def load_pecas(self):
        filtro = self.filtro_peca.text().strip()
        sql = "SELECT id_peca, nome, codigo_interno, unidade_medida FROM pecas"
        params = ()
        if filtro:
            sql += " WHERE nome LIKE %s OR codigo_interno LIKE %s"
            params = (f"%{filtro}%", f"%{filtro}%")
        rows = run_select(sql, params)
        self.tbl_pecas.setColumnCount(4)
        self.tbl_pecas.setHorizontalHeaderLabels(["ID","Código", "Nome","Unidade"])
        self.tbl_pecas.setRowCount(len(rows))
        for i,r in enumerate(rows):
            self.tbl_pecas.setItem(i,0,QTableWidgetItem(str(r['id_peca'])))
            self.tbl_pecas.setItem(i,2,QTableWidgetItem(r['nome']))
            self.tbl_pecas.setItem(i,1,QTableWidgetItem(str(r.get('codigo_interno') or '')))
            self.tbl_pecas.setItem(i,3,QTableWidgetItem(str(r.get('unidade_medida') or '')))
        header = self.tbl_pecas.horizontalHeader(); header.setSectionResizeMode(QHeaderView.ResizeToContents); header.setStretchLastSection(True)

    def add_peca(self):
        fields = [("nome","line",None), ("codigo_interno","line",None), ("unidade_medida","line",None)]
        dlg = RecordDialog("Nova Peça", fields, parent=self)
        if dlg.exec_():
            data = dlg.get_data()
            try:
                run_commit("INSERT INTO pecas (nome, codigo_interno, unidade_medida) VALUES (%s,%s,%s)",
                           (data['nome'], data['codigo_interno'], data['unidade_medida'])) 
                # ensure estoque row
                run_commit("INSERT IGNORE INTO estoque (id_peca, quantidade_atual, quantidade_minima) SELECT id_peca,0,0 FROM pecas WHERE codigo_interno=%s", (data['codigo_interno'],))
                QMessageBox.information(self, "OK", "Peça inserida."); self.load_pecas(); self.load_estoque()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha: {e}")

    def edit_peca(self):
        row = self.tbl_pecas.currentRow()
        if row < 0: QMessageBox.warning(self, "Selecionar", "Selecione uma peça."); return
        id_ = int(self.tbl_pecas.item(row,0).text())
        vals = {"nome": self.tbl_pecas.item(row,2).text(), "codigo_interno": self.tbl_pecas.item(row,1).text(), "unidade_medida": self.tbl_pecas.item(row,3).text()}
        fields = [("nome","line",None), ("codigo_interno","line",None), ("unidade_medida","line",None)]
        dlg = RecordDialog("Editar Peça", fields, values=vals, parent=self)
        if dlg.exec_():
            data = dlg.get_data()
            try:
                run_commit("UPDATE pecas SET nome=%s, codigo_interno=%s, unidade_medida=%s WHERE id_peca=%s",
                           (data['nome'], data['codigo_interno'], data['unidade_medida'], id_))
                QMessageBox.information(self, "OK", "Peça atualizada."); self.load_pecas(); self.load_estoque()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha: {e}")

    def del_peca(self):
        row = self.tbl_pecas.currentRow()
        if row < 0: QMessageBox.warning(self, "Selecionar", "Selecione uma peça."); return
        id_ = int(self.tbl_pecas.item(row,0).text())
        if QMessageBox.question(self, "Confirmar", "Excluir peça?")==QMessageBox.Yes:
            try:
                run_commit("DELETE FROM pecas WHERE id_peca=%s", (id_,)); QMessageBox.information(self, "OK", "Peça excluída."); self.load_pecas(); self.load_estoque()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha: {e}")

    # ------- Preços por Fornecedor -------
    def init_precos_tab(self):
        layout = QVBoxLayout(self.tab_precos)
        h = QHBoxLayout()
        self.filtro_precos = QLineEdit(); self.filtro_precos.setPlaceholderText("Pesquisar peça ou fornecedor...")
        btn = QPushButton("Filtrar"); btn.clicked.connect(self.load_precos)
        h.addWidget(self.filtro_precos); h.addWidget(btn); layout.addLayout(h)
        self.tbl_precos = QTableWidget(); layout.addWidget(self.tbl_precos)
        bl = QHBoxLayout()
        btn_add = QPushButton("Adicionar Cotação"); btn_add.clicked.connect(self.add_preco)
        btn_del = QPushButton("Excluir Cotação"); btn_del.clicked.connect(self.del_preco)
        bl.addWidget(btn_add); bl.addWidget(btn_del); bl.addStretch()
        layout.addLayout(bl)
        self.load_precos()

    def load_precos(self):
        filtro = self.filtro_precos.text().strip()
        sql = """SELECT pf.id_peca_fornecedor, p.nome AS peca, f.nome AS fornecedor, pf.preco_unitario, pf.data_cotacao
                 FROM pecas_fornecedores pf
                 JOIN pecas p ON pf.id_peca = p.id_peca
                 JOIN fornecedores f ON pf.id_fornecedor = f.id_fornecedor"""
        params = ()
        if filtro:
            sql += " WHERE p.nome LIKE %s OR f.nome LIKE %s"
            params = (f"%{filtro}%", f"%{filtro}%")
        rows = run_select(sql, params)
        self.tbl_precos.setColumnCount(5)
        self.tbl_precos.setHorizontalHeaderLabels(["ID","Peça","Fornecedor","Preço","Data Cotação"])
        self.tbl_precos.setRowCount(len(rows))
        for i, r in enumerate(rows):
            self.tbl_precos.setItem(i,0,QTableWidgetItem(str(r['id_peca_fornecedor'])))
            self.tbl_precos.setItem(i,1,QTableWidgetItem(r['peca'])); self.tbl_precos.setItem(i,2,QTableWidgetItem(r['fornecedor']))
            self.tbl_precos.setItem(i,3,QTableWidgetItem(str(r['preco_unitario']))); self.tbl_precos.setItem(i,4,QTableWidgetItem(str(r['data_cotacao'])))
        header = self.tbl_precos.horizontalHeader(); header.setSectionResizeMode(QHeaderView.ResizeToContents); header.setStretchLastSection(True)

    def add_preco(self):
        pecas = run_select("SELECT id_peca, nome FROM pecas ORDER BY nome")
        fns = run_select("SELECT id_fornecedor, nome FROM fornecedores ORDER BY nome")
        if not pecas or not fns: QMessageBox.warning(self, "Dados", "Cadastre peças e fornecedores antes."); return
        fields = [("id_peca","combo",[(p['nome'], p['id_peca']) for p in pecas]), ("id_fornecedor","combo",[(f['nome'], f['id_fornecedor']) for f in fns]), ("preco_unitario","line",None), ("data_cotacao","date",None)]
        dlg = RecordDialog("Nova Cotação", fields, parent=self)
        if dlg.exec_():
            data = dlg.get_data()
            try:
                run_commit("INSERT INTO pecas_fornecedores (id_peca, id_fornecedor, preco_unitario, data_cotacao) VALUES (%s,%s,%s,%s)",
                           (data['id_peca'], data['id_fornecedor'], float(data['preco_unitario'].replace(',','.')) if data['preco_unitario'] else 0.0, data['data_cotacao']))
                QMessageBox.information(self, "OK", "Cotação registrada."); self.load_precos()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha: {e}")

    def del_preco(self):
        row = self.tbl_precos.currentRow()
        if row < 0: QMessageBox.warning(self, "Selecionar", "Selecione uma cotação."); return
        id_ = int(self.tbl_precos.item(row,0).text())
        if QMessageBox.question(self, "Confirmar", "Excluir cotação?")==QMessageBox.Yes:
            try:
                run_commit("DELETE FROM pecas_fornecedores WHERE id_peca_fornecedor=%s", (id_,)); QMessageBox.information(self, "OK", "Cotação excluída."); self.load_precos()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha: {e}")

    # ------- Estoque -------
    def init_estoque_tab(self):
        layout = QVBoxLayout(self.tab_estoque)
        h = QHBoxLayout(); self.filtro_estoque = QLineEdit(); self.filtro_estoque.setPlaceholderText("Pesquisar peça..."); btn = QPushButton("Filtrar"); btn.clicked.connect(self.load_estoque); h.addWidget(self.filtro_estoque); h.addWidget(btn); layout.addLayout(h)
        self.tbl_estoque = QTableWidget(); layout.addWidget(self.tbl_estoque)
        bl = QHBoxLayout(); btn_refresh = QPushButton("Atualizar"); btn_refresh.clicked.connect(self.load_estoque); btn_adj = QPushButton("Ajustar"); btn_adj.clicked.connect(self.adjust_estoque); btn_del = QPushButton("Remover do estoque"); btn_del.clicked.connect(self.remove_from_estoque); bl.addWidget(btn_refresh); bl.addWidget(btn_adj); bl.addWidget(btn_del); bl.addStretch(); layout.addLayout(bl)
        self.load_estoque()

    def load_estoque(self):
        filtro = self.filtro_estoque.text().strip()
        sql = """SELECT e.id_estoque, p.nome, e.quantidade_atual, e.quantidade_minima
                 FROM estoque e JOIN pecas p ON e.id_peca = p.id_peca"""
        params = ()
        if filtro:
            sql += " WHERE p.nome LIKE %s"
            params = (f"%{filtro}%",)
        rows = run_select(sql, params)
        self.tbl_estoque.setColumnCount(4); self.tbl_estoque.setHorizontalHeaderLabels(["ID Estoque","Peça","Qtd Atual","Qtd Mínima"]); self.tbl_estoque.setRowCount(len(rows))
        alerta = []
        for i, r in enumerate(rows):
            self.tbl_estoque.setItem(i,0,QTableWidgetItem(str(r['id_estoque'])))
            self.tbl_estoque.setItem(i,1,QTableWidgetItem(r['nome'])); self.tbl_estoque.setItem(i,2,QTableWidgetItem(str(r['quantidade_atual']))); self.tbl_estoque.setItem(i,3,QTableWidgetItem(str(r['quantidade_minima'])))
            if float(r['quantidade_atual']) < float(r['quantidade_minima']): alerta.append(f"{r['nome']} (Qt: {r['quantidade_atual']}, Mín: {r['quantidade_minima']})")
        header = self.tbl_estoque.horizontalHeader(); header.setSectionResizeMode(QHeaderView.ResizeToContents); header.setStretchLastSection(True)
        if alerta: QMessageBox.warning(self, "Estoque baixo", "Peças abaixo do mínimo:\n" + "\n".join(alerta))

    def adjust_estoque(self):
        row = self.tbl_estoque.currentRow(); 
        if row < 0: QMessageBox.warning(self, "Selecionar", "Selecione um item do estoque."); return
        id_est = int(self.tbl_estoque.item(row,0).text())
        current = float(self.tbl_estoque.item(row,2).text())
        min = float(self.tbl_estoque.item(row,3).text())
        fields = [("nova_quantidade","int",None), ("quantidade_minima", "int", None)]
        dlg = RecordDialog("Ajustar Estoque", fields, values={"nova_quantidade": int(current), "quantidade_minima": int(min)}, parent=self)
        if dlg.exec_():
            new_q = dlg.get_data()['nova_quantidade']
            new_m = dlg.get_data()['quantidade_minima']
            try:
                run_commit("UPDATE estoque SET quantidade_atual = %s, quantidade_minima = %s WHERE id_estoque = %s", (new_q, new_m, id_est))
                QMessageBox.information(self, "OK", "Estoque ajustado.")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha: {e}")

    def remove_from_estoque(self):
        row = self.tbl_estoque.currentRow(); 
        if row < 0: QMessageBox.warning(self, "Selecionar", "Selecione um item do estoque."); return
        id_est = int(self.tbl_estoque.item(row,0).text()); nome = self.tbl_estoque.item(row,1).text()
        if QMessageBox.question(self, "Confirmar", f"Remover {nome} do estoque?")==QMessageBox.Yes:
            try:
                run_commit("DELETE FROM estoque WHERE id_estoque = %s", (id_est,)); QMessageBox.information(self, "OK", "Removido."); self.load_estoque()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha: {e}")

    # ------- Compras Tab -------
    def init_compras_tab(self):
        layout = QVBoxLayout(self.tab_compras)
        h = QHBoxLayout(); self.filtro_compras = QLineEdit(); self.filtro_compras.setPlaceholderText("Pesquisar compras por fornecedor..."); btn = QPushButton("Filtrar"); btn.clicked.connect(self.load_compras); h.addWidget(self.filtro_compras); h.addWidget(btn); layout.addLayout(h)
        self.tbl_compras = QTableWidget(); layout.addWidget(self.tbl_compras)
        bl = QHBoxLayout(); btn_add = QPushButton("Registrar Compra"); btn_add.clicked.connect(self.open_compra_dialog); btn_del = QPushButton("Excluir Compra"); btn_del.clicked.connect(self.del_compra); bl.addWidget(btn_add); bl.addWidget(btn_del); bl.addStretch(); layout.addLayout(bl)
        self.load_compras()

    def load_compras(self):
        filtro = self.filtro_compras.text().strip()
        sql = """SELECT c.id_compra, f.nome AS fornecedor, c.data_compra, c.valor_total
                 FROM compras c JOIN fornecedores f ON c.id_fornecedor = f.id_fornecedor"""
        params = ()
        if filtro:
            sql += " WHERE f.nome LIKE %s"
            params = (f"%{filtro}%",)
        rows = run_select(sql, params)
        self.tbl_compras.setColumnCount(4); self.tbl_compras.setHorizontalHeaderLabels(["ID","Fornecedor","Data","Valor Total"]); self.tbl_compras.setRowCount(len(rows))
        for i, r in enumerate(rows):
            self.tbl_compras.setItem(i,0,QTableWidgetItem(str(r['id_compra']))); self.tbl_compras.setItem(i,1,QTableWidgetItem(r['fornecedor'])); self.tbl_compras.setItem(i,2,QTableWidgetItem(str(r['data_compra']))); self.tbl_compras.setItem(i,3,QTableWidgetItem(str(r['valor_total'])))
        header = self.tbl_compras.horizontalHeader(); header.setSectionResizeMode(QHeaderView.ResizeToContents); header.setStretchLastSection(True)

    def open_compra_dialog(self):
        dlg = CompraDialog(self); 
        if dlg.exec_(): self.load_compras(); self.load_estoque()

    def del_compra(self):
        row = self.tbl_compras.currentRow(); 
        if row < 0: QMessageBox.warning(self, "Selecionar", "Selecione uma compra."); return
        id_ = int(self.tbl_compras.item(row,0).text())
        if QMessageBox.question(self, "Confirmar", "Excluir compra? (não reverte estoque)")==QMessageBox.Yes:
            try:
                run_commit("DELETE FROM compras WHERE id_compra = %s", (id_,))
                QMessageBox.information(self, "OK", "Compra excluída."); self.load_compras(); self.load_estoque()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha: {e}")

    # ------- Manutenções Tab -------
    def init_manut_tab(self):
        layout = QVBoxLayout(self.tab_manut)
        h = QHBoxLayout(); self.filtro_manut = QLineEdit(); self.filtro_manut.setPlaceholderText("Pesquisar..."); btn = QPushButton("Filtrar"); btn.clicked.connect(self.load_manutencoes); h.addWidget(self.filtro_manut); h.addWidget(btn); layout.addLayout(h)
        self.tbl_manut = QTableWidget(); layout.addWidget(self.tbl_manut)
        bl = QHBoxLayout(); btn_add = QPushButton("Registrar Manutenção"); btn_add.clicked.connect(self.open_manut_dialog); btn_del = QPushButton("Excluir"); btn_del.clicked.connect(self.del_manut); btn_rel = QPushButton("Gerar Relatório (CSV)"); btn_rel.clicked.connect(self.export_manut_csv); bl.addWidget(btn_add); bl.addWidget(btn_del); bl.addWidget(btn_rel); bl.addStretch(); layout.addLayout(bl)
        self.load_manutencoes()

    def load_manutencoes(self):
        filtro = self.filtro_manut.text().strip()
        sql = """SELECT m.id_manutencao, e.placa, e.descricao AS equipamento, m.data_inicio, m.data_fim, m.tipo, m.custo_total
                 FROM manutencoes m JOIN equipamentos e ON m.id_equipamento = e.id_equipamento ORDER BY m.data_inicio DESC"""
        params = ()
        if filtro:
            sql += " WHERE e.placa LIKE %s OR e.descricao LIKE %s"
            params = (f"%{filtro}%", f"%{filtro}%")
        rows = run_select(sql, params)
        self.tbl_manut.setColumnCount(7); self.tbl_manut.setHorizontalHeaderLabels(["ID","Placa","Equipamento","Início","Fim","Tipo","Custo Total"]); self.tbl_manut.setRowCount(len(rows))
        for i, r in enumerate(rows):
            self.tbl_manut.setItem(i,0,QTableWidgetItem(str(r['id_manutencao']))); self.tbl_manut.setItem(i,1,QTableWidgetItem(str(r.get('placa') or ''))); self.tbl_manut.setItem(i,2,QTableWidgetItem(str(r.get('equipamento') or '')))
            self.tbl_manut.setItem(i,3,QTableWidgetItem(str(r.get('data_inicio') or ''))); self.tbl_manut.setItem(i,4,QTableWidgetItem(str(r.get('data_fim') or '')))
            self.tbl_manut.setItem(i,5,QTableWidgetItem(str(r.get('tipo') or ''))); self.tbl_manut.setItem(i,6,QTableWidgetItem(str(r.get('custo_total') or '0')))
        header = self.tbl_manut.horizontalHeader(); header.setSectionResizeMode(QHeaderView.ResizeToContents); header.setStretchLastSection(True)

    def open_manut_dialog(self):
        dlg = ManutencaoDialog(self); 
        if dlg.exec_(): self.load_manutencoes(); self.load_estoque()

    def del_manut(self):
        row = self.tbl_manut.currentRow(); 
        if row < 0: QMessageBox.warning(self, "Selecionar", "Selecione uma manutenção."); return
        id_ = int(self.tbl_manut.item(row,0).text())
        if QMessageBox.question(self, "Confirmar", "Excluir manutenção? (não reverte estoque)")==QMessageBox.Yes:
            try:
                run_commit("DELETE FROM manutencoes WHERE id_manutencao=%s", (id_,)); QMessageBox.information(self, "OK", "Excluído"); self.load_manutencoes(); self.load_estoque()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha: {e}")

    def export_manut_csv(self):
        row = self.tbl_manut.currentRow(); 
        if row < 0: QMessageBox.warning(self, "Selecionar", "Selecione uma manutenção."); return
        id_ = int(self.tbl_manut.item(row,0).text())
        rows = run_select("""SELECT mp.id_item_manutencao, p.nome, mp.quantidade_usada, mp.preco_unitario FROM manutencoes_pecas mp JOIN pecas p ON mp.id_peca = p.id_peca WHERE mp.id_manutencao = %s""", (id_,))
        if not rows: QMessageBox.information(self, "Relatório", "Nenhuma peça nesta manutenção."); return
        path, _ = QFileDialog.getSaveFileName(self, "Salvar CSV", f"manut_{id_}.csv", "CSV (*.csv)")
        if not path: return
        with open(path, "w", newline='', encoding='utf-8') as f:
            w = csv.writer(f, delimiter=';'); w.writerow(["Peça","Qtd","Preço Unit.","Total"])
            for r in rows:
                w.writerow([r['nome'], r['quantidade_usada'], float(r['preco_unitario']), float(r['quantidade_usada'])*float(r['preco_unitario'])])
        QMessageBox.information(self, "Exportado", f"CSV salvo em: {path}")

    # ------- Orçamentador -------
    def init_orc_tab(self):
        layout = QVBoxLayout(self.tab_orc)
        hl = QHBoxLayout(); btn = QPushButton("Abrir Orçamentador"); btn.clicked.connect(self.open_orc_dialog); hl.addStretch(); hl.addWidget(btn); layout.addLayout(hl)

    def open_orc_dialog(self):
        dlg = OrcamentoDialog(self); dlg.exec_()

    # ------- Import -------
    def init_import_tab(self):
        layout = QVBoxLayout(self.tab_import)
        btn = QPushButton("Importar Excel"); btn.clicked.connect(self.open_import_dialog)
        layout.addWidget(btn)

    def open_import_dialog(self):
        dlg = ImportDialog(self); dlg.exec_()

    # ------- Usuarios -------
    def init_usuarios_tab(self):
        layout = QVBoxLayout(self.tab_usuarios)
        h = QHBoxLayout(); self.filtro_usuario = QLineEdit(); self.filtro_usuario.setPlaceholderText("Pesquisar..."); btn = QPushButton("Filtrar"); btn.clicked.connect(self.load_usuarios); h.addWidget(self.filtro_usuario); h.addWidget(btn); layout.addLayout(h)
        self.tbl_usuarios = QTableWidget(); layout.addWidget(self.tbl_usuarios)
        bl = QHBoxLayout(); btn_add = QPushButton("Adicionar"); btn_add.clicked.connect(self.add_usuario); btn_edit = QPushButton("Editar"); btn_edit.clicked.connect(self.edit_usuario); btn_del = QPushButton("Excluir"); btn_del.clicked.connect(self.del_usuario); bl.addWidget(btn_add); bl.addWidget(btn_edit); bl.addWidget(btn_del); bl.addStretch(); layout.addLayout(bl)
        self.load_usuarios()

    def load_usuarios(self):
        filtro = self.filtro_usuario.text().strip()
        sql = "SELECT id_usuario, nome, email, perfil, status FROM usuarios"
        params = ()
        if filtro:
            sql += " WHERE nome LIKE %s OR email LIKE %s"
            params = (f"%{filtro}%", f"%{filtro}%")
        rows = run_select(sql, params)
        self.tbl_usuarios.setColumnCount(5); self.tbl_usuarios.setHorizontalHeaderLabels(["ID","Nome","Email","Perfil","Status"]); self.tbl_usuarios.setRowCount(len(rows))
        for i,r in enumerate(rows):
            self.tbl_usuarios.setItem(i,0,QTableWidgetItem(str(r['id_usuario']))); self.tbl_usuarios.setItem(i,1,QTableWidgetItem(r['nome'])); self.tbl_usuarios.setItem(i,2,QTableWidgetItem(str(r.get('email') or ''))); self.tbl_usuarios.setItem(i,3,QTableWidgetItem(str(r.get('perfil') or ''))); self.tbl_usuarios.setItem(i,4,QTableWidgetItem(str(r.get('status') or '')))
        header = self.tbl_usuarios.horizontalHeader(); header.setSectionResizeMode(QHeaderView.ResizeToContents); header.setStretchLastSection(True)

    def add_usuario(self):
        fields = [("nome","line",None),("email","line",None),("senha","line",None),("perfil","combo",[("Administrador","admin"),("Mecânico","mecanico"),("Gestor","gestor")])]
        dlg = RecordDialog("Novo Usuário", fields, parent=self)
        if dlg.exec_():
            data = dlg.get_data(); senha_hash = hashlib.sha256(data['senha'].encode()).hexdigest() if data['senha'] else None
            try:
                run_commit("INSERT INTO usuarios (nome, email, senha_hash, perfil, status) VALUES (%s,%s,%s,%s,%s)",
                           (data['nome'], data['email'], senha_hash, data['perfil'], 'ativo'))
                QMessageBox.information(self, "OK", "Usuário criado."); self.load_usuarios()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha: {e}")

    def edit_usuario(self):
        row = self.tbl_usuarios.currentRow(); 
        if row < 0: QMessageBox.warning(self, "Selecionar", "Selecione um usuário."); return
        id_ = int(self.tbl_usuarios.item(row,0).text()); vals = {"nome": self.tbl_usuarios.item(row,1).text(), "email": self.tbl_usuarios.item(row,2).text(), "perfil": self.tbl_usuarios.item(row,3).text()}
        fields = [("nome","line",None),("email","line",None),("senha","line",None),("perfil","combo",[("Administrador","admin"),("Mecânico","mecanico"),("Gestor","gestor")])]
        dlg = RecordDialog("Editar Usuário", fields, values=vals, parent=self)
        if dlg.exec_():
            data = dlg.get_data()
            try:
                params = [data['nome'], data['email'], data['perfil']]
                sql = "UPDATE usuarios SET nome=%s, email=%s, perfil=%s"
                if data['senha']:
                    senha_hash = hashlib.sha256(data['senha'].encode()).hexdigest()
                    sql += ", senha_hash=%s"; params.append(senha_hash)
                sql += " WHERE id_usuario=%s"; params.append(id_)
                run_commit(sql, tuple(params)); QMessageBox.information(self, "OK", "Usuário atualizado."); self.load_usuarios()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha: {e}")

    def del_usuario(self):
        row = self.tbl_usuarios.currentRow(); 
        if row < 0: QMessageBox.warning(self, "Selecionar", "Selecione um usuário."); return
        id_ = int(self.tbl_usuarios.item(row,0).text())
        if QMessageBox.question(self, "Confirmar", "Excluir usuário?")==QMessageBox.Yes:
            try:
                run_commit("DELETE FROM usuarios WHERE id_usuario=%s", (id_,)); QMessageBox.information(self, "OK", "Excluído"); self.load_usuarios()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha: {e}")

    # ------- Equipamentos -------
    def init_equip_tab(self):
        layout = QVBoxLayout(self.tab_equip)
        h = QHBoxLayout(); self.filtro_equip = QLineEdit(); self.filtro_equip.setPlaceholderText("Pesquisar..."); btn = QPushButton("Filtrar"); btn.clicked.connect(self.load_equipamentos); h.addWidget(self.filtro_equip); h.addWidget(btn); layout.addLayout(h)
        self.tbl_equip = QTableWidget(); layout.addWidget(self.tbl_equip)
        bl = QHBoxLayout(); btn_add = QPushButton("Adicionar"); btn_add.clicked.connect(self.add_equip); btn_edit = QPushButton("Editar"); btn_edit.clicked.connect(self.edit_equip); btn_del = QPushButton("Excluir"); btn_del.clicked.connect(self.del_equip); bl.addWidget(btn_add); bl.addWidget(btn_edit); bl.addWidget(btn_del); bl.addStretch(); layout.addLayout(bl)
        self.load_equipamentos()

    def load_equipamentos(self):
        filtro = self.filtro_equip.text().strip()
        sql = "SELECT id_equipamento, placa, descricao, modelo, ano, renavam, chassi, status FROM equipamentos"
        params = ()
        if filtro:
            sql += " WHERE placa LIKE %s OR descricao LIKE %s"
            params = (f"%{filtro}%", f"%{filtro}%")
        rows = run_select(sql, params)
        self.tbl_equip.setColumnCount(8); self.tbl_equip.setHorizontalHeaderLabels(["ID","Placa","Descrição","Modelo","Ano", "Chassi", "Renavam","Status"]); self.tbl_equip.setRowCount(len(rows))
        for i,r in enumerate(rows):
            self.tbl_equip.setItem(i,0,QTableWidgetItem(str(r['id_equipamento']))); self.tbl_equip.setItem(i,1,QTableWidgetItem(str(r.get('placa') or ''))); self.tbl_equip.setItem(i,2,QTableWidgetItem(str(r.get('descricao') or '')))
            self.tbl_equip.setItem(i,3,QTableWidgetItem(str(r.get('modelo') or ''))); self.tbl_equip.setItem(i,4,QTableWidgetItem(str(r.get('ano') or ''))); self.tbl_equip.setItem(i,5,QTableWidgetItem(str(r.get('chassi') or ''))); self.tbl_equip.setItem(i,6,QTableWidgetItem(str(r.get('renavam') or ''))); self.tbl_equip.setItem(i,7,QTableWidgetItem(str(r.get('status') or '')))
        header = self.tbl_equip.horizontalHeader(); header.setSectionResizeMode(QHeaderView.ResizeToContents); header.setStretchLastSection(True)

    def add_equip(self):
        fields = [("placa","line",None),("descricao","line",None),("modelo","line",None),("ano","int",None),("chassi","line",None), ("renavam", "int", None)]
        dlg = RecordDialog("Novo Equipamento", fields, parent=self)
        if dlg.exec_():
            data = dlg.get_data()
            try:
                run_commit("INSERT INTO equipamentos (placa, descricao, modelo, ano, chassi, renavam, status) VALUES (%s,%s,%s,%s,%s, %s, 'ativo')",
                           (data['placa'], data['descricao'], data['modelo'], data['ano'], data['chassi'], data['renavam'])); QMessageBox.information(self, "OK", "Equipamento inserido."); self.load_equipamentos()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha: {e}")

    def edit_equip(self):
        row = self.tbl_equip.currentRow(); 
        if row < 0: QMessageBox.warning(self, "Selecionar", "Selecione um equipamento."); return
        id_ = int(self.tbl_equip.item(row,0).text()); vals = {"placa": self.tbl_equip.item(row,1).text(), "descricao": self.tbl_equip.item(row,2).text(), "modelo": self.tbl_equip.item(row,3).text(), "ano": int(self.tbl_equip.item(row,4).text()) if self.tbl_equip.item(row,4).text() else None, "chassi": self.tbl_equip.item(row,5).text(), "renavam": int(self.tbl_equip.item(row,6).text()) if self.tbl_equip.item(row,6).text() else None}
        fields = [("placa","line",None),("descricao","line",None),("modelo","line",None),("ano","int",None),("chassi","line",None)]
        dlg = RecordDialog("Editar Equipamento", fields, values=vals, parent=self)
        if dlg.exec_():
            data = dlg.get_data()
            try:
                run_commit("UPDATE equipamentos SET placa=%s, descricao=%s, modelo=%s, ano=%s, chassi=%s, renavam=%s WHERE id_equipamento=%s",
                           (data['placa'], data['descricao'], data['modelo'], data['ano'], data['chassi'], data['renavam'], id_)); QMessageBox.information(self, "OK", "Atualizado."); self.load_equipamentos()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha: {e}")

    def del_equip(self):
        row = self.tbl_equip.currentRow(); 
        if row < 0: QMessageBox.warning(self, "Selecionar", "Selecione um equipamento."); return
        id_ = int(self.tbl_equip.item(row,0).text())
        if QMessageBox.question(self, "Confirmar", "Excluir equipamento?")==QMessageBox.Yes:
            try:
                run_commit("DELETE FROM equipamentos WHERE id_equipamento=%s", (id_,)); QMessageBox.information(self, "OK", "Excluído"); self.load_equipamentos()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha: {e}")


# --------------------
# App start
# --------------------
def main():
    app = QApplication(sys.argv)
    try:
        ensure_database_and_tables()
    except Exception as e:
        QMessageBox.critical(None, "DB Error", f"Erro ao preparar banco MySQL: {e}")
        return
    
    qss = load_stylesheet("estilo.qss")
    app.setStyleSheet(qss)

    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

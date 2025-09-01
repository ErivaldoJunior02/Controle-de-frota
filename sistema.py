# sistema_frota_full.py
import sys
import pandas as pd
from datetime import datetime, date
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import mysql.connector
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QTabWidget,
    QLabel, QMessageBox, QDialog, QFormLayout, QComboBox, QSpinBox, QDateEdit, QFileDialog, QHeaderView, QMenuBar, QAction
)
from PyQt5.QtCore import QDate, Qt

# ---------- Helper: DB connection (adjust credentials) ----------
def get_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="Juninho0209@",   # <<--- coloque sua senha
        database="sis"    # <<--- seu banco
    )

# ---------- Generic dialog for Add / Edit ----------
class RecordDialog(QDialog):
    def __init__(self, title, fields, values=None, parent=None):
        """
        fields: list of tuples (name, widget_type) widget_type: 'line','int','date','combo'
        values: dict name->value for edit
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.layout = QFormLayout()
        self.inputs = {}
        for name, wtype, extra in fields:
            if wtype == 'line':
                le = QLineEdit()
                if values and name in values:
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
                # extra expected to be list of tuples (display, value)
                for disp, val in extra:
                    cb.addItem(disp, val)
                if values and name in values:
                    # try select by value
                    idx = next((i for i in range(cb.count()) if cb.itemData(i) == values[name]), 0)
                    cb.setCurrentIndex(idx)
                self.inputs[name] = cb
                self.layout.addRow(QLabel(name.replace('_',' ').capitalize()), cb)

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
                data[k] = widget.text()
            elif isinstance(widget, QSpinBox):
                data[k] = widget.value()
            elif isinstance(widget, QDateEdit):
                data[k] = widget.date().toString("yyyy-MM-dd")
            elif isinstance(widget, QComboBox):
                data[k] = widget.currentData()
        return data

from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton, QVBoxLayout, QLabel, QMessageBox
import hashlib

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login")
        layout = QVBoxLayout()

        self.user_edit = QLineEdit()
        self.user_edit.setPlaceholderText("Usuário")
        layout.addWidget(QLabel("Usuário:"))
        layout.addWidget(self.user_edit)

        self.pass_edit = QLineEdit()
        self.pass_edit.setEchoMode(QLineEdit.Password)
        self.pass_edit.setPlaceholderText("Senha")
        layout.addWidget(QLabel("Senha:"))
        layout.addWidget(self.pass_edit)

        btn_login = QPushButton("Entrar")
        btn_login.clicked.connect(self.check_login)
        layout.addWidget(btn_login)

        self.setLayout(layout)
        self.user_data = None

    def check_login(self):
        user = self.user_edit.text().strip()
        senha = self.pass_edit.text().strip()

        if not user or not senha:
            QMessageBox.warning(self, "Erro", "Preencha todos os campos.")
            return

        try:
            conn = get_connection()  # Função que retorna a conexão MySQL
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT * FROM usuarios WHERE usuario=%s", (user,))
            row = cursor.fetchone()

            if row:
                # Hash da senha digitada
                senha_hash = hashlib.sha256(senha.encode()).hexdigest()
                if row["senha"] == senha_hash:
                    self.user_data = row  # Guarda dados do usuário logado
                    self.accept()         # Fecha o diálogo com sucesso
                else:
                    QMessageBox.warning(self, "Erro", "Usuário ou senha inválidos.")
            else:
                QMessageBox.warning(self, "Erro", "Usuário ou senha inválidos.")

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Ocorreu um erro: {e}")

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

class SistemaFrotaApp(QMainWindow):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user   # 🔹 agora sempre existe
        self.setWindowTitle("Sistema de Frota - Completo")
        self.resize(1100, 700)
        try:
            self.conn = get_connection()
            self.cursor = self.conn.cursor()
        except Exception as e:
            QMessageBox.critical(self, "DB Error", f"Erro ao conectar ao banco: {e}")
            raise

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.init_fornecedores_tab()
        self.init_pecas_tab()
        self.init_veiculos_tab()
        self.init_compras_tab()
        self.init_manutencoes_tab()
        self.init_estoque_tab()
        self.init_relatorios_tab()
        self.init_usuarios_tab()

        menubar = QMenuBar(self)
        menu_usuario = menubar.addMenu("Usuário")

        acao_logoff = QAction("Logoff", self)
        acao_logoff.triggered.connect(self.logoff)
        menu_usuario.addAction(acao_logoff)

        self.setMenuBar(menubar)
        self.setCentralWidget(self.tabs)

    def logoff(self):
        self.hide()  # fecha a janela principal

        # 🔹 reabre a tela de login
        self.login_window = LoginDialog()
        self.login_window.show()

    # ------- Generic helpers -------
    def run_select(self, sql, params=()):
        self.cursor.execute(sql, params)
        return self.cursor.fetchall()

    def run_commit(self, sql, params=()):
        self.cursor.execute(sql, params)
        self.conn.commit()
        return self.cursor.lastrowid

    def show_error(self, msg):
        QMessageBox.critical(self, "Erro", msg)

    # ------- Fornecedores Tab -------
    def init_fornecedores_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)

        # filtro
        h = QHBoxLayout()
        self.filtro_fornecedor = QLineEdit()
        self.filtro_fornecedor.setPlaceholderText("Pesquisar fornecedor (nome ou cnpj)...")
        btn_filtrar = QPushButton("Filtrar")
        btn_filtrar.clicked.connect(self.filter_fornecedores)
        h.addWidget(self.filtro_fornecedor); h.addWidget(btn_filtrar)
        layout.addLayout(h)

        # tabela
        self.tbl_fornecedor = QTableWidget(); layout.addWidget(self.tbl_fornecedor)

        # botoes
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("Adicionar")
        btn_edit = QPushButton("Editar")
        btn_del = QPushButton("Excluir")
        btn_add.clicked.connect(self.add_fornecedor)
        btn_edit.clicked.connect(self.edit_fornecedor)
        btn_del.clicked.connect(self.delete_fornecedor)
        btn_layout.addWidget(btn_add); btn_layout.addWidget(btn_edit); btn_layout.addWidget(btn_del)
        layout.addLayout(btn_layout)

        self.tabs.addTab(tab, "Fornecedores")
        self.load_fornecedores()

    def load_fornecedores(self, filtro=None):
        sql = "SELECT id, nome, cnpj, n_contato, n_contato2, coordenadas FROM fornecedor"
        params = ()
        if filtro:
            sql += " WHERE nome LIKE %s OR cnpj LIKE %s"
            params = (f"%{filtro}%", f"%{filtro}%")
        rows = self.run_select(sql, params)
        self.tbl_fornecedor.setColumnCount(6)
        self.tbl_fornecedor.setHorizontalHeaderLabels(["ID","Nome","CNPJ","Contato1","Contato2","Coordenadas"])
        header = self.tbl_fornecedor.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)  # ajusta pelo conteúdo
        header.setStretchLastSection(True)
        self.tbl_fornecedor.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.tbl_fornecedor.setItem(i, j, QTableWidgetItem(str(val)))

    def filter_fornecedores(self):
        self.load_fornecedores(self.filtro_fornecedor.text().strip())

    def add_fornecedor(self):
        if self.current_user["tipo"] != "admin":
            QMessageBox.warning(self, "Permissão negada", "Somente administradores podem adicionar fornecedores.")
            return
        fields = [("nome","line",None),("cnpj","line",None),("n_contato","line",None),("n_contato2","line",None),("coordenadas","line",None)]
        dlg = RecordDialog("Novo Fornecedor", fields, parent=self)
        if dlg.exec_():
            data = dlg.get_data()
            try:
                self.run_commit("INSERT INTO fornecedor (nome, cnpj, n_contato, n_contato2, coordenadas) VALUES (%s,%s,%s,%s,%s)",
                                (data['nome'], data['cnpj'], data['n_contato'], data['n_contato2'], data['coordenadas']))
                QMessageBox.information(self, "OK", "Fornecedor criado.")
                self.load_fornecedores()
            except Exception as e:
                self.show_error(f"Erro ao inserir fornecedor: {e}")

    def edit_fornecedor(self):
        row = self.tbl_fornecedor.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Seleção", "Selecione uma linha para editar.")
            return
        id_ = int(self.tbl_fornecedor.item(row,0).text())
        vals = { "nome": self.tbl_fornecedor.item(row,1).text(),
                 "cnpj": self.tbl_fornecedor.item(row,2).text(),
                 "n_contato": self.tbl_fornecedor.item(row,3).text(),
                 "n_contato2": self.tbl_fornecedor.item(row,4).text(),
                 "coordenadas": self.tbl_fornecedor.item(row,5).text()
               }
        fields = [("nome","line",None),("cnpj","line",None),("n_contato","line",None),("n_contato2","line",None),("coordenadas","line",None)]
        dlg = RecordDialog("Editar Fornecedor", fields, values=vals, parent=self)
        if dlg.exec_():
            data = dlg.get_data()
            try:
                self.run_commit("UPDATE fornecedor SET nome=%s, cnpj=%s, n_contato=%s, n_contato2=%s, coordenadas=%s WHERE id=%s",
                                (data['nome'], data['cnpj'], data['n_contato'], data['n_contato2'], data['coordenadas'], id_))
                QMessageBox.information(self, "OK", "Fornecedor atualizado.")
                self.load_fornecedores()
            except Exception as e:
                self.show_error(f"Erro ao atualizar fornecedor: {e}")

    def delete_fornecedor(self):
        row = self.tbl_fornecedor.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Seleção", "Selecione uma linha para excluir.")
            return
        id_ = int(self.tbl_fornecedor.item(row,0).text())
        if QMessageBox.question(self, "Confirmar", "Excluir fornecedor?") == QMessageBox.Yes:
            try:
                self.run_commit("DELETE FROM fornecedor WHERE id=%s", (id_,))
                QMessageBox.information(self, "OK", "Fornecedor excluído.")
                self.load_fornecedores()
            except Exception as e:
                self.show_error(f"Erro ao excluir: {e}")

    # ------- Pecas Tab -------
    def init_pecas_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        h = QHBoxLayout()
        self.filtro_peca = QLineEdit(); self.filtro_peca.setPlaceholderText("Pesquisar peça...")
        btn = QPushButton("Filtrar"); btn.clicked.connect(self.filter_pecas)
        h.addWidget(self.filtro_peca); h.addWidget(btn); layout.addLayout(h)

        self.tbl_pecas = QTableWidget(); layout.addWidget(self.tbl_pecas)

        bl = QHBoxLayout()
        btn_add = QPushButton("Adicionar"); btn_edit = QPushButton("Editar"); btn_del = QPushButton("Excluir")
        btn_add.clicked.connect(self.add_peca); btn_edit.clicked.connect(self.edit_peca); btn_del.clicked.connect(self.delete_peca)
        bl.addWidget(btn_add); bl.addWidget(btn_edit); bl.addWidget(btn_del)
        layout.addLayout(bl)

        self.tabs.addTab(tab, "Itens")
        self.load_pecas()

    def load_pecas(self, filtro=None):
        sql = "SELECT id, nome FROM pecas"
        params = ()
        if filtro:
            sql += " WHERE nome LIKE %s"
            params = (f"%{filtro}%",)
        rows = self.run_select(sql, params)
        self.tbl_pecas.setColumnCount(2)
        self.tbl_pecas.setHorizontalHeaderLabels(["ID","Nome"])
        header = self.tbl_pecas.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)  # ajusta pelo conteúdo
        header.setStretchLastSection(True)
        self.tbl_pecas.setRowCount(len(rows))
        for i,row in enumerate(rows):
            for j,val in enumerate(row):
                self.tbl_pecas.setItem(i,j,QTableWidgetItem(str(val)))

    def filter_pecas(self):
        self.load_pecas(self.filtro_peca.text().strip())

    def add_peca(self):
        fields = [("nome","line",None), ("estoque_minimo", "int", None)]
        dlg = RecordDialog("Nova Peça", fields, parent=self)
        if dlg.exec_():
            data = dlg.get_data()
            try:
                self.run_commit("INSERT INTO pecas (nome, estoque_minimo) VALUES (%s, %s)", (data['nome'], data['estoque_minimo']))
                QMessageBox.information(self, "OK", "Peça inserida.")
                self.load_pecas()
            except Exception as e:
                self.show_error(f"Erro ao inserir peça: {e}")

    def edit_peca(self):
        row = self.tbl_pecas.currentRow()
        if row < 0:
            QMessageBox.warning(self,"Seleção","Selecione uma peça para editar.")
            return
        id_ = int(self.tbl_pecas.item(row,0).text())
        vals = {"nome": self.tbl_pecas.item(row,1).text()}
        dlg = RecordDialog("Editar Peça", [("nome","line",None)], values=vals, parent=self)
        if dlg.exec_():
            data = dlg.get_data()
            try:
                self.run_commit("UPDATE pecas SET nome=%s, estoque_minimo=%s WHERE id=%s", (data['nome'], id_))
                QMessageBox.information(self,"OK","Peça atualizada.")
                self.load_pecas()
            except Exception as e:
                self.show_error(f"Erro ao atualizar peça: {e}")

    def delete_peca(self):
        row = self.tbl_pecas.currentRow()
        if row < 0:
            QMessageBox.warning(self,"Seleção","Selecione uma peça para excluir.")
            return
        id_ = int(self.tbl_pecas.item(row,0).text())
        if QMessageBox.question(self,"Confirmar","Excluir peça?")==QMessageBox.Yes:
            try:
                self.run_commit("DELETE FROM pecas WHERE id=%s",(id_,))
                QMessageBox.information(self,"OK","Peça excluída.")
                self.load_pecas()
            except Exception as e:
                self.show_error(f"Erro ao excluir peça: {e}")

    # ------- Veiculos Tab -------
    def init_veiculos_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        h = QHBoxLayout()
        self.filtro_veiculo = QLineEdit(); self.filtro_veiculo.setPlaceholderText("Pesquisar placa/modelo...")
        btn = QPushButton("Filtrar"); btn.clicked.connect(self.filter_veiculos)
        h.addWidget(self.filtro_veiculo); h.addWidget(btn); layout.addLayout(h)

        self.tbl_veiculos = QTableWidget(); layout.addWidget(self.tbl_veiculos)

        bl = QHBoxLayout()
        btn_add = QPushButton("Adicionar"); btn_edit = QPushButton("Editar"); btn_del = QPushButton("Excluir")
        btn_add.clicked.connect(self.add_veiculo); btn_edit.clicked.connect(self.edit_veiculo); btn_del.clicked.connect(self.delete_veiculo)
        bl.addWidget(btn_add); bl.addWidget(btn_edit); bl.addWidget(btn_del)
        layout.addLayout(bl)

        self.tabs.addTab(tab, "Veículos")
        self.load_veiculos()

    def load_veiculos(self, filtro=None):
        sql = "SELECT id, placa, tipo, modelo, chassi, renavam, ano, regime, tipo_equipamento FROM veiculos"
        params = ()
        if filtro:
            sql += " WHERE placa LIKE %s OR modelo LIKE %s"
            params = (f"%{filtro}%", f"%{filtro}%")
        rows = self.run_select(sql, params)
        self.tbl_veiculos.setColumnCount(9)
        self.tbl_veiculos.setHorizontalHeaderLabels(["ID","Placa","Tipo","Modelo","Chassi","Renavam","Ano","Regime","TipoEquip"])
        header = self.tbl_veiculos.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)  # ajusta pelo conteúdo
        header.setStretchLastSection(True)
        self.tbl_veiculos.setRowCount(len(rows))
        for i,row in enumerate(rows):
            for j,val in enumerate(row):
                self.tbl_veiculos.setItem(i,j,QTableWidgetItem(str(val)))

    def filter_veiculos(self):
        self.load_veiculos(self.filtro_veiculo.text().strip())

    def add_veiculo(self):
        fields = [("placa","line",None),("tipo","line",None),("modelo","line",None),("chassi","line",None),
                  ("renavam","line",None),("ano","int",None),("regime","line",None),("tipo_equipamento","line",None)]
        dlg = RecordDialog("Novo Veículo", fields, parent=self)
        if dlg.exec_():
            data = dlg.get_data()
            try:
                self.run_commit("INSERT INTO veiculos (placa,tipo,modelo,chassi,renavam,ano,regime,tipo_equipamento) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                                (data['placa'],data['tipo'],data['modelo'],data['chassi'],data['renavam'],data['ano'],data['regime'],data['tipo_equipamento']))
                QMessageBox.information(self,"OK","Veículo inserido.")
                self.load_veiculos()
            except Exception as e:
                self.show_error(f"Erro ao inserir veículo: {e}")

    def edit_veiculo(self):
        row = self.tbl_veiculos.currentRow()
        if row < 0:
            QMessageBox.warning(self,"Seleção","Selecione um veículo.")
            return
        id_ = int(self.tbl_veiculos.item(row,0).text())
        vals = { "placa":self.tbl_veiculos.item(row,1).text(), "tipo":self.tbl_veiculos.item(row,2).text(),
                 "modelo":self.tbl_veiculos.item(row,3).text(), "chassi":self.tbl_veiculos.item(row,4).text(),
                 "renavam":self.tbl_veiculos.item(row,5).text(), "ano":int(self.tbl_veiculos.item(row,6).text()),
                 "regime":self.tbl_veiculos.item(row,7).text(), "tipo_equipamento":self.tbl_veiculos.item(row,8).text() }
        fields = [("placa","line",None),("tipo","line",None),("modelo","line",None),("chassi","line",None),
                  ("renavam","line",None),("ano","int",None),("regime","line",None),("tipo_equipamento","line",None)]
        dlg = RecordDialog("Editar Veículo", fields, values=vals, parent=self)
        if dlg.exec_():
            data = dlg.get_data()
            try:
                self.run_commit("UPDATE veiculos SET placa=%s,tipo=%s,modelo=%s,chassi=%s,renavam=%s,ano=%s,regime=%s,tipo_equipamento=%s WHERE id=%s",
                                (data['placa'],data['tipo'],data['modelo'],data['chassi'],data['renavam'],data['ano'],data['regime'],data['tipo_equipamento'], id_))
                QMessageBox.information(self,"OK","Veículo atualizado.")
                self.load_veiculos()
            except Exception as e:
                self.show_error(f"Erro ao atualizar veículo: {e}")

    def delete_veiculo(self):
        row = self.tbl_veiculos.currentRow()
        if row < 0:
            QMessageBox.warning(self,"Seleção","Selecione um veículo.")
            return
        id_ = int(self.tbl_veiculos.item(row,0).text())
        if QMessageBox.question(self,"Confirmar","Excluir veículo?")==QMessageBox.Yes:
            try:
                self.run_commit("DELETE FROM veiculos WHERE id=%s",(id_,))
                QMessageBox.information(self,"OK","Veículo excluído.")
                self.load_veiculos()
            except Exception as e:
                self.show_error(f"Erro ao excluir veículo: {e}")

    # ------- Compras Tab -------
    def init_compras_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        h = QHBoxLayout()
        self.filtro_compra = QLineEdit(); self.filtro_compra.setPlaceholderText("Pesquisar compras por peça/fornecedor...")
        btn = QPushButton("Filtrar"); btn.clicked.connect(self.filter_compras)
        h.addWidget(self.filtro_compra); h.addWidget(btn); layout.addLayout(h)

        self.tbl_compras = QTableWidget(); layout.addWidget(self.tbl_compras)

        bl = QHBoxLayout()
        btn_add = QPushButton("Registrar Compra"); btn_edit=QPushButton("Editar"); btn_del=QPushButton("Excluir")
        btn_add.clicked.connect(self.add_compra); btn_edit.clicked.connect(self.edit_compra); btn_del.clicked.connect(self.delete_compra)
        bl.addWidget(btn_add); bl.addWidget(btn_edit); bl.addWidget(btn_del)
        layout.addLayout(bl)

        self.tabs.addTab(tab, "Compras")
        self.load_compras()

    def load_compras(self, filtro=None):
        # Join to show readable names
        sql = ("SELECT c.id, p.nome, f.nome, c.data_compra, c.quantidade, c.valor_unitario, (c.quantidade * c.valor_unitario) "
               "FROM compra c JOIN pecas p ON c.id_peca = p.id JOIN fornecedor f ON c.id_fornecedor = f.id")
        params = ()
        if filtro:
            sql += " WHERE p.nome LIKE %s OR f.nome LIKE %s"
            params = (f"%{filtro}%", f"%{filtro}%")
        rows = self.run_select(sql, params)
        self.tbl_compras.setColumnCount(7)
        self.tbl_compras.setHorizontalHeaderLabels(["ID","Peça","Fornecedor","Data","Qtd","Preco Unit","Valor Total"])
        header = self.tbl_compras.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)  # ajusta pelo conteúdo
        header.setStretchLastSection(True)
        self.tbl_compras.setRowCount(len(rows))
        for i,row in enumerate(rows):
            for j,val in enumerate(row):
                self.tbl_compras.setItem(i,j,QTableWidgetItem(str(val)))

    def filter_compras(self):
        self.load_compras(self.filtro_compra.text().strip())

    def add_compra(self):
        # need to show combo boxes for pieces and suppliers
        pcs = self.run_select("SELECT id, nome FROM pecas")
        fns = self.run_select("SELECT id, nome FROM fornecedor")
        if not pcs or not fns:
            QMessageBox.warning(self,"Dados faltando","Cadastre peças e fornecedores antes de registrar compras.")
            return
        # build fields: id_peca (combo), id_fornecedor (combo), quantidade (int), valor_unitario (line)
        fields = [
            ("id_peca","combo",[(nome,id_) for id_,nome in pcs]),
            ("id_fornecedor","combo",[(nome,id_) for id_,nome in fns]),
            ("quantidade","int",None),
            ("valor_unitario","line",None)
        ]
        dlg = RecordDialog("Registrar Compra", fields, parent=self)
        if dlg.exec_():
            data = dlg.get_data()
            try:
                id_peca = data['id_peca']; id_fornecedor = data['id_fornecedor']
                quantidade = int(data['quantidade']); preco = float(data['valor_unitario'])
                # insert into compra
                self.run_commit("INSERT INTO compra (id_peca, id_fornecedor, data_compra, quantidade, valor_unitario) VALUES (%s,%s,%s,%s,%s)",
                                (id_peca, id_fornecedor, date.today(), quantidade, preco))
                # update estoque (insert or update)
                r = self.run_select("SELECT quantidade FROM estoque WHERE id_peca=%s", (id_peca,))
                if r:
                    self.run_commit("UPDATE estoque SET quantidade = quantidade + %s WHERE id_peca = %s", (quantidade, id_peca))
                else:
                    self.run_commit("INSERT INTO estoque (id_peca, quantidade) VALUES (%s, %s)", (id_peca, quantidade))
                # upsert peca_fornecedor price
                r2 = self.run_select("SELECT id FROM peca_fornecedor WHERE id_peca=%s AND id_fornecedor=%s", (id_peca, id_fornecedor))
                if r2:
                    self.run_commit("UPDATE peca_fornecedor SET preco=%s WHERE id_peca=%s AND id_fornecedor=%s", (preco, id_peca, id_fornecedor))
                else:
                    self.run_commit("INSERT INTO peca_fornecedor (id_peca, id_fornecedor, preco) VALUES (%s,%s,%s)", (id_peca, id_fornecedor, preco))
                QMessageBox.information(self,"OK","Compra registrada e estoque atualizado.")
                self.load_compras()
                self.load_estoque()
            except Exception as e:
                self.show_error(f"Erro ao registrar compra: {e}")

    def edit_compra(self):
        row = self.tbl_compras.currentRow()
        if row < 0:
            QMessageBox.warning(self,"Seleção","Selecione uma compra para editar.")
            return
        # For simplicity, editing purchases is limited here (could be expanded)
        QMessageBox.information(self,"Info","Editar compra: recurso a implementar com regras de ajuste de estoque.")

    def delete_compra(self):
        row = self.tbl_compras.currentRow()
        if row < 0:
            QMessageBox.warning(self,"Seleção","Selecione uma compra para excluir.")
            return
        id_ = int(self.tbl_compras.item(row,0).text())
        if QMessageBox.question(self,"Confirmar","Excluir compra? (não reverte automaticamente estoque)") == QMessageBox.Yes:
            try:
                self.run_commit("DELETE FROM compra WHERE id=%s", (id_,))
                QMessageBox.information(self,"OK","Compra excluída.")
                self.load_compras(); self.load_estoque()
            except Exception as e:
                self.show_error(f"Erro ao excluir compra: {e}")

    # ------- Manutencoes Tab -------
    def init_manutencoes_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 🔎 Barra de filtro
        filtros_layout = QHBoxLayout()
        self.filtro_manut = QLineEdit()
        self.filtro_manut.setPlaceholderText("Pesquisar manutenções por descrição/peça...")
        btn_filtrar = QPushButton("Filtrar")
        btn_filtrar.clicked.connect(self.filter_manutencoes)
        filtros_layout.addWidget(self.filtro_manut)
        filtros_layout.addWidget(btn_filtrar)
        layout.addLayout(filtros_layout)

        # 🔎 Tabela de manutenções
        self.tbl_manut = QTableWidget()
        layout.addWidget(self.tbl_manut)

        # 🔎 Botões
        botoes_layout = QHBoxLayout()

        btn_add = QPushButton("Registrar Manutenção")
        btn_edit = QPushButton("Editar")
        btn_del = QPushButton("Excluir")
        btn_relatorio = QPushButton("Gerar Relatório")

        btn_add.clicked.connect(self.add_manutencao)
        btn_edit.clicked.connect(self.edit_manutencao)
        btn_del.clicked.connect(self.delete_manutencao)
        btn_relatorio.clicked.connect(self.gerar_relatorio_manutencao)

        botoes_layout.addWidget(btn_add)
        botoes_layout.addWidget(btn_edit)
        botoes_layout.addWidget(btn_del)
        botoes_layout.addWidget(btn_relatorio)

        layout.addLayout(botoes_layout)

        self.tabs.addTab(tab, "Manutenções")
        self.load_manutencoes()

    def criar_pdf_manutencao(self, dados):
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet

        nome_arquivo = f"relatorio_manutencao_{dados['placa']}_{dados['id']}.pdf"
        doc = SimpleDocTemplate(nome_arquivo, pagesize=A4)
        estilo = getSampleStyleSheet()
        elementos = []

        # Cabeçalho
        elementos.append(Paragraph("Relatório de Manutenção", estilo['Title']))

        # Veículo
        tabela_veiculo = Table([
            ["Placa:", dados['placa'], "Modelo:", dados['modelo']],
            ["Ano:", str(dados['ano']), "KM:", str(dados['km'])]
        ])
        tabela_veiculo.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.black)]))
        elementos.append(tabela_veiculo)

        # Manutenção
        tabela_manut = Table([
            ["Data Início:", str(dados['data_inicio']), "Data Fim:", str(dados['data_fim'])],
            ["Responsável:", dados['responsavel'], "Peça Usada:", dados['peca']],
            ["Quantidade:", str(dados['quantidade']), "", ""]
        ])
        tabela_manut.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.black)]))
        elementos.append(tabela_manut)

        doc.build(elementos)
        return nome_arquivo


    def gerar_relatorio_manutencao(self):
        selected = self.tbl_manut.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Erro", "Selecione uma manutenção para gerar o relatório.")
            return

        manutencao_id = int(self.tbl_manut.item(selected, 0).text())

        sql = """
                SELECT m.id, v.placa, v.modelo, v.ano_fabricacao, v.km,
                    m.data_manutencao_inicio, m.data_manutencao_fim,
                    p.nome, m.quantidade_peca_usada
                FROM manutencao m
                JOIN veiculos v ON m.veiculo_usado = v.id
                LEFT JOIN pecas p ON m.peca_usada_id = p.id
                WHERE m.id = %s
            """
        row = self.run_select(sql, (manutencao_id,))
        if not row:
            QMessageBox.warning(self, "Erro", "Não foi possível encontrar os dados da manutenção.")
            return

        dados = {
            "id": row[0][0],
            "placa": row[0][1],
            "modelo": row[0][2],
            "ano": row[0][3],
            "km": row[0][4],
            "data_inicio": row[0][5],
            "data_fim": row[0][6],
            "peca": row[0][8] if row[0][8] else "—",
            "quantidade": row[0][9] if row[0][9] else 0
        }

        arquivo = self.criar_pdf_manutencao(dados)
        QMessageBox.information(self, "Relatório", f"Relatório salvo em:\n{arquivo}")

    def load_manutencoes(self):
        sql = """
            SELECT m.id, v.placa, p.nome, m.quantidade_peca_usada,
                m.data_manutencao_inicio, m.data_manutencao_fim
            FROM manutencao m
            JOIN veiculos v ON m.veiculo_usado = v.id
            LEFT JOIN pecas p ON m.peca_usada_id = p.id
            ORDER BY m.data_manutencao_inicio DESC
        """
        rows = self.run_select(sql)

        self.tbl_manut.setRowCount(len(rows))
        self.tbl_manut.setColumnCount(len(rows[0]) if rows else 0)

        headers = ["ID", "Placa", "Peça", "Qtd Usada",
                "Data Início", "Data Fim"]
        self.tbl_manut.setHorizontalHeaderLabels(headers)

        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.tbl_manut.setItem(i, j, QTableWidgetItem(str(val)))


    def filter_manutencoes(self):
        self.load_manutencoes(self.filtro_manut.text().strip())

    def add_manutencao(self):
        pcs = self.run_select("SELECT id, nome FROM pecas")
        vcl = self.run_select("SELECT id, placa FROM veiculos")
        if not pcs or not vcl:
            QMessageBox.warning(self,"Dados faltando","Cadastre peças e veículos antes de registrar manutenção.")
            return
        fields = [
            ("peca_usada_id","combo",[(nome,id_) for id_,nome in pcs]),
            ("quantidade_peca_usada","int",None),
            ("tipo_manutencao","line",None),
            ("data_manutencao_inicio","date",None),
            ("data_manutencao_fim","date",None),
            ("descricao","line",None),
            ("veiculo_usado","combo",[(placa,id_) for id_,placa in vcl])
        ]
        dlg = RecordDialog("Registrar Manutenção", fields, parent=self)
        if dlg.exec_():
            data = dlg.get_data()
            try:
                id_peca = data['peca_usada_id']; qtd = int(data['quantidade_peca_usada'])
                tipo = data['tipo_manutencao']; din = data['data_manutencao_inicio']; dfim = data['data_manutencao_fim']
                desc = data['descricao']; veic = data['veiculo_usado']
                # check stock
                r = self.run_select("SELECT quantidade FROM estoque WHERE id_peca=%s", (id_peca,))
                if not r or r[0][0] < qtd:
                    QMessageBox.warning(self,"Estoque","Quantidade insuficiente em estoque para esta peça.")
                    return
                # insert manutencao
                self.run_commit("INSERT INTO manutencao (peca_usada_id, quantidade_peca_usada, tipo_manutencao, data_manutencao_inicio, data_manutencao_fim, descricao, veiculo_usado) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                                (id_peca, qtd, tipo, din, dfim, desc, veic))
                # decrease stock
                self.run_commit("UPDATE estoque SET quantidade = quantidade - %s WHERE id_peca=%s", (qtd, id_peca))
                QMessageBox.information(self,"OK","Manutenção registrada e estoque atualizado.")
                self.load_manutencoes(); self.load_estoque()
            except Exception as e:
                self.show_error(f"Erro ao registrar manutenção: {e}")

    def edit_manutencao(self):
        QMessageBox.information(self,"Info","Editar manutenção: recurso a implementar com cuidado (ajuste de estoque).")

    def delete_manutencao(self):
        row = self.tbl_manut.currentRow()
        if row < 0:
            QMessageBox.warning(self,"Seleção","Selecione uma manutenção.")
            return
        id_ = int(self.tbl_manut.item(row,0).text())
        if QMessageBox.question(self,"Confirmar","Excluir manutenção? (não fará ajuste de estoque automaticamente)")==QMessageBox.Yes:
            try:
                self.run_commit("DELETE FROM manutencao WHERE id=%s",(id_,))
                QMessageBox.information(self,"OK","Manutenção excluída.")
                self.load_manutencoes(); self.load_estoque()
            except Exception as e:
                self.show_error(f"Erro ao excluir manut.: {e}")

    # ------- Estoque Tab -------
    def init_estoque_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        h = QHBoxLayout()
        self.filtro_estoque = QLineEdit(); self.filtro_estoque.setPlaceholderText("Pesquisar por peça...")
        btn = QPushButton("Filtrar"); btn.clicked.connect(self.filter_estoque)
        h.addWidget(self.filtro_estoque); h.addWidget(btn); layout.addLayout(h)

        self.tbl_estoque = QTableWidget(); layout.addWidget(self.tbl_estoque)
        bl = QHBoxLayout()
        btn_refresh = QPushButton("Atualizar"); btn_refresh.clicked.connect(self.load_estoque)
        btn_adjust = QPushButton("Ajustar Estoque")
        btn_del = QPushButton("Excluir do Estoque")
        btn_del.clicked.connect(self.delete_from_estoque)
        bl.addWidget(btn_del)
        btn_adjust.clicked.connect(self.adjust_estoque)
        bl.addWidget(btn_refresh); bl.addWidget(btn_adjust)
        layout.addLayout(bl)
        self.tabs.addTab(tab, "Estoque")
        self.load_estoque()

    def load_estoque(self, filtro=None):
        sql = """SELECT e.id_peca, p.nome, e.quantidade, p.estoque_minimo
                FROM estoque e 
                JOIN pecas p ON e.id_peca = p.id"""
        params = ()
        if filtro:
            sql += " WHERE p.nome LIKE %s"
            params = (f"%{filtro}%",)
        rows = self.run_select(sql, params)
        self.tbl_estoque.setColumnCount(4)
        self.tbl_estoque.setHorizontalHeaderLabels(["ID Peça","Nome","Quantidade","Mínimo"])
        header = self.tbl_estoque.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)  # ajusta pelo conteúdo
        header.setStretchLastSection(True)
        self.tbl_estoque.setRowCount(len(rows))

        alerta = []
        for i,row in enumerate(rows):
            for j,val in enumerate(row):
                self.tbl_estoque.setItem(i,j,QTableWidgetItem(str(val)))
            # 🔹 verifica alerta
            if row[2] < row[3]:  
                alerta.append(f"{row[1]} (Qtd: {row[2]}, Mín: {row[3]})")

        if alerta:
            QMessageBox.warning(self, "Estoque Baixo",
                                "As seguintes peças estão abaixo do mínimo:\n" + "\n".join(alerta))

    def filter_estoque(self):
        self.load_estoque(self.filtro_estoque.text().strip())

    def adjust_estoque(self):
        # allow user to adjust a selected piece quantity (positive or negative)
        row = self.tbl_estoque.currentRow()
        if row < 0:
            QMessageBox.warning(self,"Seleção","Selecione um item do estoque.")
            return
        id_peca = int(self.tbl_estoque.item(row,0).text())
        current = int(self.tbl_estoque.item(row,2).text())
        fields = [("nova_quantidade","int",None)]
        dlg = RecordDialog("Ajustar Estoque", fields, values={"nova_quantidade": current}, parent=self)
        if dlg.exec_():
            new_q = dlg.get_data()['nova_quantidade']
            try:
                self.run_commit("UPDATE estoque SET quantidade=%s WHERE id_peca=%s", (new_q, id_peca))
                QMessageBox.information(self,"OK","Estoque ajustado.")
                self.load_estoque()
            except Exception as e:
                self.show_error(f"Erro ao ajustar estoque: {e}")
    def delete_from_estoque(self):
        row = self.tbl_estoque.currentRow()
        if row < 0:
            QMessageBox.warning(self,"Seleção","Selecione uma peça do estoque para excluir.")
            return
        
        id_peca = int(self.tbl_estoque.item(row,0).text())
        nome_peca = self.tbl_estoque.item(row,1).text()

        if QMessageBox.question(
            self,
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir a peça '{nome_peca}' do estoque?"
        ) == QMessageBox.Yes:
            try:
                self.run_commit("DELETE FROM estoque WHERE id_peca=%s",(id_peca,))
                QMessageBox.information(self,"OK","Peça removida do estoque.")
                self.load_estoque()
            except Exception as e:
                self.show_error(f"Erro ao excluir do estoque: {e}")    
    def init_relatorios_tab(self):
        self.tab_relatorios = QWidget()
        layout = QVBoxLayout(self.tab_relatorios)

        filtros_layout = QHBoxLayout()

        self.combo_tipo_relatorio = QComboBox()
        self.combo_tipo_relatorio.addItems([
            "Orçamento de peças por fornecedor",
            "Saída de peças do estoque por período"
        ])
        filtros_layout.addWidget(QLabel("Tipo de Relatório:"))
        filtros_layout.addWidget(self.combo_tipo_relatorio)

        self.combo_fornecedor_rel = QComboBox()
        self.load_fornecedores_rel()
        filtros_layout.addWidget(QLabel("Fornecedor:"))
        filtros_layout.addWidget(self.combo_fornecedor_rel)

        self.data_inicio_rel = QDateEdit()
        self.data_inicio_rel.setCalendarPopup(True)
        self.data_inicio_rel.setDate(QDate.currentDate().addMonths(-1))
        filtros_layout.addWidget(QLabel("Data Início:"))
        filtros_layout.addWidget(self.data_inicio_rel)

        self.data_fim_rel = QDateEdit()
        self.data_fim_rel.setCalendarPopup(True)
        self.data_fim_rel.setDate(QDate.currentDate())
        filtros_layout.addWidget(QLabel("Data Fim:"))
        filtros_layout.addWidget(self.data_fim_rel)

        btn_gerar = QPushButton("Gerar Relatório")
        btn_gerar.clicked.connect(self.gerar_relatorio)
        filtros_layout.addWidget(btn_gerar)

        layout.addLayout(filtros_layout)

        self.table_relatorios = QTableWidget()
        layout.addWidget(self.table_relatorios)

        export_layout = QHBoxLayout()
        btn_excel = QPushButton("Exportar para Excel")
        btn_excel.clicked.connect(self.exportar_excel)
        export_layout.addWidget(btn_excel)

        btn_pdf = QPushButton("Exportar para PDF")
        btn_pdf.clicked.connect(self.exportar_pdf)
        export_layout.addWidget(btn_pdf)

        layout.addLayout(export_layout)

        self.tabs.addTab(self.tab_relatorios, "Relatórios")

    def load_fornecedores_rel(self):
        self.combo_fornecedor_rel.clear()
        fornecedores = self.run_select("SELECT id, nome FROM fornecedor")
        for f in fornecedores:
            self.combo_fornecedor_rel.addItem(f[1], f[0])

    def gerar_relatorio(self):
        self.load_fornecedores_rel()  # garante que a lista está atualizada
        tipo = self.combo_tipo_relatorio.currentText()
        data_inicio = self.data_inicio_rel.date().toString("yyyy-MM-dd")
        data_fim = self.data_fim_rel.date().toString("yyyy-MM-dd")

        if tipo == "Orçamento de peças por fornecedor":
            fornecedor_id = self.combo_fornecedor_rel.currentData()
            sql = """
                SELECT f.nome, p.nome, c.quantidade, c.valor_unitario, 
                    (c.quantidade * c.valor_unitario) AS total, c.data_compra
                FROM compra c
                JOIN pecas p ON c.id_peca = p.id
                JOIN fornecedor f ON c.id_fornecedor = f.id
                WHERE f.id = %s AND c.data_compra BETWEEN %s AND %s
                ORDER BY c.data_compra DESC
            """
            params = (fornecedor_id, data_inicio, data_fim)

        elif tipo == "Saída de peças do estoque por período":
            sql = """
                SELECT p.nome, m.quantidade_peca_usada, m.data_manutencao_inicio, v.placa
                FROM manutencao m
                JOIN pecas p ON m.peca_usada_id = p.id
                JOIN veiculos v ON m.veiculo_usado = v.id
                WHERE m.data_manutencao_inicio BETWEEN %s AND %s
                ORDER BY m.data_manutencao_inicio DESC
            """
            params = (data_inicio, data_fim)

        else:
            QMessageBox.warning(self, "Erro", "Tipo de relatório inválido!")
            return

        rows = self.run_select(sql, params)

        if rows:
            self.table_relatorios.setRowCount(len(rows))
            self.table_relatorios.setColumnCount(len(rows[0]))
            self.table_relatorios.setHorizontalHeaderLabels([desc[0] for desc in self.cursor.description])
            header = self.table_relatorios.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeToContents)  # ajusta pelo conteúdo
            header.setStretchLastSection(True)
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    self.table_relatorios.setItem(i, j, QTableWidgetItem(str(val)))
        else:
            self.table_relatorios.setRowCount(0)
            QMessageBox.information(self, "Relatório", "Nenhum dado encontrado para os filtros selecionados.")

    def exportar_excel(self):
        if self.table_relatorios.rowCount() == 0:
            QMessageBox.warning(self, "Erro", "Nenhum dado para exportar.")
            return

        dados = []
        colunas = [self.table_relatorios.horizontalHeaderItem(i).text() for i in range(self.table_relatorios.columnCount())]
        for i in range(self.table_relatorios.rowCount()):
            linha = []
            for j in range(self.table_relatorios.columnCount()):
                linha.append(self.table_relatorios.item(i, j).text())
            dados.append(linha)

        df = pd.DataFrame(dados, columns=colunas)

        # 🔹 abre janela para escolher onde salvar
        nome_arquivo, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Relatório Excel",
            f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            "Arquivos Excel (*.xlsx)"
        )
        if not nome_arquivo:
            return  # usuário cancelou

        df.to_excel(nome_arquivo, index=False)
        QMessageBox.information(self, "Exportação concluída", f"Arquivo salvo em:\n{nome_arquivo}")


    def exportar_pdf(self):
        if self.table_relatorios.rowCount() == 0:
            QMessageBox.warning(self, "Erro", "Nenhum dado para exportar.")
            return

        dados = []
        colunas = [self.table_relatorios.horizontalHeaderItem(i).text() for i in range(self.table_relatorios.columnCount())]
        dados.append(colunas)

        for i in range(self.table_relatorios.rowCount()):
            linha = []
            for j in range(self.table_relatorios.columnCount()):
                linha.append(self.table_relatorios.item(i, j).text())
            dados.append(linha)

        # 🔹 abre janela para escolher onde salvar
        nome_arquivo, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Relatório PDF",
            f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            "Arquivos PDF (*.pdf)"
        )
        if not nome_arquivo:
            return  # usuário cancelou

        pdf = SimpleDocTemplate(nome_arquivo, pagesize=A4)
        estilo = getSampleStyleSheet()
        tabela = Table(dados)
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ]))
        elementos = [Paragraph("Relatório gerado", estilo['Title']), tabela]
        pdf.build(elementos)
        QMessageBox.information(self, "Exportação concluída", f"Arquivo salvo em:\n{nome_arquivo}")


    def init_usuarios_tab(self):
    # Apenas admins podem acessar
        if self.current_user["tipo"] != "admin":
            return
        
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Filtro de pesquisa
        h = QHBoxLayout()
        self.filtro_usuario = QLineEdit()
        self.filtro_usuario.setPlaceholderText("Pesquisar usuário (nome ou usuario)...")
        btn_filtrar = QPushButton("Filtrar")
        btn_filtrar.clicked.connect(self.filter_usuarios)
        h.addWidget(self.filtro_usuario)
        h.addWidget(btn_filtrar)
        layout.addLayout(h)

        # Tabela
        self.tbl_usuarios = QTableWidget()
        layout.addWidget(self.tbl_usuarios)

        # Botões CRUD
        bl = QHBoxLayout()
        btn_add = QPushButton("Adicionar")
        btn_edit = QPushButton("Editar")
        btn_del = QPushButton("Excluir")
        btn_add.clicked.connect(self.add_usuario)
        btn_edit.clicked.connect(self.edit_usuario)
        btn_del.clicked.connect(self.delete_usuario)
        bl.addWidget(btn_add)
        bl.addWidget(btn_edit)
        bl.addWidget(btn_del)
        layout.addLayout(bl)

        self.tabs.addTab(tab, "Usuários")
        self.load_usuarios()

    def load_usuarios(self, filtro=None):
        sql = "SELECT id, nome, usuario, tipo FROM usuarios"
        params = ()
        if filtro:
            sql += " WHERE nome LIKE %s OR usuario LIKE %s"
            params = (f"%{filtro}%", f"%{filtro}%")
        rows = self.run_select(sql, params)
        self.tbl_usuarios.setColumnCount(4)
        self.tbl_usuarios.setHorizontalHeaderLabels(["ID","Nome","Usuário","Tipo"])
        header = self.tbl_usuarios.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)  # ajusta pelo conteúdo
        header.setStretchLastSection(True)
        self.tbl_usuarios.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.tbl_usuarios.setItem(i,j,QTableWidgetItem(str(val)))

    def filter_usuarios(self):
        self.load_usuarios(self.filtro_usuario.text().strip())

    def add_usuario(self):
        fields = [
            ("nome","line",None),
            ("usuario","line",None),
            ("senha","line",None),
            ("tipo","combo",[("Administrador","admin"),("Comum","comum")])
        ]
        dlg = RecordDialog("Novo Usuário", fields, parent=self)
        if dlg.exec_():
            data = dlg.get_data()
            senha_hash = hashlib.sha256(data['senha'].encode()).hexdigest()
            try:
                self.run_commit("INSERT INTO usuarios (nome, usuario, senha, tipo) VALUES (%s,%s,%s,%s)",
                                (data['nome'], data['usuario'], senha_hash, data['tipo']))
                QMessageBox.information(self,"OK","Usuário criado.")
                self.load_usuarios()
            except Exception as e:
                self.show_error(f"Erro ao criar usuário: {e}")

    def edit_usuario(self):
        row = self.tbl_usuarios.currentRow()
        if row < 0:
            QMessageBox.warning(self,"Seleção","Selecione um usuário para editar.")
            return
        id_ = int(self.tbl_usuarios.item(row,0).text())
        vals = {
            "nome": self.tbl_usuarios.item(row,1).text(),
            "usuario": self.tbl_usuarios.item(row,2).text(),
            "tipo": self.tbl_usuarios.item(row,3).text()
        }
        fields = [
            ("nome","line",None),
            ("usuario","line",None),
            ("senha","line",None),  # opcional: se vazio, mantém a atual
            ("tipo","combo",[("Administrador","admin"),("Comum","comum")])
        ]
        dlg = RecordDialog("Editar Usuário", fields, values=vals, parent=self)
        if dlg.exec_():
            data = dlg.get_data()
            sql = "UPDATE usuarios SET nome=%s, usuario=%s, tipo=%s"
            params = [data['nome'], data['usuario'], data['tipo']]
            if data['senha']:
                senha_hash = hashlib.sha256(data['senha'].encode()).hexdigest()
                sql += ", senha=%s"
                params.append(senha_hash)
            sql += " WHERE id=%s"
            params.append(id_)
            try:
                self.run_commit(sql, tuple(params))
                QMessageBox.information(self,"OK","Usuário atualizado.")
                self.load_usuarios()
            except Exception as e:
                self.show_error(f"Erro ao atualizar usuário: {e}")

    def delete_usuario(self):
        row = self.tbl_usuarios.currentRow()
        if row < 0:
            QMessageBox.warning(self,"Seleção","Selecione um usuário para excluir.")
            return
        id_ = int(self.tbl_usuarios.item(row,0).text())
        if QMessageBox.question(self,"Confirmar","Excluir usuário?")==QMessageBox.Yes:
            try:
                self.run_commit("DELETE FROM usuarios WHERE id=%s",(id_,))
                QMessageBox.information(self,"OK","Usuário excluído.")
                self.load_usuarios()
            except Exception as e:
                self.show_error(f"Erro ao excluir usuário: {e}")
    # ------- on close -------
    def closeEvent(self, event):
        try:
            self.conn.close()
        except:
            pass
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        with open("estilo.qss", "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        pass  # se o arquivo de estilo não existir, ignora

    login = LoginDialog()
    if login.exec_() == QDialog.Accepted:
        user = login.user_data
        win = SistemaFrotaApp(user)   # 🔹 passa o usuário para o construtor
        win.show()
        sys.exit(app.exec_())
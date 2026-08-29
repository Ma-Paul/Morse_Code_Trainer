from __future__ import annotations

import sys
import threading
from datetime import datetime, timedelta, timezone

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QApplication, QComboBox, QDateTimeEdit, QDialog, QDialogButtonBox,
    QFormLayout, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMessageBox,
    QPushButton, QTableWidget, QTableWidgetItem, QTabWidget, QTreeWidget,
    QTreeWidgetItem, QVBoxLayout, QWidget
)

import server

STAR_TEXT = {1: "★ Gold", 2: "★ Silver", 3: "★ Bronze"}

class CreateTournamentDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Tournament")
        self.resize(460, 300)
        form = QFormLayout(self)
        self.name = QLineEdit("Morse Tournament")
        self.visibility = QComboBox(); self.visibility.addItems(["Open to all", "Invite code only"])
        self.recurrence = QComboBox(); self.recurrence.addItems(["Once", "Daily", "Weekly", "Every 2 weeks", "Monthly"])
        self.mode = QComboBox(); self.mode.addItems(["Letter", "Word", "Sentence"])
        self.starts = QDateTimeEdit(); self.starts.setCalendarPopup(True)
        self.starts.setDateTime(datetime.now().astimezone() + timedelta(minutes=5))
        form.addRow("Name", self.name); form.addRow("Access", self.visibility)
        form.addRow("Recurrence", self.recurrence); form.addRow("Mode", self.mode); form.addRow("Starts", self.starts)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject); form.addRow(buttons)

    def payload(self):
        recurrence = {"Once":"once","Daily":"daily","Weekly":"weekly","Every 2 weeks":"biweekly","Monthly":"monthly"}[self.recurrence.currentText()]
        dt = self.starts.dateTime().toPython()
        if dt.tzinfo is None: dt = dt.astimezone()
        return server.TournamentCreate(
            name=self.name.text().strip() or "Morse Tournament",
            visibility="open" if self.visibility.currentIndex()==0 else "invite",
            recurrence=recurrence, mode=self.mode.currentText(),
            starts_at=dt.astimezone(timezone.utc).isoformat(),
        )

class AdminWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle("Morse Code Tournament Server"); self.resize(1180,760)
        tabs = QTabWidget(); self.setCentralWidget(tabs)

        tournament_page = QWidget(); layout = QVBoxLayout(tournament_page)
        bar = QHBoxLayout()
        create = QPushButton("Create Tournament"); create.clicked.connect(self.create_tournament)
        start = QPushButton("Start Selected"); start.clicked.connect(self.start_selected)
        refresh = QPushButton("Refresh"); refresh.clicked.connect(self.refresh_all)
        bar.addWidget(create); bar.addWidget(start); bar.addStretch(); bar.addWidget(refresh); layout.addLayout(bar)

        self.tournaments = QTableWidget(0,7); self.tournaments.setHorizontalHeaderLabels(["ID","Name","Access","Mode","Recurrence","Starts","Status"])
        self.tournaments.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tournaments.itemSelectionChanged.connect(self.refresh_tree)
        layout.addWidget(self.tournaments, 2)

        layout.addWidget(QLabel("Round-robin match tree / schedule"))
        self.tree = QTreeWidget(); self.tree.setHeaderLabels(["Match","Scheduled","Status","Result"]); layout.addWidget(self.tree, 3)
        tabs.addTab(tournament_page, "Tournaments")

        leader_page = QWidget(); leader_layout = QVBoxLayout(leader_page)
        reset = QPushButton("Reset Daily Leaderboard"); reset.clicked.connect(self.reset_leaderboard); leader_layout.addWidget(reset, alignment=Qt.AlignmentFlag.AlignLeft)
        self.leader = QTableWidget(0,4); self.leader.setHorizontalHeaderLabels(["Place","Player","Daily points","Public tournament award"]); leader_layout.addWidget(self.leader)
        tabs.addTab(leader_page, "Leaderboard")

        self.timer = QTimer(self); self.timer.timeout.connect(self.refresh_all); self.timer.start(3000)
        self.refresh_all()

    def selected_id(self):
        row = self.tournaments.currentRow()
        if row < 0: return None
        item = self.tournaments.item(row,0); return int(item.text()) if item else None

    def create_tournament(self):
        d = CreateTournamentDialog(self)
        if d.exec() != QDialog.DialogCode.Accepted: return
        result = server.create_tournament(d.payload())
        if result.get("invite_code"):
            QMessageBox.information(self,"Invite code",f"Invite code: {result['invite_code']}")
        self.refresh_all()

    def start_selected(self):
        tid = self.selected_id()
        if tid is None:
            QMessageBox.information(self,"Tournament","Select a tournament first."); return
        try: server.start_tournament(tid)
        except Exception as e: QMessageBox.critical(self,"Could not start",str(e))
        self.refresh_all()

    def refresh_all(self):
        server.ensure_daily_challenges(); self.refresh_tournaments(); self.refresh_leader(); self.refresh_tree()

    def refresh_tournaments(self):
        rows = server.list_tournaments(); current = self.selected_id()
        self.tournaments.setRowCount(len(rows))
        selected_row = -1
        for r,t in enumerate(rows):
            vals=[t['id'],t['name'],t['visibility'],t['mode'],t['recurrence'],t['starts_at'],t['status']]
            for c,v in enumerate(vals): self.tournaments.setItem(r,c,QTableWidgetItem(str(v or '')))
            if current == t['id']: selected_row = r
        if selected_row >= 0: self.tournaments.selectRow(selected_row)
        self.tournaments.resizeColumnsToContents()

    def refresh_tree(self):
        self.tree.clear(); tid = self.selected_id()
        if tid is None: return
        try: details = server.get_tournament(tid)
        except Exception: return
        root = QTreeWidgetItem([details['name'], details['starts_at'], details['status'], ''])
        self.tree.addTopLevelItem(root)
        for m in details['matches']:
            result = f"{m['player1_score']} : {m['player2_score']}"
            if m['winner_name']: result += f"  → {m['winner_name']}"
            elif m['status']=='finished': result += "  → Draw"
            item=QTreeWidgetItem([f"{m['player1_name']}  vs  {m['player2_name']}",m['scheduled_at'],m['status'],result]); root.addChild(item)
        standings = QTreeWidgetItem(["Final / current standings", "", "", ""]); root.addChild(standings)
        for s in details['standings']:
            standings.addChild(QTreeWidgetItem([f"{s['place']}. {s['display_name']}","",f"{s['tournament_points']} pts",f"{s['wins']} W / {s['draws']} D / {s['losses']} L"]))
        root.setExpanded(True); standings.setExpanded(True); self.tree.resizeColumnToContents(0)

    def refresh_leader(self):
        rows = server.leaderboard(); self.leader.setRowCount(len(rows))
        for r,p in enumerate(rows):
            vals=[r+1,p['display_name'],p['daily_points'],STAR_TEXT.get(p['tournament_place'],'')]
            for c,v in enumerate(vals): self.leader.setItem(r,c,QTableWidgetItem(str(v)))
        self.leader.resizeColumnsToContents()

    def reset_leaderboard(self):
        if QMessageBox.question(self,"Reset leaderboard?","Reset all daily challenge points? This cannot be undone.") != QMessageBox.StandardButton.Yes: return
        server.reset_leaderboard(); self.refresh_leader()

def main():
    server.init_db(); server.ensure_daily_challenges()
    threading.Thread(target=server.run_server, kwargs={'host':'0.0.0.0','port':8000}, daemon=True).start()
    app=QApplication(sys.argv); window=AdminWindow(); window.show(); return app.exec()

if __name__=='__main__': raise SystemExit(main())

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSplitter
from qfluentwidgets import (
    BodyLabel,
    PushButton,
    PrimaryPushButton,
    TogglePushButton,
    PlainTextEdit,
    FluentIcon,
)

from src.views.interface import Interface, InfoTip
from src.utils.translator import Translator
from src.utils.webview import Webview
from src.user import User


class Message(Interface):
    def __init__(self):
        super().__init__(title=Translator().message_title)
        self.setObjectName("massage")

        layout = QVBoxLayout()

        self.toolbar = QWidget(self)
        self.toolbarLayout = QHBoxLayout(self.toolbar)

        self.select_all_button = TogglePushButton(
            FluentIcon.CHECKBOX, self.tr("Select All")
        )
        self.select_all_button.toggled.connect(self.toggleSelectAll)

        self.inverse_button = PushButton(FluentIcon.CANCEL, self.tr("Inverse"))
        self.inverse_button.clicked.connect(self.inverse)

        self.send_button = PrimaryPushButton(FluentIcon.SEND, self.tr("Send"))
        self.send_button.clicked.connect(self.send)
        self.send_button.setEnabled(False)

        self.toolbarLayout.addWidget(self.select_all_button)
        self.toolbarLayout.addWidget(self.inverse_button)
        self.toolbarLayout.addStretch()
        self.toolbarLayout.addWidget(self.send_button)

        self.splitter = QSplitter(Qt.Vertical, self)

        self.edit_area = PlainTextEdit()
        self.edit_area.textChanged.connect(self.edit)

        self.webview_area = QWidget(self)
        self.webview_layout = QVBoxLayout(self.webview_area)
        self.webview_layout.setContentsMargins(0, 0, 0, 0)

        self.webview_banned = QWidget(self)
        self.banned_layout = QVBoxLayout(self.webview_banned)
        self.banned_tip = BodyLabel(self.tr("You are not logged in yet"))
        self.banned_tip.setAlignment(Qt.AlignCenter)
        self.banned_layout.addWidget(self.banned_tip)
        self.login_button = PushButton(self.tr("Go to Login"))
        self.login_button.clicked.connect(self.goLogin)
        self.login_button.setFixedWidth(100)
        self.banned_layout.addWidget(self.login_button, alignment=Qt.AlignCenter)
        self.webview_layout.addWidget(self.webview_banned, alignment=Qt.AlignCenter)

        self.webview = Webview(self)
        self.webview.loadFinished.connect(self.onLoaded)
        self.webview_layout.addWidget(self.webview)

        self.splitter.addWidget(self.edit_area)
        self.splitter.addWidget(self.webview_area)
        self.splitter.setSizes([300, 1000])

        layout.addWidget(self.toolbar)
        layout.addWidget(self.splitter, 1)

        self.view.setLayout(layout)

        User(self).infoUpdated.connect(self.checkLogin)
        self.checkLogin(User)

    def toggleSelectAll(self, checked):
        if not hasattr(self, "webview"):
            return

        if checked:
            self.webview.run("SelectAll();")
        else:
            self.webview.run("SelectNone();")

    def inverse(self):
        if not hasattr(self, "webview"):
            return

        self.webview.run("SelectInverse();")

    def send(self):
        if not self.webview.run("$('.selected').length"):
            InfoTip(type="warning", title=self.tr("Please select at least one friend"))
            return
        try:
            self.webview.run("""document.querySelector('#comment_submit').click();""")

            InfoTip(title=self.tr("Message sent"))
        except:
            print("Failed to send message")
            InfoTip(type="error", title=self.tr("Failed to send message"))

    def edit(self):
        text = self.edit_area.toPlainText()

        if text == "":
            self.send_button.setEnabled(False)
        else:
            self.send_button.setEnabled(True)

        self.webview.run(
            f"""document.querySelector('#comment_textarea').value = "{text}";"""
        )

    def onLoaded(self):
        script = """
        ToggleManageFriends();
        
        var delay = 5; 
        jQuery("#manage_friends").after('<div class="commentthread_entry"><div class="commentthread_entry_quotebox"><textarea rows="1" class="commentthread_textarea" id="comment_textarea" placeholder="Add a comment" style="overflow: hidden; height: 20px;"></textarea></div><div class="commentthread_entry_submitlink" style=""><a class="btn_grey_black btn_small_thin" href="javascript:CCommentThread.FormattingHelpPopup( \\'Profile\\' );"><span>Formatting help</span></a>   <span class="emoticon_container"><span class="emoticon_button small" id="emoticonbtn"></span></span><span class="btn_green_white_innerfade btn_small" id="comment_submit"><span>Post Comments to Selected Friends</span></span></div></div><div id="log"><span id="log_head"></span><span id="log_body"></span></div>');
        new CEmoticonPopup( $J('#emoticonbtn'), $J('#commentthread_Profile_0_textarea') );
        jQuery("#comment_submit").click(function() {
          const total = jQuery(".selected").length;
          const msg = jQuery("#comment_textarea").val();
          if (total > 0 && msg.length > 0) {
            jQuery("#log_head, #log_body").html("");
            jQuery(".selected").each(function(i) {
              let profileID = this.getAttribute("data-steamid");
              (function(i, profileID) {
                setTimeout(function() {
                  jQuery.post("//steamcommunity.com/comment/Profile/post/" + profileID + "/-1/", { comment: msg, count: 6, sessionid: g_sessionID }, function(response) {
                    if (response.success === false) {
                      jQuery("#log_body")[0].innerHTML += "<br>" + response.error;
                    } else {
                      jQuery("#log_body")[0].innerHTML += "<br>Successfully posted comment on <a href=\\"http://steamcommunity.com/profiles/" + profileID + "\\">" + profileID + "</a>";
                    }
                  }).fail(function() {
                    jQuery("#log_body")[0].innerHTML += "<br>Failed to post comment on <a href=\\"http://steamcommunity.com/profiles/" + profileID + "\\">" + profileID + "</a>";
                  }).always(function() {
                    jQuery("#log_head").html("<br><b>Processed " + (i+1) + " out of " + total + " friends.<b>");
                  });
                }, i * 6000);
              })(i, profileID);
            });
          }
        });
        
        document.querySelector(".responsive_header").remove();
        document.querySelector(".friends_header_bg").remove();
        document.querySelector(".friends_nav").remove();
        document.querySelector(".profile_friends.title_bar").remove();
        document.querySelector(".manage_friends_panel").remove();
        document.querySelector(".commentthread_entry").style.display = "none";
        document.querySelector(".responsive_page_content").style.paddingTop = "0";
        """
        self.webview.run(script)

    def goLogin(self):
        self.window().switchInterface("login")

    def checkLogin(self, info):
        if info.get("status"):
            self.webview.open("https://steamcommunity.com/friends")
            self.webview.show()
            self.webview_banned.hide()
            self.edit_area.setEnabled(True)
            self.select_all_button.setEnabled(True)
            self.inverse_button.setEnabled(True)
            self.send_button.setEnabled(True)
        else:
            self.webview.hide()
            self.webview_banned.show()
            self.edit_area.setEnabled(False)
            self.select_all_button.setEnabled(False)
            self.inverse_button.setEnabled(False)
            self.send_button.setEnabled(False)

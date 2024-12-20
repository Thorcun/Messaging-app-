from tkinter import Tk, Button, Checkbutton, IntVar, Label, Entry, Text, messagebox, Frame, Scrollbar, END, VERTICAL #Tkinter Python Module for GUI  
import socket #Sockets for network connection
import threading # for multiple proccess 

class GUI:
    client_socket = None
    last_received_message = None

    def __init__(self, master):
        self.root = master
        self.chat_transcript_area = None
        self.name_widget = None
        self.enter_text_widget = None
        self.join_button = None
        self.initialize_socket()
        self.initialize_gui()
        self.listen_for_incoming_messages_in_a_thread()

    def initialize_socket(self):
        # Socket initialize işlemi...
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_ip = '127.0.0.1'
        remote_port = 10319
        self.client_socket.connect((remote_ip, remote_port))

    def initialize_gui(self):
        self.root.title("How'u Doin?")
        self.root.resizable(0, 0)
        self.root.geometry("850x600")

        # Arka plan rengini değiştirmek için Frame kullanma
        background_frame = Frame(self.root, width=400, height=650, bg='#e6e6e6')
        background_frame.place(x=0, y=0)

        self.display_chat_box(background_frame)
        self.display_name_section(background_frame)
        self.display_chat_entry_box(background_frame)

    def listen_for_incoming_messages_in_a_thread(self):
        # Thread oluşturma işlemi...
        thread = threading.Thread(target=self.receive_message_from_server, args=(self.client_socket,))
        thread.start()

    def display_user_list(self, users):
        if not hasattr(self, 'user_list_frame'):
            self.user_list_frame = Frame(self.root)
            Label(self.user_list_frame, text='Kullanıcı Listesi:', font=("Serif", 12)).pack(side='top', anchor='w')

            self.user_list_area = Text(self.user_list_frame, width=25, height=10, font=("Serif", 12))
            self.user_list_area.config(state='disabled')
            self.user_list_area.pack(side='left', padx=10, fill='both')

            self.user_list_frame.pack(side='top', anchor='ne', padx=10, pady=10)  # Kullanıcı listesi frame'i sağ üst köşeye yerleştirildi

        else:
            self.user_list_frame.pack_forget()  # Var olan kullanıcı listesi frame'i unutulur
            self.user_list_frame.destroy()  # Var olan frame yok edilir

            self.user_list_frame = Frame(self.root)
            Label(self.user_list_frame, text='Kullanıcı Listesi:', font=("Serif", 12)).pack(side='top', anchor='w')

            self.user_list_area = Text(self.user_list_frame, width=25, height=10, font=("Serif", 12))
            self.user_list_area.config(state='disabled')
            self.user_list_area.pack(side='left', padx=10, fill='both')

            self.user_list_frame.pack(side='top', anchor='ne', padx=10, pady=10)  # Yeniden oluşturulan kullanıcı listesi frame'i sağ üst köşeye yerleştirilir

        user_list_text = "\n".join(users)
        self.user_list_area.config(state='normal')
        self.user_list_area.delete(1.0, 'end')
        self.user_list_area.insert('end', user_list_text)
        self.user_list_area.config(state='disabled')


    

    def receive_message_from_server(self, so):
        self.users = []  # Kullanıcı listesini saklamak için sınıf düzeyinde bir değişken oluşturuldu

        while True:
            buffer = so.recv(256)
            if not buffer:
                break
            message = buffer.decode('utf-8')

            if "joined" in message:
                user = message.split(":")[1]
                message = user + " sohbete katıldı."
                self.chat_transcript_area.insert('end', message + '\n')
                self.chat_transcript_area.yview(END)
                self.users.append(user)  # Kullanıcıyı listeye ekle
                self.display_user_list(self.users)
            elif "left" in message:
                user = message.split(":")[1]
                message = user + " sohbetten ayrıldı."
                self.chat_transcript_area.insert('end', message + '\n')
                self.chat_transcript_area.yview(END)
                self.remove_user_from_list(user)  # Kullanıcıyı listeden çıkar
            else:
                self.chat_transcript_area.insert('end', message + '\n')
                self.chat_transcript_area.yview(END)

        so.close()

    def display_name_section(self, parent):
        frame = Frame(parent)
        Label(frame, text='İsminizi Giriniz:', font=("Helvetica", 12)).pack(side='left', padx=10)
        self.name_widget = Entry(frame, width=35, borderwidth=2)
        self.name_widget.pack(side='left', anchor='e')
        self.join_button = Button(frame, text="Katıl", width=10, command=self.on_join).pack(side='left')
        frame.pack(side='top', anchor='nw')

    def display_chat_box(self, parent):
        frame = Frame(parent)
        Label(frame, text='Mesajlar:', font=("Serif", 12)).pack(side='top', anchor='w')
        self.chat_transcript_area = Text(frame, width=60, height=15, font=("Serif", 12))
        scrollbar = Scrollbar(frame, command=self.chat_transcript_area.yview, orient=VERTICAL)
        self.chat_transcript_area.config(yscrollcommand=scrollbar.set)
        self.chat_transcript_area.bind('<KeyPress>', lambda e: 'break')
        self.chat_transcript_area.pack(side='left', padx=10)
        scrollbar.pack(side='right', fill='y')
        frame.pack(side='top')
    
    def remove_user_from_list(self, username):
        if username in self.users:
            self.users.remove(username)
            self.display_user_list(self.users)
    

    def display_chat_entry_box(self, parent):
        frame = Frame(parent)
        Label(frame, text='Mesajınızı Giriniz:', font=("Serif", 12)).pack(side='top', anchor='w')
        self.enter_text_widget = Text(frame, width=60, height=20, font=("Serif", 12))
        self.enter_text_widget.pack(side='left', pady=15)
        self.enter_text_widget.bind('<Return>', self.on_enter_key_pressed)
        frame.pack(side='top')

    def on_join(self):
        # Katılma işlemi...
        if len(self.name_widget.get()) == 0:
            messagebox.showerror("İsmini Gir", "Mesaj göndermek için isminizi giriniz.")
            return

        # Bağlandığınızda kullanıcı adınızı belirleyin
        self.username = self.name_widget.get().strip()

        # Kullanıcı adını listeye ekle
        if self.username not in self.users:
            self.users.append("Siz")  # sınıf düzeyindeki kullanıcı listesine ekle
        
        self.name_widget.config(state='disabled')
        self.client_socket.send(("joined:" + self.name_widget.get()).encode('utf-8'))
        message = "Bağlandınız!"
        self.chat_transcript_area.insert('end', message + '\n')
        self.chat_transcript_area.yview(END)
        self.display_user_list(self.users)  # Kullanıcı listesini güncelle
        self.join_button.config(state='disabled')



    def on_enter_key_pressed(self, event):
        # Enter tuşuna basılınca işlem...
        if len(self.name_widget.get()) == 0:
            messagebox.showerror("İsmini Gir", "Mesaj göndermek için isminizi giriniz.")
            return
        self.send_chat()
        self.clear_text()

    def clear_text(self):
        # Metin temizleme işlemi...
        self.enter_text_widget.delete(1.0, 'end')

    def send_chat(self):
        # Mesaj gönderme işlemi...
        senders_name = self.name_widget.get().strip() + ": "
        data = self.enter_text_widget.get(1.0, 'end').strip()
        message = (senders_name + data).encode('utf-8')
        self.chat_transcript_area.insert('end', message.decode('utf-8') + '\n')
        self.chat_transcript_area.yview(END)
        self.client_socket.send(message)
        self.enter_text_widget.delete(1.0, 'end')
        return 'break'

    def on_close_window(self):
        if messagebox.askokcancel("Çık", "Çıkmak mı istiyorsunuz?"):
            self.client_socket.send(("left:" + self.username).encode('utf-8'))  # Kullanıcıyı ayrıldı olarak işaretle
            self.root.destroy()
            self.client_socket.close()
            exit(0)

    def create_new_group(self):
        # Yeni bir pencere oluştur
        self.group_window = Tk()
        self.group_window.title("Yeni Grup Oluştur")
        self.group_window.geometry("300x400")

        self.selected_users = []  # Seçilen kullanıcıları saklamak için liste

        for user in self.users:
            var = IntVar()
            Checkbutton(self.group_window, text=user, variable=var, onvalue=1, offvalue=0).pack(anchor='w')
            self.selected_users.append((user, var))

        # Grup oluşturma butonu
        Button(self.group_window, text="Oluştur", width=10, command=self.create_group_chat).pack()


    def create_group_chat(self):
        # Seçilen kullanıcıları al
        selected_indices = self.group_user_list_area.curselection()
        for index in selected_indices:
            self.selected_users.append(self.group_user_list_area.get(index))

        # Eğer seçili kullanıcı yoksa uyarı ver ve işlemi sonlandır
        if not self.selected_users:
            messagebox.showerror("Hata", "Lütfen kullanıcı seçiniz.")
            return

        # Yeni grup sohbet penceresini aç
        self.new_group_chat_window = Tk()
        self.new_group_chat_window.title("Yeni Grup Sohbeti")
        self.new_group_chat_window.geometry("850x600")

        # Arayüzü initialize et
        background_frame = Frame(self.new_group_chat_window, width=400, height=650, bg='#e6e6e6')
        background_frame.place(x=0, y=0)

        # Yeni sohbet alanını göster
        self.display_chat_box(background_frame)
        self.display_chat_entry_box(background_frame)

        # Sadece seçilen kullanıcıların sohbet edebileceği bir mesaj gönder
        self.client_socket.send(f"new_group:{','.join(self.selected_users)}".encode('utf-8'))

        # Pencere kapatılınca socket'i kapat ve çık
        self.new_group_chat_window.protocol("WM_DELETE_WINDOW", self.on_close_group_window)

    def on_close_group_window(self):
        if messagebox.askokcancel("Çık", "Yeni grup sohbetinden çıkmak istiyor musunuz?"):
            self.new_group_chat_window.destroy()

    def display_name_section(self, parent):
        frame = Frame(parent)
        Label(frame, text='İsminizi Giriniz:', font=("Helvetica", 12)).pack(side='left', padx=10)
        self.name_widget = Entry(frame, width=35, borderwidth=2)
        self.name_widget.pack(side='left', anchor='e')
        
        # Yeni grup oluşturma butonu
        Button(frame, text="Yeni Grup Kur", width=15, command=self.create_new_group).pack(side='left', padx=10)
        self.join_button = Button(frame, text="Katıl", width=10, command=self.on_join).pack(side='left')
        frame.pack(side='top', anchor='nw')

if __name__ == '__main__':
    root = Tk()
    gui = GUI(root)
    root.protocol("WM_DELETE_WINDOW", gui.on_close_window)
    root.mainloop()



import tkinter as tk
from tkinter import scrolledtext, messagebox
import pika
import threading

class ChatApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Application")
        self.root.geometry("400x300")

        self.message_area = scrolledtext.ScrolledText(root, height=15, width=40)
        self.message_area.pack(padx=10, pady=10)

        self.entry_field = tk.Entry(root, width=40)
        self.entry_field.pack(padx=10, pady=5)

        self.send_button = tk.Button(root, text="Send", command=self.send_message)
        self.send_button.pack(padx=10, pady=5)

        self.connect()

    def connect(self):
        try:
            # Connection for publishing
            self.pub_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            self.pub_channel = self.pub_connection.channel()
            self.pub_channel.queue_declare(queue='chat_queue')

            # Connection for consuming
            self.sub_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            self.sub_channel = self.sub_connection.channel()
            self.sub_channel.queue_declare(queue='chat_queue')

            self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
            self.receive_thread.start()

        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def send_message(self):
        message = self.entry_field.get()
        if message and hasattr(self, 'pub_channel'):
            self.pub_channel.basic_publish(exchange='',
                                           routing_key='chat_queue',
                                           body=message)
            self.message_area.insert(tk.END, "Me: " + message + "\n")
            self.entry_field.delete(0, tk.END)

    def receive_messages(self):
        def callback(ch, method, properties, body):
            message = body.decode()
            self.message_area.insert(tk.END, "Student 2: " + message + "\n")
            self.message_area.see(tk.END)

        self.sub_channel.basic_consume(queue='chat_queue',
                                       on_message_callback=callback,
                                       auto_ack=True)
        try:
            self.sub_channel.start_consuming()
        except pika.exceptions.ConnectionClosedByBroker:
            pass
        except Exception as e:
            print("Error in consuming messages:", e)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApplication(root)
    root.mainloop()

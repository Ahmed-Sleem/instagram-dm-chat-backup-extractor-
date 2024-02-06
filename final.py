import json
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from datetime import datetime
import csv
import os

def decode_text(text):
    if isinstance(text, (bool, int)):
        return str(text)
    try:
        return text.encode('latin1').decode('utf-8')
    except UnicodeDecodeError:
        return text

def format_data(data):
    formatted_data = []

    for message in data["messages"]:
        timestamp_ms = message["timestamp_ms"]
        timestamp_utc = datetime.utcfromtimestamp(timestamp_ms / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + " UTC"

        row = [
            timestamp_utc,
            decode_text(data["participants"][0]["name"]),
            message["timestamp_ms"],
            decode_text(message["sender_name"]),
            decode_text(message.get("content", "")),
            decode_text(message.get("reactions", [{}])[0].get("reaction", "")),
            decode_text(message.get("reactions", [{}])[0].get("actor", "")),
            decode_text(message.get("share", {}).get("link", "")),
            decode_text(message.get("share", {}).get("profile_share_username", "")),
            decode_text(message.get("share", {}).get("profile_share_name", "")),
            decode_text(message.get("share", {}).get("share_text", "")),
            decode_text(message.get("share", {}).get("original_content_owner", "")),
            decode_text(message.get("is_geoblocked_for_viewer", "")),
            decode_text(data.get("title", "")),
            decode_text(data.get("is_still_participant", "")),
            decode_text(data.get("thread_path", "")),
            decode_text(data.get("joinable_mode", {}).get("mode", "")),
            decode_text(data.get("joinable_mode", {}).get("link", "")),
            decode_text(message.get("photos", [{}])[0].get("uri", "")),
            decode_text(message.get("photos", [{}])[0].get("creation_timestamp", ""))
        ]

        formatted_data.append(row)

    return formatted_data

class InstagramBackupDecoderGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Instagram Backup Decoder")
        self.file_path = None
        self.chat_folder = None
        self.sort_order_var = tk.IntVar()  # 0 for ascending, 1 for descending

        # Configure style
        style = ttk.Style()
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TButton", background="#4caf50", foreground="black")
        style.configure("TLabel", background="#f0f0f0", foreground="#333")
        style.configure("TCombobox", background="white", foreground="#333")
        style.configure("TEntry", background="white", foreground="#333")
        style.configure("TText", background="white", foreground="#333")

        # Main Frame
        self.main_frame = ttk.Frame(self.master, style="TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Left Frame
        self.left_frame = ttk.Frame(self.main_frame, style="TFrame")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Text Widget for Preview
        self.preview_text = tk.Text(self.left_frame, wrap=tk.WORD, height=20, width=50, state=tk.DISABLED, bd=2, relief=tk.SOLID)
        self.preview_text.pack(pady=10)

        # Status Label for Preview
        self.preview_status_label = ttk.Label(self.left_frame, text="")
        self.preview_status_label.pack(pady=5)

        # Right Frame
        self.right_frame = ttk.Frame(self.main_frame, style="TFrame")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Load button
        self.load_button = ttk.Button(self.right_frame, text="Load Backup Folder", command=self.load_backup_folder)
        self.load_button.pack(pady=10)

        # Dropdown for chat folders
        self.chat_folders_label = ttk.Label(self.right_frame, text="Select Chat Folder:")
        self.chat_folders_label.pack()
        self.chat_folders_var = tk.StringVar()
        self.chat_folders_dropdown = ttk.Combobox(self.right_frame, textvariable=self.chat_folders_var, state="disabled")
        self.chat_folders_dropdown.pack(pady=10)

        # Preview button
        self.preview_button = ttk.Button(self.right_frame, text="Preview", command=self.preview)
        self.preview_button.pack(pady=10)

        # Output file name entry
        self.output_label = ttk.Label(self.right_frame, text="Output File Name:")
        self.output_label.pack()
        self.output_var = tk.StringVar()
        self.output_entry = ttk.Entry(self.right_frame, textvariable=self.output_var)
        self.output_entry.pack(pady=10)

        # Ascending checkbox
        self.ascending_checkbox = ttk.Checkbutton(self.right_frame, text="Ascending Order",
                                                  variable=self.sort_order_var, onvalue=0, offvalue=0)
        self.ascending_checkbox.pack()

        # Descending checkbox
        self.descending_checkbox = ttk.Checkbutton(self.right_frame, text="Descending Order",
                                                   variable=self.sort_order_var, onvalue=1, offvalue=0)
        self.descending_checkbox.pack()

        # Save button
        self.save_button = ttk.Button(self.right_frame, text="Save to CSV", command=self.save_to_csv)
        self.save_button.pack(pady=10)

        # Status Label for Save
        self.save_status_label = ttk.Label(self.right_frame, text="")
        self.save_status_label.pack(pady=5)

    def load_backup_folder(self):
        self.file_path = filedialog.askdirectory(title="Select Backup Folder")
        if self.file_path:
            inbox_folder_path = f"{self.file_path}/your_instagram_activity/messages/inbox"
            chat_folders = [folder for folder in os.listdir(inbox_folder_path) if os.path.isdir(os.path.join(inbox_folder_path, folder))]
            self.chat_folders_dropdown["values"] = chat_folders
            self.chat_folders_dropdown["state"] = "readonly"

    def preview(self):
        if self.file_path and self.chat_folders_var.get():
            chat_folder_path = f"{self.file_path}/your_instagram_activity/messages/inbox/{self.chat_folders_var.get()}"
            json_file_path = f"{chat_folder_path}/message_1.json"

            try:
                with open(json_file_path, 'r', encoding='utf-8') as file:
                    json_data = json.load(file)
                formatted_data = format_data(json_data)

                # Display the formatted data in the preview text widget
                preview_text = ""
                sort_order = "asc" if self.sort_order_var.get() == 0 else "desc"
                formatted_data.sort(key=lambda x: x[0], reverse=(sort_order == "desc"))
                for row in formatted_data[:5]:
                    preview_text += '\t'.join(map(str, row)) + '\n'

                self.preview_text.config(state=tk.NORMAL)
                self.preview_text.delete("1.0", tk.END)
                self.preview_text.insert(tk.END, preview_text)
                self.preview_text.config(state=tk.DISABLED)

                self.preview_status_label["text"] = "Preview successful."

            except FileNotFoundError:
                self.preview_status_label["text"] = f"File not found at path: {json_file_path}"
            except json.JSONDecodeError:
                self.preview_status_label["text"] = f"Invalid JSON file at path: {json_file_path}"
            except Exception as e:
                self.preview_status_label["text"] = f"An error occurred: {str(e)}"
        else:
            self.preview_status_label["text"] = "Please select a backup folder and chat folder."

    def save_to_csv(self):
        if self.file_path and self.chat_folders_var.get() and self.output_var.get():
            chat_folder_path = f"{self.file_path}/your_instagram_activity/messages/inbox/{self.chat_folders_var.get()}"
            json_file_path = f"{chat_folder_path}/message_1.json"
            output_file_path = f"{self.output_var.get()}.csv"

            try:
                with open(json_file_path, 'r', encoding='utf-8') as file:
                    json_data = json.load(file)
                formatted_data = format_data(json_data)

                # Sort data based on timestamp
                sort_order = "asc" if self.sort_order_var.get() == 0 else "desc"
                formatted_data.sort(key=lambda x: x[0], reverse=(sort_order == "desc"))

                # Save to CSV
                with open(output_file_path, 'w', newline='', encoding='utf-8') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    # Add headers
                    headers = ["Timestamp_UTC", "Participant_Name", "Timestamp_ms", "Sender_Name", "Content",
                               "Reaction", "Reaction_Actor", "Share_Link", "Share_Profile_Username",
                               "Share_Profile_Name", "Share_Text", "Original_Content_Owner", "Is_Geoblocked",
                               "Title", "Is_Still_Participant", "Thread_Path", "Joinable_Mode", "Joinable_Mode_Link",
                               "Photo_URI", "Photo_Creation_Timestamp"]
                    csv_writer.writerow(headers)
                    csv_writer.writerows(formatted_data)

                self.save_status_label["text"] = f"Data saved to: {output_file_path}"

            except FileNotFoundError:
                self.save_status_label["text"] = f"File not found at path: {json_file_path}"
            except json.JSONDecodeError:
                self.save_status_label["text"] = f"Invalid JSON file at path: {json_file_path}"
            except Exception as e:
                self.save_status_label["text"] = f"An error occurred: {str(e)}"
        else:
            self.save_status_label["text"] = "Please select a backup folder, chat folder, and enter an output file name."

if __name__ == "__main__":
    root = tk.Tk()
    app = InstagramBackupDecoderGUI(root)
    root.mainloop()

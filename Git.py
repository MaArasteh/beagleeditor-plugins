import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from git import Repo, GitCommandError, InvalidGitRepositoryError

class GitApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Git Integration for BeagleEditor')
        self.geometry('800x800')
        self.repo = None
        self.initUI()

    def initUI(self):
        self.repo_path_label = tk.Label(self, text='Repository Path:')
        self.repo_path_label.pack()

        self.repo_path_input = tk.Entry(self)
        self.repo_path_input.pack()
        self.repo_path_input.bind("<KeyRelease>", lambda event: self.open_repo())

        self.repo_check_button = tk.Button(self, text="Check Status")
        self.repo_check_button.pack()

        self.select_directory_btn = tk.Button(self, text='Select Directory', command=self.get_directory)
        self.select_directory_btn.pack()

        self.init_repo_button = tk.Button(self, text='Initialize Repository', command=self.init_repo)
        self.init_repo_button.pack()

        self.repo_path_label = tk.Label(self, text='Files that should be added')
        self.repo_path_label.pack()

        self.file_path_input = tk.Entry(self)
        self.file_path_input.pack()

        self.add_all_files_btn = tk.Button(self, text="Add All Files", command=self.add_all_files)
        self.add_all_files_btn.pack()

        self.add_file_button = tk.Button(self, text='Add File', command=self.add_file)
        self.add_file_button.pack()
        self.add_file_button.config(state=tk.DISABLED)

        self.repo_path_label = tk.Label(self, text='Commit message')
        self.repo_path_label.pack()

        self.commit_message_input = tk.Entry(self)
        self.commit_message_input.pack()

        self.commit_button = tk.Button(self, text='Commit', command=self.commit)
        self.commit_button.pack()
        self.commit_button.config(state=tk.DISABLED)

        self.repo_path_label = tk.Label(self, text="GitHub username: (It remains private. It won't be shared to anyone")
        self.repo_path_label.pack()

        self.github_username_input = tk.Entry(self)
        self.github_username_input.pack()

        self.push_button = tk.Button(self, text='Push', command=self.push)
        self.push_button.pack()

        self.status_output = scrolledtext.ScrolledText(self)
        self.status_output.pack()

    def get_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.repo_path_input.delete(0, tk.END)
            self.repo_path_input.insert(0, directory)

    def init_repo(self):
        repo_path = self.repo_path_input.get()
        try:
            self.repo = Repo.init(repo_path)
            self.status_output.insert(tk.END, f"Initialized empty Git repository in {repo_path}\n")
            self.commit_button.config(state=tk.NORMAL)
            self.add_file_button.config(state=tk.NORMAL)
            self.init_repo_button.config(state=tk.DISABLED)
        except GitCommandError as e:
            self.status_output.insert(tk.END, f"Error: {e}\n")

    def add_file(self):
        if self.repo is None:
            self.status_output.insert(tk.END, "Repository is not initialized.\n")
            return

        file_path = self.file_path_input.get()
        try:
            self.repo.index.add([file_path])
            self.repo.index.write()
            self.status_output.insert(tk.END, f"Added {file_path} to the staging area.\n")
        except Exception as e:
            self.status_output.insert(tk.END, f"Error: {e}\n")

    def add_all_files(self):
        if self.repo is None:
            self.status_output.insert(tk.END, "Repository is not initialized.\n")
            return

        file_path = self.file_path_input.get()
        try:
            self.repo.git.add(all=True)
            self.repo.index.write()
            self.status_output.insert(tk.END, f"Added all files to the staging area.\n")
        except Exception as e:
            self.status_output.insert(tk.END, f"Error: {e}\n")

    def commit(self):
        if self.repo is None:
            self.status_output.insert(tk.END, "Repository is not initialized.\n")
            return

        commit_message = self.commit_message_input.get()
        try:
            self.repo.index.commit(commit_message)
            self.status_output.insert(tk.END, f"Committed with message: {commit_message}\n")
        except Exception as e:
            self.status_output.insert(tk.END, f"Error: {e}\n")

    def push(self):
        if self.repo is None:
            self.status_output.insert(tk.END, "Repository is not initialized.\n")
            return
        try:
            self.status_output.insert(tk.END, "Trying to push\n")
            github_username = self.github_username_input.get()
            repo_name = os.path.basename(os.path.normpath(self.repo_path_input.get()))
            remote_url = f'https://github.com/{github_username}/{repo_name}.git'
            if 'origin' not in [remote.name for remote in self.repo.remotes]:
                self.repo.create_remote('origin', remote_url)
            else:
                self.repo.remotes.origin.set_url(remote_url)
            # Push the changes to the remote repository
            origin = self.repo.remote(name='origin')
            try:
                origin.push()
            except Exception as e:
                if 'exit code(128)' in str(e) and 'has no upstream branch' in str(e):
                    # Set the upstream branch if it's not set
                    origin.push(refspec='HEAD:refs/heads/master', set_upstream=True)
                else:
                    raise
            self.status_output.insert(tk.END, "Pushed successfully! Now available on GitHub.\n")
        except GitCommandError as e:
            self.status_output.insert(tk.END, f"GitCommandError: {e}\n")
        except Exception as e:
            self.status_output.insert(tk.END, f"Error: {e}\n")

    def open_repo(self):
        try:
            self.repo = Repo(self.repo_path_input.get())
            self.show_status()
        except InvalidGitRepositoryError:
            self.show_status()

    def show_status(self):
        if self.repo is None:
            self.status_output.insert(tk.END, "Repository is not initialized.\n")
            self.init_repo_button.config(state=tk.NORMAL)
            return
        try:
            status = self.repo.git.status()
            self.status_output.insert(tk.END, status + "\n")
            self.commit_button.config(state=tk.NORMAL)
            self.add_file_button.config(state=tk.NORMAL)
            self.init_repo_button.config(state=(tk.DISABLED))
        except Exception as e:
            self.status_output.insert(tk.END, f"Error: {e}\n")

def run_from_beagleeditor():
    app = GitApp()
    app.mainloop()

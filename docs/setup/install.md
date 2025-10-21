# Installation Guide

## Windows (tested)

1. **Install Docker Desktop**  
   - Download and install [Docker Desktop](https://www.docker.com/get-started/) for Windows.  
   - Docker Desktop requires **WSL2**.  
   - Follow the installer instructions to enable WSL2 if it is not already installed.

2. **Install WSL2 (if not already installed)**  
   - Open PowerShell as Administrator and run:
     ```powershell
     wsl --install
     ```
   - Reboot your system if prompted.  
   - Ensure you have a Linux distribution installed (Ubuntu is recommended).

3. **Verify installations**
   ```powershell
   docker --version
   wsl --list --verbose
   ```

4. **Install VS Code**
   - Download and install [VS Code](https://code.visualstudio.com/download)

5. **Install Extension**
   - Install Dev Containers (ms-vscode-remote.remote-containers)

## Linux (not tested)

1. **Install Docker**
    ```bash
    sudo apt update
    sudo apt install apt-transport-https ca-certificates curl software-properties-common -y
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt update
    sudo apt install docker-ce docker-ce-cli containerd.io -y
    sudo systemctl start docker
    sudo systemctl enable docker
    docker --version

    ```

2. **Optional: Allow running Docker without sudo**
    ```bash
    sudo usermod -aG docker $USER
    newgrp docker
    ```

3. **Verify Docker**
    ```bash
    docker run hello-world
    ```

4. **Install VS Code**
   - Download and install [VS Code](https://code.visualstudio.com/download)
  
5. **Install Extension**
   - Install Dev Containers (ms-vscode-remote.remote-containers)
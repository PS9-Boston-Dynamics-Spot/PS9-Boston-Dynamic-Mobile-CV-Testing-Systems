# Installation Guide

## Windows (tested)

1. **Install Python**  
   - Download and install [Python](https://www.python.org/downloads/) from the official website.  
   - Make sure to check **"Add Python to PATH"** during installation.

2. **Install Docker Desktop**  
   - Download and install [Docker Desktop](https://www.docker.com/get-started/) for Windows.  
   - Docker Desktop requires **WSL2**.  
   - Follow the installer instructions to enable WSL2 if it is not already installed.

3. **Install WSL2 (if not already installed)**  
   - Open PowerShell as Administrator and run:
     ```powershell
     wsl --install
     ```
   - Reboot your system if prompted.  
   - Ensure you have a Linux distribution installed (Ubuntu is recommended).

4. **Verify installations**
   ```powershell
   python --version
   docker --version
   wsl --list --verbose
   ```

5. **Install VS Code**
   - Download and install [VS Code](https://code.visualstudio.com/download)

6. **Install Extensions**
   - Dev Containers
   - Docker
   - Python
   - Pylance
   - Remote - SSH

## Linux (not tested)
1. **Install Python**
    Most distributions already have Python installed.

    ```bash
    sudo apt update
    sudo apt install python3 python3-pip -y
    python3 --version
    ```
2. **Install Docker**
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

3. **Optional: Allow running Docker without sudo**
    ```bash
    sudo usermod -aG docker $USER
    newgrp docker
    ```

4. **Verify Python and Docker**
    ```bash
    python3 --version
    docker run hello-world
    ```

5. **Install VS Code**
   - Download and install [VS Code](https://code.visualstudio.com/download)

6. **Install Extensions**
   - Dev Containers
   - Docker
   - Python
   - Pylance
   - Remote - SSH

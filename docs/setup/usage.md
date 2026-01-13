# Initial Setup

## Start Container

1. Press F1 and select **"Dev Containers: Reopen in Container"**
2. Wait for the container to build and start (first time may take a few minutes)

**Your bottom bar should include a similar element**

![./image.png](image.png)

## Configure Python Interpreter
After the container is running:
1. Open a terminal in VS Code
2. Run `which python` to check the current Python interpreter
3. **If the output is NOT** `/workspaces/PS9-Boston-Dynamic-Mobile-CV-Testing-Systems/.venv/bin/python`
    - Press F1
    - Select **"Python: Select Interpreter"**
    - Choose `./.venv/bin/python` from the list

## Verify Setup
Confirm everything is working:
```bash
which python
# Should show: /workspaces/PS9-Boston-Dynamic-Mobile-CV-Testing-Systems/.venv/bin/python

make qa-check
# Should run your quality checks
```

## Troubleshooting
- If Python features don't work, reload VS Code: **F1 → "Developer: Reload Window"**
- To rebuild the container: **F1 → "Dev Containers: Rebuild Container"**
---

## Development Commands

### Environment Management

| Command                                  | Description                               |
|------------------------------------------|-------------------------------------------|
| ```make create-venv```                   | Create Python virtual environment         |
| ```make use-venv```                      | Activate virtual environment in new shell |
| ```make check-venv-using```              | Check if virtual environment is active    |
| ```make install```                       | Install project dependencies              |

### Code Quality & Testing
| Command                                  | Description                                    |
|------------------------------------------|------------------------------------------------|
| ```make test```                          | Run all tests with pytest                      |
| ```make fix```                           | Run code quality checks (ruff, Black)          |
| ```make qa-check```                      | Run format + lint + tests (full quality check) |

### Maintenance
| Command                                  | Description                                    |
|------------------------------------------|------------------------------------------------|
| ```make clean```                         | Remove cache and temporary files               |
| ```make help```                          | Show all available commands                    |

---

## Daily Development Workflow

**Run App**

```bash
make run
```

**Before committing code**
```bash
make qa-check
```

**Installing new dependencies**
1. Add package to requirements.txt
2. Run:
```bash
make install
```

**Running tests only**
```bash
make test
```

---

## Verify Everything Works

```bash
# Check which Python is being used
which python # Expected output: /workspaces/PS9-Boston-Dynamic-Mobile-CV-Testing-Systems/.venv/bin/python

# OR check if the virtual environment is active
make check-venv-using # Expected output: Virtual environment is active.

# Run the App
make run
```
---

## Troubleshooting

### Virtual Environment Issues
+ **Not activated:** Run `make use-venv`
+ **Check status:** Run `make check-venv-using`
+ **Recreate:** Delete `.venv` folder and run `make create-venv`

### Dependency Issues
```bash
make clean
make install
```

### Test Failures
+ Run `make test` to see detailed failure information
+ Check test files in `tests/` directory
--- 

## Best Practices
+ Always work in the virtual environment (your prompt should show)
+ Run `make qa-check` before committing
+ Add new dependencies to `requirements.txt`
+ Use `make format` to maintain consistent code style

# Accessing MinIO Console in Browser from Windows

To access MinIO's web interface when running in WSL, you need to find your WSL network adapter's IP address:

## Steps

1. Open Command Prompt or PowerShell
2. Run the `ipconfig` command
3. Look for an adapter named similar to:
   - `Ethernet adapter vEthernet (WSL (Hyper-V firewall))`
   - `Ethernet adapter vEthernet (WSL)`
4. Note the **IPv4 Address** shown for this adapter
5. Open your browser and navigate to: `http://<IP_ADDRESS>:9001`

## Example
```
Ethernet adapter vEthernet (WSL (Hyper-V firewall)):

   Connection-specific DNS Suffix  . :
   Link-local IPv6 Address . . . . . : fe80::d03:a45f:1997:bb8f%52
   IPv4 Address. . . . . . . . . . . : 172.20.80.1
   Subnet Mask . . . . . . . . . . . : 255.255.240.0
   Default Gateway . . . . . . . . . :
```

In this example, you would access MinIO at: `http://172.20.80.1:9001`

## Troubleshooting

- If you cannot find the WSL adapter, ensure WSL 2 is running
- The IP address may change after system restarts
- Ensure MinIO is running and bound to `0.0.0.0` or the WSL IP address

# Using OPC UA Interfaces

The OPC UA interfaces are only accessible via the internal network. To establish a connection, the physical device (e.g. a laptop) must be connected to the network via LAN. After that, the network has to be configured accordingly (further details can be provided by the project supervisor).

This network may use different IP addresses, which are defined administratively in advance. These IP addresses correspond to the networks of the respective OPC UA nodes.

The network configuration is as follows:

- Network Mask: 255.255.255.0  
- Gateway: 192.168.110.254  

Accordingly, the PLC system is reachable at the address **192.168.2.1**.

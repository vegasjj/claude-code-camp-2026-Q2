#!/usr/bin/env python3
import subprocess
import time
import sys
import select
import re
import argparse

class MudClient:
    def __init__(self, host="localhost", port=4000, debug=False):
        self.host = host
        self.port = port
        self.debug = debug
        self.proc = None
        self.ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    def log(self, *args):
        if self.debug:
            print("[DEBUG]", *args, file=sys.stderr)

    def clean_text(self, b_data):
        # 1. Filter out telnet options starting with 0xFF (IAC)
        res = []
        i = 0
        while i < len(b_data):
            if b_data[i] == 255: # IAC
                if i + 1 < len(b_data):
                    cmd = b_data[i+1]
                    if cmd in (251, 252, 253, 254): # WILL, WONT, DO, DONT
                        i += 3
                    else:
                        i += 2
                else:
                    i += 1
            else:
                res.append(b_data[i])
                i += 1
        
        # 2. Decode as latin1 (safe for any byte values)
        text = bytes(res).decode('latin1')
        
        # 3. Strip ANSI escape sequences
        clean = self.ansi_escape.sub('', text)
        return clean

    def connect(self):
        self.log(f"Connecting to {self.host}:{self.port} using nc...")
        self.proc = subprocess.Popen(
            ['nc', self.host, str(self.port)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0
        )

    def read_until(self, expected_suffixes, timeout=5.0):
        """
        Reads from stdout until the cleaned buffer ends with one of the expected_suffixes,
        or a regex matches, or timeout is reached.
        """
        buffer = b""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            r, w, x = select.select([self.proc.stdout], [], [], 0.1)
            if r:
                data = self.proc.stdout.read(4096)
                if not data:
                    self.log("EOF reached on stdout")
                    break
                buffer += data
                
                # Clean and check
                clean = self.clean_text(buffer)
                
                # Check for suffix matches
                for suffix in expected_suffixes:
                    if isinstance(suffix, str):
                        if clean.endswith(suffix):
                            return clean
                    elif isinstance(suffix, re.Pattern):
                        if suffix.search(clean):
                            return clean
            else:
                # No data ready. If we have some data, check if it matches a prompt pattern
                # to avoid waiting for the full timeout.
                clean = self.clean_text(buffer)
                if clean:
                    for suffix in expected_suffixes:
                        if isinstance(suffix, str) and clean.endswith(suffix):
                            return clean
                        elif isinstance(suffix, re.Pattern) and suffix.search(clean):
                            return clean
                            
        clean = self.clean_text(buffer)
        self.log("Timeout or EOF. Returning partial buffer.")
        return clean

    def send(self, cmd):
        self.log(f"Sending: {repr(cmd)}")
        self.proc.stdin.write(cmd.encode('latin1') + b'\n')
        self.proc.stdin.flush()

    def login(self, username="dummy", password="helloworld"):
        # 1. Wait for connect detection screen
        self.read_until(["Attempting to Detect Client, Please Wait...\r\n"], timeout=2.0)
        
        # 2. Bypass client detection by sending newline
        self.send("")
        
        # 3. Wait for "By what name do you wish to be known? "
        self.read_until(["By what name do you wish to be known? "], timeout=3.0)
        
        # 4. Send username
        self.send(username)
        
        # 5. Wait for password prompt
        self.read_until(["Password: "], timeout=3.0)
        
        # 6. Send password
        self.send(password)
        
        # 7. Wait for "PRESS RETURN"
        self.read_until(["*** PRESS RETURN: "], timeout=5.0)
        self.send("")
        
        # 8. Wait for menu and select "1" to enter game
        self.read_until(["   Make your choice: "], timeout=5.0)
        self.send("1")
        
        # 9. Wait for game prompt. The game prompt ends with "> " or contains health info
        prompt_pat = re.compile(r'\d+H \d+M \d+V.*>\s*$')
        welcome_text = self.read_until([prompt_pat], timeout=5.0)
        self.log("Logged in successfully!")
        
        # 10. Turn off color in-game for easier parsing
        self.send("color off")
        self.read_until([prompt_pat], timeout=2.0)
        
        return welcome_text

    def run_command(self, cmd, timeout=3.0):
        """Sends a command and returns the output up to the next prompt."""
        self.send(cmd)
        prompt_pat = re.compile(r'(?:\d+H \d+M \d+V.*>\s*$)|(?:>\s*$)')
        return self.read_until([prompt_pat], timeout=timeout)

    def close(self):
        if self.proc:
            self.proc.terminate()
            self.proc.wait()

def main():
    parser = argparse.ArgumentParser(description="tbaMUD Client CLI using nc")
    parser.add_argument("--host", default="localhost", help="MUD hostname/IP")
    parser.add_argument("--port", type=int, default=4000, help="MUD port")
    parser.add_argument("--username", default="dummy", help="Character username")
    parser.add_argument("--password", default="helloworld", help="Character password")
    parser.add_argument("--cmd", help="Single command to run")
    parser.add_argument("--cmds", help="Comma-separated commands to run")
    parser.add_argument("--interactive", action="store_true", help="Start interactive shell loop")
    parser.add_argument("--debug", action="store_true", help="Print debug logs to stderr")
    
    args = parser.parse_args()
    
    client = MudClient(host=args.host, port=args.port, debug=args.debug)
    try:
        client.connect()
        welcome = client.login(username=args.username, password=args.password)
        
        if args.cmd:
            output = client.run_command(args.cmd)
            print(output)
        elif args.cmds:
            for cmd in args.cmds.split(","):
                cmd = cmd.strip()
                if cmd:
                    print(f"--- Running: {cmd} ---")
                    output = client.run_command(cmd)
                    print(output)
        elif args.interactive:
            print(welcome)
            print("\nMUD Client Connected. Type your commands below. Type 'exit' to quit.\n")
            while True:
                print("MUD_CLIENT_READY>", end="", flush=True)
                line = sys.stdin.readline()
                if not line:
                    break
                cmd = line.strip()
                if cmd.lower() in ('exit', 'quit'):
                    break
                output = client.run_command(cmd)
                print(output, end="", flush=True)
        else:
            # If no command is provided, just print welcome screen and exit
            print(welcome)
            
    except KeyboardInterrupt:
        pass
    finally:
        client.close()

if __name__ == "__main__":
    main()

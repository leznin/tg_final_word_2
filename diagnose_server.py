#!/usr/bin/env python3
"""
Server diagnostics script for finalword.cc
"""

import subprocess
import sys
import os
import requests
import time

def run_command(cmd, description):
    """Run shell command and return result"""
    print(f"\n🔍 {description}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ Success: {result.stdout.strip()}")
            return result.stdout.strip()
        else:
            print(f"❌ Failed: {result.stderr.strip()}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def check_processes():
    """Check running processes"""
    print("\n" + "="*50)
    print("🔍 CHECKING RUNNING PROCESSES")
    print("="*50)

    # Check Docker containers
    run_command("docker ps", "Docker containers")

    # Check Python processes
    run_command("ps aux | grep python", "Python processes")

    # Check uvicorn processes
    run_command("ps aux | grep uvicorn", "Uvicorn processes")

    # Check nginx
    run_command("ps aux | grep nginx", "Nginx processes")

def check_ports():
    """Check listening ports"""
    print("\n" + "="*50)
    print("🔍 CHECKING LISTENING PORTS")
    print("="*50)

    run_command("netstat -tlnp | grep :80", "Port 80 (HTTP)")
    run_command("netstat -tlnp | grep :443", "Port 443 (HTTPS)")
    run_command("netstat -tlnp | grep :8000", "Port 8000 (FastAPI)")

def check_api_endpoints():
    """Check API endpoints"""
    print("\n" + "="*50)
    print("🔍 CHECKING API ENDPOINTS")
    print("="*50)

    base_url = "https://finalword.cc"

    endpoints = [
        "/health",
        "/api/v1/chats/",
        "/api/v1/dashboard/",
        "/api/v1/openrouter/settings"
    ]

    for endpoint in endpoints:
        url = base_url + endpoint
        print(f"\nTesting {url}...")
        try:
            response = requests.get(url, timeout=10)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print(f"Response: {response.text[:200]}...")
            else:
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")

def check_nginx_config():
    """Check nginx configuration"""
    print("\n" + "="*50)
    print("🔍 CHECKING NGINX CONFIGURATION")
    print("="*50)

    run_command("nginx -t", "Nginx config test")
    run_command("cat /etc/nginx/sites-available/default | head -50", "Nginx site config")

def check_docker_logs():
    """Check Docker container logs"""
    print("\n" + "="*50)
    print("🔍 CHECKING DOCKER LOGS")
    print("="*50)

    # Get container names
    containers = run_command("docker ps --format 'table {{.Names}}'", "Get container names")
    if containers:
        for line in containers.split('\n')[1:]:  # Skip header
            if line.strip():
                container_name = line.strip()
                print(f"\nLogs for {container_name}:")
                run_command(f"docker logs --tail 20 {container_name}", f"Last 20 lines of {container_name} logs")

def check_files():
    """Check important files"""
    print("\n" + "="*50)
    print("🔍 CHECKING IMPORTANT FILES")
    print("="*50)

    files_to_check = [
        "/etc/nginx/sites-available/default",
        "/home/app/.env",
        "/home/app/docker-compose.yml",
        "/home/app/Dockerfile"
    ]

    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"\n{file_path} exists:")
            run_command(f"head -20 {file_path}", f"First 20 lines of {file_path}")
        else:
            print(f"\n{file_path} does NOT exist")

def main():
    """Main diagnostics function"""
    print("🚀 SERVER DIAGNOSTICS FOR finalword.cc")
    print("=======================================")

    check_processes()
    check_ports()
    check_api_endpoints()
    check_nginx_config()
    check_docker_logs()
    check_files()

    print("\n" + "="*50)
    print("✅ DIAGNOSTICS COMPLETED")
    print("="*50)

if __name__ == "__main__":
    main()

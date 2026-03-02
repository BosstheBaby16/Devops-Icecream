#!/usr/bin/env python3
"""
==============================================================
Fault Simulation & Observability Script - IceCream App
==============================================================
Uses kubectl to:
1. Monitor pod status, logs, and resource usage
2. Simulate a pod crash and observe recovery
3. Check HPA (autoscaler) status
4. Generate an observability report

Usage:
    python fault_simulation.py --namespace default --app icecream
"""

import subprocess
import argparse
import time
import sys
from datetime import datetime


# -------------------------------------------------------
# Utility: Run kubectl command
# -------------------------------------------------------
def kubectl(args: list[str], capture: bool = True) -> str:
    """Run a kubectl command and return output."""
    cmd = ["kubectl"] + args
    print(f"  $ {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture,
            text=True,
            timeout=30,
        )
        if result.returncode != 0 and result.stderr:
            return f"[ERROR] {result.stderr.strip()}"
        return result.stdout.strip() if capture else ""
    except subprocess.TimeoutExpired:
        return "[ERROR] Command timed out"
    except FileNotFoundError:
        return "[ERROR] kubectl not found. Please install kubectl."


def section(title: str):
    print(f"\n{'=' * 55}")
    print(f"  {title}")
    print(f"{'=' * 55}")


# -------------------------------------------------------
# 1. Pod Status Monitor
# -------------------------------------------------------
def monitor_pods(namespace: str, app: str):
    section("1. POD STATUS")
    output = kubectl(["get", "pods", "-n", namespace, "-l", f"app={app}", "-o", "wide"])
    print(output)


# -------------------------------------------------------
# 2. Pod Logs
# -------------------------------------------------------
def fetch_logs(namespace: str, app: str, lines: int = 50):
    section("2. RECENT POD LOGS (last 50 lines)")
    # Get first pod name
    pod_name = kubectl(
        ["get", "pods", "-n", namespace, "-l", f"app={app}",
         "-o", "jsonpath={.items[0].metadata.name}"]
    )
    if "[ERROR]" in pod_name or not pod_name:
        print("  No pods found.")
        return pod_name

    print(f"  Fetching logs from pod: {pod_name}")
    logs = kubectl(["logs", pod_name, "-n", namespace, f"--tail={lines}"])
    print(logs)
    return pod_name


# -------------------------------------------------------
# 3. Resource Usage
# -------------------------------------------------------
def check_resources(namespace: str, app: str):
    section("3. RESOURCE USAGE (kubectl top)")
    output = kubectl(["top", "pods", "-n", namespace, "-l", f"app={app}"])
    print(output)


# -------------------------------------------------------
# 4. Describe Deployment
# -------------------------------------------------------
def describe_deployment(namespace: str, app: str):
    section("4. DEPLOYMENT DESCRIPTION")
    output = kubectl(["describe", "deployment", f"{app}-deployment", "-n", namespace])
    # Print key sections only to keep output manageable
    for line in output.splitlines():
        if any(key in line for key in [
            "Name:", "Replicas:", "StrategyType:", "RollingUpdate",
            "Image:", "Limits:", "Requests:", "Liveness:", "Readiness:",
            "Events:", "Normal", "Warning"
        ]):
            print(f"  {line}")


# -------------------------------------------------------
# 5. Simulate Pod Crash
# -------------------------------------------------------
def simulate_crash(namespace: str, app: str, pod_name: str):
    section("5. FAULT SIMULATION - CRASH A POD")

    if not pod_name or "[ERROR]" in pod_name:
        print("  No pod available to crash.")
        return

    print(f"\n  [⚡] Deleting pod '{pod_name}' to simulate crash...")
    result = kubectl(["delete", "pod", pod_name, "-n", namespace])
    print(f"  {result}")

    print("\n  [⏳] Waiting 5 seconds for Kubernetes to detect crash...")
    time.sleep(5)

    print("\n  [📋] Pod status immediately after crash:")
    output = kubectl(["get", "pods", "-n", namespace, "-l", f"app={app}", "-o", "wide"])
    print(output)

    print("\n  [⏳] Waiting 15 more seconds for pod recovery...")
    for i in range(15, 0, -1):
        print(f"\r  Recovery check in {i}s...", end="", flush=True)
        time.sleep(1)

    print("\n\n  [✅] Pod status after recovery window:")
    output = kubectl(["get", "pods", "-n", namespace, "-l", f"app={app}", "-o", "wide"])
    print(output)


# -------------------------------------------------------
# 6. Check Restart Count
# -------------------------------------------------------
def check_restart_count(namespace: str, app: str):
    section("6. RESTART COUNTS (Fault Tolerance Check)")
    output = kubectl([
        "get", "pods", "-n", namespace, "-l", f"app={app}",
        "-o", "jsonpath={range .items[*]}{.metadata.name}{'\\t'}{.status.containerStatuses[0].restartCount}{'\\n'}{end}"
    ])
    print("  Pod Name                                  Restarts")
    print("  " + "-" * 50)
    for line in output.splitlines():
        parts = line.split("\t")
        if len(parts) == 2:
            print(f"  {parts[0]:<42} {parts[1]}")


# -------------------------------------------------------
# 7. Autoscaling Evaluation
# -------------------------------------------------------
def check_hpa(namespace: str):
    section("7. HORIZONTAL POD AUTOSCALER (HPA)")
    output = kubectl(["get", "hpa", "-n", namespace])
    if "No resources found" in output or "[ERROR]" in output:
        print("  ℹ️  No HPA configured. Consider adding HPA for production:")
        print("""
  Example HPA manifest:
  ----------------------
  apiVersion: autoscaling/v2
  kind: HorizontalPodAutoscaler
  metadata:
    name: icecream-hpa
  spec:
    scaleTargetRef:
      apiVersion: apps/v1
      kind: Deployment
      name: icecream-deployment
    minReplicas: 2
    maxReplicas: 10
    metrics:
      - type: Resource
        resource:
          name: cpu
          target:
            type: Utilization
            averageUtilization: 70
        """)
    else:
        print(output)


# -------------------------------------------------------
# 8. Service Check
# -------------------------------------------------------
def check_service(namespace: str, app: str):
    section("8. SERVICE STATUS")
    output = kubectl(["get", "service", f"{app}-service", "-n", namespace, "-o", "wide"])
    print(output)


# -------------------------------------------------------
# Main Orchestration
# -------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Fault simulation and observability for IceCream app")
    parser.add_argument("--namespace", default="default", help="Kubernetes namespace")
    parser.add_argument("--app", default="icecream", help="App label value")
    parser.add_argument("--skip-crash", action="store_true", help="Skip the crash simulation")
    args = parser.parse_args()

    print(f"\n{'#' * 55}")
    print(f"  DevOps Observability & Fault Simulation Report")
    print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  App: {args.app}  |  Namespace: {args.namespace}")
    print(f"{'#' * 55}")

    monitor_pods(args.namespace, args.app)
    pod_name = fetch_logs(args.namespace, args.app)
    check_resources(args.namespace, args.app)
    describe_deployment(args.namespace, args.app)
    check_service(args.namespace, args.app)
    check_hpa(args.namespace)
    check_restart_count(args.namespace, args.app)

    if not args.skip_crash:
        print("\n  ⚠️  About to simulate a pod crash in 5 seconds...")
        print("  Press Ctrl+C to skip the crash simulation.")
        try:
            time.sleep(5)
            simulate_crash(args.namespace, args.app, pod_name)
        except KeyboardInterrupt:
            print("\n  Crash simulation skipped by user.")

    print(f"\n{'#' * 55}")
    print("  ✅ Observability Report Complete")
    print(f"{'#' * 55}\n")


if __name__ == "__main__":
    main()

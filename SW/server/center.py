import socket
import threading
import time
import sys
import json
import heapq
from collections import deque

UDP_IP = "0.0.0.0"
UDP_PORT_RX = 6010
EDGE_TIMEOUT = 15

graph = {}
graph_lock = threading.Lock()

def get_canonical_edge(node1, node2):
    return tuple(sorted((node1, node2)))

def parse_packet(packet_json):
    try:
        data = json.loads(packet_json)
        sender = data.get("sender")
        edges_from_packet = {}
        for k_str, v in data.get("edges", {}).items():
            nodes = tuple(k_str.split(','))
            if len(nodes) == 2:
                edges_from_packet[get_canonical_edge(nodes[0], nodes[1])] = v
        return sender, edges_from_packet
    except (json.JSONDecodeError, AttributeError):
        return None, None

def receiver_thread():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT_RX))
    print(f"[RX Thread] 리스닝 시작 (UDP Port: {UDP_PORT_RX})")

    while True:
        try:
            packet, addr = sock.recvfrom(1024)
            packet_str = packet.decode('utf-8')
            
            sender_id, received_edges = parse_packet(packet_str)
            if not sender_id:
                continue

            with graph_lock:
                for edge, data in received_edges.items():
                    if edge not in graph or data['timestamp'] > graph[edge]['timestamp']:
                        graph[edge] = data
        except Exception as e:
            print(f"[RX Thread] Error: {e}")

def cleaner_thread():
    while True:
        time.sleep(EDGE_TIMEOUT / 2)
        with graph_lock:
            now = time.time()
            edges_to_delete = []
            for edge, data in graph.items():
                if now - data['timestamp'] > EDGE_TIMEOUT:
                    edges_to_delete.append(edge)
            
            if edges_to_delete:
                for edge in edges_to_delete:
                    del graph[edge]
                print(f"\n[Cleaner Thread] {len(edges_to_delete)}개의 오래된 간선 삭제 (명령어를 입력하세요): ", end='')
                sys.stdout.flush()

def build_adjacency_list():
    adj = {}
    with graph_lock:
        for (u, v), data in graph.items():
            if u not in adj: adj[u] = []
            if v not in adj: adj[v] = []
            weight = abs(data.get('rssi', -100))
            adj[u].append((v, weight))
            adj[v].append((u, weight))
    return adj

def dijkstra(start_node, end_node):
    adj = build_adjacency_list()
    if start_node not in adj or end_node not in adj:
        return None, float('inf')

    distances = {node: float('inf') for node in adj}
    previous_nodes = {node: None for node in adj}
    distances[start_node] = 0
    
    pq = [(0, start_node)]

    while pq:
        current_distance, current_node = heapq.heappop(pq)

        if current_distance > distances[current_node]:
            continue

        if current_node == end_node:
            break

        for neighbor, weight in adj.get(current_node, []):
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node
                heapq.heappush(pq, (distance, neighbor))

    path = []
    current = end_node
    while current is not None:
        path.insert(0, current)
        current = previous_nodes[current]

    if path[0] == start_node:
        return path, distances[end_node]
    else:
        return None, float('inf')

def bfs(start_node):
    adj = build_adjacency_list()
    if start_node not in adj:
        return []

    visited = set()
    queue = deque([start_node])
    visited.add(start_node)
    
    reachable_nodes = []
    while queue:
        node = queue.popleft()
        reachable_nodes.append(node)
        for neighbor, weight in adj.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return reachable_nodes

if __name__ == "__main__":
    print("--- 서버(관제) 프로그램을 시작합니다 ---")

    rx = threading.Thread(target=receiver_thread, daemon=True)
    cl = threading.Thread(target=cleaner_thread, daemon=True)
    rx.start()
    cl.start()

    print("\n사용 가능한 명령어:")
    print("  map                          - 현재 전체 네트워크 맵을 표시합니다.")
    print("  nodes                        - 현재 활성화된 모든 노드를 표시합니다.")
    print("  bfs [start_node]             - 특정 노드에서 연결된 모든 노드를 탐색합니다.")
    print("  path [start_node] [end_node] - 두 노드 간 최적 경로를 계산합니다.")
    print("  exit                         - 프로그램을 종료합니다.")

    while True:
        try:
            cmd = input("\n명령어를 입력하세요: ").strip().split()
            if not cmd:
                continue

            if cmd[0] == "map":
                print("\n--- 현재 네트워크 맵 ---")
                with graph_lock:
                    if not graph: print("  (수신된 정보 없음)")
                    for edge, data in sorted(graph.items()):
                        print(f"  - {edge[0]:<10} <--> {edge[1]:<10} | RSSI: {data['rssi']:<4} | Updated: {time.time() - data['timestamp']:.1f}s ago")
            
            elif cmd[0] == "nodes":
                adj = build_adjacency_list()
                print("\n--- 활성화된 노드 ---")
                if not adj: print("  (없음)")
                else: print(f"  {', '.join(sorted(adj.keys()))}")
            
            elif cmd[0] == "bfs":
                if len(cmd) < 2: print("  사용법: bfs [start_node]")
                else:
                    reachable = bfs(cmd[1])
                    print(f"\n--- {cmd[1]} 에서 탐색 가능한 노드 (BFS) ---")
                    print(f"  -> {' -> '.join(reachable)}")

            elif cmd[0] == "path":
                if len(cmd) < 3: print("  사용법: path [start_node] [end_node]")
                else:
                    path, cost = dijkstra(cmd[1], cmd[2])
                    print(f"\n--- 최적 경로 탐색 ({cmd[1]} -> {cmd[2]}) ---")
                    if path:
                        print(f"  경로: {' -> '.join(path)}")
                        print(f"  총 비용 (낮을수록 좋음): {cost}")
                    else:
                        print("  경로를 찾을 수 없습니다.")

            elif cmd[0] == "exit":
                break
            
            else:
                print("  알 수 없는 명령어입니다.")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"  오류 발생: {e}")

    print("\n--- 서버(관제) 프로그램을 종료합니다. ---")
    sys.exit(0)

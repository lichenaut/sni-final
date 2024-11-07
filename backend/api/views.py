from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os
import shutil
import cv2
import subprocess
from glob import glob
import networkx as nx
import matplotlib.pyplot as plt


class Videoize(APIView):
    def post(self, request, *args, **kwargs):
        data_folder = request.data.get("data_folder")
        try:
            node_count = int(request.data.get("node_count"))
        except ValueError:
            return Response({"error": "Invalid node count provided."}, status=status.HTTP_400_BAD_REQUEST)
        show_uncircled = bool(request.data.get("show_uncircled"))

        root_dir = os.path.dirname(os.getcwd())
        extract_dir = os.path.expanduser(f"{root_dir}/data/{data_folder}/")
        file_paths = {
            "edges": glob(os.path.join(extract_dir, "*.edges")),
            "circles": glob(os.path.join(extract_dir, "*.circles")),
        }


        def read_files(file_list):
            data = []
            for file_path in file_list:
                with open(file_path, "r") as file:
                    lines = file.readlines()
                    cleaned_lines = [
                        line.replace("\n", "").replace("\t", " ").strip() for line in lines
                    ]
                    data.extend(cleaned_lines)
            return data

        edges_data = read_files(file_paths["edges"])[:node_count]
        circles_data = read_files(file_paths["circles"])[:node_count]

        G = nx.Graph()

        for edge in edges_data:
            u, v = map(int, edge.split())
            G.add_edge(u, v)

        circle_colors = {}
        nodes_with_circles = set()
        num_colors = len(circles_data)
        colors = plt.cm.get_cmap("hsv", num_colors)

        for index, circle in enumerate(circles_data):
            members = list(map(int, circle.split()[1:]))
            color = colors(index)[:3]

            for member in members:
                circle_colors[member] = color
                nodes_with_circles.add(member)

        if show_uncircled:
            for node in G.nodes():
                if node not in nodes_with_circles:
                    circle_colors[node] = (0.5, 0.5, 0.5)
                    nodes_with_circles.add(node)

        pos = nx.spring_layout(G)
        centrality = nx.betweenness_centrality(G)

        images_dir = f"{root_dir}/images/"
        if os.path.exists(images_dir):
            shutil.rmtree(images_dir)
        os.makedirs(images_dir)


        def gen_graph(i, show_title, edges_to_highlight=None):
            filtered_nodes = [node for node in G.nodes() if node in nodes_with_circles]
            filtered_colors = [circle_colors[node] for node in filtered_nodes]

            H = G.subgraph(filtered_nodes)

            plt.figure(figsize=(12, 12))
            nx.draw_networkx_nodes(H, pos, node_size=50, node_color=filtered_colors, alpha=0.6)
            nx.draw_networkx_edges(
                H,
                pos,
                edgelist=set(H.edges()) - set(edges_to_highlight or []),
                width=0.5,
                alpha=0.5,
                edge_color="black",
            )

            if edges_to_highlight:
                nx.draw_networkx_edges(
                    H, pos, edgelist=edges_to_highlight, width=1.5, alpha=0.8, edge_color="red"
                )

            if show_title:
                plt.title("Result")

            plt.axis("equal")
            plt.tight_layout()
            plt.savefig(os.path.join(images_dir, f"{i+1}.png"))
            plt.close()


        for i in range(node_count):
            highest_node = max(centrality, key=centrality.get)
            edges_to_remove = list(G.edges(highest_node))

            if not edges_to_remove:
                G.remove_edges_from(list(G.edges()))
                images = [img for img in os.listdir(images_dir) if img.endswith((".png"))]
                for j in range(len(images) // 5):
                    gen_graph(i + j, True)
                break

            gen_graph(i, False, edges_to_highlight=edges_to_remove)

            G.remove_edges_from(edges_to_remove)

            centrality = nx.betweenness_centrality(G)

        images = [img for img in os.listdir(images_dir) if img.endswith(('.png'))]

        images.sort(key=lambda x: int(os.path.splitext(x)[0]))

        first_image = cv2.imread(os.path.join(images_dir, images[0]))
        height, width, layers = first_image.shape

        public_dir = f"{root_dir}/frontend/public"

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        os.remove(f"{public_dir}/video.mp4")
        video = cv2.VideoWriter(f"{public_dir}/video.mp4", fourcc, len(images) / 30, (width, height))

        for image in images:
            img_path = os.path.join(images_dir, image)
            frame = cv2.imread(img_path)
            
            video.write(frame)

        video.release()

        def reencode_video(input_directory, output_directory):
            for filename in os.listdir(input_directory):
                if filename.endswith('.mp4'):
                    input_path = os.path.join(input_directory, filename)
                    output_path = os.path.join(output_directory, f'reencoded_video.mp4')

                    command = [
                        'ffmpeg',
                        '-i', input_path,
                        '-c:v', 'libx264',
                        '-c:a', 'aac',
                        '-strict', 'experimental',
                        output_path
                    ]

                    try:
                        subprocess.run(command, check=True)
                        print(f'Successfully re-encoded: {filename} to {output_path}')
                    except subprocess.CalledProcessError as e:
                        print(f'Error re-encoding {filename}: {e}')

        os.remove(f"{public_dir}/reencoded_video.mp4")
        reencode_video(public_dir, public_dir)

        return Response({"message": "Video generated and re-encoded successfully."}, status=status.HTTP_200_OK)
import numpy as np
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm  # For progress bar

# Helper function to process a chunk of query points in parallel
def process_chunk(query_chunk, points, n, rank):
    indices = []

    # Find rank 
    for query_point in tqdm(query_chunk, disable=(rank != 0)):
        distances = np.linalg.norm(points - query_point, axis=1)
        indices.append(list(np.argsort(distances)[:n]))

    return indices

def find_n_closest_points(query_points, points, n, n_jobs=16):
    # Split query points into roughly equal chunks
    chunks = np.array_split(query_points, n_jobs)

    # Use a ProcessPoolExecutor to run the process_chunk function in parallel
    with ProcessPoolExecutor(max_workers=n_jobs) as executor:
        # Map each chunk to a process with progress bar
        results = executor.map(process_chunk, chunks, [points]*n_jobs, [n]*n_jobs, list(range(n_jobs)))

    # Concatenate the results from all the processes
    indices = []
    for result in results:
        indices.extend(result)

    return indices
